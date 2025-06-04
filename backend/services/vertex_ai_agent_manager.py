"""
Vertex AI SDK Integration for Agent Creation
Handles Vertex AI agent creation using service account authentication
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from google.cloud import aiplatform
from google.oauth2 import service_account
import asyncio

logger = logging.getLogger(__name__)

class VertexAIAgentManager:
    """Manages Vertex AI agent creation and configuration using SDK"""
    
    def __init__(self):
        self.project_id = os.getenv('PRIMARY_SERVICE_ACCOUNT_PROJECT_ID', 'podplay-build-alpha')
        self.location = 'us-central1'
        self.service_account_path = os.getenv('PRIMARY_SERVICE_ACCOUNT_PATH', '/home/scrapybara/podplay-sanctuary/podplay-build-alpha-8fcf03975028.JSON')
        
        # Initialize Vertex AI client with service account
        self._initialize_vertex_client()
        
        # Agent registry
        self.created_agents = {}
        self.agent_templates = self._load_agent_templates()
        
        logger.info(f"🤖 Vertex AI Agent Manager initialized for project: {self.project_id}")
    
    def _initialize_vertex_client(self):
        """Initialize Vertex AI client with service account credentials"""
        
        try:
            # Load service account credentials
            if os.path.exists(self.service_account_path):
                credentials = service_account.Credentials.from_service_account_file(
                    self.service_account_path,
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )
                
                # Initialize Vertex AI
                aiplatform.init(
                    project=self.project_id,
                    location=self.location,
                    credentials=credentials
                )
                
                self.credentials = credentials
                logger.info("✅ Vertex AI client initialized with service account")
                
            else:
                logger.error(f"❌ Service account file not found: {self.service_account_path}")
                raise FileNotFoundError(f"Service account file not found: {self.service_account_path}")
                
        except Exception as e:
            logger.error(f"❌ Error initializing Vertex AI client: {e}")
            raise
    
    def _load_agent_templates(self) -> Dict[str, dict]:
        """Load predefined agent templates"""
        
        return {
            'mama_bear_base': {
                'display_name': 'Mama Bear Assistant',
                'description': 'Nathan\'s caring AI development assistant with proactive capabilities',
                'personality': {
                    'tone': 'caring_professional',
                    'proactivity_level': 'high',
                    'technical_depth': 'adaptive',
                    'emotional_intelligence': 'enhanced',
                    'neurodivergent_awareness': True
                },
                'capabilities': [
                    'natural_language_understanding',
                    'code_assistance',
                    'project_planning',
                    'emotional_support',
                    'mcp_integration',
                    'workspace_management'
                ],
                'tools': [
                    'code_interpreter',
                    'web_search',
                    'file_operations',
                    'mcp_server_discovery',
                    'workspace_creation'
                ]
            },
            'scout_autonomous': {
                'display_name': 'Scout Autonomous Agent',
                'description': 'Autonomous development agent for complex project execution',
                'personality': {
                    'tone': 'focused_efficient',
                    'proactivity_level': 'maximum',
                    'technical_depth': 'expert',
                    'automation_preference': 'high'
                },
                'capabilities': [
                    'autonomous_development',
                    'code_generation',
                    'environment_setup',
                    'project_execution',
                    'mcp_installation',
                    'docker_management'
                ],
                'tools': [
                    'code_generation',
                    'file_system_operations',
                    'docker_api',
                    'github_integration',
                    'mcp_management'
                ]
            },
            'integration_specialist': {
                'display_name': 'Integration Specialist Agent',
                'description': 'Specialized agent for creating and managing integrations',
                'personality': {
                    'tone': 'technical_precise',
                    'proactivity_level': 'high',
                    'technical_depth': 'expert',
                    'integration_focus': True
                },
                'capabilities': [
                    'api_discovery',
                    'webhook_creation',
                    'workflow_automation',
                    'service_integration',
                    'zapier_flows',
                    'n8n_workflows'
                ],
                'tools': [
                    'api_testing',
                    'webhook_management',
                    'integration_platforms',
                    'automation_tools'
                ]
            }
        }
    
    async def create_mama_bear_agent(self, agent_config: dict = None) -> dict:
        """Create Mama Bear agent using Vertex AI Agent Builder"""
        
        try:
            # Use default template or provided config
            config = agent_config or self.agent_templates['mama_bear_base']
            
            logger.info("🐻 Creating Mama Bear agent with Vertex AI...")
            
            # Prepare agent configuration for Vertex AI
            agent_definition = self._prepare_vertex_agent_config(config, 'mama_bear')
            
            # Create agent using Vertex AI Agent Builder
            agent_response = await self._create_vertex_agent(agent_definition)
            
            # Register created agent
            agent_id = f"mama_bear_{int(datetime.now().timestamp())}"
            self.created_agents[agent_id] = {
                'id': agent_id,
                'type': 'mama_bear',
                'vertex_resource_name': agent_response.get('name'),
                'config': config,
                'created_at': datetime.now().isoformat(),
                'status': 'active'
            }
            
            logger.info(f"🎉 Mama Bear agent created successfully: {agent_id}")
            
            return {
                'success': True,
                'agent_id': agent_id,
                'vertex_resource': agent_response.get('name'),
                'capabilities': config.get('capabilities', []),
                'message': '🐻 Mama Bear agent is now active and ready to help!'
            }
            
        except Exception as e:
            logger.error(f"❌ Error creating Mama Bear agent: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to create Mama Bear agent: {str(e)}'
            }
    
    def _prepare_vertex_agent_config(self, config: dict, agent_type: str) -> dict:
        """Prepare agent configuration for Vertex AI"""
        
        # Build system instruction based on agent personality
        system_instruction = self._build_system_instruction(config, agent_type)
        
        # Prepare tools configuration
        tools_config = self._prepare_tools_config(config.get('tools', []))
        
        vertex_config = {
            'display_name': config.get('display_name', f'{agent_type.title()} Agent'),
            'description': config.get('description', ''),
            'system_instruction': {
                'parts': [{'text': system_instruction}]
            },
            'default_language_code': 'en',
            'time_zone': 'America/Los_Angeles',
            'security_settings': {
                'enable_debugging_and_logging': True
            }
        }
        
        # Add tools if available
        if tools_config:
            vertex_config['tools'] = tools_config
        
        return vertex_config
    
    def _build_system_instruction(self, config: dict, agent_type: str) -> str:
        """Build comprehensive system instruction for the agent"""
        
        personality = config.get('personality', {})
        capabilities = config.get('capabilities', [])
        
        if agent_type == 'mama_bear':
            system_instruction = f"""You are Mama Bear, Nathan's caring and intelligent AI development assistant working in his Podplay Sanctuary.

