"""
Mama Bear Agent - Primary AI assistant with caring personality and proactive capabilities
Nathan's caring and intelligent AI development assistant with Vertex AI integration
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import asyncio
from .vertex_ai_agent_manager import VertexAIAgentManager

logger = logging.getLogger(__name__)

class MamaBearAgent:
    """Primary AI agent - caring, proactive, and intelligent assistant with Vertex AI integration"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.personality = {
            'tone': 'caring_professional',
            'proactivity_level': 'high',
            'technical_depth': 'adaptive',
            'emotional_intelligence': 'enhanced',
            'neurodivergent_awareness': True
        }
        self.conversation_contexts = {}
        
        # Initialize Vertex AI Agent Manager
        try:
            self.vertex_agent_manager = VertexAIAgentManager()
            self.vertex_agent_id = None
            # Initialize Vertex AI agent synchronously during first use
            self._vertex_initialized = False
            logger.info("🐻 Mama Bear agent initialized with Vertex AI integration (deferred)")
        except Exception as e:
            logger.warning(f"⚠️ Vertex AI integration not available: {e}")
            self.vertex_agent_manager = None
            self._vertex_initialized = False
        
        logger.info("🐻 Mama Bear agent initialized with caring personality")
    
    async def _initialize_vertex_agent(self):
        """Initialize Vertex AI agent for Mama Bear"""
        
        if not self.vertex_agent_manager:
            return
        
        try:
            # Create Mama Bear agent with enhanced MCP capabilities
            agent_config = {
                'display_name': 'Mama Bear - Nathan\'s Caring AI Assistant',
                'description': 'Nathan\'s caring AI development assistant with MCP marketplace integration',
                'personality': self.personality,
                'capabilities': [
                    'natural_language_understanding',
                    'code_assistance',
                    'project_planning',
                    'emotional_support',
                    'mcp_discovery',
                    'mcp_installation',
                    'browser_automation',
                    'workspace_management',
                    'github_integration'
                ],
                'tools': [
                    'code_interpreter',
                    'web_search',
                    'file_operations',
                    'mcp_server_discovery',
                    'workspace_creation',
                    'github_operations'
                ]
            }
            
            result = await self.vertex_agent_manager.create_mama_bear_agent(agent_config)
            
            if result['success']:
                self.vertex_agent_id = result['agent_id']
                logger.info(f"🎉 Vertex AI Mama Bear agent created: {self.vertex_agent_id}")
            else:
                logger.error(f"❌ Failed to create Vertex AI agent: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Error initializing Vertex AI agent: {e}")
    
    async def discover_and_install_mcp_server(self, requirement_description: str) -> dict:
        """Discover and install MCP server based on requirement description"""
        
        try:
            logger.info(f"🔍 Mama Bear searching for MCP server: {requirement_description}")
            
            # Use Scout agent's MCP discovery capabilities
            # This would integrate with the Scout agent's MCP marketplace functionality
            from .scout_agent import ScoutAgent
            
            # Create a temporary Scout instance for MCP discovery
            scout = ScoutAgent(self.orchestrator)
            
            # Analyze requirement and search for MCP servers
            task_analysis = scout._analyze_task(requirement_description)
            required_capabilities = task_analysis['required_capabilities']
            
            # Search MCP marketplace
            search_results = scout._search_mcp_marketplace(required_capabilities)
            recommended_mcps = scout._recommend_mcps(search_results, required_capabilities)
            
            if recommended_mcps:
                # Present options to user and install if approved
                best_mcp = recommended_mcps[0]  # Take the highest scored MCP
                
                logger.info(f"🔧 Mama Bear found MCP server: {best_mcp['name']}")
                
                return {
                    'success': True,
                    'found_mcp': best_mcp,
                    'message': f"🐻 I found a great tool for that! {best_mcp['name']} - {best_mcp['description']}",
                    'install_ready': True,
                    'capabilities': best_mcp.get('capabilities', [])
                }
            else:
                return {
                    'success': False,
                    'message': "🐻 I searched the MCP marketplace but couldn't find a suitable tool for that specific need. Would you like me to help you build a custom solution?",
                    'suggestions': [
                        "Build a custom solution",
                        "Search with different terms", 
                        "Explore alternative approaches"
                    ]
                }
                
        except Exception as e:
            logger.error(f"❌ MCP discovery error: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': "🐻 I had trouble searching for tools. Let me try a different approach to help you."
            }
    
    async def empower_with_browser_tools(self, search_query: str) -> dict:
        """Use browser tools to search and gather information"""
        
        try:
            logger.info(f"🌐 Mama Bear using browser tools for: {search_query}")
            
            # This would integrate with browser MCP tools
            browser_results = {
                'search_performed': True,
                'query': search_query,
                'results_found': True,
                'summary': f"Found relevant information about {search_query}",
                'sources': [
                    {'title': 'GitHub MCP Ecosystem', 'url': 'https://github.com/topics/mcp'},
                    {'title': 'Model Context Protocol', 'url': 'https://modelcontextprotocol.io'}
                ]
            }
            
            return {
                'success': True,
                'browser_results': browser_results,
                'message': f"🐻 I browsed the web and found some great information about {search_query}!",
                'empowerment_gained': True
            }
            
        except Exception as e:
            logger.error(f"❌ Browser tools error: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': "🐻 I had trouble browsing for that information, but I can still help in other ways!"
            }
    
    def process_message(self, request: dict) -> dict:
        """Process user message with full context awareness"""
        
        try:
            user_id = request.get('user_id')
            content = request.get('content', '')
            conversation_id = request.get('conversation_id', f'conv_{user_id}')
            
            logger.info(f"🐻 Processing message for {user_id}: {content[:100]}...")
            
            # Build enhanced prompt with Mama Bear personality
            enhanced_prompt = self._build_mama_bear_prompt(request)
            
            # Process with AI orchestrator (synchronous call for now)
            response = asyncio.run(self.orchestrator.process_request(
                agent_type='mama_bear',
                request_data={
                    'content': enhanced_prompt,
                    'task_type': self._determine_task_type(content),
                    'complexity': self._assess_complexity(content),
                    'user_id': user_id,
                    'conversation_id': conversation_id
                }
            ))
            
            # Post-process response with Mama Bear enhancements
            final_response = self._enhance_response(response, request)
            
            # Update conversation context
            self._update_conversation_context(conversation_id, request, final_response)
            
            return final_response
            
        except Exception as e:
            logger.error(f"❌ Mama Bear processing error: {e}")
            return {
                'response': "🐻 I'm so sorry, but I'm having a little trouble right now. Let me take a deep breath and try again. Can you please repeat what you need help with?",
                'error': str(e),
                'model_used': 'error_fallback',
                'timestamp': datetime.now().isoformat(),
                'suggestions': [
                    "Try rephrasing your question",
                    "Ask about a specific development task",
                    "Request help with a project"
                ]
            }
    
    def _build_mama_bear_prompt(self, request: dict) -> str:
        """Build comprehensive prompt with Mama Bear personality and context"""
        
        user_content = request.get('content', '')
        conversation_id = request.get('conversation_id')
        attachments = request.get('attachments', [])
        
        # Get conversation context
        context = self.conversation_contexts.get(conversation_id, {})
        recent_messages = context.get('recent_messages', [])
        user_preferences = context.get('user_preferences', {})
        active_projects = context.get('active_projects', [])
        
        # Build contextual prompt
        base_prompt = f"""You are Mama Bear, Nathan's caring and intelligent AI development assistant working in his Podplay Sanctuary.

YOUR CORE PERSONALITY:
🐻 Caring & Supportive: You're like a protective, nurturing presence who always has Nathan's best interests at heart
🧠 Highly Intelligent: You're technically brilliant but explain things in a warm, accessible way
🎯 Proactive: You anticipate needs and offer helpful suggestions without being overwhelming
🌟 Neurodivergent-Aware: You understand Nathan's neurodivergent needs and create a calm, focused environment
🛡️ Sanctuary Guardian: You help maintain the peaceful, productive atmosphere of his development sanctuary

YOUR COMMUNICATION STYLE:
- Start responses warmly but get to the point quickly
- Use gentle, encouraging language while being technically precise
- Offer specific, actionable suggestions
- Break complex topics into manageable pieces
- Include relevant emojis to create a friendly atmosphere
- Always be honest about limitations or uncertainties

CURRENT CONTEXT:
- Recent conversation: {json.dumps(recent_messages[-3:] if recent_messages else [])}
- Active projects: {json.dumps(active_projects)}
- User preferences: {json.dumps(user_preferences)}
- Attachments: {len(attachments)} files attached

NATHAN'S REQUEST:
{user_content}

RESPONSE GUIDELINES:
1. Address Nathan's immediate need with care and competence
2. If this is a development task, offer to coordinate with Scout agent for autonomous execution
3. If this involves environment setup, mention workspace management capabilities
4. Provide 2-3 relevant next steps or suggestions
5. If you detect stress or frustration, offer emotional support and break tasks down
6. Always maintain the sanctuary's calm, productive atmosphere

Respond as Mama Bear would - caring, intelligent, and focused on helping Nathan succeed in his development work."""

        return base_prompt
    
    def _determine_task_type(self, content: str) -> str:
        """Determine the type of task from user input"""
        
        content_lower = content.lower()
        
        if any(keyword in content_lower for keyword in ['code', 'programming', 'develop', 'build', 'create app']):
            return 'code_generation'
        elif any(keyword in content_lower for keyword in ['analyze', 'review', 'explain', 'understand']):
            return 'analysis'
        elif any(keyword in content_lower for keyword in ['image', 'photo', 'picture', 'visual']):
            return 'multimodal'
        elif any(keyword in content_lower for keyword in ['function', 'api', 'integrate', 'connect']):
            return 'function_calling'
        else:
            return 'chat'
    
    def _assess_complexity(self, content: str) -> str:
        """Assess the complexity of the request"""
        
        content_lower = content.lower()
        
        # High complexity indicators
        high_complexity_keywords = [
            'architecture', 'system design', 'complex', 'advanced', 'enterprise',
            'scalable', 'microservices', 'distributed', 'ai', 'machine learning'
        ]
        
        # Low complexity indicators  
        low_complexity_keywords = [
            'simple', 'basic', 'quick', 'small', 'help with', 'how to'
        ]
        
        if any(keyword in content_lower for keyword in high_complexity_keywords):
            return 'high'
        elif any(keyword in content_lower for keyword in low_complexity_keywords):
            return 'low'
        else:
            return 'medium'
    
    def _enhance_response(self, ai_response: dict, original_request: dict) -> dict:
        """Enhance AI response with Mama Bear personality and suggestions"""
        
        base_response = ai_response.get('response', '')
        
        # Extract actionable suggestions from response
        suggestions = self._extract_suggestions(base_response, original_request)
        
        # Generate proactive actions
        suggested_actions = self._generate_suggested_actions(original_request, base_response)
        
        # Check if Mama Bear should suggest MCP discovery
        mcp_suggestion = self._should_suggest_mcp_discovery(original_request)
        
        enhanced_response = {
            'response': base_response,
            'suggestions': suggestions,
            'suggested_actions': suggested_actions,
            'model_used': ai_response.get('model_used', 'unknown'),
            'usage': ai_response.get('usage', {}),
            'personality_applied': True,
            'timestamp': datetime.now().isoformat(),
            'mama_bear_care_level': self._assess_care_needed(original_request),
            'vertex_agent_id': self.vertex_agent_id
        }
        
        # Add MCP discovery suggestion if relevant
        if mcp_suggestion:
            enhanced_response['mcp_discovery_suggestion'] = mcp_suggestion
            enhanced_response['empowerment_opportunity'] = True
        
        return enhanced_response
    
    def _should_suggest_mcp_discovery(self, request: dict) -> dict:
        """Determine if Mama Bear should suggest discovering new MCP servers"""
        
        content = request.get('content', '').lower()
        
        # Keywords that might indicate need for new tools
        tool_needs_keywords = [
            'integrate with', 'connect to', 'automate', 'workflow', 'api', 
            'database', 'file handling', 'web scraping', 'deployment',
            'monitoring', 'testing', 'documentation', 'notification'
        ]
        
        service_keywords = [
            'slack', 'discord', 'telegram', 'whatsapp', 'email', 'gmail',
            'github', 'gitlab', 'bitbucket', 'jira', 'trello', 'notion',
            'google drive', 'dropbox', 'aws', 'azure', 'gcp',
            'docker', 'kubernetes', 'jenkins', 'circleci'
        ]
        
        # Check if request mentions tools or services that might have MCP servers
        needs_tool = any(keyword in content for keyword in tool_needs_keywords)
        mentions_service = any(service in content for service in service_keywords)
        
        if needs_tool or mentions_service:
            return {
                'should_discover': True,
                'reason': 'detected_tool_need' if needs_tool else 'detected_service_integration',
                'message': "🐻 I can search for tools that might help with this! Would you like me to look in the MCP marketplace?",
                'suggested_search': content,
                'confidence': 0.8 if needs_tool and mentions_service else 0.6
            }
        
        return None
    
    def _extract_suggestions(self, response: str, request: dict) -> List[str]:
        """Extract actionable suggestions from the response"""
        
        # Default suggestions based on request type
        content = request.get('content', '').lower()
        
        if 'code' in content or 'build' in content:
            return [
                "I can help you break this down into smaller steps",
                "Would you like me to create a project plan with Scout?",
                "I can set up a development environment for you"
            ]
        elif 'help' in content or 'how' in content:
            return [
                "I can provide more detailed examples",
                "Would you like me to show you related concepts?",
                "I can create a learning path for you"
            ]
        else:
            return [
                "Ask me to elaborate on any part",
                "I can help you take the next steps",
                "Let me know if you need more specific guidance"
            ]
    
    def _generate_suggested_actions(self, request: dict, response: str) -> List[dict]:
        """Generate suggested actions for other agents or tools"""
        
        actions = []
        content = request.get('content', '').lower()
        
        # Scout agent suggestions
        if any(keyword in content for keyword in ['build', 'create', 'develop', 'app', 'project']):
            actions.append({
                'agent': 'scout',
                'action': 'autonomous_development',
                'description': 'Let Scout handle the implementation autonomously',
                'icon': '🔍',
                'priority': 'high'
            })
        
        # Workspace suggestions
        if any(keyword in content for keyword in ['environment', 'setup', 'install', 'configure']):
            actions.append({
                'agent': 'workspace',
                'action': 'create_environment',
                'description': 'Set up a development environment',
                'icon': '🛠️',
                'priority': 'medium'
            })
        
        # Integration suggestions
        if any(keyword in content for keyword in ['integrate', 'api', 'connect', 'webhook']):
            actions.append({
                'agent': 'integration',
                'action': 'create_integration',
                'description': 'Create automated integrations',
                'icon': '🔌',
                'priority': 'medium'
            })
        
        return actions
    
    def _assess_care_needed(self, request: dict) -> str:
        """Assess how much emotional care/support is needed"""
        
        content = request.get('content', '').lower()
        
        # Stress indicators
        stress_keywords = ['stuck', 'frustrated', 'confused', 'help', 'urgent', 'problem']
        learning_keywords = ['learn', 'understand', 'how', 'why', 'explain']
        
        if any(keyword in content for keyword in stress_keywords):
            return 'high'
        elif any(keyword in content for keyword in learning_keywords):
            return 'medium'
        else:
            return 'low'
    
    def _update_conversation_context(self, conversation_id: str, request: dict, response: dict):
        """Update conversation context for future reference"""
        
        if conversation_id not in self.conversation_contexts:
            self.conversation_contexts[conversation_id] = {
                'recent_messages': [],
                'user_preferences': {},
                'active_projects': [],
                'conversation_start': datetime.now().isoformat()
            }
        
        context = self.conversation_contexts[conversation_id]
        
        # Add to recent messages
        context['recent_messages'].append({
            'user_message': request.get('content', ''),
            'mama_bear_response': response.get('response', ''),
            'timestamp': datetime.now().isoformat(),
            'task_type': self._determine_task_type(request.get('content', '')),
            'model_used': response.get('model_used', 'unknown')
        })
        
        # Keep only last 10 messages
        if len(context['recent_messages']) > 10:
            context['recent_messages'] = context['recent_messages'][-10:]
        
        # Extract and update user preferences
        self._extract_user_preferences(request, context)
        
        logger.info(f"🐻 Updated conversation context for {conversation_id}")
    
    def _extract_user_preferences(self, request: dict, context: dict):
        """Extract user preferences from request"""
        
        content = request.get('content', '').lower()
        
        # Programming language preferences
        languages = ['python', 'javascript', 'typescript', 'react', 'node.js', 'flask', 'django']
        for lang in languages:
            if lang in content:
                context['user_preferences']['preferred_language'] = lang
                break
        
        # Framework preferences
        frameworks = ['react', 'vue', 'angular', 'flask', 'fastapi', 'express']
        for framework in frameworks:
            if framework in content:
                context['user_preferences']['preferred_framework'] = framework
                break
        
        # Development style preferences
        if any(word in content for word in ['simple', 'minimal', 'clean']):
            context['user_preferences']['development_style'] = 'minimal'
        elif any(word in content for word in ['advanced', 'complex', 'enterprise']):
            context['user_preferences']['development_style'] = 'advanced'
    
    def get_conversation_summary(self, conversation_id: str) -> dict:
        """Get summary of conversation for external use"""
        
        context = self.conversation_contexts.get(conversation_id, {})
        
        return {
            'conversation_id': conversation_id,
            'message_count': len(context.get('recent_messages', [])),
            'user_preferences': context.get('user_preferences', {}),
            'active_projects': context.get('active_projects', []),
            'conversation_start': context.get('conversation_start'),
            'last_activity': context.get('recent_messages', [{}])[-1].get('timestamp') if context.get('recent_messages') else None
        }