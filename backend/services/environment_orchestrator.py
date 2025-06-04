"""
Dynamic Environment Orchestration System
Provides Mama Bear with full agentic control over development environments
"""

import os
import logging
import json
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import docker
import yaml
import tempfile
from pathlib import Path

from .nixos_environment_manager import NixOSEnvironmentManager
from .code_server_manager import CodeServerManager
from .vertex_ai_agent_manager import VertexAIAgentManager

logger = logging.getLogger(__name__)

class EnvironmentType(Enum):
    NIXOS = "nixos"
    DOCKER = "docker"
    CLOUD = "cloud"
    HYBRID = "hybrid"

class EnvironmentStatus(Enum):
    PENDING = "pending"
    PROVISIONING = "provisioning"
    READY = "ready"
    SCALING = "scaling"
    UPDATING = "updating"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"

@dataclass
class EnvironmentTemplate:
    """Template for creating standardized environments"""
    id: str
    name: str
    description: str
    type: EnvironmentType
    base_config: Dict[str, Any]
    required_resources: Dict[str, Any]
    auto_scaling: Dict[str, Any]
    extensions: List[str]
    dependencies: List[str]
    startup_scripts: List[str]
    health_checks: List[str]
    created_by: str
    tags: List[str]

@dataclass
class ManagedEnvironment:
    """Represents a managed development environment"""
    id: str
    template_id: str
    name: str
    type: EnvironmentType
    status: EnvironmentStatus
    config: Dict[str, Any]
    resources: Dict[str, Any]
    endpoints: Dict[str, str]
    metadata: Dict[str, Any]
    created_at: str
    last_accessed: str
    owner: str
    collaborators: List[str]
    auto_scaling_enabled: bool
    health_status: Dict[str, Any]
    cost_tracking: Dict[str, Any]

