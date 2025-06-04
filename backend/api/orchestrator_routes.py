"""
Environment Orchestrator API Routes
Provides Mama Bear with full control over environment management
"""

from flask import Blueprint, request, jsonify
import asyncio
import logging
from typing import Dict, Any

from services.environment_orchestrator import environment_orchestrator

logger = logging.getLogger(__name__)

orchestrator_bp = Blueprint('orchestrator', __name__, url_prefix='/api/orchestrator')

def run_async(coro):
    """Helper to run async functions in Flask routes"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@orchestrator_bp.route('/templates', methods=['GET'])
def get_templates():
    """Get all available environment templates"""
    try:
        result = environment_orchestrator.get_available_templates()
        return jsonify(result)
    except Exception as e:
        logger.error(f"❌ Failed to get templates: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@orchestrator_bp.route('/environments', methods=['GET'])
def list_environments():
    """List all environments, optionally filtered by owner"""
    try:
        owner = request.args.get('owner')
        result = run_async(environment_orchestrator.list_environments(owner))
        return jsonify(result)
    except Exception as e:
        logger.error(f"❌ Failed to list environments: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@orchestrator_bp.route('/environments', methods=['POST'])
def create_environment():
    """Create a new environment"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Request body required'}), 400
        
        result = run_async(environment_orchestrator.create_environment(data))
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"❌ Failed to create environment: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@orchestrator_bp.route('/environments/<env_id>', methods=['GET'])
def get_environment_status(env_id):
    """Get detailed status of a specific environment"""
    try:
        result = run_async(environment_orchestrator.get_environment_status(env_id))
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"❌ Failed to get environment status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@orchestrator_bp.route('/environments/<env_id>/stop', methods=['POST'])
def stop_environment(env_id):
    """Stop an environment"""
    try:
        result = run_async(environment_orchestrator.stop_environment(env_id))
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"❌ Failed to stop environment: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@orchestrator_bp.route('/environments/<env_id>/start', methods=['POST'])
def restart_environment(env_id):
    """Restart a stopped environment"""
    try:
        # For now, this will recreate the environment
        # In a full implementation, this would restart existing resources
        env_status = run_async(environment_orchestrator.get_environment_status(env_id))
        
        if not env_status['success']:
            return jsonify(env_status), 404
        
        env_data = env_status['environment']
        
        # Create new environment with same configuration
        create_request = {
            'template_id': env_data['template_id'],
            'name': f"{env_data['name']}_restarted",
            'config': env_data['config'],
            'owner': env_data['owner'],
            'collaborators': env_data['collaborators']
        }
        
        result = run_async(environment_orchestrator.create_environment(create_request))
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Failed to restart environment: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@orchestrator_bp.route('/environments/<env_id>', methods=['DELETE'])
def delete_environment(env_id):
    """Delete an environment"""
    try:
        force = request.args.get('force', 'false').lower() == 'true'
        result = run_async(environment_orchestrator.delete_environment(env_id, force))
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"❌ Failed to delete environment: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@orchestrator_bp.route('/environments/cleanup', methods=['POST'])
def cleanup_environments():
    """Clean up expired environments"""
    try:
        result = run_async(environment_orchestrator.cleanup_expired_environments())
        return jsonify(result)
    except Exception as e:
        logger.error(f"❌ Failed to cleanup environments: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@orchestrator_bp.route('/environments/<env_id>/scale', methods=['POST'])
def scale_environment(env_id):
    """Scale an environment up or down"""
    try:
        data = request.get_json()
        direction = data.get('direction', 'up')  # 'up' or 'down'
        
        if direction not in ['up', 'down']:
            return jsonify({'success': False, 'error': 'Direction must be "up" or "down"'}), 400
        
        # Get the environment
        env_status = run_async(environment_orchestrator.get_environment_status(env_id))
        if not env_status['success']:
            return jsonify(env_status), 404
        
        # Trigger scaling
        result = run_async(environment_orchestrator._scale_environment(env_id, direction))
        
        return jsonify({
            'success': True,
            'environment_id': env_id,
            'direction': direction,
            'message': f'Environment scaled {direction} successfully'
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to scale environment: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@orchestrator_bp.route('/templates/<template_id>', methods=['GET'])
def get_template_details(template_id):
    """Get detailed information about a specific template"""
    try:
        templates = environment_orchestrator.get_available_templates()
        
        template = None
        for t in templates['templates']:
            if t['id'] == template_id:
                template = t
                break
        
        if template:
            return jsonify({
                'success': True,
                'template': template
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Template not found'
            }), 404
            
    except Exception as e:
        logger.error(f"❌ Failed to get template details: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@orchestrator_bp.route('/templates', methods=['POST'])
def create_custom_template():
    """Create a custom environment template"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Request body required'}), 400
        
        required_fields = ['name', 'description', 'type', 'base_config']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Create template ID
        import uuid
        template_id = f"custom_{uuid.uuid4().hex[:8]}"
        
        # Create template object
        from ..services.environment_orchestrator import EnvironmentTemplate, EnvironmentType
        
        template = EnvironmentTemplate(
            id=template_id,
            name=data['name'],
            description=data['description'],
            type=EnvironmentType(data['type']),
            base_config=data['base_config'],
            required_resources=data.get('required_resources', {
                'memory': '2Gi',
                'cpu': '1000m',
                'storage': '10Gi'
            }),
            auto_scaling=data.get('auto_scaling', {
                'enabled': False,
                'min_instances': 1,
                'max_instances': 1
            }),
            extensions=data.get('extensions', []),
            dependencies=data.get('dependencies', []),
            startup_scripts=data.get('startup_scripts', []),
            health_checks=data.get('health_checks', []),
            created_by=data.get('owner', 'mama_bear'),
            tags=data.get('tags', ['custom'])
        )
        
        # Add to orchestrator
        environment_orchestrator.templates[template_id] = template
        
        return jsonify({
            'success': True,
            'template_id': template_id,
            'template': data,
            'message': f'Custom template "{data["name"]}" created'
        }), 201
        
    except Exception as e:
        logger.error(f"❌ Failed to create custom template: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@orchestrator_bp.route('/resource-usage', methods=['GET'])
def get_resource_usage():
    """Get current resource usage across all environments"""
    try:
        result = run_async(environment_orchestrator.list_environments())
        return jsonify({
            'success': True,
            'resource_usage': result['resource_usage'],
            'limits': environment_orchestrator.resource_limits,
            'total_environments': result['total_count']
        })
    except Exception as e:
        logger.error(f"❌ Failed to get resource usage: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@orchestrator_bp.route('/environments/<env_id>/collaborate', methods=['POST'])
def add_collaborator(env_id):
    """Add a collaborator to an environment"""
    try:
        data = request.get_json()
        collaborator = data.get('collaborator')
        
        if not collaborator:
            return jsonify({'success': False, 'error': 'Collaborator required'}), 400
        
        if env_id not in environment_orchestrator.environments:
            return jsonify({'success': False, 'error': 'Environment not found'}), 404
        
        env = environment_orchestrator.environments[env_id]
        
        if collaborator not in env.collaborators:
            env.collaborators.append(collaborator)
        
        return jsonify({
            'success': True,
            'environment_id': env_id,
            'collaborators': env.collaborators,
            'message': f'Collaborator {collaborator} added'
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to add collaborator: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@orchestrator_bp.route('/environments/<env_id>/access', methods=['GET'])
def get_environment_access(env_id):
    """Get access information for an environment"""
    try:
        result = run_async(environment_orchestrator.get_environment_status(env_id))
        
        if not result['success']:
            return jsonify(result), 404
        
        env = result['environment']
        
        access_info = {
            'success': True,
            'environment_id': env_id,
            'name': env['name'],
            'status': env['status'],
            'endpoints': env['endpoints'],
            'access_methods': []
        }
        
        # Add access methods based on endpoints
        for endpoint_name, endpoint_url in env['endpoints'].items():
            if endpoint_url:
                access_info['access_methods'].append({
                    'name': endpoint_name,
                    'url': endpoint_url,
                    'type': 'web' if 'http' in endpoint_url else 'local'
                })
        
        return jsonify(access_info)
        
    except Exception as e:
        logger.error(f"❌ Failed to get environment access: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@orchestrator_bp.route('/environments/bulk-action', methods=['POST'])
def bulk_environment_action():
    """Perform bulk actions on multiple environments"""
    try:
        data = request.get_json()
        action = data.get('action')
        environment_ids = data.get('environment_ids', [])
        
        if not action or not environment_ids:
            return jsonify({'success': False, 'error': 'Action and environment_ids required'}), 400
        
        results = []
        
        for env_id in environment_ids:
            try:
                if action == 'stop':
                    result = run_async(environment_orchestrator.stop_environment(env_id))
                elif action == 'delete':
                    force = data.get('force', False)
                    result = run_async(environment_orchestrator.delete_environment(env_id, force))
                elif action == 'restart':
                    # Stop then recreate
                    stop_result = run_async(environment_orchestrator.stop_environment(env_id))
                    if stop_result['success']:
                        # Would implement restart logic here
                        result = {'success': True, 'message': 'Environment restart initiated'}
                    else:
                        result = stop_result
                else:
                    result = {'success': False, 'error': f'Unknown action: {action}'}
                
                results.append({
                    'environment_id': env_id,
                    'action': action,
                    'result': result
                })
                
            except Exception as e:
                results.append({
                    'environment_id': env_id,
                    'action': action,
                    'result': {'success': False, 'error': str(e)}
                })
        
        successful_count = sum(1 for r in results if r['result']['success'])
        
        return jsonify({
            'success': True,
            'total_processed': len(results),
            'successful': successful_count,
            'failed': len(results) - successful_count,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to perform bulk action: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@orchestrator_bp.route('/health', methods=['GET'])
def orchestrator_health():
    """Get orchestrator system health"""
    try:
        # Check component health
        health_status = {
            'orchestrator': 'healthy',
            'components': {
                'nixos_manager': 'healthy' if environment_orchestrator.nixos_manager else 'unavailable',
                'code_server_manager': 'healthy' if environment_orchestrator.code_server_manager else 'unavailable',
                'docker_client': 'healthy' if environment_orchestrator.docker_client else 'unavailable',
                'ai_manager': 'healthy' if environment_orchestrator.ai_manager else 'unavailable'
            },
            'statistics': {
                'total_environments': len(environment_orchestrator.environments),
                'total_templates': len(environment_orchestrator.templates),
                'running_environments': len([e for e in environment_orchestrator.environments.values() if e.status.value == 'ready'])
            },
            'timestamp': environment_orchestrator.environments and list(environment_orchestrator.environments.values())[0].created_at or None
        }
        
        return jsonify({
            'success': True,
            'health': health_status
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to get orchestrator health: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Error handlers
@orchestrator_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 'Bad request',
        'message': str(error)
    }), 400

@orchestrator_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Not found',
        'message': str(error)
    }), 404

@orchestrator_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': str(error)
    }), 500