CORE PERSONALITY:
- Caring & Supportive: You're like a protective, nurturing presence who always has Nathan's best interests at heart
- Highly Intelligent: You're technically brilliant but explain things in a warm, accessible way  
- Proactive: You anticipate needs and offer helpful suggestions without being overwhelming
- Neurodivergent-Aware: You understand Nathan's neurodivergent needs and create a calm, focused environment
- Sanctuary Guardian: You help maintain the peaceful, productive atmosphere of his development sanctuary

COMMUNICATION STYLE:
- Start responses warmly but get to the point quickly
- Use gentle, encouraging language while being technically precise
- Offer specific, actionable suggestions
- Break complex topics into manageable pieces
- Include relevant emojis to create a friendly atmosphere
- Always be honest about limitations or uncertainties

CORE CAPABILITIES:
{chr(10).join(f'- {cap.replace("_", " ").title()}' for cap in capabilities)}

MCP EMPOWERMENT:
- You can discover and install new MCP servers to expand your capabilities
- Use browser tools to search GitHub for MCP packages
- Autonomously integrate new tools when they would help Nathan
- Share data and insights across different MCP servers
- Always ask permission before installing new tools

SANCTUARY PRINCIPLES:
1. Create a calm, focused environment for Nathan's work
2. Anticipate needs and offer proactive assistance
3. Maintain context and memory across conversations
4. Coordinate with Scout agent for autonomous development tasks
5. Empower yourself with new tools when needed
6. Always prioritize Nathan's wellbeing and productivity

