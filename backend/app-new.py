#!/usr/bin/env python3
"""
Podplay Sanctuary - Main Flask Application
Nathan's AI-Powered Development Sanctuary with Mama Bear Agent
"""

import os
import sys
import logging
import asyncio
from datetime import datetime
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from dotenv import load_dotenv

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Configure logging first
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.getenv('LOG_FILE', 'mama_bear.log')),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

try:
    # Import our services with error handling
    from services.ai_orchestrator import AIOrchestrator
    from services.mama_bear_agent import MamaBearAgent
    from services.scout_agent import ScoutAgent
    from services.workspace_manager import WorkspaceManager
    from services.vertex_ai_agent_manager import VertexAIAgentManager
    from models.database import init_database
    from utils.memory_manager import MemoryManager
    
    # Import API routes
    from api.mcp_routes import mcp_bp, init_mcp_routes
    from api.workspace_routes import workspace_bp, init_workspace_routes
    from api.nixos_routes import nixos_bp
    from api.code_server_routes import code_server_bp
    from api.orchestrator_routes import orchestrator_bp
    from api.gemini_live_routes import gemini_live_bp, init_gemini_live_service
    
    logger.info("✅ All imports successful")
    
except ImportError as e:
    logger.error(f"❌ Import error: {e}")
    sys.exit(1)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'sanctuary_mama_bear_secret_dev')

# Configure CORS with proper origins
cors_origins = [
    "http://localhost:3000", 
    "http://localhost:5173", 
    "https://8001-*.public.scrapybara.com",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173"
]

CORS(app, origins=cors_origins, supports_credentials=True)

# Initialize SocketIO with proper configuration
socketio = SocketIO(
    app, 
    cors_allowed_origins=cors_origins,
    logger=True, 
    engineio_logger=False,  # Reduce noise
    async_mode='threading'
)

# Global service instances
ai_orchestrator = None
mama_bear = None
scout_agent = None
workspace_manager = None
memory_manager = None
vertex_agent_manager = None

def initialize_services():
    """Initialize all AI services and dependencies"""
    global ai_orchestrator, mama_bear, scout_agent, workspace_manager, memory_manager, vertex_agent_manager
    
    try:
        logger.info("🐻 Initializing Podplay Sanctuary services...")
        
        # Initialize database
        logger.info("📊 Initializing database...")
        init_database()
        
        # Initialize memory manager
        logger.info("🧠 Initializing memory manager...")
        memory_manager = MemoryManager()
        
        # Initialize Vertex AI agent manager
        logger.info("🤖 Initializing Vertex AI agent manager...")
        try:
            vertex_agent_manager = VertexAIAgentManager()
            logger.info("✅ Vertex AI Agent Manager initialized")
        except Exception as e:
            logger.warning(f"⚠️ Vertex AI integration not available: {e}")
            vertex_agent_manager = None
        
        # Initialize AI orchestrator
        logger.info("🎭 Initializing AI orchestrator...")
        ai_orchestrator = AIOrchestrator()
        
        # Initialize agents
        logger.info("🐻 Initializing Mama Bear agent...")
        mama_bear = MamaBearAgent(ai_orchestrator)
        mama_bear.memory_manager = memory_manager  # Link memory manager
        
        logger.info("🔍 Initializing Scout agent...")
        scout_agent = ScoutAgent(ai_orchestrator)
        
        logger.info("🛠️ Initializing workspace manager...")
        workspace_manager = WorkspaceManager()
        
        # Initialize API routes with service dependencies
        logger.info("🌐 Initializing API routes...")
        init_mcp_routes(scout_agent, vertex_agent_manager)
        init_workspace_routes(workspace_manager)
        init_gemini_live_service(mama_bear)
        
        logger.info("🎉 All services initialized successfully!")
        
        # Trigger Mama Bear's daily briefing if enabled
        if os.getenv('DAILY_BRIEFING_ENABLED', 'True').lower() == 'true':
            asyncio.create_task(mama_bear.daily_briefing())
        
    except Exception as e:
        logger.error(f"❌ Error initializing services: {e}")
        raise