class EnvironmentOrchestrator:
    """
    Master orchestration system for development environments
    Provides Mama Bear with intelligent environment management
    """
    
    def __init__(self):
        self.environments: Dict[str, ManagedEnvironment] = {}
        self.templates: Dict[str, EnvironmentTemplate] = {}
        self.resource_limits = {
            'max_environments_per_user': 5,
            'max_total_environments': 50,
            'default_memory_limit': '4Gi',
            'default_cpu_limit': '2000m',
            'max_environment_lifetime': 24  # hours
        }
        
        # Initialize component managers
        self.nixos_manager = NixOSEnvironmentManager()
        self.code_server_manager = CodeServerManager()
        self.ai_manager = VertexAIAgentManager()
        
        # Docker client
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            logger.warning(f"Docker not available: {e}")
            self.docker_client = None
        
        # Load predefined templates
        self._load_environment_templates()
        
        logger.info("🎭 Environment Orchestrator initialized")

    def _load_environment_templates(self):
        """Load predefined environment templates"""
        
        templates = {
            'web_development': EnvironmentTemplate(
                id='web_dev_template',
                name='Web Development',
                description='Full-stack web development with Node.js, Python, and modern frameworks',
                type=EnvironmentType.DOCKER,
                base_config={
                    'base_image': 'node:18-bullseye',
                    'additional_packages': ['python3', 'python3-pip', 'git', 'curl']
                },
                required_resources={
                    'memory': '2Gi',
                    'cpu': '1000m',
                    'storage': '10Gi'
                },
                auto_scaling={
                    'enabled': True,
                    'min_instances': 1,
                    'max_instances': 3,
                    'scale_triggers': ['cpu_usage > 80%', 'memory_usage > 85%']
                },
                extensions=[
                    'ms-vscode.vscode-typescript-next',
                    'esbenp.prettier-vscode',
                    'ms-python.python',
                    'ms-vscode.vscode-json'
                ],
                dependencies=['nodejs', 'npm', 'bun', 'python3', 'pip'],
                startup_scripts=[
                    'npm install -g @types/node typescript',
                    'pip3 install --upgrade pip'
                ],
                health_checks=[
                    'curl -f http://localhost:3000/health || exit 1'
                ],
                created_by='system',
                tags=['web', 'fullstack', 'javascript', 'python']
            ),
            
            'ai_development': EnvironmentTemplate(
                id='ai_dev_template',
                name='AI/ML Development',
                description='AI development with Python, Jupyter, TensorFlow, and GPU support',
                type=EnvironmentType.HYBRID,
                base_config={
                    'base_image': 'tensorflow/tensorflow:latest-gpu-jupyter',
                    'gpu_enabled': True,
                    'jupyter_enabled': True
                },
                required_resources={
                    'memory': '8Gi',
                    'cpu': '4000m',
                    'storage': '50Gi',
                    'gpu': '1'
                },
                auto_scaling={
                    'enabled': True,
                    'min_instances': 1,
                    'max_instances': 2,
                    'scale_triggers': ['gpu_usage > 90%', 'memory_usage > 90%']
                },
                extensions=[
                    'ms-python.python',
                    'ms-python.jupyter',
                    'ms-python.pylance',
                    'github.copilot'
                ],
                dependencies=['python3', 'jupyter', 'tensorflow', 'pytorch', 'numpy', 'pandas'],
                startup_scripts=[
                    'pip install --upgrade tensorflow torch transformers',
                    'jupyter notebook --generate-config'
                ],
                health_checks=[
                    'python -c "import tensorflow as tf; print(tf.__version__)"'
                ],
                created_by='system',
                tags=['ai', 'ml', 'python', 'jupyter', 'gpu']
            ),
            
            'devops_playground': EnvironmentTemplate(
                id='devops_template',
                name='DevOps Playground',
                description='DevOps tools with Docker, Kubernetes, Terraform, and cloud CLIs',
                type=EnvironmentType.NIXOS,
                base_config={
                    'nix_packages': [
                        'docker', 'kubectl', 'terraform', 'ansible', 
                        'aws-cli', 'google-cloud-sdk', 'azure-cli'
                    ]
                },
                required_resources={
                    'memory': '4Gi',
                    'cpu': '2000m',
                    'storage': '20Gi'
                },
                auto_scaling={
                    'enabled': False,
                    'min_instances': 1,
                    'max_instances': 1
                },
                extensions=[
                    'ms-azuretools.vscode-docker',
                    'hashicorp.terraform',
                    'redhat.ansible',
                    'ms-kubernetes-tools.vscode-kubernetes-tools'
                ],
                dependencies=['docker', 'kubectl', 'terraform', 'ansible'],
                startup_scripts=[
                    'docker --version',
                    'kubectl version --client',
                    'terraform version'
                ],
                health_checks=[
                    'docker ps',
                    'kubectl cluster-info'
                ],
                created_by='system',
                tags=['devops', 'docker', 'kubernetes', 'terraform', 'cloud']
            ),
            
            'rapid_prototype': EnvironmentTemplate(
                id='prototype_template',
                name='Rapid Prototyping',
                description='Quick prototyping with multiple languages and frameworks',
                type=EnvironmentType.DOCKER,
                base_config={
                    'base_image': 'ubuntu:22.04',
                    'multi_language': True
                },
                required_resources={
                    'memory': '3Gi',
                    'cpu': '1500m',
                    'storage': '15Gi'
                },
                auto_scaling={
                    'enabled': True,
                    'min_instances': 1,
                    'max_instances': 2,
                    'scale_triggers': ['cpu_usage > 75%']
                },
                extensions=[
                    'ms-vscode.vscode-typescript-next',
                    'ms-python.python',
                    'golang.go',
                    'rust-lang.rust-analyzer'
                ],
                dependencies=['nodejs', 'python3', 'go', 'rust', 'git'],
                startup_scripts=[
                    'apt-get update && apt-get install -y curl git',
                    'curl -fsSL https://deb.nodesource.com/setup_18.x | bash -',
                    'apt-get install -y nodejs python3 golang rustc'
                ],
                health_checks=[
                    'node --version',
                    'python3 --version',
                    'go version'
                ],
                created_by='system',
                tags=['prototype', 'multi-language', 'javascript', 'python', 'go', 'rust']
            )
        }
        
        self.templates.update(templates)
        logger.info(f"✅ Loaded {len(templates)} environment templates")

    async def create_environment(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new managed environment
        Mama Bear can use this to spin up any development environment
        """
        try:
            # Validate request
            if 'template_id' not in request:
                return self._error_response("template_id is required")
            
            template_id = request['template_id']
            if template_id not in self.templates:
                return self._error_response(f"Template '{template_id}' not found")
            
            template = self.templates[template_id]
            
            # Generate environment ID
            env_id = f"env_{uuid.uuid4().hex[:8]}"
            env_name = request.get('name', f"{template.name}_{env_id}")
            owner = request.get('owner', 'mama_bear')
            
            # Check resource limits
            user_envs = [e for e in self.environments.values() if e.owner == owner]
            if len(user_envs) >= self.resource_limits['max_environments_per_user']:
                return self._error_response(f"Maximum environments per user ({self.resource_limits['max_environments_per_user']}) reached")
            
            logger.info(f"🚀 Creating environment: {env_name} ({template.type.value})")
            
            # Create managed environment
            managed_env = ManagedEnvironment(
                id=env_id,
                template_id=template_id,
                name=env_name,
                type=template.type,
                status=EnvironmentStatus.PENDING,
                config=self._merge_configs(template.base_config, request.get('config', {})),
                resources=template.required_resources.copy(),
                endpoints={},
                metadata={
                    'template_name': template.name,
                    'creation_request': request,
                    'provisioning_start': datetime.now().isoformat()
                },
                created_at=datetime.now().isoformat(),
                last_accessed=datetime.now().isoformat(),
                owner=owner,
                collaborators=request.get('collaborators', []),
                auto_scaling_enabled=template.auto_scaling.get('enabled', False),
                health_status={'status': 'unknown', 'last_check': None},
                cost_tracking={'estimated_hourly': 0, 'total_cost': 0}
            )
            
            # Register environment
            self.environments[env_id] = managed_env
            
            # Start provisioning asynchronously
            asyncio.create_task(self._provision_environment(env_id))
            
            return {
                'success': True,
                'environment_id': env_id,
                'environment': asdict(managed_env),
                'message': f"Environment '{env_name}' is being created",
                'estimated_ready_time': '2-5 minutes'
            }
            
        except Exception as e:
            logger.error(f"❌ Environment creation failed: {e}")
            return self._error_response(f"Environment creation failed: {str(e)}")

    async def _provision_environment(self, env_id: str):
        """Provision the actual environment based on type"""
        try:
            env = self.environments[env_id]
            template = self.templates[env.template_id]
            
            env.status = EnvironmentStatus.PROVISIONING
            logger.info(f"🔧 Provisioning environment: {env.name} ({env.type.value})")
            
            # Provision based on environment type
            if env.type == EnvironmentType.NIXOS:
                result = await self._provision_nixos_environment(env, template)
            elif env.type == EnvironmentType.DOCKER:
                result = await self._provision_docker_environment(env, template)
            elif env.type == EnvironmentType.CLOUD:
                result = await self._provision_cloud_environment(env, template)
            elif env.type == EnvironmentType.HYBRID:
                result = await self._provision_hybrid_environment(env, template)
            else:
                raise ValueError(f"Unsupported environment type: {env.type}")
            
            if result['success']:
                env.status = EnvironmentStatus.READY
                env.endpoints.update(result.get('endpoints', {}))
                env.metadata.update({
                    'provisioning_complete': datetime.now().isoformat(),
                    'provisioning_result': result
                })
                
                # Start health monitoring
                asyncio.create_task(self._monitor_environment_health(env_id))
                
                logger.info(f"✅ Environment ready: {env.name}")
                
                # Notify Mama Bear
                await self._notify_mama_bear(env_id, 'environment_ready', {
                    'environment_id': env_id,
                    'name': env.name,
                    'endpoints': env.endpoints,
                    'message': f"Environment '{env.name}' is ready for use!"
                })
                
            else:
                env.status = EnvironmentStatus.ERROR
                env.metadata['provisioning_error'] = result.get('error', 'Unknown error')
                logger.error(f"❌ Environment provisioning failed: {env.name}")
                
        except Exception as e:
            logger.error(f"❌ Environment provisioning failed: {e}")
            if env_id in self.environments:
                self.environments[env_id].status = EnvironmentStatus.ERROR
                self.environments[env_id].metadata['provisioning_error'] = str(e)

    async def _provision_nixos_environment(self, env: ManagedEnvironment, template: EnvironmentTemplate) -> Dict[str, Any]:
        """Provision NixOS-based environment"""
        try:
            nixos_config = {
                'name': env.name,
                'packages': template.base_config.get('nix_packages', []),
                'resources': env.resources,
                'extensions': template.extensions
            }
            
            result = await self.nixos_manager.create_environment(nixos_config)
            
            if result['success']:
                # Create code-server instance
                code_server_config = {
                    'name': f"code-{env.name}",
                    'workspace_path': result.get('workspace_path'),
                    'environment_id': env.id,
                    'extensions': template.extensions
                }
                
                cs_result = await self.code_server_manager.create_code_server_instance(code_server_config)
                
                if cs_result['success']:
                    return {
                        'success': True,
                        'endpoints': {
                            'code_server': cs_result.get('access_url'),
                            'workspace': result.get('workspace_path')
                        },
                        'nixos_result': result,
                        'code_server_result': cs_result
                    }
                else:
                    return cs_result
            else:
                return result
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _provision_docker_environment(self, env: ManagedEnvironment, template: EnvironmentTemplate) -> Dict[str, Any]:
        """Provision Docker-based environment"""
        try:
            # Create code-server instance with custom Docker configuration
            code_server_config = {
                'name': env.name,
                'docker_image': template.base_config.get('base_image', 'codercom/code-server:latest'),
                'resources': env.resources,
                'extensions': template.extensions,
                'startup_scripts': template.startup_scripts,
                'custom_dockerfile': self._generate_custom_dockerfile(template)
            }
            
            result = await self.code_server_manager.create_code_server_instance(code_server_config)
            
            if result['success']:
                # Run startup scripts
                await self._run_startup_scripts(result['instance_id'], template.startup_scripts)
                
                return {
                    'success': True,
                    'endpoints': {
                        'code_server': result.get('access_url'),
                        'container_id': result.get('instance', {}).get('container_id')
                    },
                    'code_server_result': result
                }
            else:
                return result
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _provision_cloud_environment(self, env: ManagedEnvironment, template: EnvironmentTemplate) -> Dict[str, Any]:
        """Provision cloud-based environment"""
        try:
            # First create local instance
            docker_result = await self._provision_docker_environment(env, template)
            
            if not docker_result['success']:
                return docker_result
            
            # Deploy to cloud
            instance_id = docker_result['code_server_result']['instance_id']
            
            cloud_config = {
                'region': 'us-central1',
                'memory': env.resources.get('memory', '2Gi'),
                'cpu': env.resources.get('cpu', '1000m'),
                'max_instances': template.auto_scaling.get('max_instances', 1)
            }
            
            cloud_result = await self.code_server_manager.deploy_to_google_cloud(instance_id, cloud_config)
            
            if cloud_result['success']:
                return {
                    'success': True,
                    'endpoints': {
                        'cloud_url': cloud_result.get('service_url'),
                        'local_url': docker_result['endpoints']['code_server']
                    },
                    'docker_result': docker_result,
                    'cloud_result': cloud_result
                }
            else:
                return cloud_result
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _provision_hybrid_environment(self, env: ManagedEnvironment, template: EnvironmentTemplate) -> Dict[str, Any]:
        """Provision hybrid environment (NixOS + Cloud)"""
        try:
            # Create NixOS environment for local development
            nixos_result = await self._provision_nixos_environment(env, template)
            
            if not nixos_result['success']:
                return nixos_result
            
            # Deploy to cloud for production/testing
            cloud_result = await self._provision_cloud_environment(env, template)
            
            return {
                'success': True,
                'endpoints': {
                    'local_nixos': nixos_result['endpoints']['code_server'],
                    'cloud_production': cloud_result['endpoints']['cloud_url'] if cloud_result['success'] else None,
                    'workspace': nixos_result['endpoints']['workspace']
                },
                'nixos_result': nixos_result,
                'cloud_result': cloud_result
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _generate_custom_dockerfile(self, template: EnvironmentTemplate) -> str:
        """Generate custom Dockerfile based on template"""
        base_image = template.base_config.get('base_image', 'ubuntu:22.04')
        packages = template.dependencies
        
        dockerfile = f"""FROM {base_image}

USER root

# Install base packages
RUN apt-get update && apt-get install -y \\
    curl \\
    wget \\
    git \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

"""
        
        # Add language-specific installations
        if 'nodejs' in packages:
            dockerfile += """
# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \\
    && apt-get install -y nodejs

"""
        
        if 'python3' in packages:
            dockerfile += """
# Install Python
RUN apt-get update && apt-get install -y \\
    python3 \\
    python3-pip \\
    && rm -rf /var/lib/apt/lists/*

"""
        
        if 'go' in packages:
            dockerfile += """
# Install Go
RUN wget https://go.dev/dl/go1.21.0.linux-amd64.tar.gz \\
    && tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz \\
    && rm go1.21.0.linux-amd64.tar.gz
ENV PATH=$PATH:/usr/local/go/bin

"""
        
        dockerfile += """
# Create workspace
RUN mkdir -p /workspace
RUN chown -R 1000:1000 /workspace

# Switch to non-root user
USER 1000
WORKDIR /workspace

"""
        
        return dockerfile

    async def _run_startup_scripts(self, instance_id: str, scripts: List[str]):
        """Run startup scripts in the environment"""
        try:
            if not scripts:
                return
            
            logger.info(f"🔄 Running startup scripts for {instance_id}")
            
            for script in scripts:
                logger.info(f"Executing: {script}")
                # Implementation would execute scripts in the container
                # For now, just log them
                
        except Exception as e:
            logger.error(f"❌ Startup script execution failed: {e}")

    async def _monitor_environment_health(self, env_id: str):
        """Monitor environment health and perform auto-scaling if needed"""
        try:
            env = self.environments[env_id]
            
            while env.status == EnvironmentStatus.READY:
                # Check environment health
                health_status = await self._check_environment_health(env)
                env.health_status = health_status
                
                # Update last accessed time if environment is being used
                if health_status.get('active', False):
                    env.last_accessed = datetime.now().isoformat()
                
                # Check if auto-scaling is needed
                if env.auto_scaling_enabled:
                    await self._evaluate_auto_scaling(env)
                
                # Sleep before next check
                await asyncio.sleep(60)  # Check every minute
                
        except Exception as e:
            logger.error(f"❌ Health monitoring failed for {env_id}: {e}")

    async def _check_environment_health(self, env: ManagedEnvironment) -> Dict[str, Any]:
        """Check the health of an environment"""
        try:
            health_data = {
                'status': 'healthy',
                'last_check': datetime.now().isoformat(),
                'active': False,
                'metrics': {}
            }
            
            # Check endpoints
            for endpoint_name, endpoint_url in env.endpoints.items():
                if endpoint_url:
                    # Would implement actual health checks here
                    health_data['metrics'][endpoint_name] = {'status': 'available'}
            
            return health_data
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'last_check': datetime.now().isoformat(),
                'error': str(e)
            }

    async def _evaluate_auto_scaling(self, env: ManagedEnvironment):
        """Evaluate if auto-scaling actions are needed"""
        try:
            template = self.templates[env.template_id]
            scaling_config = template.auto_scaling
            
            if not scaling_config.get('enabled', False):
                return
            
            # Get current metrics
            metrics = env.health_status.get('metrics', {})
            
            # Evaluate scaling triggers
            should_scale_up = False
            should_scale_down = False
            
            for trigger in scaling_config.get('scale_triggers', []):
                # Parse trigger condition (simplified)
                if 'cpu_usage > 80%' in trigger and metrics.get('cpu_usage', 0) > 80:
                    should_scale_up = True
                elif 'memory_usage > 85%' in trigger and metrics.get('memory_usage', 0) > 85:
                    should_scale_up = True
            
            if should_scale_up:
                await self._scale_environment(env.id, 'up')
            elif should_scale_down:
                await self._scale_environment(env.id, 'down')
                
        except Exception as e:
            logger.error(f"❌ Auto-scaling evaluation failed: {e}")

    async def _scale_environment(self, env_id: str, direction: str):
        """Scale environment up or down"""
        try:
            env = self.environments[env_id]
            env.status = EnvironmentStatus.SCALING
            
            logger.info(f"📈 Scaling environment {direction}: {env.name}")
            
            # Implementation would depend on environment type
            # For now, just update status
            
            await asyncio.sleep(2)  # Simulate scaling time
            env.status = EnvironmentStatus.READY
            
            logger.info(f"✅ Environment scaled {direction}: {env.name}")
            
        except Exception as e:
            logger.error(f"❌ Environment scaling failed: {e}")
            if env_id in self.environments:
                self.environments[env_id].status = EnvironmentStatus.ERROR

    async def _notify_mama_bear(self, env_id: str, event_type: str, data: Dict[str, Any]):
        """Notify Mama Bear about environment events"""
        try:
            notification = {
                'event_type': event_type,
                'environment_id': env_id,
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            
            # Send notification to Mama Bear agent
            await self.ai_manager.send_notification('mama_bear', notification)
            
        except Exception as e:
            logger.error(f"❌ Failed to notify Mama Bear: {e}")

    def _merge_configs(self, base_config: Dict[str, Any], user_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge base template config with user-provided config"""
        merged = base_config.copy()
        
        for key, value in user_config.items():
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                merged[key] = {**merged[key], **value}
            else:
                merged[key] = value
        
        return merged

    def _error_response(self, message: str) -> Dict[str, Any]:
        """Generate standardized error response"""
        return {
            'success': False,
            'error': message,
            'timestamp': datetime.now().isoformat()
        }

    # Public API methods for Mama Bear

    async def get_environment_status(self, env_id: str) -> Dict[str, Any]:
        """Get detailed status of an environment"""
        if env_id not in self.environments:
            return self._error_response("Environment not found")
        
        env = self.environments[env_id]
        
        return {
            'success': True,
            'environment': asdict(env),
            'template': asdict(self.templates[env.template_id]) if env.template_id in self.templates else None,
            'uptime': self._calculate_uptime(env),
            'cost_estimate': self._calculate_cost_estimate(env)
        }

    async def list_environments(self, owner: str = None) -> Dict[str, Any]:
        """List all environments, optionally filtered by owner"""
        environments = list(self.environments.values())
        
        if owner:
            environments = [e for e in environments if e.owner == owner]
        
        return {
            'success': True,
            'environments': [asdict(env) for env in environments],
            'total_count': len(environments),
            'resource_usage': self._calculate_total_resource_usage()
        }

    async def stop_environment(self, env_id: str) -> Dict[str, Any]:
        """Stop an environment"""
        try:
            if env_id not in self.environments:
                return self._error_response("Environment not found")
            
            env = self.environments[env_id]
            env.status = EnvironmentStatus.STOPPING
            
            logger.info(f"⏹️ Stopping environment: {env.name}")
            
            # Stop based on environment type
            if env.type in [EnvironmentType.DOCKER, EnvironmentType.CLOUD, EnvironmentType.HYBRID]:
                # Find associated code-server instance
                code_server_instances = self.code_server_manager.list_instances()
                for instance in code_server_instances:
                    if instance.get('environment_id') == env_id:
                        await self.code_server_manager.stop_instance(instance['id'])
            
            if env.type in [EnvironmentType.NIXOS, EnvironmentType.HYBRID]:
                # Stop NixOS environment
                await self.nixos_manager.stop_environment(env_id)
            
            env.status = EnvironmentStatus.STOPPED
            
            return {
                'success': True,
                'environment_id': env_id,
                'message': f"Environment '{env.name}' stopped"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to stop environment: {e}")
            return self._error_response(f"Failed to stop environment: {str(e)}")

    async def delete_environment(self, env_id: str, force: bool = False) -> Dict[str, Any]:
        """Delete an environment permanently"""
        try:
            if env_id not in self.environments:
                return self._error_response("Environment not found")
            
            env = self.environments[env_id]
            
            logger.info(f"🗑️ Deleting environment: {env.name}")
            
            # Stop first if running
            if env.status == EnvironmentStatus.READY:
                await self.stop_environment(env_id)
            
            # Clean up resources based on type
            if env.type in [EnvironmentType.DOCKER, EnvironmentType.CLOUD, EnvironmentType.HYBRID]:
                # Delete code-server instances
                code_server_instances = self.code_server_manager.list_instances()
                for instance in code_server_instances:
                    if instance.get('environment_id') == env_id:
                        await self.code_server_manager.delete_instance(instance['id'], force=force)
            
            if env.type in [EnvironmentType.NIXOS, EnvironmentType.HYBRID]:
                # Delete NixOS environment
                await self.nixos_manager.delete_environment(env_id, force=force)
            
            # Remove from registry
            del self.environments[env_id]
            
            return {
                'success': True,
                'environment_id': env_id,
                'message': f"Environment '{env.name}' deleted"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to delete environment: {e}")
            return self._error_response(f"Failed to delete environment: {str(e)}")

    def get_available_templates(self) -> Dict[str, Any]:
        """Get all available environment templates"""
        return {
            'success': True,
            'templates': [asdict(template) for template in self.templates.values()],
            'categories': self._categorize_templates(),
            'total_count': len(self.templates)
        }

    def _categorize_templates(self) -> Dict[str, List[str]]:
        """Categorize templates by their tags"""
        categories = {}
        
        for template in self.templates.values():
            for tag in template.tags:
                if tag not in categories:
                    categories[tag] = []
                categories[tag].append(template.id)
        
        return categories

    def _calculate_uptime(self, env: ManagedEnvironment) -> str:
        """Calculate environment uptime"""
        try:
            created = datetime.fromisoformat(env.created_at)
            uptime = datetime.now() - created
            
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            return f"{days}d {hours}h {minutes}m"
        except:
            return "unknown"

    def _calculate_cost_estimate(self, env: ManagedEnvironment) -> Dict[str, float]:
        """Calculate cost estimate for environment"""
        # Simplified cost calculation
        base_hourly = 0.05  # $0.05 per hour base
        
        memory_gb = float(env.resources.get('memory', '1Gi').replace('Gi', ''))
        cpu_cores = float(env.resources.get('cpu', '1000m').replace('m', '')) / 1000
        
        hourly_cost = base_hourly + (memory_gb * 0.01) + (cpu_cores * 0.02)
        
        # Calculate total based on uptime
        try:
            created = datetime.fromisoformat(env.created_at)
            hours_running = (datetime.now() - created).total_seconds() / 3600
            total_cost = hourly_cost * hours_running
        except:
            total_cost = 0
        
        return {
            'hourly_estimate': round(hourly_cost, 4),
            'total_cost': round(total_cost, 4),
            'currency': 'USD'
        }

    def _calculate_total_resource_usage(self) -> Dict[str, Any]:
        """Calculate total resource usage across all environments"""
        total_memory = 0
        total_cpu = 0
        running_count = 0
        
        for env in self.environments.values():
            if env.status == EnvironmentStatus.READY:
                running_count += 1
                memory_gb = float(env.resources.get('memory', '0Gi').replace('Gi', ''))
                cpu_cores = float(env.resources.get('cpu', '0m').replace('m', '')) / 1000
                
                total_memory += memory_gb
                total_cpu += cpu_cores
        
        return {
            'total_environments': len(self.environments),
            'running_environments': running_count,
            'total_memory_gb': total_memory,
            'total_cpu_cores': total_cpu,
            'resource_utilization': f"{running_count}/{self.resource_limits['max_total_environments']}"
        }

    async def cleanup_expired_environments(self) -> Dict[str, Any]:
        """Clean up environments that have exceeded their lifetime"""
        try:
            logger.info("🧹 Cleaning up expired environments")
            
            max_lifetime_hours = self.resource_limits['max_environment_lifetime']
            cutoff_time = datetime.now() - timedelta(hours=max_lifetime_hours)
            
            expired_environments = []
            
            for env_id, env in list(self.environments.items()):
                try:
                    last_accessed = datetime.fromisoformat(env.last_accessed)
                    if last_accessed < cutoff_time and env.status != EnvironmentStatus.READY:
                        expired_environments.append({
                            'id': env_id,
                            'name': env.name,
                            'last_accessed': env.last_accessed
                        })
                        
                        # Delete expired environment
                        await self.delete_environment(env_id, force=True)
                        
                except Exception as e:
                    logger.error(f"Error processing environment {env_id}: {e}")
            
            return {
                'success': True,
                'cleaned_environments': expired_environments,
                'total_cleaned': len(expired_environments),
                'message': f"Cleaned up {len(expired_environments)} expired environments"
            }
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            return self._error_response(f"Cleanup failed: {str(e)}")

# Global orchestrator instance
environment_orchestrator = EnvironmentOrchestrator()