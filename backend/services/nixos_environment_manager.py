"""
NixOS Environment Manager - Advanced environment management and reproducibility
Enables Mama Bear to create, configure, and manage NixOS environments with full control
"""

import os
import logging
import json
import yaml
import asyncio
import subprocess
import tempfile
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import docker
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class NixEnvironment:
    """Data class for NixOS environment configuration"""
    id: str
    name: str
    description: str
    nix_config: Dict[str, Any]
    packages: List[str]
    environment_variables: Dict[str, str]
    shell_hooks: List[str]
    status: str  # 'creating', 'active', 'stopped', 'error'
    created_at: str
    last_updated: str
    resource_limits: Dict[str, Any]
    persistent_storage: bool
    auto_cleanup: bool

class NixOSEnvironmentManager:
    """Manages NixOS environments with advanced configuration and orchestration"""
    
    def __init__(self):
        self.environments = {}
        self.templates = self._load_environment_templates()
        self.docker_client = None
        self.nix_store_path = "/nix/store"
        self.environments_base_path = "/tmp/nixos_environments"
        
        # Initialize Docker client for containerized environments
        try:
            self.docker_client = docker.from_env()
            logger.info("🐳 Docker client initialized for NixOS containers")
        except Exception as e:
            logger.warning(f"⚠️ Docker client not available: {e}")
        
        # Ensure base paths exist
        os.makedirs(self.environments_base_path, exist_ok=True)
        
        # Check Nix availability
        self.nix_available = self._check_nix_availability()
        
        logger.info("❄️ NixOS Environment Manager initialized")
    
    def _check_nix_availability(self) -> bool:
        """Check if Nix is available on the system"""
        
        try:
            result = subprocess.run(['nix', '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info(f"✅ Nix available: {result.stdout.strip()}")
                return True
            else:
                logger.warning("⚠️ Nix not available, will use containerized environments")
                return False
        except Exception as e:
            logger.warning(f"⚠️ Nix check failed: {e}")
            return False
    
    def _load_environment_templates(self) -> Dict[str, dict]:
        """Load predefined NixOS environment templates"""
        
        return {
            'development_minimal': {
                'name': 'Minimal Development Environment',
                'description': 'Lightweight development environment with essential tools',
                'packages': [
                    'git', 'curl', 'wget', 'vim', 'htop', 'tree',
                    'nodejs', 'python3', 'python3Packages.pip'
                ],
                'environment_variables': {
                    'EDITOR': 'vim',
                    'LANG': 'en_US.UTF-8'
                },
                'shell_hooks': [
                    'echo "Welcome to Minimal Development Environment"',
                    'echo "Available tools: git, nodejs, python3"'
                ],
                'resource_limits': {
                    'memory': '1GB',
                    'cpu': '1',
                    'disk': '5GB'
                }
            },
            'full_stack_web': {
                'name': 'Full Stack Web Development',
                'description': 'Complete web development environment with modern tools',
                'packages': [
                    'git', 'nodejs_20', 'yarn', 'python3', 'python3Packages.pip',
                    'docker', 'docker-compose', 'postgresql', 'redis',
                    'nginx', 'chromium', 'firefox', 'code-server'
                ],
                'environment_variables': {
                    'NODE_ENV': 'development',
                    'EDITOR': 'code',
                    'DATABASE_URL': 'postgresql://localhost:5432/dev'
                },
                'shell_hooks': [
                    'echo "Full Stack Web Development Environment Ready"',
                    'echo "Starting services..."',
                    'pg_ctl start -D $PGDATA || true',
                    'redis-server --daemonize yes || true',
                    'echo "Services started. Happy coding!"'
                ],
                'resource_limits': {
                    'memory': '4GB',
                    'cpu': '2',
                    'disk': '20GB'
                }
            },
            'data_science': {
                'name': 'Data Science & ML Environment',
                'description': 'Comprehensive data science environment with ML libraries',
                'packages': [
                    'git', 'python3', 'python3Packages.pip', 'python3Packages.numpy',
                    'python3Packages.pandas', 'python3Packages.scikit-learn',
                    'python3Packages.matplotlib', 'python3Packages.seaborn',
                    'python3Packages.jupyter', 'python3Packages.tensorflow',
                    'python3Packages.pytorch', 'r', 'rstudio'
                ],
                'environment_variables': {
                    'JUPYTER_CONFIG_DIR': '/tmp/jupyter',
                    'PYTHONPATH': '/workspace/src',
                    'R_LIBS_USER': '/workspace/r_libs'
                },
                'shell_hooks': [
                    'echo "Data Science Environment Initialized"',
                    'echo "Starting Jupyter Lab..."',
                    'mkdir -p $JUPYTER_CONFIG_DIR',
                    'jupyter lab --allow-root --ip=0.0.0.0 --port=8888 &'
                ],
                'resource_limits': {
                    'memory': '8GB',
                    'cpu': '4',
                    'disk': '50GB'
                }
            },
            'devops_infrastructure': {
                'name': 'DevOps & Infrastructure',
                'description': 'Infrastructure management and DevOps tooling',
                'packages': [
                    'git', 'docker', 'docker-compose', 'kubectl', 'terraform',
                    'ansible', 'packer', 'vault', 'consul', 'nomad',
                    'prometheus', 'grafana', 'nginx', 'helm'
                ],
                'environment_variables': {
                    'KUBECONFIG': '/workspace/.kube/config',
                    'TERRAFORM_LOG': 'INFO',
                    'ANSIBLE_HOST_KEY_CHECKING': 'False'
                },
                'shell_hooks': [
                    'echo "DevOps Infrastructure Environment Ready"',
                    'echo "Available tools: docker, kubectl, terraform, ansible"',
                    'mkdir -p /workspace/.kube',
                    'echo "Configure your cloud credentials to get started"'
                ],
                'resource_limits': {
                    'memory': '6GB',
                    'cpu': '3',
                    'disk': '30GB'
                }
            },
            'nixos_development': {
                'name': 'NixOS Development Environment',
                'description': 'Specialized environment for NixOS development and packaging',
                'packages': [
                    'git', 'nix', 'nixpkgs-review', 'nix-build', 'nix-shell',
                    'nixfmt', 'nix-tree', 'nix-du', 'cachix'
                ],
                'environment_variables': {
                    'NIX_PATH': 'nixpkgs=/nix/var/nix/profiles/per-user/root/channels/nixos',
                    'NIX_BUILD_CORES': '0'
                },
                'shell_hooks': [
                    'echo "NixOS Development Environment Ready"',
                    'echo "Nix flakes enabled by default"',
                    'nix --version'
                ],
                'resource_limits': {
                    'memory': '4GB',
                    'cpu': '2',
                    'disk': '25GB'
                }
            }
        }
    
    async def create_environment(self, template_name: str, custom_config: dict = None, user_id: str = None) -> dict:
        """Create a new NixOS environment from template or custom configuration"""
        
        try:
            logger.info(f"❄️ Creating NixOS environment: {template_name}")
            
            # Get template or use custom config
            if template_name in self.templates:
                base_config = self.templates[template_name].copy()
            else:
                base_config = custom_config or {}
            
            # Merge custom configuration
            if custom_config:
                base_config.update(custom_config)
            
            # Generate environment ID
            env_id = f"nix_{template_name}_{int(datetime.now().timestamp())}"
            env_path = os.path.join(self.environments_base_path, env_id)
            
            # Create environment configuration
            environment = NixEnvironment(
                id=env_id,
                name=base_config.get('name', template_name),
                description=base_config.get('description', 'Custom NixOS environment'),
                nix_config=base_config,
                packages=base_config.get('packages', []),
                environment_variables=base_config.get('environment_variables', {}),
                shell_hooks=base_config.get('shell_hooks', []),
                status='creating',
                created_at=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat(),
                resource_limits=base_config.get('resource_limits', {}),
                persistent_storage=base_config.get('persistent_storage', True),
                auto_cleanup=base_config.get('auto_cleanup', False)
            )
            
            # Create environment directory
            os.makedirs(env_path, exist_ok=True)
            
            # Generate Nix configuration files
            await self._generate_nix_config(environment, env_path)
            
            # Build the environment
            if self.nix_available:
                build_result = await self._build_nix_environment(environment, env_path)
            else:
                build_result = await self._build_containerized_environment(environment, env_path)
            
            if build_result['success']:
                environment.status = 'active'
                self.environments[env_id] = environment
                
                logger.info(f"✅ NixOS environment created successfully: {env_id}")
                
                return {
                    'success': True,
                    'environment_id': env_id,
                    'environment': asdict(environment),
                    'build_info': build_result,
                    'message': f'Environment "{environment.name}" created successfully',
                    'access_info': {
                        'shell_command': f'nix-shell {env_path}/shell.nix',
                        'environment_path': env_path,
                        'container_name': build_result.get('container_name')
                    }
                }
            else:
                environment.status = 'error'
                return {
                    'success': False,
                    'error': build_result.get('error'),
                    'message': f'Failed to create environment: {build_result.get("error")}'
                }
                
        except Exception as e:
            logger.error(f"❌ Environment creation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to create environment: {str(e)}'
            }
    
    async def _generate_nix_config(self, environment: NixEnvironment, env_path: str):
        """Generate Nix configuration files for the environment"""
        
        try:
            # Generate shell.nix
            shell_nix_content = self._generate_shell_nix(environment)
            with open(os.path.join(env_path, 'shell.nix'), 'w') as f:
                f.write(shell_nix_content)
            
            # Generate flake.nix for modern Nix workflows
            flake_nix_content = self._generate_flake_nix(environment)
            with open(os.path.join(env_path, 'flake.nix'), 'w') as f:
                f.write(flake_nix_content)
            
            # Generate flake.lock
            flake_lock_content = self._generate_flake_lock()
            with open(os.path.join(env_path, 'flake.lock'), 'w') as f:
                f.write(json.dumps(flake_lock_content, indent=2))
            
            # Generate environment activation script
            activation_script = self._generate_activation_script(environment)
            activation_path = os.path.join(env_path, 'activate.sh')
            with open(activation_path, 'w') as f:
                f.write(activation_script)
            os.chmod(activation_path, 0o755)
            
            # Generate Docker configuration if needed
            if not self.nix_available:
                dockerfile_content = self._generate_dockerfile(environment)
                with open(os.path.join(env_path, 'Dockerfile'), 'w') as f:
                    f.write(dockerfile_content)
                
                docker_compose_content = self._generate_docker_compose(environment)
                with open(os.path.join(env_path, 'docker-compose.yml'), 'w') as f:
                    f.write(docker_compose_content)
            
            logger.info(f"✅ Nix configuration files generated for {environment.id}")
            
        except Exception as e:
            logger.error(f"❌ Config generation failed: {e}")
            raise
    
    def _generate_shell_nix(self, environment: NixEnvironment) -> str:
        """Generate shell.nix content"""
        
        packages_list = '\n    '.join(environment.packages)
        env_vars = '\n    '.join([f'{k} = "{v}";' for k, v in environment.environment_variables.items()])
        shell_hooks = '\n    '.join(environment.shell_hooks)
        
        return f'''{{ pkgs ? import <nixpkgs> {{}} }}:

pkgs.mkShell {{
  buildInputs = with pkgs; [
    {packages_list}
  ];

  shellHook = ''
    # Environment Variables
    export {' '.join([f'{k}="{v}"' for k, v in environment.environment_variables.items()])}
    
    # Shell Hooks
    {chr(10).join(environment.shell_hooks)}
    
    # Custom prompt
    export PS1="\\n\\[\\033[1;32m\\][{environment.name}]\\[\\033[0m\\] \\[\\033[1;34m\\]\\w\\[\\033[0m\\] \\$ "
    
    echo "🏗️  Environment: {environment.name}"
    echo "📦 Packages: {len(environment.packages)} installed"
    echo "🚀 Ready for development!"
  '';

  # Environment variables
  {env_vars}
}}
'''
    
    def _generate_flake_nix(self, environment: NixEnvironment) -> str:
        """Generate flake.nix for modern Nix workflows"""
        
        packages_list = '\n        '.join(environment.packages)
        
        return f'''{{
  description = "{environment.description}";

  inputs = {{
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  }};

  outputs = {{ self, nixpkgs, flake-utils }}:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${{system}};
      in
      {{
        devShells.default = pkgs.mkShell {{
          buildInputs = with pkgs; [
            {packages_list}
          ];

          shellHook = ''
            {chr(10).join(environment.shell_hooks)}
            
            echo "🏗️  Environment: {environment.name}"
            echo "📦 Packages available via Nix Flake"
            echo "🚀 Development environment ready!"
          '';

          # Environment variables
          {chr(10).join([f'          {k} = "{v}";' for k, v in environment.environment_variables.items()])}
        }};

        # Optional: provide the environment as a package
        packages.environment = pkgs.buildEnv {{
          name = "{environment.id}";
          paths = with pkgs; [
            {packages_list}
          ];
        }};
      }});
}}
'''
    
    def _generate_flake_lock(self) -> dict:
        """Generate basic flake.lock structure"""
        
        return {
            "nodes": {
                "flake-utils": {
                    "locked": {
                        "lastModified": 1678901627,
                        "narHash": "sha256-U02riOqrKKzwjsxGdhZnXzTrt3hGFh9XWX7Okl9/bnY=",
                        "owner": "numtide",
                        "repo": "flake-utils",
                        "rev": "93a2b84fc4b70d9e089d029deacc3583435c2ed6",
                        "type": "github"
                    },
                    "original": {
                        "owner": "numtide",
                        "repo": "flake-utils",
                        "type": "github"
                    }
                },
                "nixpkgs": {
                    "locked": {
                        "lastModified": 1678875422,
                        "narHash": "sha256-T3o6NcQPwXjxJMn2shz86Chch4ljXgZn746c2caGxd8=",
                        "owner": "NixOS",
                        "repo": "nixpkgs",
                        "rev": "56528ee42526794d413314b6d1a8005a93bb0c67",
                        "type": "github"
                    },
                    "original": {
                        "owner": "NixOS",
                        "ref": "nixos-unstable",
                        "repo": "nixpkgs",
                        "type": "github"
                    }
                },
                "root": {
                    "inputs": {
                        "flake-utils": "flake-utils",
                        "nixpkgs": "nixpkgs"
                    }
                }
            },
            "root": "root",
            "version": 7
        }
    
    def _generate_activation_script(self, environment: NixEnvironment) -> str:
        """Generate environment activation script"""
        
        return f'''#!/bin/bash
# Activation script for {environment.name}
# Environment ID: {environment.id}

set -e

echo "🏗️  Activating NixOS Environment: {environment.name}"
echo "📍 Environment ID: {environment.id}"

# Set environment variables
{chr(10).join([f'export {k}="{v}"' for k, v in environment.environment_variables.items()])}

# Create workspace directories
mkdir -p /workspace/src
mkdir -p /workspace/data
mkdir -p /workspace/logs

# Run shell hooks
{chr(10).join(environment.shell_hooks)}

# Start environment-specific services
echo "🚀 Environment ready!"

# Drop into nix-shell
if command -v nix-shell &> /dev/null; then
    echo "Entering nix-shell..."
    nix-shell shell.nix
else
    echo "⚠️  Nix not available, using system shell"
    bash
fi
'''
    
    def _generate_dockerfile(self, environment: NixEnvironment) -> str:
        """Generate Dockerfile for containerized environments"""
        
        packages_install = ' '.join(environment.packages)
        env_vars = '\n'.join([f'ENV {k}="{v}"' for k, v in environment.environment_variables.items()])
        
        return f'''FROM nixos/nix:latest

# Install packages
RUN nix-env -iA nixpkgs.{' nixpkgs.'.join(environment.packages)}

# Set environment variables
{env_vars}

# Create workspace
WORKDIR /workspace
RUN mkdir -p /workspace/src /workspace/data /workspace/logs

# Copy configuration files
COPY shell.nix /workspace/
COPY flake.nix /workspace/
COPY flake.lock /workspace/
COPY activate.sh /workspace/

# Make activation script executable
RUN chmod +x /workspace/activate.sh

# Expose common ports
EXPOSE 3000 8000 8080 8888 9000

# Set up shell hooks
RUN echo '{chr(10).join(environment.shell_hooks)}' > /workspace/.nixos_hooks

# Default command
CMD ["/workspace/activate.sh"]
'''
    
    def _generate_docker_compose(self, environment: NixEnvironment) -> str:
        """Generate docker-compose.yml for the environment"""
        
        resource_limits = environment.resource_limits
        
        return f'''version: '3.8'

services:
  nixos-env:
    build: .
    container_name: {environment.id}
    volumes:
      - ./workspace:/workspace
      - nixos-store:/nix/store
    ports:
      - "3000:3000"
      - "8000:8000"
      - "8080:8080"
      - "8888:8888"
      - "9000:9000"
    environment:
      - ENVIRONMENT_ID={environment.id}
      - ENVIRONMENT_NAME={environment.name}
    deploy:
      resources:
        limits:
          memory: {resource_limits.get('memory', '2GB')}
          cpus: '{resource_limits.get('cpu', '1')}'
    restart: unless-stopped
    stdin_open: true
    tty: true

volumes:
  nixos-store:
    driver: local
'''
    
    async def _build_nix_environment(self, environment: NixEnvironment, env_path: str) -> dict:
        """Build environment using native Nix"""
        
        try:
            logger.info(f"🔨 Building Nix environment: {environment.id}")
            
            # Build using nix-shell
            build_cmd = ['nix-shell', '--pure', os.path.join(env_path, 'shell.nix'), '--run', 'echo "Build successful"']
            
            result = subprocess.run(
                build_cmd,
                cwd=env_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Nix environment built successfully: {environment.id}")
                return {
                    'success': True,
                    'build_method': 'nix-shell',
                    'build_output': result.stdout,
                    'environment_path': env_path
                }
            else:
                logger.error(f"❌ Nix build failed: {result.stderr}")
                return {
                    'success': False,
                    'error': result.stderr,
                    'build_method': 'nix-shell'
                }
                
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Nix build timeout for {environment.id}")
            return {
                'success': False,
                'error': 'Build timeout (5 minutes)',
                'build_method': 'nix-shell'
            }
        except Exception as e:
            logger.error(f"❌ Nix build error: {e}")
            return {
                'success': False,
                'error': str(e),
                'build_method': 'nix-shell'
            }
    
    async def _build_containerized_environment(self, environment: NixEnvironment, env_path: str) -> dict:
        """Build environment using Docker containers"""
        
        try:
            if not self.docker_client:
                return {
                    'success': False,
                    'error': 'Docker client not available'
                }
            
            logger.info(f"🐳 Building containerized environment: {environment.id}")
            
            # Build Docker image
            image, build_logs = self.docker_client.images.build(
                path=env_path,
                tag=f"nixos-env-{environment.id}",
                rm=True
            )
            
            logger.info(f"✅ Docker image built: {image.id}")
            
            # Create and start container
            container = self.docker_client.containers.run(
                image.id,
                name=environment.id,
                detach=True,
                ports={
                    '3000/tcp': None,
                    '8000/tcp': None,
                    '8080/tcp': None,
                    '8888/tcp': None,
                    '9000/tcp': None
                },
                volumes={
                    os.path.join(env_path, 'workspace'): {'bind': '/workspace', 'mode': 'rw'}
                },
                environment={
                    'ENVIRONMENT_ID': environment.id,
                    'ENVIRONMENT_NAME': environment.name
                }
            )
            
            logger.info(f"✅ Container started: {container.id}")
            
            return {
                'success': True,
                'build_method': 'docker',
                'image_id': image.id,
                'container_id': container.id,
                'container_name': environment.id,
                'ports': container.ports
            }
            
        except Exception as e:
            logger.error(f"❌ Docker build failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'build_method': 'docker'
            }
    
    async def start_environment(self, environment_id: str) -> dict:
        """Start a stopped environment"""
        
        try:
            if environment_id not in self.environments:
                return {
                    'success': False,
                    'error': 'Environment not found'
                }
            
            environment = self.environments[environment_id]
            
            if environment.status == 'active':
                return {
                    'success': True,
                    'message': 'Environment is already active'
                }
            
            logger.info(f"🚀 Starting environment: {environment_id}")
            
            if self.docker_client:
                # Start Docker container
                try:
                    container = self.docker_client.containers.get(environment_id)
                    container.start()
                    environment.status = 'active'
                    environment.last_updated = datetime.now().isoformat()
                    
                    return {
                        'success': True,
                        'environment_id': environment_id,
                        'message': f'Environment {environment.name} started successfully'
                    }
                except docker.errors.NotFound:
                    return {
                        'success': False,
                        'error': 'Container not found'
                    }
            else:
                # For native Nix environments, they're always "active" once built
                environment.status = 'active'
                environment.last_updated = datetime.now().isoformat()
                
                return {
                    'success': True,
                    'environment_id': environment_id,
                    'message': f'Environment {environment.name} is ready'
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to start environment {environment_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def stop_environment(self, environment_id: str) -> dict:
        """Stop a running environment"""
        
        try:
            if environment_id not in self.environments:
                return {
                    'success': False,
                    'error': 'Environment not found'
                }
            
            environment = self.environments[environment_id]
            
            logger.info(f"⏹️ Stopping environment: {environment_id}")
            
            if self.docker_client:
                # Stop Docker container
                try:
                    container = self.docker_client.containers.get(environment_id)
                    container.stop()
                    environment.status = 'stopped'
                    environment.last_updated = datetime.now().isoformat()
                    
                    return {
                        'success': True,
                        'environment_id': environment_id,
                        'message': f'Environment {environment.name} stopped successfully'
                    }
                except docker.errors.NotFound:
                    return {
                        'success': False,
                        'error': 'Container not found'
                    }
            else:
                # For native Nix environments, mark as stopped
                environment.status = 'stopped'
                environment.last_updated = datetime.now().isoformat()
                
                return {
                    'success': True,
                    'environment_id': environment_id,
                    'message': f'Environment {environment.name} stopped'
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to stop environment {environment_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def delete_environment(self, environment_id: str, force: bool = False) -> dict:
        """Delete an environment and clean up resources"""
        
        try:
            if environment_id not in self.environments:
                return {
                    'success': False,
                    'error': 'Environment not found'
                }
            
            environment = self.environments[environment_id]
            
            logger.info(f"🗑️ Deleting environment: {environment_id}")
            
            # Stop environment first
            if environment.status == 'active':
                await self.stop_environment(environment_id)
            
            # Remove Docker container and image
            if self.docker_client:
                try:
                    # Remove container
                    container = self.docker_client.containers.get(environment_id)
                    container.remove(force=force)
                    
                    # Remove image
                    image_tag = f"nixos-env-{environment_id}"
                    try:
                        self.docker_client.images.remove(image_tag, force=force)
                    except docker.errors.ImageNotFound:
                        pass
                        
                except docker.errors.NotFound:
                    pass
            
            # Remove environment directory
            env_path = os.path.join(self.environments_base_path, environment_id)
            if os.path.exists(env_path):
                shutil.rmtree(env_path)
            
            # Remove from registry
            del self.environments[environment_id]
            
            logger.info(f"✅ Environment deleted: {environment_id}")
            
            return {
                'success': True,
                'environment_id': environment_id,
                'message': f'Environment {environment.name} deleted successfully'
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to delete environment {environment_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_environments(self) -> List[dict]:
        """List all environments"""
        
        return [
            {
                'id': env_id,
                'name': env.name,
                'description': env.description,
                'status': env.status,
                'created_at': env.created_at,
                'last_updated': env.last_updated,
                'packages_count': len(env.packages),
                'resource_limits': env.resource_limits
            }
            for env_id, env in self.environments.items()
        ]
    
    def get_environment_details(self, environment_id: str) -> dict:
        """Get detailed information about an environment"""
        
        if environment_id not in self.environments:
            return {
                'success': False,
                'error': 'Environment not found'
            }
        
        environment = self.environments[environment_id]
        
        return {
            'success': True,
            'environment': asdict(environment),
            'access_info': {
                'shell_command': f'nix-shell {self.environments_base_path}/{environment_id}/shell.nix',
                'container_name': environment_id if self.docker_client else None,
                'environment_path': os.path.join(self.environments_base_path, environment_id)
            }
        }
    
    def get_available_templates(self) -> dict:
        """Get available environment templates"""
        
        return {
            'templates': self.templates,
            'total_templates': len(self.templates)
        }
    
    async def install_package_in_environment(self, environment_id: str, packages: List[str]) -> dict:
        """Install additional packages in an existing environment"""
        
        try:
            if environment_id not in self.environments:
                return {
                    'success': False,
                    'error': 'Environment not found'
                }
            
            environment = self.environments[environment_id]
            
            logger.info(f"📦 Installing packages in {environment_id}: {packages}")
            
            # Add packages to environment configuration
            for package in packages:
                if package not in environment.packages:
                    environment.packages.append(package)
            
            # Regenerate configuration
            env_path = os.path.join(self.environments_base_path, environment_id)
            await self._generate_nix_config(environment, env_path)
            
            # Rebuild environment
            if self.nix_available:
                rebuild_result = await self._build_nix_environment(environment, env_path)
            else:
                rebuild_result = await self._rebuild_containerized_environment(environment, env_path)
            
            if rebuild_result['success']:
                environment.last_updated = datetime.now().isoformat()
                
                return {
                    'success': True,
                    'environment_id': environment_id,
                    'installed_packages': packages,
                    'total_packages': len(environment.packages),
                    'message': f'Successfully installed {len(packages)} packages'
                }
            else:
                return {
                    'success': False,
                    'error': rebuild_result.get('error'),
                    'message': 'Failed to rebuild environment after package installation'
                }
                
        except Exception as e:
            logger.error(f"❌ Package installation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _rebuild_containerized_environment(self, environment: NixEnvironment, env_path: str) -> dict:
        """Rebuild containerized environment after changes"""
        
        try:
            if not self.docker_client:
                return {
                    'success': False,
                    'error': 'Docker client not available'
                }
            
            # Stop and remove old container
            try:
                container = self.docker_client.containers.get(environment.id)
                container.stop()
                container.remove()
            except docker.errors.NotFound:
                pass
            
            # Remove old image
            try:
                old_image = self.docker_client.images.get(f"nixos-env-{environment.id}")
                self.docker_client.images.remove(old_image.id, force=True)
            except docker.errors.ImageNotFound:
                pass
            
            # Rebuild
            return await self._build_containerized_environment(environment, env_path)
            
        except Exception as e:
            logger.error(f"❌ Environment rebuild failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def execute_command_in_environment(self, environment_id: str, command: str, working_directory: str = '/workspace') -> dict:
        """Execute a command in the specified environment"""
        
        try:
            if environment_id not in self.environments:
                return {
                    'success': False,
                    'error': 'Environment not found'
                }
            
            environment = self.environments[environment_id]
            
            if environment.status != 'active':
                return {
                    'success': False,
                    'error': 'Environment is not active'
                }
            
            logger.info(f"🔧 Executing command in {environment_id}: {command}")
            
            if self.docker_client:
                # Execute in Docker container
                try:
                    container = self.docker_client.containers.get(environment_id)
                    result = container.exec_run(
                        cmd=command,
                        workdir=working_directory,
                        environment=environment.environment_variables
                    )
                    
                    return {
                        'success': True,
                        'environment_id': environment_id,
                        'command': command,
                        'exit_code': result.exit_code,
                        'output': result.output.decode('utf-8'),
                        'timestamp': datetime.now().isoformat()
                    }
                except docker.errors.NotFound:
                    return {
                        'success': False,
                        'error': 'Container not found'
                    }
            else:
                # Execute in nix-shell
                env_path = os.path.join(self.environments_base_path, environment_id)
                full_command = f'nix-shell {env_path}/shell.nix --run "{command}"'
                
                result = subprocess.run(
                    full_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=working_directory,
                    timeout=60
                )
                
                return {
                    'success': True,
                    'environment_id': environment_id,
                    'command': command,
                    'exit_code': result.returncode,
                    'output': result.stdout,
                    'error_output': result.stderr,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ Command execution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cleanup_inactive_environments(self, max_age_hours: int = 24) -> dict:
        """Clean up inactive environments older than specified age"""
        
        try:
            logger.info(f"🧹 Cleaning up environments older than {max_age_hours} hours")
            
            current_time = datetime.now()
            cleaned_environments = []
            
            for env_id, environment in list(self.environments.items()):
                if environment.auto_cleanup:
                    last_updated = datetime.fromisoformat(environment.last_updated)
                    age_hours = (current_time - last_updated).total_seconds() / 3600
                    
                    if age_hours > max_age_hours and environment.status != 'active':
                        asyncio.create_task(self.delete_environment(env_id, force=True))
                        cleaned_environments.append({
                            'id': env_id,
                            'name': environment.name,
                            'age_hours': age_hours
                        })
            
            return {
                'success': True,
                'cleaned_environments': cleaned_environments,
                'total_cleaned': len(cleaned_environments),
                'message': f'Cleaned up {len(cleaned_environments)} inactive environments'
            }
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }