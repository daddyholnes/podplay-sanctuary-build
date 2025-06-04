"""
Code-Server API Routes
Provides REST API endpoints for managing code-server instances with Docker/Cloud deployment
"""

from flask import Blueprint, request, jsonify
from services.code_server_manager import CodeServerManager
import logging
import asyncio
import os
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Create Blueprint
code_server_bp = Blueprint('code_server', __name__, url_prefix='/api/code-server')

# Initialize Code-Server Manager
code_server_manager = CodeServerManager()

@code_server_bp.route('/status', methods=['GET'])
def get_status():
    """Get code-server manager status"""
    try:
        instances = code_server_manager.list_instances()
        running_count = len([i for i in instances if i['status'] == 'running'])
        
        return jsonify({
            'success': True,
            'status': 'ready',
            'docker_available': code_server_manager.docker_client is not None,
            'gcp_configured': bool(code_server_manager.service_account_path),
            'total_instances': len(instances),
            'running_instances': running_count,
            'base_port': code_server_manager.base_port,
            'max_instances': code_server_manager.max_instances
        })
        
    except Exception as e:
        logger.error(f"Error getting code-server status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_server_bp.route('/instances', methods=['GET'])
def list_instances():
    """List all code-server instances"""
    try:
        instances = code_server_manager.list_instances()
        return jsonify({
            'success': True,
            'instances': instances,
            'total_instances': len(instances)
        })
    except Exception as e:
        logger.error(f"Error listing instances: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_server_bp.route('/instances', methods=['POST'])
def create_instance():
    """Create a new code-server instance"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate required fields
        config = {
            'name': data.get('name', f"Code Server {len(code_server_manager.instances) + 1}"),
            'environment_id': data.get('environment_id'),
            'workspace_path': data.get('workspace_path', '/workspace'),
            'extensions': data.get('extensions', []),
            'settings': data.get('settings', {}),
            'user_id': data.get('user_id', 'anonymous')
        }
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            code_server_manager.create_code_server_instance(config)
        )
        loop.close()
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error creating instance: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_server_bp.route('/instances/<instance_id>', methods=['GET'])
def get_instance_details(instance_id):
    """Get detailed information about a specific instance"""
    try:
        result = code_server_manager.get_instance_details(instance_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Error getting instance details: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_server_bp.route('/instances/<instance_id>/stop', methods=['POST'])
def stop_instance(instance_id):
    """Stop a running instance"""
    try:
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            code_server_manager.stop_instance(instance_id)
        )
        loop.close()
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error stopping instance: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_server_bp.route('/instances/<instance_id>', methods=['DELETE'])
def delete_instance(instance_id):
    """Delete an instance"""
    try:
        force = request.args.get('force', 'false').lower() == 'true'
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            code_server_manager.delete_instance(instance_id, force)
        )
        loop.close()
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error deleting instance: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_server_bp.route('/instances/<instance_id>/deploy-cloud', methods=['POST'])
def deploy_to_cloud(instance_id):
    """Deploy instance to Google Cloud"""
    try:
        data = request.get_json() or {}
        
        deployment_config = {
            'region': data.get('region', 'us-central1'),
            'memory': data.get('memory', '2Gi'),
            'cpu': data.get('cpu', '1000m'),
            'max_instances': data.get('max_instances', 1),
            'timeout': data.get('timeout', 3600)
        }
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            code_server_manager.deploy_to_google_cloud(instance_id, deployment_config)
        )
        loop.close()
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error deploying to cloud: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_server_bp.route('/instances/<instance_id>/extensions', methods=['POST'])
def install_extension(instance_id):
    """Install an extension in a running instance"""
    try:
        data = request.get_json()
        
        if not data or 'extension_id' not in data:
            return jsonify({
                'success': False,
                'error': 'extension_id required'
            }), 400
        
        extension_id = data['extension_id']
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            code_server_manager.install_extension(instance_id, extension_id)
        )
        loop.close()
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error installing extension: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_server_bp.route('/extensions', methods=['GET'])
def get_extensions_catalog():
    """Get available extensions catalog"""
    try:
        catalog = code_server_manager.get_extension_catalog()
        return jsonify({
            'success': True,
            'catalog': catalog
        })
        
    except Exception as e:
        logger.error(f"Error getting extensions catalog: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_server_bp.route('/instances/cleanup', methods=['POST'])
def cleanup_instances():
    """Clean up inactive instances"""
    try:
        data = request.get_json() or {}
        max_age_hours = data.get('max_age_hours', 24)
        
        result = code_server_manager.cleanup_inactive_instances(max_age_hours)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error cleaning up instances: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_server_bp.route('/mama-bear/create-workspace', methods=['POST'])
def mama_bear_create_workspace():
    """Mama Bear's intelligent workspace creation with code-server"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        project_description = data.get('project_description', '')
        project_type = data.get('project_type', 'general')
        nixos_environment_id = data.get('nixos_environment_id')
        user_preferences = data.get('user_preferences', {})
        user_id = data.get('user_id', 'mama_bear')
        
        # Analyze project and suggest extensions and settings
        suggested_config = _analyze_project_for_code_server(
            project_description, project_type, user_preferences
        )
        
        # Create code-server instance with intelligent configuration
        instance_config = {
            'name': f"Mama Bear Workspace - {suggested_config['workspace_name']}",
            'environment_id': nixos_environment_id,
            'workspace_path': '/workspace',
            'extensions': suggested_config['extensions'],
            'settings': suggested_config['settings'],
            'user_id': user_id
        }
        
        # Create instance
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            code_server_manager.create_code_server_instance(instance_config)
        )
        loop.close()
        
        if result['success']:
            result['mama_bear_analysis'] = suggested_config['analysis']
            result['message'] = f"🐻 I've created a perfect code workspace for your {project_type} project!"
            
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in Mama Bear workspace creation: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_server_bp.route('/mama-bear/suggest-extensions', methods=['POST'])
def mama_bear_suggest_extensions():
    """Mama Bear suggests extensions based on project analysis"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        project_files = data.get('project_files', [])
        project_description = data.get('project_description', '')
        current_extensions = data.get('current_extensions', [])
        
        # Analyze and suggest extensions
        suggestions = _suggest_extensions_for_project(
            project_files, project_description, current_extensions
        )
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'message': f"🐻 I found {len(suggestions['recommended'])} extensions that could help with your project!"
        })
        
    except Exception as e:
        logger.error(f"Error in extension suggestions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def _analyze_project_for_code_server(project_description: str, project_type: str, user_preferences: dict) -> dict:
    """Analyze project requirements and suggest optimal code-server configuration"""
    
    description_lower = project_description.lower()
    
    # Initialize analysis result
    analysis = {
        'detected_languages': [],
        'detected_frameworks': [],
        'detected_tools': [],
        'complexity': 'medium',
        'primary_language': 'javascript'
    }
    
    # Language detection
    if any(term in description_lower for term in ['python', 'django', 'flask', 'fastapi']):
        analysis['detected_languages'].append('python')
        analysis['primary_language'] = 'python'
    
    if any(term in description_lower for term in ['javascript', 'typescript', 'js', 'ts', 'node', 'react', 'vue', 'angular']):
        analysis['detected_languages'].append('javascript')
        if 'python' not in analysis['detected_languages']:
            analysis['primary_language'] = 'javascript'
    
    if any(term in description_lower for term in ['rust', 'cargo']):
        analysis['detected_languages'].append('rust')
    
    if any(term in description_lower for term in ['go', 'golang']):
        analysis['detected_languages'].append('go')
    
    # Framework detection
    frameworks = ['react', 'vue', 'angular', 'svelte', 'django', 'flask', 'fastapi', 'express']
    for framework in frameworks:
        if framework in description_lower:
            analysis['detected_frameworks'].append(framework)
    
    # Tool detection
    tools = ['docker', 'kubernetes', 'terraform', 'git']
    for tool in tools:
        if tool in description_lower:
            analysis['detected_tools'].append(tool)
    
    # Generate extension recommendations
    extensions = []
    
    # Language-specific extensions
    if 'python' in analysis['detected_languages']:
        extensions.extend(['ms-python.python', 'ms-python.pylint'])
    
    if 'javascript' in analysis['detected_languages']:
        extensions.extend(['ms-vscode.vscode-typescript-next', 'esbenp.prettier-vscode', 'dbaeumer.vscode-eslint'])
    
    if 'rust' in analysis['detected_languages']:
        extensions.append('rust-lang.rust-analyzer')
    
    if 'go' in analysis['detected_languages']:
        extensions.append('golang.go')
    
    # Framework-specific extensions
    if 'react' in analysis['detected_frameworks']:
        extensions.append('ms-vscode.vscode-react-native')
    
    if 'vue' in analysis['detected_frameworks']:
        extensions.append('octref.vetur')
    
    if 'svelte' in analysis['detected_frameworks']:
        extensions.append('svelte.svelte-vscode')
    
    # Tool-specific extensions
    if 'docker' in analysis['detected_tools']:
        extensions.append('ms-azuretools.vscode-docker')
    
    if 'kubernetes' in analysis['detected_tools']:
        extensions.append('ms-kubernetes-tools.vscode-kubernetes-tools')
    
    if 'terraform' in analysis['detected_tools']:
        extensions.append('hashicorp.terraform')
    
    # Universal productivity extensions
    extensions.extend([
        'eamodio.gitlens',  # GitLens
        'visualstudioexptteam.vscodeintellicode',  # IntelliCode
        'ms-vsliveshare.vsliveshare'  # Live Share
    ])
    
    # Generate settings based on preferences and project type
    settings = {
        'workbench.colorTheme': user_preferences.get('theme', 'Default Dark+'),
        'editor.fontSize': user_preferences.get('fontSize', 14),
        'editor.fontFamily': 'Fira Code, Cascadia Code, monospace',
        'editor.fontLigatures': True,
        'editor.minimap.enabled': True,
        'editor.wordWrap': 'on',
        'files.autoSave': 'afterDelay',
        'files.autoSaveDelay': 500,
        'editor.formatOnSave': True,
        'editor.codeActionsOnSave': {
            'source.organizeImports': True
        },
        'terminal.integrated.shell.linux': '/bin/bash',
        'git.enableSmartCommit': True,
        'git.confirmSync': False,
        'extensions.autoUpdate': False
    }
    
    # Language-specific settings
    if analysis['primary_language'] == 'python':
        settings.update({
            'python.defaultInterpreterPath': '/usr/bin/python3',
            'python.formatting.provider': 'black',
            'python.linting.enabled': True,
            'python.linting.pylintEnabled': True
        })
    
    if analysis['primary_language'] == 'javascript':
        settings.update({
            'typescript.preferences.quoteStyle': 'single',
            'javascript.preferences.quoteStyle': 'single',
            'prettier.singleQuote': True,
            'prettier.trailingComma': 'es5'
        })
    
    # Generate workspace name\n    workspace_name = f\"{project_type.replace('_', ' ').title()}\"\n    if analysis['detected_frameworks']:\n        workspace_name += f\" ({analysis['detected_frameworks'][0].title()})\"\n    \n    return {\n        'workspace_name': workspace_name,\n        'extensions': list(set(extensions)),  # Remove duplicates\n        'settings': settings,\n        'analysis': analysis\n    }\n\ndef _suggest_extensions_for_project(project_files: List[str], project_description: str, current_extensions: List[str]) -> dict:\n    \"\"\"Suggest extensions based on project files and description\"\"\"\n    \n    # Get file extensions\n    file_extensions = [os.path.splitext(f)[1] for f in project_files]\n    \n    suggestions = {\n        'recommended': [],\n        'optional': [],\n        'categories': {}\n    }\n    \n    # Language-based suggestions\n    if any(ext in ['.py', '.pyx'] for ext in file_extensions):\n        suggestions['recommended'].extend([\n            {'id': 'ms-python.python', 'name': 'Python', 'reason': 'Python files detected'},\n            {'id': 'ms-python.pylint', 'name': 'Pylint', 'reason': 'Python linting support'}\n        ])\n    \n    if any(ext in ['.js', '.ts', '.jsx', '.tsx'] for ext in file_extensions):\n        suggestions['recommended'].extend([\n            {'id': 'esbenp.prettier-vscode', 'name': 'Prettier', 'reason': 'JavaScript/TypeScript formatting'},\n            {'id': 'dbaeumer.vscode-eslint', 'name': 'ESLint', 'reason': 'JavaScript/TypeScript linting'}\n        ])\n    \n    if any(ext in ['.rs'] for ext in file_extensions):\n        suggestions['recommended'].append(\n            {'id': 'rust-lang.rust-analyzer', 'name': 'Rust Analyzer', 'reason': 'Rust files detected'}\n        )\n    \n    if any(ext in ['.go'] for ext in file_extensions):\n        suggestions['recommended'].append(\n            {'id': 'golang.go', 'name': 'Go', 'reason': 'Go files detected'}\n        )\n    \n    # Framework-based suggestions\n    if 'package.json' in project_files:\n        suggestions['recommended'].append(\n            {'id': 'ms-vscode.vscode-npm-script', 'name': 'npm Scripts', 'reason': 'package.json detected'}\n        )\n    \n    if 'Dockerfile' in project_files or any('docker' in f.lower() for f in project_files):\n        suggestions['recommended'].append(\n            {'id': 'ms-azuretools.vscode-docker', 'name': 'Docker', 'reason': 'Docker files detected'}\n        )\n    \n    # Universal suggestions (always useful)\n    universal_extensions = [\n        {'id': 'eamodio.gitlens', 'name': 'GitLens', 'reason': 'Enhanced Git capabilities'},\n        {'id': 'visualstudioexptteam.vscodeintellicode', 'name': 'IntelliCode', 'reason': 'AI-assisted development'},\n        {'id': 'ms-vsliveshare.vsliveshare', 'name': 'Live Share', 'reason': 'Collaborative editing'}\n    ]\n    \n    suggestions['optional'] = universal_extensions\n    \n    # Filter out already installed extensions\n    suggestions['recommended'] = [\n        ext for ext in suggestions['recommended']\n        if ext['id'] not in current_extensions\n    ]\n    \n    suggestions['optional'] = [\n        ext for ext in suggestions['optional']\n        if ext['id'] not in current_extensions\n    ]\n    \n    return suggestions