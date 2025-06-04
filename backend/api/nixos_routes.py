"""
NixOS Environment Management API Routes
Provides REST API endpoints for creating, managing, and controlling NixOS environments
"""

from flask import Blueprint, request, jsonify
from services.nixos_environment_manager import NixOSEnvironmentManager
import logging
import asyncio
import os
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Create Blueprint
nixos_bp = Blueprint('nixos', __name__, url_prefix='/api/nixos')

# Initialize NixOS Environment Manager
nixos_manager = NixOSEnvironmentManager()

@nixos_bp.route('/templates', methods=['GET'])
def get_templates():
    """Get available NixOS environment templates"""
    try:
        templates = nixos_manager.get_available_templates()
        return jsonify({
            'success': True,
            'templates': templates['templates'],
            'total_templates': templates['total_templates']
        })
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@nixos_bp.route('/environments', methods=['GET'])
def list_environments():
    """List all NixOS environments"""
    try:
        environments = nixos_manager.list_environments()
        return jsonify({
            'success': True,
            'environments': environments,
            'total_environments': len(environments)
        })
    except Exception as e:
        logger.error(f"Error listing environments: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@nixos_bp.route('/environments', methods=['POST'])
def create_environment():
    """Create a new NixOS environment"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        template_name = data.get('template_name')
        custom_config = data.get('custom_config', {})
        user_id = data.get('user_id', 'anonymous')
        
        if not template_name and not custom_config:
            return jsonify({
                'success': False,
                'error': 'Either template_name or custom_config must be provided'
            }), 400
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            nixos_manager.create_environment(template_name, custom_config, user_id)
        )
        loop.close()
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error creating environment: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@nixos_bp.route('/environments/<environment_id>', methods=['GET'])
def get_environment_details(environment_id):
    """Get detailed information about a specific environment"""
    try:
        result = nixos_manager.get_environment_details(environment_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Error getting environment details: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@nixos_bp.route('/environments/<environment_id>/start', methods=['POST'])
def start_environment(environment_id):
    """Start a stopped environment"""
    try:
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            nixos_manager.start_environment(environment_id)
        )
        loop.close()
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error starting environment: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@nixos_bp.route('/environments/<environment_id>/stop', methods=['POST'])
def stop_environment(environment_id):
    """Stop a running environment"""
    try:
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            nixos_manager.stop_environment(environment_id)
        )
        loop.close()
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error stopping environment: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@nixos_bp.route('/environments/<environment_id>', methods=['DELETE'])
def delete_environment(environment_id):
    """Delete an environment"""
    try:
        force = request.args.get('force', 'false').lower() == 'true'
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            nixos_manager.delete_environment(environment_id, force)
        )
        loop.close()
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error deleting environment: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@nixos_bp.route('/environments/<environment_id>/packages', methods=['POST'])
def install_packages(environment_id):
    """Install additional packages in an environment"""
    try:
        data = request.get_json()
        
        if not data or 'packages' not in data:
            return jsonify({
                'success': False,
                'error': 'packages list required'
            }), 400
        
        packages = data['packages']
        if not isinstance(packages, list):
            return jsonify({
                'success': False,
                'error': 'packages must be a list'
            }), 400
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            nixos_manager.install_package_in_environment(environment_id, packages)
        )
        loop.close()
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error installing packages: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@nixos_bp.route('/environments/<environment_id>/execute', methods=['POST'])
def execute_command(environment_id):
    """Execute a command in the environment"""
    try:
        data = request.get_json()
        
        if not data or 'command' not in data:
            return jsonify({
                'success': False,
                'error': 'command required'
            }), 400
        
        command = data['command']
        working_directory = data.get('working_directory', '/workspace')
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            nixos_manager.execute_command_in_environment(
                environment_id, command, working_directory
            )
        )
        loop.close()
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@nixos_bp.route('/environments/cleanup', methods=['POST'])
def cleanup_environments():
    """Clean up inactive environments"""
    try:
        data = request.get_json() or {}
        max_age_hours = data.get('max_age_hours', 24)
        
        result = nixos_manager.cleanup_inactive_environments(max_age_hours)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error cleaning up environments: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@nixos_bp.route('/mama-bear/create-development-environment', methods=['POST'])
def mama_bear_create_dev_environment():
    """Mama Bear's intelligent environment creation based on project analysis"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        project_description = data.get('project_description', '')
        project_files = data.get('project_files', [])
        requirements = data.get('requirements', [])
        user_id = data.get('user_id', 'mama_bear')
        
        # Analyze project requirements and suggest environment
        suggested_config = _analyze_project_requirements(
            project_description, project_files, requirements
        )
        
        # Create environment with intelligent configuration
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            nixos_manager.create_environment(
                template_name=suggested_config['template'],
                custom_config=suggested_config['config'],
                user_id=user_id
            )
        )
        loop.close()
        
        if result['success']:
            result['mama_bear_analysis'] = suggested_config['analysis']
            result['message'] = f"🐻 I've created a perfect environment for your {suggested_config['project_type']} project!"
            
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in Mama Bear environment creation: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def _analyze_project_requirements(project_description: str, project_files: List[str], requirements: List[str]) -> dict:
    """Analyze project requirements and suggest optimal environment configuration"""
    
    project_description_lower = project_description.lower()
    file_extensions = [os.path.splitext(f)[1] for f in project_files]
    
    # Initialize analysis result
    analysis = {
        'detected_languages': [],
        'detected_frameworks': [],
        'detected_databases': [],
        'detected_tools': [],
        'project_type': 'general',
        'complexity': 'medium'
    }
    
    # Language detection
    if any(ext in ['.py', '.pyx'] for ext in file_extensions) or 'python' in project_description_lower:
        analysis['detected_languages'].append('python')
    
    if any(ext in ['.js', '.ts', '.jsx', '.tsx'] for ext in file_extensions) or any(term in project_description_lower for term in ['javascript', 'typescript', 'node', 'react', 'vue', 'angular']):
        analysis['detected_languages'].append('javascript')
    
    if any(ext in ['.rs'] for ext in file_extensions) or 'rust' in project_description_lower:
        analysis['detected_languages'].append('rust')
    
    if any(ext in ['.go'] for ext in file_extensions) or 'golang' in project_description_lower:
        analysis['detected_languages'].append('golang')
    
    # Framework detection
    if any(term in project_description_lower for term in ['react', 'next.js', 'nextjs']):
        analysis['detected_frameworks'].append('react')
    
    if any(term in project_description_lower for term in ['vue', 'nuxt']):
        analysis['detected_frameworks'].append('vue')
    
    if any(term in project_description_lower for term in ['django', 'flask', 'fastapi']):
        analysis['detected_frameworks'].append('python_web')
    
    if any(term in project_description_lower for term in ['express', 'fastify', 'koa']):
        analysis['detected_frameworks'].append('node_web')
    
    # Database detection
    if any(term in project_description_lower for term in ['postgres', 'postgresql']):
        analysis['detected_databases'].append('postgresql')
    
    if any(term in project_description_lower for term in ['mysql', 'mariadb']):
        analysis['detected_databases'].append('mysql')
    
    if any(term in project_description_lower for term in ['redis', 'cache']):
        analysis['detected_databases'].append('redis')
    
    if any(term in project_description_lower for term in ['mongodb', 'mongo']):
        analysis['detected_databases'].append('mongodb')
    
    # Tool detection
    if any(term in project_description_lower for term in ['docker', 'container']):
        analysis['detected_tools'].append('docker')
    
    if any(term in project_description_lower for term in ['kubernetes', 'k8s']):
        analysis['detected_tools'].append('kubernetes')
    
    if any(term in project_description_lower for term in ['terraform', 'infrastructure']):
        analysis['detected_tools'].append('terraform')
    
    # Project type determination
    if any(term in project_description_lower for term in ['web app', 'website', 'frontend', 'backend', 'api']):
        analysis['project_type'] = 'web_development'
    elif any(term in project_description_lower for term in ['data science', 'machine learning', 'ai', 'ml', 'analysis']):
        analysis['project_type'] = 'data_science'
    elif any(term in project_description_lower for term in ['devops', 'infrastructure', 'deployment', 'ci/cd']):
        analysis['project_type'] = 'devops'
    elif any(term in project_description_lower for term in ['mobile', 'ios', 'android']):
        analysis['project_type'] = 'mobile_development'
    
    # Complexity assessment
    complexity_indicators = len(analysis['detected_languages']) + len(analysis['detected_frameworks']) + len(analysis['detected_databases']) + len(analysis['detected_tools'])
    
    if complexity_indicators >= 5:
        analysis['complexity'] = 'high'
    elif complexity_indicators >= 3:
        analysis['complexity'] = 'medium'
    else:
        analysis['complexity'] = 'low'
    
    # Template selection
    template_mapping = {
        'web_development': 'full_stack_web',
        'data_science': 'data_science',
        'devops': 'devops_infrastructure',
        'mobile_development': 'development_minimal'
    }
    
    selected_template = template_mapping.get(analysis['project_type'], 'development_minimal')
    
    # Custom configuration
    custom_packages = []
    custom_env_vars = {}
    custom_hooks = []
    
    # Add language-specific packages
    if 'python' in analysis['detected_languages']:
        custom_packages.extend(['python3', 'python3Packages.pip', 'python3Packages.virtualenv'])
    
    if 'javascript' in analysis['detected_languages']:
        custom_packages.extend(['nodejs_20', 'yarn', 'bun'])
    
    if 'rust' in analysis['detected_languages']:
        custom_packages.extend(['rustc', 'cargo'])
    
    if 'golang' in analysis['detected_languages']:
        custom_packages.extend(['go'])
    
    # Add database packages
    if 'postgresql' in analysis['detected_databases']:
        custom_packages.append('postgresql')
        custom_env_vars['DATABASE_URL'] = 'postgresql://localhost:5432/dev'
    
    if 'redis' in analysis['detected_databases']:
        custom_packages.append('redis')
    
    # Add tool packages
    if 'docker' in analysis['detected_tools']:
        custom_packages.extend(['docker', 'docker-compose'])
    
    if 'kubernetes' in analysis['detected_tools']:
        custom_packages.extend(['kubectl', 'helm'])
    
    if 'terraform' in analysis['detected_tools']:
        custom_packages.append('terraform')
    
    return {
        'template': selected_template,
        'project_type': analysis['project_type'],
        'analysis': analysis,
        'config': {
            'name': f"Smart Environment - {analysis['project_type'].replace('_', ' ').title()}",
            'description': f"Intelligently configured environment for {project_description}",
            'packages': custom_packages,
            'environment_variables': custom_env_vars,
            'shell_hooks': custom_hooks,
            'resource_limits': {
                'memory': '6GB' if analysis['complexity'] == 'high' else '4GB' if analysis['complexity'] == 'medium' else '2GB',
                'cpu': '3' if analysis['complexity'] == 'high' else '2' if analysis['complexity'] == 'medium' else '1',
                'disk': '30GB' if analysis['complexity'] == 'high' else '20GB' if analysis['complexity'] == 'medium' else '10GB'
            }
        }
    }

@nixos_bp.route('/status', methods=['GET'])
def get_nixos_status():
    """Get NixOS environment manager status"""
    try:
        environments = nixos_manager.list_environments()
        active_count = len([env for env in environments if env['status'] == 'active'])
        
        return jsonify({
            'success': True,
            'status': 'ready',
            'nix_available': nixos_manager.nix_available,
            'docker_available': nixos_manager.docker_client is not None,
            'total_environments': len(environments),
            'active_environments': active_count,
            'base_path': nixos_manager.environments_base_path
        })
        
    except Exception as e:
        logger.error(f"Error getting NixOS status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500