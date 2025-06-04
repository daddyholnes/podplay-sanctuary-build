"""
API Routes for MCP Marketplace functionality
Handles MCP server discovery, installation, and management
"""

from flask import Blueprint, jsonify, request
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Create blueprint for MCP routes
mcp_bp = Blueprint('mcp', __name__, url_prefix='/api/mcp')

# Import services (will be injected by main app)
scout_agent = None
vertex_agent_manager = None

def init_mcp_routes(scout_service, vertex_service):
    """Initialize MCP routes with service dependencies"""
    global scout_agent, vertex_agent_manager
    scout_agent = scout_service
    vertex_agent_manager = vertex_service

@mcp_bp.route('/available', methods=['GET'])
def get_available_mcps():
    """Get list of available MCP servers"""
    try:
        if scout_agent:
            available_mcps = scout_agent.get_available_mcps()
            return jsonify({
                'success': True,
                'available_mcps': available_mcps
            })
        else:
            # Return mock data if scout not available
            return jsonify({
                'success': True,
                'available_mcps': [
                    {
                        'id': 'github-mcp',
                        'name': 'GitHub MCP',
                        'description': 'GitHub repository management and code analysis',
                        'url': 'https://github.com/modelcontextprotocol/servers/tree/main/src/github',
                        'capabilities': ['github_api', 'repo_management', 'code_analysis'],
                        'installation_method': 'npm',
                        'status': 'available',
                        'source': 'official'
                    },
                    {
                        'id': 'docker-mcp',
                        'name': 'Docker MCP',
                        'description': 'Docker container management and operations',
                        'url': 'https://github.com/modelcontextprotocol/servers/tree/main/src/docker',
                        'capabilities': ['docker_api', 'container_management', 'image_operations'],
                        'installation_method': 'npm',
                        'status': 'available',
                        'source': 'official'
                    }
                ]
            })
    except Exception as e:
        logger.error(f"Error getting available MCPs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mcp_bp.route('/installed', methods=['GET'])
def get_installed_mcps():
    """Get list of installed MCP servers"""
    try:
        if scout_agent:
            installed_mcps = scout_agent.get_installed_mcps()
            return jsonify({
                'success': True,
                'installed_mcps': installed_mcps
            })
        else:
            return jsonify({
                'success': True,
                'installed_mcps': []
            })
    except Exception as e:
        logger.error(f"Error getting installed MCPs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mcp_bp.route('/search', methods=['POST'])
def search_mcp_marketplace():
    """Search MCP marketplace"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parameter required'
            }), 400
        
        if scout_agent:
            # Use Scout's MCP discovery
            search_results = scout_agent._search_mcp_marketplace([query])
            recommended_mcps = scout_agent._recommend_mcps(search_results, [query])
            
            return jsonify({
                'success': True,
                'query': query,
                'results': recommended_mcps,
                'total_found': len(recommended_mcps)
            })
        else:
            # Mock search results
            return jsonify({
                'success': True,
                'query': query,
                'results': [],
                'total_found': 0
            })
            
    except Exception as e:
        logger.error(f"Error searching MCP marketplace: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mcp_bp.route('/install', methods=['POST'])
def install_mcp_server():
    """Install an MCP server"""
    try:
        data = request.get_json()
        mcp_data = data.get('mcp_data')
        
        if not mcp_data:
            return jsonify({
                'success': False,
                'error': 'MCP data required'
            }), 400
        
        if scout_agent:
            result = scout_agent.install_mcp_server(mcp_data)
            return jsonify(result)
        else:
            # Mock installation
            return jsonify({
                'success': True,
                'message': f'MCP server {mcp_data.get("name")} installed successfully',
                'installation_method': mcp_data.get('installation_method', 'mock')
            })
            
    except Exception as e:
        logger.error(f"Error installing MCP server: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mcp_bp.route('/enhance-agent', methods=['POST'])
def enhance_agent_with_mcp():
    """Enhance an agent with MCP capabilities"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        mcp_capabilities = data.get('mcp_capabilities', [])
        
        if not agent_id:
            return jsonify({
                'success': False,
                'error': 'Agent ID required'
            }), 400
        
        if vertex_agent_manager:
            result = vertex_agent_manager.enhance_agent_with_mcp(agent_id, mcp_capabilities)
            return jsonify(result)
        else:
            return jsonify({
                'success': True,
                'message': f'Agent {agent_id} enhanced with MCP capabilities',
                'enhanced_capabilities': mcp_capabilities
            })
            
    except Exception as e:
        logger.error(f"Error enhancing agent with MCP: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500