# Enhanced API Routes with better error handling
@app.route('/api/health', methods=['GET'])
def health_check():
    """Enhanced health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'services': {
                'mama_bear': mama_bear is not None,
                'scout_agent': scout_agent is not None,
                'workspace_manager': workspace_manager is not None,
                'memory_manager': memory_manager is not None,
                'vertex_ai': vertex_agent_manager is not None,
                'ai_orchestrator': ai_orchestrator is not None
            },
            'environment': {
                'python_version': sys.version,
                'flask_env': os.getenv('FLASK_ENV', 'production'),
                'log_level': os.getenv('LOG_LEVEL', 'INFO')
            }
        })
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Get available AI agents with enhanced status"""
    try:
        agents_data = [
            {
                'id': 'mama_bear',
                'name': 'Mama Bear',
                'description': 'Your caring AI development assistant with persistent memory',
                'emoji': '🐻',
                'status': 'active' if mama_bear else 'inactive',
                'capabilities': [
                    'natural_language_chat',
                    'code_assistance',
                    'project_planning',
                    'emotional_support',
                    'context_awareness',
                    'daily_briefings',
                    'mcp_discovery',
                    'persistent_memory'
                ],
                'personality': {
                    'tone': 'caring_professional',
                    'proactivity_level': 'high',
                    'technical_depth': 'adaptive'
                }
            },
            {
                'id': 'scout',
                'name': 'Scout',
                'description': 'Autonomous development agent with MCP marketplace integration',
                'emoji': '🔍',
                'status': 'active' if scout_agent else 'inactive',
                'capabilities': [
                    'autonomous_development',
                    'code_generation',
                    'environment_setup',
                    'project_execution',
                    'mcp_discovery',
                    'mcp_installation',
                    'github_integration'
                ]
            }
        ]
        
        return jsonify({
            'agents': agents_data,
            'total_agents': len(agents_data),
            'active_agents': sum(1 for agent in agents_data if agent['status'] == 'active')
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting agents: {e}")
        return jsonify({
            'error': str(e),
            'agents': []
        }), 500

# Enhanced Socket.IO Events with better error handling
@socketio.on('connect')
def handle_connect():
    """Handle client connection with enhanced logging"""
    try:
        user_id = request.sid
        client_info = {
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'remote_addr': request.remote_addr
        }
        
        logger.info(f"🔌 Client connected: {user_id} from {client_info['remote_addr']}")
        
        join_room('sanctuary')
        
        emit('connection_established', {
            'user_id': user_id,
            'message': '🐻 Welcome to your Podplay Sanctuary! Mama Bear is here to help.',
            'timestamp': datetime.now().isoformat(),
            'sanctuary_status': 'active',
            'available_agents': ['mama_bear', 'scout'] if mama_bear and scout_agent else []
        })
        
    except Exception as e:
        logger.error(f"❌ Connection error: {e}")
        emit('connection_error', {'error': str(e)})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    try:
        user_id = request.sid
        logger.info(f"🔌 Client disconnected: {user_id}")
        leave_room('sanctuary')
    except Exception as e:
        logger.error(f"❌ Disconnection error: {e}")

@socketio.on('mama_bear_chat')
def handle_mama_bear_chat(data):
    """Enhanced Mama Bear chat with error handling and async support"""
    try:
        user_id = request.sid
        message_content = data.get('content', '')
        conversation_id = data.get('conversation_id', f'conv_{user_id}')
        
        if not message_content.strip():
            emit('error', {'message': 'Empty message received'}, room=user_id)
            return
        
        logger.info(f"🐻 Mama Bear chat from {user_id}: {message_content[:100]}...")
        
        # Emit typing indicator
        emit('mama_bear_typing', {'is_typing': True}, room=user_id)
        
        try:
            # Process with Mama Bear
            if mama_bear:
                response = mama_bear.process_message({
                    'content': message_content,
                    'user_id': user_id,
                    'conversation_id': conversation_id,
                    'timestamp': datetime.now().isoformat(),
                    'attachments': data.get('attachments', [])
                })
                
                # Store interaction in memory if available
                if memory_manager:
                    asyncio.create_task(memory_manager.store_interaction(
                        user_id, 'mama_bear', 
                        {'content': message_content, 'conversation_id': conversation_id}, 
                        response, 
                        response.get('model_used', 'unknown')
                    ))
                
                # Stop typing indicator
                emit('mama_bear_typing', {'is_typing': False}, room=user_id)
                
                # Send enhanced response
                emit('mama_bear_response', {
                    'response': response.get('response', 'I\'m sorry, I\'m having trouble right now. Please try again.'),
                    'suggestions': response.get('suggestions', []),
                    'actions': response.get('suggested_actions', []),
                    'model_used': response.get('model_used', 'unknown'),
                    'timestamp': datetime.now().isoformat(),
                    'mcp_discovery_suggestion': response.get('mcp_discovery_suggestion'),
                    'empowerment_opportunity': response.get('empowerment_opportunity', False),
                    'care_level': response.get('mama_bear_care_level', 'medium')
                }, room=user_id)
                
            else:
                emit('mama_bear_typing', {'is_typing': False}, room=user_id)
                emit('mama_bear_response', {
                    'response': '🐻 I\'m still waking up! Please wait a moment while I get ready to help you.',
                    'timestamp': datetime.now().isoformat(),
                    'status': 'initializing'
                }, room=user_id)
                
        except Exception as e:
            logger.error(f"❌ Mama Bear processing error: {e}")
            emit('mama_bear_typing', {'is_typing': False}, room=user_id)
            emit('error', {
                'message': 'Mama Bear encountered an error. Please try again.',
                'error_type': 'processing_error',
                'suggestion': 'Try rephrasing your message or check your connection.'
            }, room=user_id)
            
    except Exception as e:
        logger.error(f"❌ Error in mama_bear_chat: {e}")
        emit('error', {
            'message': 'Something went wrong with Mama Bear. Please try again.',
            'error_type': 'general_error'
        }, room=request.sid)

@socketio.on('scout_request')
def handle_scout_request(data):
    """Enhanced Scout agent requests with error handling"""
    try:
        user_id = request.sid
        task_description = data.get('task', '')
        
        if not task_description.strip():
            emit('error', {'message': 'Empty task description received'}, room=user_id)
            return
        
        logger.info(f"🔍 Scout request from {user_id}: {task_description[:100]}...")
        
        if scout_agent:
            # Process with Scout
            result = scout_agent.process_task({
                'task': task_description,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'session_id': request.sid
            })
            
            emit('scout_response', {
                **result,
                'timestamp': datetime.now().isoformat()
            }, room=user_id)
        else:
            emit('error', {
                'message': 'Scout agent is not available right now.',
                'error_type': 'service_unavailable'
            }, room=user_id)
            
    except Exception as e:
        logger.error(f"❌ Error in scout_request: {e}")
        emit('error', {
            'message': 'Scout encountered an error. Please try again.',
            'error_type': 'processing_error'
        }, room=request.sid)

@socketio.on('create_workspace')
def handle_create_workspace(data):
    """Enhanced workspace creation with validation"""
    try:
        user_id = request.sid
        workspace_config = data.get('config', {})
        
        if not workspace_config:
            emit('error', {'message': 'Workspace configuration required'}, room=user_id)
            return
        
        logger.info(f"🛠️ Workspace creation request from {user_id}")
        
        if workspace_manager:
            result = workspace_manager.create_workspace(workspace_config)
            emit('workspace_created', {
                **result,
                'timestamp': datetime.now().isoformat()
            }, room=user_id)
        else:
            emit('error', {
                'message': 'Workspace manager is not available.',
                'error_type': 'service_unavailable'
            }, room=user_id)
            
    except Exception as e:
        logger.error(f"❌ Error creating workspace: {e}")
        emit('error', {
            'message': 'Failed to create workspace. Please try again.',
            'error_type': 'creation_error'
        }, room=request.sid)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found.',
        'status_code': 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred.',
        'status_code': 500
    }), 500

# Register API blueprints with error handling
try:
    app.register_blueprint(mcp_bp)
    app.register_blueprint(workspace_bp)
    app.register_blueprint(nixos_bp)
    app.register_blueprint(code_server_bp)
    app.register_blueprint(orchestrator_bp)
    app.register_blueprint(gemini_live_bp)
    logger.info("✅ All API blueprints registered")
except Exception as e:
    logger.error(f"❌ Error registering blueprints: {e}")
    raise

if __name__ == '__main__':
    try:
        # Initialize services
        initialize_services()
        
        # Get port from environment
        port = int(os.getenv('PORT', 5000))
        debug_mode = os.getenv('FLASK_ENV') == 'development'
        
        logger.info(f"🚀 Starting Podplay Sanctuary on port {port}")
        logger.info("🐻 Mama Bear is ready to help!")
        
        # Run the app with enhanced configuration
        socketio.run(
            app,
            host='0.0.0.0',
            port=port,
            debug=debug_mode,
            allow_unsafe_werkzeug=True,
            use_reloader=False  # Disable reloader to prevent double initialization
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        sys.exit(1)