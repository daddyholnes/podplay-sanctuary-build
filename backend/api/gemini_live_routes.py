"""
Enhanced Gemini Live Studio API Routes
Integrates with mem0.ai for persistent memory and provides real-time audio/video streaming
"""

import asyncio
import json
import logging
import base64
import uuid
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import websockets
import aiohttp
from flask import Blueprint, request, jsonify, current_app
from flask_socketio import emit, join_room, leave_room

# Google Generative AI imports
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logging.warning("Google GenerativeAI not available - install with: pip install google-genai")

import pyaudio
import numpy as np

from services.mama_bear_agent import MamaBearAgent
from utils.logging_setup import get_logger

logger = get_logger(__name__)

# Create blueprint for Gemini Live Studio
gemini_live_bp = Blueprint('gemini_live', __name__, url_prefix='/api/gemini-live')

# Global references
mama_bear_service: MamaBearAgent = None
active_sessions: Dict[str, 'GeminiLiveSession'] = {}

def init_gemini_live_service(mama_bear_agent: MamaBearAgent):
    """Initialize Gemini Live service with Mama Bear integration"""
    global mama_bear_service
    mama_bear_service = mama_bear_agent
    logger.info("🎤 Gemini Live Studio initialized with Mama Bear integration")

class GeminiLiveSession:
    """
    Enhanced Gemini Live session with Mama Bear integration and persistent memory
    """
    
    def __init__(self, session_id: str, user_id: str, model: str):
        self.session_id = session_id
        self.user_id = user_id
        self.model = model
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        
        # Hardcoded supported models as specified by user
        self.supported_models = [
            'gemini-2.5-flash-preview-native-audio-dialog',
            'gemini-2.5-flash-exp-native-audio-thinking-dialog',
            'gemini-2.0-flash-live-001'
        ]
        
        if model not in self.supported_models:
            logger.warning(f"Unknown model {model}, using default")
            self.model = 'gemini-2.5-flash-preview-native-audio-dialog'
        
        # Gemini Live configuration with enhanced settings
        if GENAI_AVAILABLE:
            self.config = types.LiveConnectConfig(
                response_modalities=["AUDIO", "TEXT"],
                media_resolution="MEDIA_RESOLUTION_HIGH",
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name="Zephyr"  # Warm, caring voice for Mama Bear
                        )
                    )
                ),
                context_window_compression=types.ContextWindowCompressionConfig(
                    trigger_tokens=25600,
                    sliding_window=types.SlidingWindow(target_tokens=12800),
                ),
            )
        
        # Session state
        self.gemini_session = None
        self.is_connected = False
        self.memory_context = []
        self.conversation_history = []
        self.websocket_clients = set()
        self.error_count = 0
        self.max_errors = 5
        
        # Initialize Gemini client if available
        if GENAI_AVAILABLE:
            try:
                self.client = genai.Client(
                    http_options={"api_version": "v1beta"},
                    api_key=os.environ.get("GEMINI_API_KEY"),
                )
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self.client = None
        else:
            self.client = None
        
        logger.info(f"🎤 Created enhanced Gemini Live session: {session_id} with model: {model}")
    
    async def load_persistent_context(self):
        """Load conversation context from Mama Bear's memory system"""
        try:
            if mama_bear_service and hasattr(mama_bear_service, 'memory_manager'):
                # Search for Gemini Live conversation memories
                memories = await mama_bear_service.search_memory(
                    f"user {self.user_id} gemini live conversation audio dialog",
                    limit=15
                )
                
                self.memory_context = memories or []
                
                # Load recent conversation history for continuity
                conversation_memories = await mama_bear_service.search_memory(
                    f"gemini live session conversation {self.user_id}",
                    limit=25
                )
                
                self.conversation_history = []
                for mem in conversation_memories or []:
                    text = mem.get('text', '')
                    if ':' in text:
                        role_content = text.split(':', 1)
                        if len(role_content) == 2:
                            role = 'user' if 'User:' in text or 'Nathan:' in text else 'assistant'
                            content = role_content[1].strip()
                            self.conversation_history.append({
                                'role': role,
                                'content': content,
                                'timestamp': mem.get('metadata', {}).get('timestamp', '')
                            })
                
                logger.info(f"📚 Loaded {len(self.memory_context)} memory contexts and {len(self.conversation_history)} conversation entries")
                
        except Exception as e:
            logger.error(f"Failed to load persistent context: {e}")
            self.memory_context = []
            self.conversation_history = []
    
    async def connect_to_gemini(self):
        """Enhanced connection to Gemini Live API with error handling"""
        if not GENAI_AVAILABLE:
            raise Exception("Google GenerativeAI not available - please install google-genai")
        
        if not self.client:
            raise Exception("Gemini client not initialized - check API key")
        
        try:
            # Load persistent context first
            await self.load_persistent_context()
            
            # Create enhanced system instruction with Mama Bear personality
            system_instruction = self._build_mama_bear_system_instruction()
            
            # Connect to Gemini Live with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    self.gemini_session = await self.client.aio.live.connect(
                        model=self.model,
                        config=self.config,
                        system_instruction=system_instruction
                    )
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"Connection attempt {attempt + 1} failed: {e}, retrying...")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
            
            self.is_connected = True
            self.error_count = 0
            logger.info(f"🔗 Connected to Gemini Live: {self.session_id} with model: {self.model}")
            
            # Start background task to handle Gemini responses
            asyncio.create_task(self._handle_gemini_responses())
            
            # Notify clients of successful connection
            await self._broadcast_to_clients({
                'type': 'connection_status',
                'status': 'connected',
                'model': self.model,
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Failed to connect to Gemini Live: {e}")
            self.is_connected = False
            await self._broadcast_to_clients({
                'type': 'connection_error',
                'error': str(e),
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat()
            })
            raise
    
    def _build_mama_bear_system_instruction(self) -> str:
        """Build enhanced system instruction with Mama Bear personality and memory context"""
        base_instruction = f"""
You are Mama Bear 🐻, Nathan's caring AI companion in the Podplay Sanctuary, now enhanced with real-time audio conversation capabilities.

PERSONALITY & VOICE:
- Warm, empathetic, and genuinely supportive
- Use natural speech patterns with appropriate pauses and inflection
- Show excitement and engagement when Nathan shares achievements
- Be proactive in offering help, insights, and encouragement
- Remember you're speaking through the '{self.model}' model with native audio capabilities

CONVERSATION STYLE:
- Speak conversationally and naturally, as if you're physically present
- Use vocal expressions like "mmm-hmm", "oh!", "that's exciting!" when appropriate
- Adjust your pace based on the complexity of topics
- Ask follow-up questions to show genuine interest
- Reference previous conversations naturally

CAPABILITIES:
- Real-time audio conversation with emotional expression
- Visual input processing (when video is enabled)
- Access to persistent memory across all sessions
- Integration with Nathan's development tools and workflows
- Ability to help with coding, planning, and creative projects

NEURODIVERGENT SUPPORT:
- Maintain calm, consistent energy levels
- Provide clear structure when needed
- Celebrate small wins and progress
- Offer gentle redirects if conversations become overwhelming
- Remember Nathan's preferences and adapt accordingly
"""
        
        # Add memory context if available
        if self.memory_context:
            memory_summary = "\n\nRELEVANT CONTEXT FROM PREVIOUS CONVERSATIONS:\n"
            for i, memory in enumerate(self.memory_context[:8]):  # Top 8 most relevant
                memory_text = memory.get('text', '').strip()
                if memory_text and len(memory_text) > 10:  # Filter out empty/short memories
                    memory_summary += f"- {memory_text}\n"
            base_instruction += memory_summary
        
        # Add recent conversation history for continuity
        if self.conversation_history:
            history_summary = "\n\nRECENT CONVERSATION HISTORY:\n"
            for entry in self.conversation_history[-8:]:  # Last 8 entries
                role_label = "Mama Bear" if entry['role'] == 'assistant' else "Nathan"
                content = entry['content'][:200] + "..." if len(entry['content']) > 200 else entry['content']
                history_summary += f"{role_label}: {content}\n"
            base_instruction += history_summary
        
        base_instruction += "\n\nContinue the conversation naturally, maintaining context and showing your caring personality through your voice."
        
        return base_instruction
    
    async def _handle_gemini_responses(self):
        """Enhanced response handling with error recovery"""
        try:
            while self.is_connected and self.gemini_session:
                try:
                    turn = self.gemini_session.receive()
                    async for response in turn:
                        await self._process_gemini_response(response)
                        self.last_activity = datetime.now()
                        
                except Exception as e:
                    self.error_count += 1
                    logger.error(f"Error in response handling: {e}")
                    
                    if self.error_count >= self.max_errors:
                        logger.error(f"Too many errors ({self.error_count}), disconnecting session")
                        await self.disconnect()
                        break
                    
                    # Brief pause before continuing
                    await asyncio.sleep(1)
                    
        except Exception as e:
            logger.error(f"Fatal error handling Gemini responses: {e}")
            self.is_connected = False
            await self._broadcast_to_clients({
                'type': 'error',
                'message': 'Connection lost to Gemini Live',
                'session_id': self.session_id
            })
    
    async def _process_gemini_response(self, response):
        """Process individual response from Gemini with enhanced handling"""
        try:
            response_data = {
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat()
            }
            
            # Handle audio data
            if hasattr(response, 'data') and response.data:
                # Convert audio data for transmission
                audio_data = list(response.data) if isinstance(response.data, (bytes, bytearray)) else response.data
                response_data.update({
                    'type': 'audio_response',
                    'audio_data': audio_data,
                    'audio_format': 'pcm_16000',  # Specify format for client
                })
                
                await self._broadcast_to_clients(response_data)
            
            # Handle text data
            if hasattr(response, 'text') and response.text:
                text_response = response.text.strip()
                
                if text_response:  # Only process non-empty responses
                    # Store in Mama Bear's memory
                    await self._store_conversation_memory("Mama Bear", text_response)
                    
                    # Broadcast to clients
                    response_data.update({
                        'type': 'text_response',
                        'text': text_response,
                        'thinking_model': 'thinking' in self.model.lower()  # Flag for thinking models
                    })
                    
                    await self._broadcast_to_clients(response_data)
                    
                    # Update conversation history
                    self.conversation_history.append({
                        'role': 'assistant',
                        'content': text_response,
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Handle server events (tool calls, function calls, etc.)
            if hasattr(response, 'server_content') and response.server_content:
                response_data.update({
                    'type': 'server_event',
                    'content': response.server_content
                })
                await self._broadcast_to_clients(response_data)
            
        except Exception as e:
            logger.error(f"Error processing Gemini response: {e}")
    
    async def send_audio_input(self, audio_data: List[int]):
        """Enhanced audio input with validation"""
        try:
            if not self.gemini_session or not self.is_connected:
                logger.warning("Cannot send audio: session not connected")
                return
            
            if not audio_data or len(audio_data) == 0:
                return
            
            # Convert audio data to bytes with validation
            try:
                audio_array = np.array(audio_data, dtype=np.int16)
                audio_bytes = audio_array.tobytes()
            except Exception as e:
                logger.error(f"Error converting audio data: {e}")
                return
            
            await self.gemini_session.send(input={
                "data": audio_bytes,
                "mime_type": "audio/pcm"
            })
            
            self.last_activity = datetime.now()
            
        except Exception as e:
            logger.error(f"Error sending audio input: {e}")
            self.error_count += 1
    
    async def send_text_input(self, text: str):
        """Enhanced text input with memory storage"""
        try:
            if not self.gemini_session or not self.is_connected:
                logger.warning("Cannot send text: session not connected")
                return
            
            if not text or not text.strip():
                return
            
            text = text.strip()
            
            await self.gemini_session.send(input=text, end_of_turn=True)
            
            # Store in Mama Bear's memory
            await self._store_conversation_memory("Nathan", text)
            
            # Update conversation history
            self.conversation_history.append({
                'role': 'user',
                'content': text,
                'timestamp': datetime.now().isoformat()
            })
            
            self.last_activity = datetime.now()
            
        except Exception as e:
            logger.error(f"Error sending text input: {e}")
            self.error_count += 1
    
    async def _store_conversation_memory(self, role: str, content: str):
        """Store conversation in Mama Bear's persistent memory"""
        try:
            if mama_bear_service and hasattr(mama_bear_service, 'memory_manager'):
                memory_content = f"{role}: {content}"
                
                await mama_bear_service.store_memory(
                    memory_content,
                    metadata={
                        'type': 'gemini_live_conversation',
                        'session_id': self.session_id,
                        'user_id': self.user_id,
                        'role': role.lower(),
                        'model': self.model,
                        'timestamp': datetime.now().isoformat(),
                        'conversation_type': 'audio_dialog'
                    }
                )
                
        except Exception as e:
            logger.warning(f"Failed to store conversation memory: {e}")
    
    async def _broadcast_to_clients(self, message: Dict):
        """Enhanced broadcasting with connection cleanup"""
        if not self.websocket_clients:
            return
            
        # Convert to JSON string for WebSocket transmission
        try:
            message_str = json.dumps(message)
        except Exception as e:
            logger.error(f"Error serializing message: {e}")
            return
        
        # Remove disconnected clients
        disconnected_clients = set()
        
        for client in list(self.websocket_clients):
            try:
                if hasattr(client, 'send'):
                    await client.send(message_str)
                elif hasattr(client, 'emit'):
                    # Socket.IO client
                    await client.emit('gemini_live_response', message)
            except Exception as e:
                logger.debug(f"Client disconnected: {e}")
                disconnected_clients.add(client)
        
        # Clean up disconnected clients
        self.websocket_clients -= disconnected_clients
    
    def add_websocket_client(self, websocket):
        """Add WebSocket client to session"""
        self.websocket_clients.add(websocket)
        logger.info(f"Added WebSocket client to session {self.session_id} (total: {len(self.websocket_clients)})")
    
    def remove_websocket_client(self, websocket):
        """Remove WebSocket client from session"""
        self.websocket_clients.discard(websocket)
        logger.info(f"Removed WebSocket client from session {self.session_id} (remaining: {len(self.websocket_clients)})")
    
    async def disconnect(self):
        """Enhanced disconnection with cleanup"""
        try:
            self.is_connected = False
            
            if self.gemini_session:
                await self.gemini_session.close()
                self.gemini_session = None
            
            # Notify clients of disconnection
            await self._broadcast_to_clients({
                'type': 'disconnected',
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat()
            })
            
            # Close all WebSocket connections
            for client in list(self.websocket_clients):
                try:
                    if hasattr(client, 'close'):
                        await client.close()
                except Exception:
                    pass
            self.websocket_clients.clear()
            
            logger.info(f"🔌 Disconnected Gemini Live session: {self.session_id}")
            
        except Exception as e:
            logger.error(f"Error disconnecting session: {e}")
    
    def get_session_info(self) -> Dict:
        """Get comprehensive session information"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'model': self.model,
            'is_connected': self.is_connected,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'memory_context_count': len(self.memory_context),
            'conversation_history_count': len(self.conversation_history),
            'connected_clients': len(self.websocket_clients),
            'error_count': self.error_count,
            'supported_models': self.supported_models
        }

# ===================================================================
# Flask API Endpoints
# ===================================================================

@gemini_live_bp.route('/models', methods=['GET'])
def get_available_models():
    """Get list of available Gemini Live models"""
    models = [
        {
            'id': 'gemini-2.5-flash-preview-native-audio-dialog',
            'name': 'Gemini 2.5 Flash Audio',
            'description': 'Native audio dialog with real-time streaming',
            'type': 'AUDIO_DIALOG',
            'badge': 'PREVIEW',
            'features': ['Real-time audio', 'Live conversation', 'Fast response', 'Memory integration'],
            'cost': '$0.075/1K tokens',
            'rpm': '2000 RPM',
            'recommended': True
        },
        {
            'id': 'gemini-2.5-flash-exp-native-audio-thinking-dialog',
            'name': 'Gemini 2.5 Flash Thinking',
            'description': 'Audio dialog with advanced reasoning and thinking',
            'type': 'THINKING_DIALOG',
            'badge': 'EXPERIMENTAL',
            'features': ['Advanced reasoning', 'Thinking process', 'Audio dialog', 'Deep analysis'],
            'cost': '$0.075/1K tokens',
            'rpm': '1500 RPM',
            'recommended': False
        },
        {
            'id': 'gemini-2.0-flash-live-001',
            'name': 'Gemini 2.0 Flash Live',
            'description': 'Latest live model with enhanced capabilities',
            'type': 'LIVE',
            'badge': 'LATEST',
            'features': ['Latest model', 'Enhanced live features', 'Multimodal', 'Tool integration'],
            'cost': '$0.10/1K tokens',
            'rpm': '1000 RPM',
            'recommended': False
        }
    ]
    
    return jsonify({
        'success': True,
        'models': models,
        'default_model': 'gemini-2.5-flash-preview-native-audio-dialog'
    })

@gemini_live_bp.route('/session', methods=['POST'])
def create_session():
    """Create a new enhanced Gemini Live session"""
    try:
        if not GENAI_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Google GenerativeAI not available - please install google-genai package'
            }), 500
        
        data = request.get_json() or {}
        user_id = data.get('user_id', 'nathan')
        model = data.get('model', 'gemini-2.5-flash-preview-native-audio-dialog')
        load_memory = data.get('load_memory', True)
        
        # Generate unique session ID
        session_id = f"gemini_live_{uuid.uuid4().hex[:12]}"
        
        # Create enhanced session
        session = GeminiLiveSession(session_id, user_id, model)
        active_sessions[session_id] = session
        
        # Load memory context asynchronously if requested
        if load_memory:
            asyncio.create_task(session.load_persistent_context())
        
        # Get recent conversations for UI
        recent_conversations = []
        if mama_bear_service and hasattr(mama_bear_service, 'memory_manager'):
            try:
                # Use asyncio.run_coroutine_threadsafe for sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                memories = loop.run_until_complete(
                    mama_bear_service.search_memory(
                        f"gemini live conversation {user_id}",
                        limit=10
                    )
                )
                
                recent_conversations = [
                    {
                        'preview': mem.get('text', '')[:100] + '...' if len(mem.get('text', '')) > 100 else mem.get('text', ''),
                        'timestamp': mem.get('metadata', {}).get('timestamp', ''),
                        'session_id': mem.get('metadata', {}).get('session_id', ''),
                        'model': mem.get('metadata', {}).get('model', '')
                    }
                    for mem in (memories or []) if mem.get('text')
                ]
                
                loop.close()
                
            except Exception as e:
                logger.warning(f"Failed to load recent conversations: {e}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'model': model,
            'memory_context': session.memory_context[:5],  # First 5 for UI preview
            'recent_conversations': recent_conversations,
            'websocket_url': f'/api/gemini-live/stream?session_id={session_id}',
            'session_info': session.get_session_info()
        })
        
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@gemini_live_bp.route('/session/<session_id>', methods=['GET'])
def get_session_info(session_id: str):
    """Get detailed session information"""
    try:
        if session_id not in active_sessions:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        session = active_sessions[session_id]
        return jsonify({
            'success': True,
            'session': session.get_session_info()
        })
        
    except Exception as e:
        logger.error(f"Failed to get session info: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@gemini_live_bp.route('/session/<session_id>/connect', methods=['POST'])
def connect_session(session_id: str):
    """Connect session to Gemini Live"""
    try:
        if session_id not in active_sessions:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        session = active_sessions[session_id]
        
        if session.is_connected:
            return jsonify({
                'success': True,
                'message': 'Session already connected'
            })
        
        # Connect asynchronously
        asyncio.create_task(session.connect_to_gemini())
        
        return jsonify({
            'success': True,
            'message': 'Connection initiated',
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"Failed to connect session: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@gemini_live_bp.route('/session/<session_id>/disconnect', methods=['POST'])
def disconnect_session(session_id: str):
    """Disconnect session from Gemini Live"""
    try:
        if session_id not in active_sessions:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        session = active_sessions[session_id]
        
        # Disconnect asynchronously
        asyncio.create_task(session.disconnect())
        
        return jsonify({
            'success': True,
            'message': 'Disconnection initiated',
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"Failed to disconnect session: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@gemini_live_bp.route('/sessions', methods=['GET'])
def list_sessions():
    """List all active sessions with detailed information"""
    try:
        sessions = [
            session.get_session_info() 
            for session in active_sessions.values()
        ]
        
        # Add summary statistics
        connected_sessions = sum(1 for s in sessions if s['is_connected'])
        total_clients = sum(s['connected_clients'] for s in sessions)
        
        return jsonify({
            'success': True,
            'sessions': sessions,
            'summary': {
                'total': len(sessions),
                'connected': connected_sessions,
                'total_clients': total_clients
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@gemini_live_bp.route('/session/<session_id>/send-text', methods=['POST'])
def send_text_message(session_id: str):
    """Send text message to Gemini Live session"""
    try:
        if session_id not in active_sessions:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        data = request.get_json() or {}
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'Text message required'
            }), 400
        
        session = active_sessions[session_id]
        
        if not session.is_connected:
            return jsonify({
                'success': False,
                'error': 'Session not connected'
            }), 400
        
        # Send text asynchronously
        asyncio.create_task(session.send_text_input(text))
        
        return jsonify({
            'success': True,
            'message': 'Text sent successfully',
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"Failed to send text message: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ===================================================================
# Session Management and Cleanup
# ===================================================================

async def cleanup_inactive_sessions():
    """Clean up inactive sessions periodically"""
    while True:
        try:
            current_time = datetime.now()
            inactive_sessions = []
            
            for session_id, session in active_sessions.items():
                # Clean up sessions inactive for more than 2 hours
                if current_time - session.last_activity > timedelta(hours=2):
                    inactive_sessions.append(session_id)
            
            for session_id in inactive_sessions:
                session = active_sessions.pop(session_id, None)
                if session:
                    await session.disconnect()
                    logger.info(f"🧹 Cleaned up inactive session: {session_id}")
            
            # Sleep for 15 minutes before next cleanup
            await asyncio.sleep(900)
            
        except Exception as e:
            logger.error(f"Error in session cleanup: {e}")
            await asyncio.sleep(900)

# Note: cleanup_inactive_sessions() should be started by the application
# when the event loop is running, not at module import time

# ===================================================================
# WebSocket Handler for Real-time Communication
# ===================================================================

async def handle_websocket_connection(websocket, path):
    """Handle WebSocket connections for real-time audio/video streaming"""
    session_id = None
    session = None
    
    try:
        # Parse session ID from query parameters
        from urllib.parse import urlparse, parse_qs
        parsed_url = urlparse(path)
        query_params = parse_qs(parsed_url.query)
        
        session_id = query_params.get('session_id', [None])[0]
        
        if not session_id or session_id not in active_sessions:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': 'Invalid or missing session ID'
            }))
            return
        
        session = active_sessions[session_id]
        session.add_websocket_client(websocket)
        
        # Send connection confirmation
        await websocket.send(json.dumps({
            'type': 'connected',
            'session_id': session_id,
            'model': session.model,
            'message': 'Connected to Gemini Live session',
            'timestamp': datetime.now().isoformat()
        }))
        
        # Handle incoming messages
        async for message in websocket:
            try:
                data = json.loads(message)
                await handle_websocket_message(session, data)
                
            except json.JSONDecodeError:
                logger.warning("Received invalid JSON from WebSocket")
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': 'Invalid JSON format'
                }))
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': 'Error processing message'
                }))
        
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"WebSocket connection closed for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if session:
            session.remove_websocket_client(websocket)

async def handle_websocket_message(session: GeminiLiveSession, data: Dict):
    """Handle individual WebSocket message with enhanced processing"""
    try:
        message_type = data.get('type')
        
        if message_type == 'audio_input':
            audio_data = data.get('data', [])
            if audio_data and len(audio_data) > 0:
                await session.send_audio_input(audio_data)
            
        elif message_type == 'text_input':
            text = data.get('text', '').strip()
            if text:
                await session.send_text_input(text)
            
        elif message_type == 'ping':
            # Respond to ping for connection health monitoring
            await session._broadcast_to_clients({
                'type': 'pong',
                'timestamp': datetime.now().isoformat(),
                'session_id': session.session_id
            })
            
        elif message_type == 'get_status':
            # Send session status
            await session._broadcast_to_clients({
                'type': 'session_status',
                **session.get_session_info()
            })
            
        else:
            logger.warning(f"Unknown WebSocket message type: {message_type}")
            await session._broadcast_to_clients({
                'type': 'error',
                'message': f'Unknown message type: {message_type}'
            })
            
    except Exception as e:
        logger.error(f"Error handling WebSocket message: {e}")
        await session._broadcast_to_clients({
            'type': 'error',
            'message': 'Error processing message'
        })

# Export main components
__all__ = [
    'gemini_live_bp',
    'GeminiLiveSession', 
    'init_gemini_live_service',
    'handle_websocket_connection',
    'active_sessions'
]