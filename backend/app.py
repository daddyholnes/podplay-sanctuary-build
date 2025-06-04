#!/usr/bin/env python3
"""
Podplay Sanctuary - Main Flask Application
Nathan's AI-Powered Development Sanctuary with Mama Bear Agent
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from dotenv import load_dotenv

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

# Import API routes
from api.mcp_routes import mcp_bp, init_mcp_routes
from api.workspace_routes import workspace_bp, init_workspace_routes
from api.nixos_routes import nixos_bp
from api.code_server_routes import code_server_bp
from api.orchestrator_routes import orchestrator_bp
from api.gemini_live_routes import gemini_live_bp, init_gemini_live_service

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.getenv('LOG_FILE', 'mama_bear.log')),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'sanctuary_mama_bear_secret_dev')

# Configure CORS
CORS(app, origins=["http://localhost:3000", "http://localhost:5173", "https://8001-*.public.scrapybara.com"])

# Initialize SocketIO
socketio = SocketIO(
    app, 
    cors_allowed_origins=["http://localhost:3000", "http://localhost:5173", "https://8001-*.public.scrapybara.com"],
    logger=True, 
    engineio_logger=True
)

# Initialize services
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
        init_database()
        
        # Initialize memory manager
        memory_manager = MemoryManager()
        
        # Initialize Vertex AI agent manager
        try:
            vertex_agent_manager = VertexAIAgentManager()
            logger.info("🤖 Vertex AI Agent Manager initialized")
        except Exception as e:
            logger.warning(f"⚠️ Vertex AI integration not available: {e}")
            vertex_agent_manager = None
        
        # Initialize AI orchestrator
        ai_orchestrator = AIOrchestrator()
        
        # Initialize agents
        mama_bear = MamaBearAgent(ai_orchestrator)
        scout_agent = ScoutAgent(ai_orchestrator)
        workspace_manager = WorkspaceManager()
        
        # Initialize API routes with service dependencies
        init_mcp_routes(scout_agent, vertex_agent_manager)
        init_workspace_routes(workspace_manager)
        init_gemini_live_service(mama_bear)
        
        logger.info("🎉 All services initialized successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error initializing services: {e}")
        raise

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'mama_bear': mama_bear is not None,
            'scout_agent': scout_agent is not None,
            'workspace_manager': workspace_manager is not None,
            'memory_manager': memory_manager is not None
        }
    })

@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Get available AI agents"""
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
                    'context_awareness'
                ]
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
                    'project_execution'
                ]
            }
        ]
    })

# Socket.IO Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    user_id = request.sid
    logger.info(f"🔌 Client connected: {user_id}")
    
    join_room('sanctuary')
    
    emit('connection_established', {
        'user_id': user_id,
        'message': '🐻 Welcome to your Podplay Sanctuary! Mama Bear is here to help.',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    user_id = request.sid
    logger.info(f"🔌 Client disconnected: {user_id}")
    
    leave_room('sanctuary')

@socketio.on('mama_bear_chat')
def handle_mama_bear_chat(data):
    """Handle Mama Bear chat messages"""
    try:
        user_id = request.sid
        message_content = data.get('content', '')
        conversation_id = data.get('conversation_id', f'conv_{user_id}')
        
        logger.info(f"🐻 Mama Bear chat from {user_id}: {message_content[:100]}...")
        
        # Emit typing indicator
        emit('mama_bear_typing', {'is_typing': True}, room=user_id)
        
        # Process with Mama Bear
        if mama_bear:
            response = mama_bear.process_message({
                'content': message_content,
                'user_id': user_id,
                'conversation_id': conversation_id,
                'timestamp': datetime.now().isoformat(),
                'attachments': data.get('attachments', [])
            })
            
            # Stop typing indicator
            emit('mama_bear_typing', {'is_typing': False}, room=user_id)
            
            # Send response
            emit('mama_bear_response', {
                'response': response.get('response', 'I\'m sorry, I\'m having trouble right now. Please try again.'),
                'suggestions': response.get('suggestions', []),
                'actions': response.get('suggested_actions', []),
                'model_used': response.get('model_used', 'unknown'),
                'timestamp': datetime.now().isoformat()
            }, room=user_id)
            
        else:
            emit('mama_bear_typing', {'is_typing': False}, room=user_id)
            emit('mama_bear_response', {
                'response': '🐻 I\'m still waking up! Please wait a moment while I get ready to help you.',
                'timestamp': datetime.now().isoformat()
            }, room=user_id)
            
    except Exception as e:
        logger.error(f"❌ Error in mama_bear_chat: {e}")
        emit('mama_bear_typing', {'is_typing': False}, room=user_id)
        emit('error', {
            'message': 'Something went wrong with Mama Bear. Please try again.',
            'error': str(e)
        }, room=user_id)

@socketio.on('scout_request')
def handle_scout_request(data):
    """Handle Scout agent requests"""
    try:
        user_id = request.sid
        task_description = data.get('task', '')
        
        logger.info(f"🔍 Scout request from {user_id}: {task_description[:100]}...")
        
        if scout_agent:
            # Process with Scout
            result = scout_agent.process_task({
                'task': task_description,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            })
            
            emit('scout_response', result, room=user_id)
        else:
            emit('error', {
                'message': 'Scout agent is not available right now.'
            }, room=user_id)
            
    except Exception as e:
        logger.error(f"❌ Error in scout_request: {e}")
        emit('error', {
            'message': 'Scout encountered an error. Please try again.',
            'error': str(e)
        }, room=user_id)

@socketio.on('create_workspace')
def handle_create_workspace(data):
    """Handle workspace creation requests"""
    try:
        user_id = request.sid
        workspace_config = data.get('config', {})
        
        logger.info(f"🛠️ Workspace creation request from {user_id}")
        
        if workspace_manager:
            result = workspace_manager.create_workspace(workspace_config)
            emit('workspace_created', result, room=user_id)
        else:
            emit('error', {
                'message': 'Workspace manager is not available.'
            }, room=user_id)
            
    except Exception as e:
        logger.error(f"❌ Error creating workspace: {e}")
        emit('error', {
            'message': 'Failed to create workspace. Please try again.',
            'error': str(e)
        }, room=user_id)

# Register API blueprints
app.register_blueprint(mcp_bp)
app.register_blueprint(workspace_bp)
app.register_blueprint(nixos_bp)
app.register_blueprint(code_server_bp)
app.register_blueprint(orchestrator_bp)
app.register_blueprint(gemini_live_bp)

if __name__ == '__main__':
    # Initialize services
    initialize_services()
    
    # Get port from environment
    port = int(os.getenv('PORT', 5000))
    
    logger.info(f"🚀 Starting Podplay Sanctuary on port {port}")
    logger.info("🐻 Mama Bear is ready to help!")
    
    # Run the app
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_ENV') == 'development',
        allow_unsafe_werkzeug=True
    )