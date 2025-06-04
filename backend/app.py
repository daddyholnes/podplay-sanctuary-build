#!/usr/bin/env python3
"""
Podplay Sanctuary - Enhanced Flask Application
Nathan's AI-Powered Development Sanctuary with Mama Bear Agent
Features: Error handling, service monitoring, enhanced SocketIO, Docker integration
"""

import os
import sys
import logging
import asyncio
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify, g
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from dotenv import load_dotenv
import threading
import time

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import our services
from services.ai_orchestrator import AIOrchestrator
from services.mama_bear_agent import MamaBearAgent
from services.scout_agent import ScoutAgent
from services.workspace_manager import WorkspaceManager
from services.vertex_ai_agent_manager import VertexAIAgentManager
from models.database import init_database
from utils.memory_manager import MemoryManager
from utils.logging_setup import setup_logging

# Import API routes
from api.mcp_routes import mcp_bp, init_mcp_routes
from api.workspace_routes import workspace_bp, init_workspace_routes
from api.nixos_routes import nixos_bp
from api.code_server_routes import code_server_bp
from api.orchestrator_routes import orchestrator_bp
from api.gemini_live_routes import gemini_live_bp, init_gemini_live_service

# Configure enhanced logging
setup_logging()
logger = logging.getLogger(__name__)

# Service Management and Health Monitoring
class ServiceManager:
    """Manages service lifecycle and health monitoring"""
    
    def __init__(self):
        self.services = {}
        self.health_status = {}
        self.startup_time = datetime.now()
        
    def register_service(self, name: str, instance: Any, health_check_fn=None):
        """Register a service for monitoring"""
        self.services[name] = {
            'instance': instance,
            'health_check': health_check_fn,
            'status': 'active',
            'last_check': datetime.now()
        }
        
    def check_service_health(self, name: str) -> bool:
        """Check health of a specific service"""
        if name not in self.services:
            return False
            
        service = self.services[name]
        try:
            if service['health_check']:
                healthy = service['health_check']()
            else:
                healthy = service['instance'] is not None
                
            service['status'] = 'healthy' if healthy else 'unhealthy'
            service['last_check'] = datetime.now()
            return healthy
        except Exception as e:
            logger.error(f"Health check failed for {name}: {e}")
            service['status'] = 'error'
            return False
            
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        all_services = {}
        for name in self.services:
            all_services[name] = self.check_service_health(name)
            
        return {
            'overall_status': 'healthy' if all(all_services.values()) else 'degraded',
            'services': all_services,
            'uptime_seconds': (datetime.now() - self.startup_time).total_seconds()
        }

# Initialize Flask app with enhanced configuration
app = Flask(__name__)
app.config.update({
    'SECRET_KEY': os.getenv('SECRET_KEY', 'sanctuary_mama_bear_secret_dev'),
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB max file upload
    'JSON_SORT_KEYS': False,
    'JSONIFY_PRETTYPRINT_REGULAR': True if os.getenv('FLASK_ENV') == 'development' else False
})

# Configure CORS with enhanced origins
cors_origins = [
    "http://localhost:3000", 
    "http://localhost:5173", 
    "https://8001-*.public.scrapybara.com",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173"
]

CORS(app, origins=cors_origins, supports_credentials=True)

# Initialize SocketIO with enhanced configuration
socketio = SocketIO(
    app, 
    cors_allowed_origins=cors_origins,
    logger=True if os.getenv('FLASK_ENV') == 'development' else False,
    engineio_logger=True if os.getenv('FLASK_ENV') == 'development' else False,
    async_mode='threading',
    ping_timeout=60,
    ping_interval=25,
    max_http_buffer_size=1000000
)

# Initialize service manager
service_manager = ServiceManager()

# Global service instances
ai_orchestrator = None
mama_bear = None
scout_agent = None
workspace_manager = None
memory_manager = None
vertex_agent_manager = None

# Connected clients tracking
connected_clients = set()
client_contexts = {}

def safe_emit(event: str, data: Dict[str, Any], to: Optional[str] = None, room: Optional[str] = None):
    """Safely emit SocketIO events with error handling"""
    try:
        if to:
            socketio.emit(event, data, to=to)
        elif room:
            socketio.emit(event, data, to=room)  # Use 'to' parameter for rooms as well
        else:
            socketio.emit(event, data)
    except Exception as e:
        logger.error(f"Failed to emit {event}: {e}")