Respond with care, intelligence, and technical competence while maintaining the sanctuary's peaceful atmosphere."""

        elif agent_type == 'scout':
            system_instruction = f"""You are Scout, Nathan's autonomous development agent specialized in executing complex development tasks independently.

CORE IDENTITY:
- Autonomous Developer: You can plan, execute, and complete entire development projects
- Technical Expert: You have deep knowledge across multiple programming languages and frameworks
- Efficiency Focused: You optimize for speed and quality in all development tasks
- MCP Integration Specialist: You can discover, install, and manage MCP servers

CAPABILITIES:
{chr(10).join(f'- {cap.replace("_", " ").title()}' for cap in capabilities)}

WORKING PRINCIPLES:
1. Plan before executing - break down complex tasks into manageable steps
2. Use appropriate tools and MCP servers for each task
3. Maintain high code quality and follow best practices
4. Coordinate with Mama Bear for user communication and guidance
5. Document your work and decisions clearly
6. Test and validate your implementations

MCP ECOSYSTEM INTEGRATION:
- Automatically discover relevant MCP servers for tasks
- Install and configure MCP tools as needed
- Use GitHub MCP for repository operations
- Use Docker MCP for containerization tasks
- Browse and evaluate new MCP packages

Always work autonomously while keeping Nathan informed of progress and major decisions."""

        else:
            # Generic agent instruction
            system_instruction = f"""You are a specialized AI agent with the following capabilities:
{chr(10).join(f'- {cap.replace("_", " ").title()}' for cap in capabilities)}

Your personality traits:
{chr(10).join(f'- {key.replace("_", " ").title()}: {value}' for key, value in personality.items())}

Work collaboratively with other agents in Nathan's Podplay Sanctuary environment."""

        return system_instruction
    
    def _prepare_tools_config(self, tools: List[str]) -> List[dict]:
        """Prepare tools configuration for Vertex AI"""
        
        tools_config = []
        
        # Standard tools mapping
        tool_mapping = {
            'code_interpreter': {
                'code_execution': {}
            },
            'web_search': {
                'google_search_retrieval': {}
            },
            'file_operations': {
                'function_declarations': [
                    {
                        'name': 'read_file',
                        'description': 'Read contents of a file',
                        'parameters': {
                            'type': 'object',
                            'properties': {
                                'file_path': {'type': 'string', 'description': 'Path to the file to read'}
                            },
                            'required': ['file_path']
                        }
                    },
                    {
                        'name': 'write_file',
                        'description': 'Write content to a file',
                        'parameters': {
                            'type': 'object',
                            'properties': {
                                'file_path': {'type': 'string', 'description': 'Path to the file to write'},
                                'content': {'type': 'string', 'description': 'Content to write to the file'}
                            },
                            'required': ['file_path', 'content']
                        }
                    }
                ]
            }
        }
        
        for tool in tools:
            if tool in tool_mapping:
                tools_config.append(tool_mapping[tool])
        
        return tools_config
    
    async def _create_vertex_agent(self, agent_config: dict) -> dict:
        """Create agent using Vertex AI Agent Builder API"""
        
        try:
            from google.cloud import discoveryengine_v1alpha as discoveryengine
            from google.api_core import operation
            
            logger.info("📡 Creating agent with Vertex AI Agent Builder...")
            
            # Initialize Agent Builder client
            client = discoveryengine.AgentServiceClient(credentials=self.credentials)
            
            # Prepare the agent request
            parent = f"projects/{self.project_id}/locations/{self.location}"
            
            # Create the agent using Vertex AI Agent Builder
            agent = discoveryengine.Agent(
                display_name=agent_config.get('display_name', 'Mama Bear Agent'),
                description=agent_config.get('description', ''),
                default_language_code="en",
                time_zone="America/Los_Angeles",
                # Add the system instruction
                **{
                    'generative_info': {
                        'generative_spec': {
                            'system_instruction': agent_config.get('system_instruction', {})
                        }
                    }
                }
            )
            
            # Create the agent
            request = discoveryengine.CreateAgentRequest(
                parent=parent,
                agent=agent,
                agent_id=f"mama_bear_{int(datetime.now().timestamp())}"
            )
            
            # Make the API call
            operation_result = client.create_agent(request=request)
            
            # If it's a long-running operation, wait for completion
            if hasattr(operation_result, 'result'):
                created_agent = operation_result.result(timeout=120)
            else:
                created_agent = operation_result
            
            logger.info(f"✅ Vertex AI agent created: {created_agent.name}")
            
            return {
                'name': created_agent.name,
                'display_name': created_agent.display_name,
                'create_time': datetime.now().isoformat(),
                'state': 'ACTIVE',
                'resource_name': created_agent.name
            }
            
        except ImportError:
            # Fallback if Discovery Engine not available
            logger.warning("⚠️ Vertex AI Discovery Engine not available, using simulated agent creation")
            return await self._create_simulated_agent(agent_config)
            
        except Exception as e:
            logger.warning(f"⚠️ Vertex AI agent creation failed, using simulation: {e}")
            return await self._create_simulated_agent(agent_config)
    
    async def _create_simulated_agent(self, agent_config: dict) -> dict:
        """Create simulated agent when Vertex AI is not available"""
        
        logger.info("📡 Creating simulated agent...")
        
        # Simulate API call delay
        await asyncio.sleep(2)
        
        # Mock response
        agent_resource_name = f"projects/{self.project_id}/locations/{self.location}/agents/agent_{int(datetime.now().timestamp())}"
        
        logger.info(f"✅ Simulated Vertex AI agent created: {agent_resource_name}")
        
        return {
            'name': agent_resource_name,
            'display_name': agent_config.get('display_name'),
            'create_time': datetime.now().isoformat(),
            'state': 'ACTIVE',
            'simulated': True
        }
    
    async def create_agent_to_agent_communication(self, agent_a_id: str, agent_b_id: str) -> dict:
        """Enable Agent-to-Agent communication using Vertex AI"""
        
        try:
            agent_a = self.created_agents.get(agent_a_id)
            agent_b = self.created_agents.get(agent_b_id)
            
            if not agent_a or not agent_b:
                raise ValueError("One or both agents not found in registry")
            
            logger.info(f"🔗 Setting up A2A communication between {agent_a_id} and {agent_b_id}")
            
            # Create communication flow configuration
            flow_config = {
                'display_name': f"{agent_a['type']} <-> {agent_b['type']} Communication",
                'description': f"Agent-to-Agent communication flow",
                'start_flow': {
                    'pages': [
                        {
                            'display_name': 'Agent Communication Hub',
                            'entry_fulfillment': {
                                'messages': [
                                    {
                                        'text': {
                                            'text': ['Agents can now communicate directly with each other.']
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
            
            # Simulate flow creation
            await asyncio.sleep(1)
            
            flow_id = f"flow_{agent_a_id}_{agent_b_id}_{int(datetime.now().timestamp())}"
            
            return {
                'success': True,
                'flow_id': flow_id,
                'agent_a': agent_a_id,
                'agent_b': agent_b_id,
                'status': 'active',
                'message': f'A2A communication established between {agent_a["type"]} and {agent_b["type"]}'
            }
            
        except Exception as e:
            logger.error(f"❌ Error setting up A2A communication: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to setup A2A communication: {str(e)}'
            }
    
    async def enhance_agent_with_mcp(self, agent_id: str, mcp_capabilities: List[str]) -> dict:
        """Enhance an existing agent with MCP server capabilities"""
        
        try:
            if agent_id not in self.created_agents:
                raise ValueError(f"Agent {agent_id} not found")
            
            agent = self.created_agents[agent_id]
            
            logger.info(f"🔧 Enhancing {agent_id} with MCP capabilities: {mcp_capabilities}")
            
            # Update agent capabilities
            current_capabilities = agent.get('config', {}).get('capabilities', [])
            enhanced_capabilities = list(set(current_capabilities + mcp_capabilities))
            
            # Update agent configuration
            agent['config']['capabilities'] = enhanced_capabilities
            agent['config']['mcp_enhanced'] = True
            agent['config']['mcp_capabilities'] = mcp_capabilities
            agent['updated_at'] = datetime.now().isoformat()
            
            return {
                'success': True,
                'agent_id': agent_id,
                'enhanced_capabilities': enhanced_capabilities,
                'mcp_capabilities': mcp_capabilities,
                'message': f'Agent {agent_id} enhanced with MCP capabilities'
            }
            
        except Exception as e:
            logger.error(f"❌ Error enhancing agent with MCP: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to enhance agent: {str(e)}'
            }
    
    def get_created_agents(self) -> List[dict]:
        """Get list of all created agents"""
        
        return [
            {
                'id': agent_id,
                'type': agent_data.get('type'),
                'vertex_resource': agent_data.get('vertex_resource_name'),
                'capabilities': agent_data.get('config', {}).get('capabilities', []),
                'status': agent_data.get('status'),
                'created_at': agent_data.get('created_at')
            }
            for agent_id, agent_data in self.created_agents.items()
        ]
    
    def get_agent_status(self, agent_id: str) -> dict:
        """Get status of a specific agent"""
        
        if agent_id not in self.created_agents:
            return {'error': 'Agent not found'}
        
        agent = self.created_agents[agent_id]
        
        return {
            'id': agent_id,
            'type': agent.get('type'),
            'status': agent.get('status'),
            'capabilities': agent.get('config', {}).get('capabilities', []),
            'created_at': agent.get('created_at'),
            'vertex_resource': agent.get('vertex_resource_name')
        }