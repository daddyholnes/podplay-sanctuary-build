"""
API Routes for Workspace Management functionality
Handles workspace creation, management, and templates
"""

from flask import Blueprint, jsonify, request
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Create blueprint for workspace routes
workspace_bp = Blueprint('workspace', __name__, url_prefix='/api')

# Import services (will be injected by main app)
workspace_manager = None

def init_workspace_routes(workspace_service):
    """Initialize workspace routes with service dependencies"""
    global workspace_manager
    workspace_manager = workspace_service

@workspace_bp.route('/workspaces', methods=['GET'])
def get_workspaces():
    """Get list of all workspaces"""
    try:
        if workspace_manager:
            workspaces = workspace_manager.list_workspaces()
            return jsonify({
                'success': True,
                'workspaces': workspaces
            })
        else:
            return jsonify({
                'success': True,
                'workspaces': []
            })
    except Exception as e:
        logger.error(f"Error getting workspaces: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@workspace_bp.route('/workspace/<workspace_id>', methods=['GET'])
def get_workspace(workspace_id):
    """Get specific workspace details"""
    try:
        if workspace_manager:
            workspace = workspace_manager.get_workspace(workspace_id)
            if workspace:
                return jsonify({
                    'success': True,
                    'workspace': workspace
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Workspace not found'
                }), 404
        else:
            return jsonify({
                'success': False,
                'error': 'Workspace manager not available'
            }), 503
    except Exception as e:
        logger.error(f"Error getting workspace {workspace_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@workspace_bp.route('/workspace-templates', methods=['GET'])
def get_workspace_templates():
    """Get available workspace templates"""
    try:
        if workspace_manager:
            templates = workspace_manager.get_workspace_templates()
            return jsonify({
                'success': True,
                'templates': templates
            })
        else:
            # Return default templates
            return jsonify({
                'success': True,
                'templates': [
                    {
                        'id': 'react_typescript',
                        'name': 'React + TypeScript',
                        'description': 'Modern React application with TypeScript',
                        'language': 'typescript',
                        'framework': 'react',
                        'tools': ['node', 'npm', 'vite', 'eslint', 'prettier']
                    },
                    {
                        'id': 'python_flask',
                        'name': 'Python + Flask',
                        'description': 'Flask web application with Python',
                        'language': 'python',
                        'framework': 'flask',
                        'tools': ['python3', 'pip', 'flask', 'pytest']
                    },
                    {
                        'id': 'full_stack',
                        'name': 'Full Stack (React + Flask)',
                        'description': 'Complete full-stack development environment',
                        'language': 'multiple',
                        'framework': 'full_stack',
                        'tools': ['node', 'python3', 'docker', 'postgres']
                    },
                    {
                        'id': 'ai_development',
                        'name': 'AI/ML Development',
                        'description': 'Machine learning and AI development environment',
                        'language': 'python',
                        'framework': 'pytorch',
                        'tools': ['python3', 'jupyter', 'pytorch', 'transformers', 'pandas']
                    }
                ]
            })
    except Exception as e:
        logger.error(f"Error getting workspace templates: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@workspace_bp.route('/workspace', methods=['POST'])
def create_workspace():
    """Create a new workspace"""
    try:
        data = request.get_json()
        config = data.get('config')
        
        if not config or not config.get('name'):
            return jsonify({
                'success': False,
                'error': 'Workspace configuration with name required'
            }), 400
        
        if workspace_manager:
            result = workspace_manager.create_workspace(config)
            return jsonify(result)
        else:
            # Mock workspace creation
            return jsonify({
                'success': True,
                'workspace': {
                    'id': f"workspace_{int(datetime.now().timestamp())}",
                    'name': config['name'],
                    'type': config.get('type', 'docker'),
                    'status': 'running',
                    'access_url': 'http://localhost:3000',
                    'created_at': datetime.now().isoformat()
                },
                'message': f'Workspace "{config["name"]}" created successfully'
            })
            
    except Exception as e:
        logger.error(f"Error creating workspace: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@workspace_bp.route('/workspace/<workspace_id>/stop', methods=['POST'])
def stop_workspace(workspace_id):
    """Stop a workspace"""
    try:
        if workspace_manager:
            result = workspace_manager.stop_workspace(workspace_id)
            return jsonify(result)
        else:
            return jsonify({
                'success': True,
                'message': f'Workspace {workspace_id} stopped'
            })
    except Exception as e:
        logger.error(f"Error stopping workspace {workspace_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@workspace_bp.route('/workspace/<workspace_id>', methods=['DELETE'])
def delete_workspace(workspace_id):
    """Delete a workspace"""
    try:
        if workspace_manager:
            result = workspace_manager.delete_workspace(workspace_id)
            return jsonify(result)
        else:
            return jsonify({
                'success': True,
                'message': f'Workspace {workspace_id} deleted'
            })
    except Exception as e:
        logger.error(f"Error deleting workspace {workspace_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500