def initialize_services():
    """Initialize all AI services and dependencies with enhanced error handling"""
    global ai_orchestrator, mama_bear, scout_agent, workspace_manager, memory_manager, vertex_agent_manager
    
    try:
        logger.info("🐻 Initializing Podplay Sanctuary services...")
        
        # Initialize database
        logger.info("📊 Initializing database...")
        init_database()
        service_manager.register_service('database', True)
        
        # Initialize memory manager
        logger.info("🧠 Initializing memory manager...")
        memory_manager = MemoryManager()
        service_manager.register_service('memory_manager', memory_manager)
        
        # Initialize Vertex AI agent manager (optional)
        try:
            logger.info("🤖 Initializing Vertex AI Agent Manager...")
            vertex_agent_manager = VertexAIAgentManager()
            service_manager.register_service('vertex_ai', vertex_agent_manager)
            logger.info("✅ Vertex AI Agent Manager initialized")
        except Exception as e:
            logger.warning(f"⚠️ Vertex AI integration not available: {e}")
            vertex_agent_manager = None
            service_manager.register_service('vertex_ai', None)
        
        # Initialize AI orchestrator
        logger.info("🎯 Initializing AI orchestrator...")
        ai_orchestrator = AIOrchestrator()
        service_manager.register_service('ai_orchestrator', ai_orchestrator)
        
        # Initialize agents
        logger.info("🐻 Initializing Mama Bear agent...")
        mama_bear = MamaBearAgent(ai_orchestrator)
        service_manager.register_service('mama_bear', mama_bear)
        
        logger.info("🔍 Initializing Scout agent...")
        scout_agent = ScoutAgent(ai_orchestrator)
        service_manager.register_service('scout_agent', scout_agent)
        
        logger.info("🛠️ Initializing workspace manager...")
        workspace_manager = WorkspaceManager()
        service_manager.register_service('workspace_manager', workspace_manager)
        
        # Initialize API routes with service dependencies
        logger.info("🔗 Initializing API routes...")
        init_mcp_routes(scout_agent, vertex_agent_manager)
        init_workspace_routes(workspace_manager)
        init_gemini_live_service(mama_bear)
        
        logger.info("🎉 All services initialized successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error initializing services: {e}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        raise

def handle_service_error(service_name: str, error: Exception, user_id: Optional[str] = None):
    """Handle service errors gracefully"""
    error_msg = f"Service {service_name} encountered an error: {str(error)}"
    logger.error(error_msg)
    
    if user_id:
        safe_emit('service_error', {
            'service': service_name,
            'message': f"The {service_name} service is temporarily unavailable. Please try again.",
            'timestamp': datetime.now().isoformat()
        }, to=user_id)

# Enhanced API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Enhanced health check endpoint with detailed service status"""
    try:
        health_info = service_manager.get_overall_health()
        
        return jsonify({
            'status': health_info['overall_status'],
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': health_info['uptime_seconds'],
            'services': {
                'mama_bear': health_info['services'].get('mama_bear', False),
                'scout_agent': health_info['services'].get('scout_agent', False),
                'workspace_manager': health_info['services'].get('workspace_manager', False),
                'memory_manager': health_info['services'].get('memory_manager', False),
                'vertex_ai': health_info['services'].get('vertex_ai', False),
                'database': health_info['services'].get('database', False)
            },
            'connected_clients': len(connected_clients),
            'environment': os.getenv('FLASK_ENV', 'production')
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Health check failed',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Get available AI agents with enhanced status information"""
    try:
        return jsonify({
            'agents': [
                {
                    'id': 'mama_bear',
                    'name': 'Mama Bear',
                    'description': 'Your caring AI development assistant',
                    'emoji': '🐻',
                    'status': 'active' if mama_bear else 'inactive',
                    'capabilities': [
                        'natural_language_chat',
                        'code_assistance',
                        'project_planning',
                        'emotional_support',
                        'context_awareness',
                        'vertex_ai_integration'
                    ],
                    'health': service_manager.check_service_health('mama_bear')
                },
                {
                    'id': 'scout',
                    'name': 'Scout',
                    'description': 'Autonomous development agent',
                    'emoji': '🔍',
                    'status': 'active' if scout_agent else 'inactive',
                    'capabilities': [
                        'autonomous_development',
                        'code_generation',
                        'environment_setup',
                        'project_execution',
                        'mcp_integration'
                    ],
                    'health': service_manager.check_service_health('scout_agent')
                }
            ],
            'total_agents': 2,
            'active_agents': sum(1 for agent in [mama_bear, scout_agent] if agent is not None)
        }), 200
    except Exception as e:
        logger.error(f"Failed to get agents: {e}")
        return jsonify({'error': 'Failed to retrieve agent information'}), 500

@app.route('/api/system/status', methods=['GET'])
def system_status():
    """Get detailed system status"""
    try:
        return jsonify({
            'system': {
                'status': 'operational',
                'timestamp': datetime.now().isoformat(),
                'uptime_seconds': (datetime.now() - service_manager.startup_time).total_seconds(),
                'python_version': sys.version,
                'environment': os.getenv('FLASK_ENV', 'production')
            },
            'services': service_manager.health_status,
            'websocket': {
                'connected_clients': len(connected_clients),
                'status': 'active'
            }
        }), 200
    except Exception as e:
        logger.error(f"System status check failed: {e}")
        return jsonify({'error': 'System status unavailable'}), 500

# Enhanced Socket.IO Events with Better Error Handling
@socketio.on('connect')
def handle_connect():
    """Handle client connection with enhanced logging and setup"""
    try:
        user_id = request.sid
        client_ip = request.environ.get('REMOTE_ADDR', 'unknown')
        
        logger.info(f"🔌 Client connected: {user_id} from {client_ip}")
        
        # Add to connected clients
        connected_clients.add(user_id)
        client_contexts[user_id] = {
            'connected_at': datetime.now(),
            'ip_address': client_ip,
            'conversations': []
        }
        
        # Join general room
        join_room('sanctuary')
        
        # Send connection confirmation
        safe_emit('connection_established', {
            'user_id': user_id,
            'message': '🐻 Welcome to your Podplay Sanctuary! Mama Bear is here to help.',
            'timestamp': datetime.now().isoformat(),
            'services_available': {
                'mama_bear': mama_bear is not None,
                'scout': scout_agent is not None,
                'workspace_manager': workspace_manager is not None
            }
        }, to=user_id)
        
    except Exception as e:
        logger.error(f"Error handling client connection: {e}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection with cleanup"""
    try:
        user_id = request.sid
        logger.info(f"🔌 Client disconnected: {user_id}")
        
        # Clean up client tracking
        connected_clients.discard(user_id)
        if user_id in client_contexts:
            del client_contexts[user_id]
        
        # Leave rooms
        leave_room('sanctuary')
        
    except Exception as e:
        logger.error(f"Error handling client disconnection: {e}")

@socketio.on('mama_bear_chat')
def handle_mama_bear_chat(data):
    """Handle Mama Bear chat messages with enhanced error handling"""
    user_id = request.sid
    
    try:
        # Validate input
        if not data or not isinstance(data, dict):
            safe_emit('error', {'message': 'Invalid message format'}, to=user_id)
            return
            
        message_content = data.get('content', '').strip()
        if not message_content:
            safe_emit('error', {'message': 'Empty message received'}, to=user_id)
            return
            
        conversation_id = data.get('conversation_id', f'conv_{user_id}')
        
        logger.info(f"🐻 Mama Bear chat from {user_id}: {message_content[:100]}...")
        
        # Check service availability
        if not mama_bear:
            safe_emit('mama_bear_response', {
                'response': '🐻 I\'m still waking up! Please wait a moment while I get ready to help you.',
                'timestamp': datetime.now().isoformat(),
                'status': 'service_unavailable'
            }, to=user_id)
            return
        
        # Emit typing indicator
        safe_emit('mama_bear_typing', {'is_typing': True}, to=user_id)
        
        try:
            # Process with Mama Bear
            response = mama_bear.process_message({
                'content': message_content,
                'user_id': user_id,
                'conversation_id': conversation_id,
                'timestamp': datetime.now().isoformat(),
                'attachments': data.get('attachments', [])
            })
            
            # Stop typing indicator
            safe_emit('mama_bear_typing', {'is_typing': False}, to=user_id)
            
            # Send response
            safe_emit('mama_bear_response', {
                'response': response.get('response', 'I\'m sorry, I\'m having trouble right now. Please try again.'),
                'suggestions': response.get('suggestions', []),
                'actions': response.get('suggested_actions', []),
                'model_used': response.get('model_used', 'unknown'),
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }, to=user_id)
            
        except Exception as e:
            safe_emit('mama_bear_typing', {'is_typing': False}, to=user_id)
            handle_service_error('mama_bear', e, user_id)
            
    except Exception as e:
        logger.error(f"❌ Error in mama_bear_chat: {e}")
        safe_emit('error', {
            'message': 'Something went wrong with Mama Bear. Please try again.',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, to=user_id)

@socketio.on('scout_request')
def handle_scout_request(data):
    """Handle Scout agent requests with enhanced error handling"""
    user_id = request.sid
    
    try:
        # Validate input
        if not data or not isinstance(data, dict):
            safe_emit('error', {'message': 'Invalid request format'}, to=user_id)
            return
            
        task_description = data.get('task', '').strip()
        if not task_description:
            safe_emit('error', {'message': 'Empty task description received'}, to=user_id)
            return
        
        logger.info(f"🔍 Scout request from {user_id}: {task_description[:100]}...")
        
        if not scout_agent:
            safe_emit('error', {
                'message': 'Scout agent is not available right now.',
                'timestamp': datetime.now().isoformat()
            }, to=user_id)
            return
        
        try:
            # Process with Scout
            result = scout_agent.process_task({
                'task': task_description,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            })
            
            safe_emit('scout_response', {
                **result,
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            }, to=user_id)
            
        except Exception as e:
            handle_service_error('scout', e, user_id)
            
    except Exception as e:
        logger.error(f"❌ Error in scout_request: {e}")
        safe_emit('error', {
            'message': 'Scout encountered an error. Please try again.',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, to=user_id)

@socketio.on('create_workspace')
def handle_create_workspace(data):
    """Handle workspace creation requests with enhanced validation"""
    user_id = request.sid
    
    try:
        # Validate input
        if not data or not isinstance(data, dict):
            safe_emit('error', {'message': 'Invalid workspace configuration'}, to=user_id)
            return
            
        workspace_config = data.get('config', {})
        if not workspace_config:
            safe_emit('error', {'message': 'Workspace configuration required'}, to=user_id)
            return
        
        logger.info(f"🛠️ Workspace creation request from {user_id}")
        
        if not workspace_manager:
            safe_emit('error', {
                'message': 'Workspace manager is not available.',
                'timestamp': datetime.now().isoformat()
            }, to=user_id)
            return
        
        try:
            result = workspace_manager.create_workspace(workspace_config)
            safe_emit('workspace_created', {
                **result,
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            }, to=user_id)
            
        except Exception as e:
            handle_service_error('workspace_manager', e, user_id)
            
    except Exception as e:
        logger.error(f"❌ Error creating workspace: {e}")
        safe_emit('error', {
            'message': 'Failed to create workspace. Please try again.',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, to=user_id)

# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}")
    logger.error(f"Stack trace: {traceback.format_exc()}")
    return jsonify({'error': 'An unexpected error occurred'}), 500

# Register API blueprints
app.register_blueprint(mcp_bp)
app.register_blueprint(workspace_bp)
app.register_blueprint(nixos_bp)
app.register_blueprint(code_server_bp)
app.register_blueprint(orchestrator_bp)
app.register_blueprint(gemini_live_bp)

# Startup and shutdown handlers
@app.teardown_appcontext
def shutdown_session(exception=None):
    """Clean up after each request"""
    if exception:
        logger.error(f"Request ended with exception: {exception}")

def run_background_tasks():
    """Run background maintenance tasks"""
    def background_loop():
        while True:
            try:
                # Periodic health checks
                service_manager.get_overall_health()
                
                # Clean up disconnected clients
                current_time = datetime.now()
                for client_id in list(client_contexts.keys()):
                    if client_id not in connected_clients:
                        client_contexts.pop(client_id, None)
                
                time.sleep(60)  # Run every minute
                
            except Exception as e:
                logger.error(f"Background task error: {e}")
                time.sleep(60)
    
    # Start background thread
    background_thread = threading.Thread(target=background_loop, daemon=True)
    background_thread.start()
    logger.info("🔄 Background tasks started")

if __name__ == '__main__':
    try:
        # Initialize services
        logger.info("🏗️ Starting service initialization...")
        if not initialize_services():
            logger.error("❌ Service initialization failed")
            sys.exit(1)
        
        # Start background tasks
        run_background_tasks()
        
        # Get configuration
        port = int(os.getenv('PORT', 5000))
        host = os.getenv('HOST', '0.0.0.0')
        debug = os.getenv('FLASK_ENV') == 'development'
        
        logger.info(f"🚀 Starting Podplay Sanctuary on {host}:{port}")
        logger.info(f"🐻 Mama Bear is ready to help!")
        logger.info(f"🔍 Scout agent is standing by!")
        logger.info(f"🛠️ Workspace manager is initialized!")
        
        # Run the app
        socketio.run(
            app,
            host=host,
            port=port,
            debug=debug,
            allow_unsafe_werkzeug=True,
            use_reloader=False  # Disable reloader to prevent double initialization
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down gracefully...")
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        sys.exit(1)
    finally:
        logger.info("👋 Podplay Sanctuary has shut down")