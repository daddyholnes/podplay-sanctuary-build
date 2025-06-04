"""
Workspace Manager - Manages development environments (NixOS, Docker, Cloud)
Handles environment creation, configuration, and management
"""

import os
import logging
import json
import subprocess
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import docker

logger = logging.getLogger(__name__)

@dataclass
class WorkspaceConfig:
    """Configuration for a development workspace"""
    type: str  # 'nixos', 'docker', 'cloud'
    name: str
    description: str
    language: str
    framework: str
    tools: List[str]
    resources: Dict[str, Any]
    environment_vars: Dict[str, str]

@dataclass
class Workspace:
    """Represents an active development workspace"""
    id: str
    name: str
    type: str
    status: str
    access_url: Optional[str]
    ssh_config: Optional[Dict]
    created_at: str
    last_used: Optional[str]
    resources: Dict[str, Any]

class WorkspaceManager:
    """Manages development environments (NixOS, Docker, Cloud)"""
    
    def __init__(self):
        self.workspaces = {}
        self.docker_client = None
        self.workspace_templates = self._load_workspace_templates()
        
        # Initialize Docker client
        self._initialize_docker()
        
        logger.info("🛠️ Workspace Manager initialized")
    
    def _initialize_docker(self):
        """Initialize Docker client"""
        try:
            self.docker_client = docker.from_env()
            self.docker_client.ping()
            logger.info("✅ Docker client initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️ Docker not available: {e}")
            self.docker_client = None
    
    def _load_workspace_templates(self) -> Dict[str, dict]:
        """Load predefined workspace templates"""
        
        return {
            'react_typescript': {
                'name': 'React + TypeScript',
                'description': 'Modern React application with TypeScript',
                'language': 'typescript',
                'framework': 'react',
                'tools': ['node', 'npm', 'vite', 'eslint', 'prettier'],
                'docker_image': 'node:18-alpine',
                'ports': [3000, 5173],
                'environment_vars': {
                    'NODE_ENV': 'development'
                }
            },
            'python_flask': {
                'name': 'Python + Flask',
                'description': 'Flask web application with Python',
                'language': 'python',
                'framework': 'flask',
                'tools': ['python3', 'pip', 'flask', 'pytest'],
                'docker_image': 'python:3.12-slim',
                'ports': [5000],
                'environment_vars': {
                    'FLASK_ENV': 'development',
                    'PYTHONPATH': '/app'
                }
            },
            'full_stack': {
                'name': 'Full Stack (React + Flask)',
                'description': 'Complete full-stack development environment',
                'language': 'multiple',
                'framework': 'full_stack',
                'tools': ['node', 'python3', 'docker', 'postgres'],
                'docker_compose': True,
                'ports': [3000, 5000, 5432],
                'environment_vars': {
                    'NODE_ENV': 'development',
                    'FLASK_ENV': 'development',
                    'DATABASE_URL': 'postgresql://user:pass@postgres:5432/dev'
                }
            },
            'ai_development': {
                'name': 'AI/ML Development',
                'description': 'Machine learning and AI development environment',
                'language': 'python',
                'framework': 'pytorch',
                'tools': ['python3', 'jupyter', 'pytorch', 'transformers', 'pandas'],
                'docker_image': 'pytorch/pytorch:2.1.0-cuda11.8-cudnn8-devel',
                'ports': [8888, 6006],
                'gpu_required': True,
                'environment_vars': {
                    'CUDA_VISIBLE_DEVICES': '0'
                }
            }
        }
    
    def create_workspace(self, config: dict) -> dict:
        """Create development environment based on configuration"""
        
        try:
            workspace_type = config.get('type', 'docker')
            template_name = config.get('template')
            
            logger.info(f"🛠️ Creating {workspace_type} workspace")
            
            if template_name and template_name in self.workspace_templates:
                # Use predefined template
                template = self.workspace_templates[template_name]
                workspace_config = WorkspaceConfig(
                    type=workspace_type,
                    name=config.get('name', template_name),
                    description=template['description'],
                    language=template['language'],
                    framework=template['framework'],
                    tools=template['tools'],
                    resources=config.get('resources', {}),
                    environment_vars=template.get('environment_vars', {})
                )
            else:
                # Custom configuration
                workspace_config = WorkspaceConfig(
                    type=workspace_type,
                    name=config.get('name', 'custom_workspace'),
                    description=config.get('description', 'Custom development workspace'),
                    language=config.get('language', 'python'),
                    framework=config.get('framework', ''),
                    tools=config.get('tools', []),
                    resources=config.get('resources', {}),
                    environment_vars=config.get('environment_vars', {})
                )
            
            if workspace_type == 'docker':
                return self._create_docker_workspace(workspace_config, template_name)
            elif workspace_type == 'nixos':
                return self._create_nixos_workspace(workspace_config)
            elif workspace_type == 'cloud':
                return self._create_cloud_workspace(workspace_config)
            else:
                raise ValueError(f"Unsupported workspace type: {workspace_type}")
                
        except Exception as e:
            logger.error(f"❌ Workspace creation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to create workspace: {str(e)}'
            }
    
    def _create_docker_workspace(self, config: WorkspaceConfig, template_name: str = None) -> dict:
        """Create Docker-based development environment"""
        
        if not self.docker_client:
            return {
                'success': False,
                'error': 'Docker not available',
                'message': 'Docker is required but not available on this system'
            }
        
        try:
            workspace_id = f"workspace_{config.name}_{int(datetime.now().timestamp())}"
            
            # Get template configuration
            template = self.workspace_templates.get(template_name, {})
            
            if template.get('docker_compose'):
                # Use docker-compose for complex environments
                return self._create_docker_compose_workspace(config, workspace_id, template)
            else:
                # Single container workspace
                return self._create_single_docker_workspace(config, workspace_id, template)
                
        except Exception as e:
            logger.error(f"❌ Docker workspace creation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Docker workspace creation failed: {str(e)}'
            }
    
    def _create_single_docker_workspace(self, config: WorkspaceConfig, workspace_id: str, template: dict) -> dict:
        """Create single Docker container workspace"""
        
        try:
            # Prepare Docker configuration
            docker_image = template.get('docker_image', 'ubuntu:22.04')
            ports = template.get('ports', [])
            environment_vars = {**template.get('environment_vars', {}), **config.environment_vars}
            
            # Create port bindings
            port_bindings = {}
            exposed_ports = {}
            for port in ports:
                port_bindings[f'{port}/tcp'] = None  # Auto-assign host port
                exposed_ports[port] = {}
            
            # Create volumes for persistence
            volumes = {
                f'{workspace_id}_data': {'bind': '/workspace', 'mode': 'rw'}
            }
            
            # Run container
            container = self.docker_client.containers.run(
                image=docker_image,
                name=workspace_id,
                detach=True,
                ports=port_bindings,
                volumes=volumes,
                environment=environment_vars,
                working_dir='/workspace',
                command='tail -f /dev/null',  # Keep container running
                remove=False
            )
            
            # Get assigned ports
            container.reload()
            assigned_ports = {}
            for port in ports:
                port_info = container.attrs['NetworkSettings']['Ports'].get(f'{port}/tcp')
                if port_info:
                    assigned_ports[port] = int(port_info[0]['HostPort'])
            
            # Create workspace object
            workspace = Workspace(
                id=workspace_id,
                name=config.name,
                type='docker',
                status='running',
                access_url=f"http://localhost:{assigned_ports.get(ports[0])}" if assigned_ports else None,
                ssh_config=None,
                created_at=datetime.now().isoformat(),
                last_used=datetime.now().isoformat(),
                resources={
                    'container_id': container.id,
                    'ports': assigned_ports,
                    'image': docker_image,
                    'volumes': volumes
                }
            )
            
            # Store workspace
            self.workspaces[workspace_id] = workspace
            
            # Install development tools in container
            self._setup_development_tools(container, config.tools)
            
            logger.info(f"✅ Docker workspace created: {workspace_id}")
            
            return {
                'success': True,
                'workspace': {
                    'id': workspace.id,
                    'name': workspace.name,
                    'type': workspace.type,
                    'status': workspace.status,
                    'access_url': workspace.access_url,
                    'ports': assigned_ports,
                    'container_id': container.id
                },
                'message': f'Docker workspace "{config.name}" created successfully'
            }
            
        except Exception as e:
            logger.error(f"❌ Single Docker workspace creation error: {e}")
            raise
    
    def _create_docker_compose_workspace(self, config: WorkspaceConfig, workspace_id: str, template: dict) -> dict:
        """Create Docker Compose workspace for complex environments"""
        
        try:
            # Generate docker-compose.yml
            compose_config = self._generate_docker_compose_config(config, template, workspace_id)
            
            # Create workspace directory
            workspace_dir = f"/tmp/workspaces/{workspace_id}"
            os.makedirs(workspace_dir, exist_ok=True)
            
            # Write docker-compose.yml
            compose_file_path = os.path.join(workspace_dir, 'docker-compose.yml')
            with open(compose_file_path, 'w') as f:
                f.write(compose_config)
            
            # Start services
            cmd = f"cd {workspace_dir} && docker-compose up -d"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Docker Compose failed: {result.stderr}")
            
            # Create workspace object
            workspace = Workspace(
                id=workspace_id,
                name=config.name,
                type='docker_compose',
                status='running',
                access_url=f"http://localhost:3000",  # Default frontend port
                ssh_config=None,
                created_at=datetime.now().isoformat(),
                last_used=datetime.now().isoformat(),
                resources={
                    'compose_file': compose_file_path,
                    'workspace_dir': workspace_dir,
                    'services': template.get('services', ['frontend', 'backend'])
                }
            )
            
            self.workspaces[workspace_id] = workspace
            
            logger.info(f"✅ Docker Compose workspace created: {workspace_id}")
            
            return {
                'success': True,
                'workspace': {
                    'id': workspace.id,
                    'name': workspace.name,
                    'type': workspace.type,
                    'status': workspace.status,
                    'access_url': workspace.access_url,
                    'compose_file': compose_file_path
                },
                'message': f'Docker Compose workspace "{config.name}" created successfully'
            }
            
        except Exception as e:
            logger.error(f"❌ Docker Compose workspace creation error: {e}")
            raise
    
    def _generate_docker_compose_config(self, config: WorkspaceConfig, template: dict, workspace_id: str) -> str:
        """Generate docker-compose.yml configuration"""
        
        if template.get('name') == 'Full Stack (React + Flask)':
            return f"""version: '3.8'
services:
  frontend:
    image: node:18-alpine
    container_name: {workspace_id}_frontend
    working_dir: /app
    ports:
      - "3000:3000"
    volumes:
      - {workspace_id}_frontend_data:/app
    environment:
      - NODE_ENV=development
    command: sh -c "npm install && npm run dev"
    
  backend:
    image: python:3.12-slim
    container_name: {workspace_id}_backend
    working_dir: /app
    ports:
      - "5000:5000"
    volumes:
      - {workspace_id}_backend_data:/app
    environment:
      - FLASK_ENV=development
      - PYTHONPATH=/app
      - DATABASE_URL=postgresql://user:password@postgres:5432/devdb
    command: sh -c "pip install flask flask-cors && python app.py"
    depends_on:
      - postgres
    
  postgres:
    image: postgres:15
    container_name: {workspace_id}_postgres
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=devdb
    ports:
      - "5432:5432"
    volumes:
      - {workspace_id}_postgres_data:/var/lib/postgresql/data

volumes:
  {workspace_id}_frontend_data:
  {workspace_id}_backend_data:
  {workspace_id}_postgres_data:
"""
        else:
            # Generic compose template
            return f"""version: '3.8'
services:
  app:
    image: {template.get('docker_image', 'ubuntu:22.04')}
    container_name: {workspace_id}_app
    working_dir: /workspace
    ports:
      - "3000:3000"
      - "5000:5000"
    volumes:
      - {workspace_id}_data:/workspace
    environment:
      - NODE_ENV=development
    command: tail -f /dev/null

volumes:
  {workspace_id}_data:
"""
    
    def _setup_development_tools(self, container, tools: List[str]):
        """Install development tools in container"""
        
        try:
            # Update package manager
            container.exec_run("apt-get update", workdir="/workspace")
            
            # Install common tools
            basic_tools = "apt-get install -y curl wget git vim nano"
            container.exec_run(basic_tools, workdir="/workspace")
            
            # Install specific tools
            for tool in tools:
                if tool == 'node':
                    container.exec_run("curl -fsSL https://deb.nodesource.com/setup_18.x | bash -", workdir="/workspace")
                    container.exec_run("apt-get install -y nodejs", workdir="/workspace")
                elif tool == 'python3':
                    container.exec_run("apt-get install -y python3 python3-pip", workdir="/workspace")
                elif tool == 'docker':
                    container.exec_run("apt-get install -y docker.io", workdir="/workspace")
                
            logger.info(f"✅ Development tools installed: {tools}")
            
        except Exception as e:
            logger.warning(f"⚠️ Tool installation warning: {e}")
    
    def _create_nixos_workspace(self, config: WorkspaceConfig) -> dict:
        """Create NixOS-based development environment"""
        
        # This would implement NixOS VM creation
        # For now, return a placeholder response
        
        return {
            'success': False,
            'message': 'NixOS workspace creation not yet implemented',
            'alternative': 'Consider using Docker workspace instead'
        }
    
    def _create_cloud_workspace(self, config: WorkspaceConfig) -> dict:
        """Create cloud-based development environment"""
        
        # This would implement cloud environment creation (GCP, Oracle, etc.)
        # For now, return a placeholder response
        
        return {
            'success': False,
            'message': 'Cloud workspace creation not yet implemented',
            'alternative': 'Consider using Docker workspace instead'
        }
    
    def list_workspaces(self) -> List[dict]:
        """List all active workspaces"""
        
        workspace_list = []
        
        for workspace in self.workspaces.values():
            workspace_list.append({
                'id': workspace.id,
                'name': workspace.name,
                'type': workspace.type,
                'status': workspace.status,
                'access_url': workspace.access_url,
                'created_at': workspace.created_at,
                'last_used': workspace.last_used
            })
        
        return workspace_list
    
    def get_workspace(self, workspace_id: str) -> Optional[dict]:
        """Get workspace details"""
        
        workspace = self.workspaces.get(workspace_id)
        if not workspace:
            return None
        
        return {
            'id': workspace.id,
            'name': workspace.name,
            'type': workspace.type,
            'status': workspace.status,
            'access_url': workspace.access_url,
            'created_at': workspace.created_at,
            'last_used': workspace.last_used,
            'resources': workspace.resources
        }
    
    def stop_workspace(self, workspace_id: str) -> dict:
        """Stop a workspace"""
        
        try:
            workspace = self.workspaces.get(workspace_id)
            if not workspace:
                return {'success': False, 'error': 'Workspace not found'}
            
            if workspace.type == 'docker':
                container_id = workspace.resources.get('container_id')
                if container_id and self.docker_client:
                    container = self.docker_client.containers.get(container_id)
                    container.stop()
                    workspace.status = 'stopped'
            
            elif workspace.type == 'docker_compose':
                workspace_dir = workspace.resources.get('workspace_dir')
                if workspace_dir:
                    cmd = f"cd {workspace_dir} && docker-compose down"
                    subprocess.run(cmd, shell=True)
                    workspace.status = 'stopped'
            
            return {
                'success': True,
                'message': f'Workspace {workspace_id} stopped successfully'
            }
            
        except Exception as e:
            logger.error(f"❌ Error stopping workspace: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to stop workspace: {str(e)}'
            }
    
    def delete_workspace(self, workspace_id: str) -> dict:
        """Delete a workspace and clean up resources"""
        
        try:
            workspace = self.workspaces.get(workspace_id)
            if not workspace:
                return {'success': False, 'error': 'Workspace not found'}
            
            # Stop workspace first
            self.stop_workspace(workspace_id)
            
            # Clean up resources
            if workspace.type == 'docker':
                container_id = workspace.resources.get('container_id')
                if container_id and self.docker_client:
                    try:
                        container = self.docker_client.containers.get(container_id)
                        container.remove(force=True)
                    except:
                        pass  # Container might already be removed
            
            elif workspace.type == 'docker_compose':
                workspace_dir = workspace.resources.get('workspace_dir')
                if workspace_dir:
                    cmd = f"cd {workspace_dir} && docker-compose down -v"
                    subprocess.run(cmd, shell=True)
                    # Remove workspace directory
                    import shutil
                    shutil.rmtree(workspace_dir, ignore_errors=True)
            
            # Remove from workspace list
            del self.workspaces[workspace_id]
            
            return {
                'success': True,
                'message': f'Workspace {workspace_id} deleted successfully'
            }
            
        except Exception as e:
            logger.error(f"❌ Error deleting workspace: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to delete workspace: {str(e)}'
            }
    
    def get_workspace_templates(self) -> List[dict]:
        """Get available workspace templates"""
        
        templates = []
        for template_id, template in self.workspace_templates.items():
            templates.append({
                'id': template_id,
                'name': template['name'],
                'description': template['description'],
                'language': template['language'],
                'framework': template['framework'],
                'tools': template['tools']
            })
        
        return templates