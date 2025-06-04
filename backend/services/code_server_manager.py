"""
Code-Server Manager - Browser-based VSCode with Docker/Cloud deployment
Provides full VSCode functionality in the browser with dynamic environment provisioning
"""

import os
import logging
import json
import asyncio
import subprocess
import tempfile
import shutil
import socket
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import docker
import yaml
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class CodeServerInstance:
    """Data class for code-server instance configuration"""
    id: str
    name: str
    port: int
    password: str
    workspace_path: str
    container_id: Optional[str]
    docker_image: str
    status: str  # 'starting', 'running', 'stopped', 'error'
    created_at: str
    last_accessed: str
    environment_id: Optional[str]  # Link to NixOS environment
    extensions: List[str]
    settings: Dict[str, Any]
    cloud_deployment: Optional[Dict[str, Any]]

class CodeServerManager:
    """Manages code-server instances with Docker and Google Cloud integration"""
    
    def __init__(self):
        self.instances = {}
        self.docker_client = None
        self.base_port = 8080
        self.max_instances = 10
        self.code_server_image = "codercom/code-server:latest"
        self.instances_base_path = "/tmp/code_server_instances"
        
        # Google Cloud configuration
        self.gcp_project_id = os.getenv('PRIMARY_SERVICE_ACCOUNT_PROJECT_ID', 'podplay-build-alpha')
        self.gcp_region = 'us-central1'
        self.service_account_path = os.getenv('PRIMARY_SERVICE_ACCOUNT_PATH')
        
        # Initialize Docker client
        try:
            self.docker_client = docker.from_env()
            logger.info("🐳 Docker client initialized for code-server")
        except Exception as e:
            logger.warning(f"⚠️ Docker client not available: {e}")
        
        # Ensure base paths exist
        os.makedirs(self.instances_base_path, exist_ok=True)
        
        # Load extension catalog
        self.extension_catalog = self._load_extension_catalog()
        
        logger.info("💻 Code-Server Manager initialized")
    
    def _load_extension_catalog(self) -> Dict[str, dict]:
        """Load catalog of popular VSCode extensions"""
        
        return {
            # Language Support
            'python': {
                'id': 'ms-python.python',
                'name': 'Python',
                'description': 'Python language support',
                'category': 'programming_languages'
            },
            'typescript': {
                'id': 'ms-vscode.vscode-typescript-next',
                'name': 'TypeScript',
                'description': 'TypeScript and JavaScript language support',
                'category': 'programming_languages'
            },
            'rust': {
                'id': 'rust-lang.rust-analyzer',
                'name': 'Rust Analyzer',
                'description': 'Rust language support',
                'category': 'programming_languages'
            },
            'go': {
                'id': 'golang.go',
                'name': 'Go',
                'description': 'Go language support',
                'category': 'programming_languages'
            },
            
            # Frameworks
            'react': {
                'id': 'ms-vscode.vscode-react-native',
                'name': 'React Native Tools',
                'description': 'React development tools',
                'category': 'frameworks'
            },
            'vue': {
                'id': 'octref.vetur',
                'name': 'Vetur',
                'description': 'Vue.js language support',
                'category': 'frameworks'
            },
            'svelte': {
                'id': 'svelte.svelte-vscode',
                'name': 'Svelte',
                'description': 'Svelte language support',
                'category': 'frameworks'
            },
            
            # Cloud & DevOps
            'docker': {
                'id': 'ms-azuretools.vscode-docker',
                'name': 'Docker',
                'description': 'Docker support',
                'category': 'devops'
            },
            'kubernetes': {
                'id': 'ms-kubernetes-tools.vscode-kubernetes-tools',
                'name': 'Kubernetes',
                'description': 'Kubernetes support',
                'category': 'devops'
            },
            'terraform': {
                'id': 'hashicorp.terraform',
                'name': 'Terraform',
                'description': 'Infrastructure as Code',
                'category': 'devops'
            },
            'gcloud': {
                'id': 'googlecloudtools.cloudcode',
                'name': 'Cloud Code',
                'description': 'Google Cloud development tools',
                'category': 'cloud'
            },
            
            # Productivity
            'prettier': {
                'id': 'esbenp.prettier-vscode',
                'name': 'Prettier',
                'description': 'Code formatter',
                'category': 'productivity'
            },
            'eslint': {
                'id': 'dbaeumer.vscode-eslint',
                'name': 'ESLint',
                'description': 'JavaScript/TypeScript linting',
                'category': 'productivity'
            },
            'git_lens': {
                'id': 'eamodio.gitlens',
                'name': 'GitLens',
                'description': 'Enhanced Git capabilities',
                'category': 'productivity'
            },
            'live_share': {
                'id': 'ms-vsliveshare.vsliveshare',
                'name': 'Live Share',
                'description': 'Collaborative editing',
                'category': 'collaboration'
            },
            
            # AI & Assistance
            'github_copilot': {
                'id': 'github.copilot',
                'name': 'GitHub Copilot',
                'description': 'AI pair programmer',
                'category': 'ai_assistance'
            },
            'intellicode': {
                'id': 'visualstudioexptteam.vscodeintellicode',
                'name': 'IntelliCode',
                'description': 'AI-assisted development',
                'category': 'ai_assistance'
            }
        }
    
    def _find_available_port(self) -> int:
        """Find an available port for code-server"""
        
        for port in range(self.base_port, self.base_port + 100):
            if not self._is_port_in_use(port):
                return port
        
        raise Exception("No available ports found")
    
    def _is_port_in_use(self, port: int) -> bool:
        """Check if a port is already in use"""
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    
    def _generate_password(self) -> str:
        """Generate a secure password for code-server"""
        
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(16))
    
    async def create_code_server_instance(self, config: dict) -> dict:
        """Create a new code-server instance"""
        
        try:
            instance_name = config.get('name', f"code_server_{int(datetime.now().timestamp())}")
            environment_id = config.get('environment_id')
            workspace_path = config.get('workspace_path', '/workspace')
            extensions = config.get('extensions', [])
            settings = config.get('settings', {})
            
            # Generate instance configuration
            instance_id = f"cs_{int(datetime.now().timestamp())}"
            port = self._find_available_port()
            password = self._generate_password()
            
            logger.info(f"💻 Creating code-server instance: {instance_name}")
            
            # Create instance directory
            instance_path = os.path.join(self.instances_base_path, instance_id)
            os.makedirs(instance_path, exist_ok=True)
            
            # Create workspace directory
            workspace_full_path = os.path.join(instance_path, 'workspace')
            os.makedirs(workspace_full_path, exist_ok=True)
            
            # Create code-server configuration
            await self._generate_code_server_config(instance_path, port, password, settings)
            
            # Create Docker configuration
            docker_config = await self._generate_docker_config(
                instance_id, port, workspace_full_path, instance_path, extensions
            )
            
            # Create instance object
            instance = CodeServerInstance(
                id=instance_id,
                name=instance_name,
                port=port,
                password=password,
                workspace_path=workspace_full_path,
                container_id=None,
                docker_image=self.code_server_image,
                status='starting',
                created_at=datetime.now().isoformat(),
                last_accessed=datetime.now().isoformat(),
                environment_id=environment_id,
                extensions=extensions,
                settings=settings,
                cloud_deployment=None
            )
            
            # Start Docker container
            if self.docker_client:
                container_result = await self._start_docker_container(instance, docker_config)
                if container_result['success']:
                    instance.container_id = container_result['container_id']
                    instance.status = 'running'
                else:
                    instance.status = 'error'
                    return {
                        'success': False,
                        'error': container_result['error'],
                        'message': f'Failed to start container: {container_result["error"]}'
                    }
            else:
                return {
                    'success': False,
                    'error': 'Docker not available',
                    'message': 'Docker is required for code-server instances'
                }
            
            # Register instance
            self.instances[instance_id] = instance
            
            # Wait for code-server to be ready
            await self._wait_for_code_server_ready(instance)
            
            logger.info(f"✅ Code-server instance created: {instance_id}")
            
            return {
                'success': True,
                'instance_id': instance_id,
                'instance': asdict(instance),
                'access_url': f'http://localhost:{port}',
                'password': password,
                'message': f'Code-server instance "{instance_name}" is ready'
            }
            
        except Exception as e:
            logger.error(f"❌ Code-server creation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to create code-server instance: {str(e)}'
            }
    
    async def _generate_code_server_config(self, instance_path: str, port: int, password: str, settings: dict):
        """Generate code-server configuration files"""
        
        # Generate config.yaml
        config = {
            'bind-addr': f'0.0.0.0:{port}',
            'auth': 'password',
            'password': password,
            'cert': False,
            'disable-telemetry': True,
            'disable-update-check': True
        }
        
        config_path = os.path.join(instance_path, 'config.yaml')
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
        
        # Generate VSCode settings.json
        default_settings = {
            'workbench.colorTheme': 'Default Dark+',
            'editor.fontSize': 14,
            'editor.fontFamily': 'Fira Code, monospace',
            'editor.fontLigatures': True,
            'editor.minimap.enabled': True,
            'editor.wordWrap': 'on',
            'files.autoSave': 'afterDelay',
            'terminal.integrated.shell.linux': '/bin/bash',
            'extensions.autoUpdate': False
        }
        
        # Merge with user settings
        final_settings = {**default_settings, **settings}
        
        # Create VSCode settings directory
        vscode_settings_path = os.path.join(instance_path, 'workspace', '.vscode')
        os.makedirs(vscode_settings_path, exist_ok=True)
        
        settings_file = os.path.join(vscode_settings_path, 'settings.json')
        with open(settings_file, 'w') as f:
            json.dump(final_settings, f, indent=2)
        
        logger.info(f"✅ Code-server config generated: {instance_path}")
    
    async def _generate_docker_config(self, instance_id: str, port: int, workspace_path: str, instance_path: str, extensions: List[str]) -> dict:
        """Generate Docker configuration for code-server"""
        
        # Create Dockerfile for custom image with extensions
        dockerfile_content = f"""FROM {self.code_server_image}

USER root

# Install additional tools
RUN apt-get update && apt-get install -y \\
    git \\
    curl \\
    wget \\
    unzip \\
    build-essential \\
    python3 \\
    python3-pip \\
    nodejs \\
    npm \\
    && rm -rf /var/lib/apt/lists/*

# Install bun
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="$PATH:/root/.bun/bin"

# Create workspace directory
RUN mkdir -p /workspace
RUN chown -R coder:coder /workspace

USER coder

# Install extensions
{chr(10).join([f'RUN code-server --install-extension {ext}' for ext in extensions])}

# Copy configuration
COPY config.yaml /home/coder/.config/code-server/

# Set working directory
WORKDIR /workspace

# Expose port
EXPOSE {port}

# Start code-server
CMD ["code-server", "--bind-addr", "0.0.0.0:{port}", "/workspace"]
"""
        
        dockerfile_path = os.path.join(instance_path, 'Dockerfile')
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        
        return {
            'dockerfile_path': dockerfile_path,
            'instance_path': instance_path,
            'workspace_path': workspace_path
        }
    
    async def _start_docker_container(self, instance: CodeServerInstance, docker_config: dict) -> dict:
        """Start Docker container for code-server"""
        
        try:
            if not self.docker_client:
                return {
                    'success': False,
                    'error': 'Docker client not available'
                }
            
            logger.info(f"🐳 Starting Docker container for {instance.id}")
            
            # Build custom image
            image_tag = f"code-server-{instance.id}"
            
            try:
                image, build_logs = self.docker_client.images.build(
                    path=docker_config['instance_path'],
                    tag=image_tag,
                    rm=True
                )
                
                logger.info(f"✅ Docker image built: {image_tag}")
                
            except docker.errors.BuildError as e:
                logger.error(f"❌ Docker build failed: {e}")
                return {
                    'success': False,
                    'error': f'Docker build failed: {str(e)}'
                }
            
            # Start container
            try:
                container = self.docker_client.containers.run(
                    image_tag,
                    name=instance.id,
                    detach=True,
                    ports={f'{instance.port}/tcp': instance.port},
                    volumes={
                        docker_config['workspace_path']: {'bind': '/workspace', 'mode': 'rw'}
                    },
                    environment={
                        'PASSWORD': instance.password
                    },
                    user='coder',
                    working_dir='/workspace'
                )
                
                logger.info(f"✅ Container started: {container.id}")
                
                return {
                    'success': True,
                    'container_id': container.id,
                    'image_tag': image_tag
                }
                
            except docker.errors.ContainerError as e:
                logger.error(f"❌ Container start failed: {e}")
                return {
                    'success': False,
                    'error': f'Container start failed: {str(e)}'
                }
            
        except Exception as e:
            logger.error(f"❌ Docker container creation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _wait_for_code_server_ready(self, instance: CodeServerInstance, timeout: int = 60):
        """Wait for code-server to be ready to accept connections"""
        
        import aiohttp
        
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < timeout:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f'http://localhost:{instance.port}', timeout=5) as response:
                        if response.status in [200, 401, 302]:  # 401 = needs auth, 302 = redirect to login
                            logger.info(f"✅ Code-server ready: {instance.id}")
                            return True
            except:
                pass
            
            await asyncio.sleep(2)
        
        logger.warning(f"⚠️ Code-server not ready within timeout: {instance.id}")
        return False
    
    def list_instances(self) -> List[dict]:
        """List all code-server instances"""
        
        return [
            {
                'id': instance_id,
                'name': instance.name,
                'status': instance.status,
                'port': instance.port,
                'access_url': f'http://localhost:{instance.port}' if instance.status == 'running' else None,
                'created_at': instance.created_at,
                'last_accessed': instance.last_accessed,
                'environment_id': instance.environment_id,
                'extensions_count': len(instance.extensions)
            }
            for instance_id, instance in self.instances.items()
        ]
    
    def get_instance_details(self, instance_id: str) -> dict:
        """Get detailed information about an instance"""
        
        if instance_id not in self.instances:
            return {
                'success': False,
                'error': 'Instance not found'
            }
        
        instance = self.instances[instance_id]
        
        return {
            'success': True,
            'instance': asdict(instance),
            'access_info': {
                'local_url': f'http://localhost:{instance.port}' if instance.status == 'running' else None,
                'password': instance.password,
                'workspace_path': instance.workspace_path
            }
        }
