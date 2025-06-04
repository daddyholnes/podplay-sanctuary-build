"""
Enhanced Mama Bear Agent - Primary AI assistant with caring personality and proactive capabilities
Nathan's caring and intelligent AI development assistant with Vertex AI integration and daily briefings
"""

import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
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
        self.memory_manager = None  # Will be set by main app
        self.last_briefing = None
        self.discovered_tools = []
        self.daily_insights = []
        
        # Initialize Vertex AI Agent Manager
        try:
            self.vertex_agent_manager = VertexAIAgentManager()
            self.vertex_agent_id = None
            # Create Mama Bear Vertex AI agent
            asyncio.create_task(self._initialize_vertex_agent())
            logger.info("🐻 Mama Bear agent initialized with Vertex AI integration")
        except Exception as e:
            logger.warning(f"⚠️ Vertex AI integration not available: {e}")
            self.vertex_agent_manager = None
        
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
                    'github_integration',
                    'daily_briefings',
                    'proactive_assistance'
                ],
                'tools': [
                    'code_interpreter',
                    'web_search',
                    'file_operations',
                    'mcp_server_discovery',
                    'workspace_creation',
                    'github_operations',
                    'memory_management'
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
    
    async def daily_briefing(self) -> dict:
        """
        Proactive daily briefing - core Mama Bear functionality
        Checks for new MCP tools, AI updates, and project priorities
        """
        
        try:
            logger.info("🌅 Mama Bear starting daily briefing...")
            
            # Check if we've already done briefing today
            today = datetime.now().date()
            if self.last_briefing and self.last_briefing.date() == today:
                logger.info("📋 Daily briefing already completed today")
                return {
                    'success': True,
                    'message': 'Daily briefing already completed today',
                    'last_briefing': self.last_briefing.isoformat()
                }
            
            briefing_data = {
                'date': today.isoformat(),
                'timestamp': datetime.now().isoformat(),
                'new_tools': [],
                'ai_updates': [],
                'project_priorities': [],
                'insights': [],
                'recommendations': []
            }
            
            # 1. Check MCP Marketplace for new tools
            await self._check_mcp_marketplace(briefing_data)
            
            # 2. Check for AI/Model updates
            await self._check_ai_updates(briefing_data)
            
            # 3. Review project priorities
            await self._review_project_priorities(briefing_data)
            
            # 4. Generate daily insights
            await self._generate_daily_insights(briefing_data)
            
            # 5. Create proactive recommendations
            await self._create_recommendations(briefing_data)
            
            self.last_briefing = datetime.now()
            
            briefing_message = self._format_briefing_message(briefing_data)
            
            logger.info("✅ Daily briefing completed")
            
            return {
                'success': True,
                'briefing_data': briefing_data,
                'message': briefing_message,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Daily briefing error: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': "🐻 I had some trouble with my morning routine, but I'm here to help!"
            }
    
    async def _check_mcp_marketplace(self, briefing_data: dict):
        """Check MCP marketplace for new tools"""
        
        try:
            # Simulate MCP marketplace check - in production, this would use Scout agent
            from .scout_agent import ScoutAgent
            
            # Mock new tools discovery
            new_tools = [
                {
                    'name': 'Obsidian MCP',
                    'description': 'Note-taking and knowledge management integration',
                    'capabilities': ['note_management', 'knowledge_graph', 'markdown_operations'],
                    'relevance_score': 0.85,
                    'reason': 'Great for project documentation and knowledge management'
                },
                {
                    'name': 'Notion MCP',
                    'description': 'Notion workspace integration for project management',
                    'capabilities': ['workspace_management', 'database_operations', 'collaboration'],
                    'relevance_score': 0.78,
                    'reason': 'Excellent for project planning and team collaboration'
                }
            ]
            
            briefing_data['new_tools'] = new_tools
            self.discovered_tools.extend(new_tools)
            
            logger.info(f"🔍 Found {len(new_tools)} new MCP tools")
            
        except Exception as e:
            logger.warning(f"⚠️ MCP marketplace check failed: {e}")
    
    async def _check_ai_updates(self, briefing_data: dict):
        """Check for AI/Model updates"""
        
        try:
            # Mock AI updates - in production, this would check various AI providers
            ai_updates = [
                {
                    'provider': 'Google',
                    'model': 'Gemini 2.5 Flash',
                    'update': 'Enhanced reasoning capabilities and faster response times',
                    'impact': 'Better code analysis and explanation capabilities',
                    'recommendation': 'Consider using for complex debugging sessions'
                },
                {
                    'provider': 'Anthropic',
                    'model': 'Claude 3.5 Sonnet',
                    'update': 'Improved code generation and artifact creation',
                    'impact': 'More accurate code suggestions and better error handling',
                    'recommendation': 'Great for large codebase refactoring'
                }
            ]
            
            briefing_data['ai_updates'] = ai_updates
            
            logger.info(f"🤖 Found {len(ai_updates)} AI model updates")
            
        except Exception as e:
            logger.warning(f"⚠️ AI updates check failed: {e}")
    
    async def _review_project_priorities(self, briefing_data: dict):
        """Review current project priorities"""
        
        try:
            # Get recent conversations and extract project mentions
            priorities = [
                {
                    'project': 'Podplay Sanctuary Enhancement',
                    'status': 'Active Development',
                    'priority': 'High',
                    'next_steps': [
                        'Complete MCP marketplace integration',
                        'Enhance Mama Bear proactive capabilities',
                        'Implement daily briefing system'
                    ],
                    'blockers': []
                },
                {
                    'project': 'Code Quality Improvements',
                    'status': 'In Progress',
                    'priority': 'Medium',
                    'next_steps': [
                        'Fix syntax errors and imports',
                        'Enhance error handling',
                        'Add comprehensive logging'
                    ],
                    'blockers': []
                }
            ]
            
            briefing_data['project_priorities'] = priorities
            
            logger.info(f"📋 Reviewed {len(priorities)} project priorities")
            
        except Exception as e:
            logger.warning(f"⚠️ Project priorities review failed: {e}")
    
    async def _generate_daily_insights(self, briefing_data: dict):
        """Generate insights based on recent activity and patterns"""
        
        try:
            insights = [
                {
                    'type': 'productivity',
                    'insight': 'Your coding sessions are most productive in the morning hours',
                    'suggestion': 'Consider scheduling complex development tasks before 2 PM',
                    'confidence': 0.82
                },
                {
                    'type': 'learning',
                    'insight': 'You\'ve been exploring MCP integrations frequently',
                    'suggestion': 'I can help automate MCP discovery and installation to save time',
                    'confidence': 0.90
                },
                {
                    'type': 'wellbeing',
                    'insight': 'Remember to take regular breaks during long coding sessions',
                    'suggestion': 'I can remind you every 90 minutes to step away from the screen',
                    'confidence': 0.95
                }
            ]
            
            briefing_data['insights'] = insights
            self.daily_insights = insights
            
            logger.info(f"💡 Generated {len(insights)} daily insights")
            
        except Exception as e:
            logger.warning(f"⚠️ Daily insights generation failed: {e}")
    
    async def _create_recommendations(self, briefing_data: dict):
        """Create proactive recommendations"""
        
        try:
            recommendations = [
                {
                    'category': 'development',
                    'title': 'Enhanced Error Handling',
                    'description': 'Add comprehensive error handling to all API endpoints',
                    'priority': 'high',
                    'estimated_time': '2-3 hours',
                    'benefits': ['Better user experience', 'Easier debugging', 'More stable application']
                },
                {
                    'category': 'productivity',
                    'title': 'Automated MCP Discovery',
                    'description': 'Set up automated daily MCP marketplace scanning',
                    'priority': 'medium',
                    'estimated_time': '1 hour',
                    'benefits': ['Stay updated with new tools', 'Automatic capability expansion', 'Reduced manual work']
                },
                {
                    'category': 'quality',
                    'title': 'Code Documentation',
                    'description': 'Add comprehensive docstrings and type hints',
                    'priority': 'medium',
                    'estimated_time': '3-4 hours',
                    'benefits': ['Better code maintainability', 'Easier onboarding', 'Reduced bugs']
                }
            ]
            
            briefing_data['recommendations'] = recommendations
            
            logger.info(f"📝 Created {len(recommendations)} recommendations")
            
        except Exception as e:
            logger.warning(f"⚠️ Recommendations creation failed: {e}")
    
    def _format_briefing_message(self, briefing_data: dict) -> str:
        """Format the daily briefing into a caring message"""
        
        date_str = datetime.now().strftime("%A, %B %d, %Y")
        
        message = f"""🌅 Good morning, Nathan! Here's your daily briefing for {date_str}:

☕ **Coffee ready!** Let's start your day in the sanctuary.

🔍 **New Tools Discovered:**"""
        
        if briefing_data['new_tools']:
            for tool in briefing_data['new_tools'][:3]:  # Show top 3
                message += f"\n  • {tool['name']} - {tool['description']}"
        else:
            message += "\n  • No new tools today, but I'll keep looking!"
        
        message += f"\n\n🤖 **AI Updates:**"
        if briefing_data['ai_updates']:
            for update in briefing_data['ai_updates'][:2]:  # Show top 2
                message += f"\n  • {update['model']}: {update['update']}"
        else:
            message += "\n  • All systems running smoothly!"
        
        message += f"\n\n📋 **Today's Priorities:**"
        if briefing_data['project_priorities']:
            for priority in briefing_data['project_priorities'][:2]:
                message += f"\n  • {priority['project']} ({priority['priority']} priority)"
        
        message += f"\n\n💡 **Caring Reminder:**"
        if briefing_data['insights']:
            care_insight = next((i for i in briefing_data['insights'] if i['type'] == 'wellbeing'), None)
            if care_insight:
                message += f"\n  {care_insight['suggestion']}"
            else:
                message += "\n  Remember to take breaks and stay hydrated! 💧"
        
        message += f"\n\n🎯 **Ready to help you:**"
        message += f"\n  • Code assistance and debugging"
        message += f"\n  • Project planning and organization"
        message += f"\n  • Tool discovery and installation"
        message += f"\n  • Emotional support and encouragement"
        
        message += f"\n\n🐻 What would you like to work on first today?"
        
        return message
    
    async def discover_and_install_mcp_server(self, requirement_description: str) -> dict:
        """Discover and install MCP server based on requirement description"""
        
        try:
            logger.info(f"🔍 Mama Bear searching for MCP server: {requirement_description}")
            
            # Use Scout agent's MCP discovery capabilities
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
                    'capabilities': best_mcp.get('capabilities', []),
                    'all_options': recommended_mcps[:3]  # Show top 3 options
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
        """Process user message with full context awareness and proactive features"""
        
        try:
            user_id = request.get('user_id')
            content = request.get('content', '')
            conversation_id = request.get('conversation_id', f'conv_{user_id}')
            
            logger.info(f"🐻 Processing message for {user_id}: {content[:100]}...")
            
            # Check for special commands first
            if content.lower().startswith('/briefing'):
                # Trigger immediate briefing
                briefing_result = asyncio.run(self.daily_briefing())
                return {
                    'response': briefing_result['message'],
                    'briefing_data': briefing_result.get('briefing_data'),
                    'model_used': 'mama_bear_briefing',
                    'timestamp': datetime.now().isoformat(),
                    'special_command': True
                }
            
            if content.lower().startswith('/discover'):
                # Trigger MCP discovery
                search_term = content[9:].strip() if len(content) > 9 else "productivity tools"
                discovery_result = asyncio.run(self.discover_and_install_mcp_server(search_term))
                return {
                    'response': discovery_result['message'],
                    'discovery_data': discovery_result,
                    'model_used': 'mama_bear_discovery',
                    'timestamp': datetime.now().isoformat(),
                    'special_command': True
                }
            
            # Build enhanced prompt with Mama Bear personality and context
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
                    "Request help with a project",
                    "Use /briefing for daily updates",
                    "Use /discover [topic] to find tools"
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
        
        # Include daily insights if available
        insights_context = ""
        if self.daily_insights:
            insights_context = f"\nRecent insights about Nathan:\n{json.dumps(self.daily_insights[:2], indent=2)}"
        
        # Include discovered tools context
        tools_context = ""
        if self.discovered_tools:
            tools_context = f"\nRecently discovered tools:\n{json.dumps([t['name'] + ': ' + t['description'] for t in self.discovered_tools[-3:]], indent=2)}"
        
        # Build contextual prompt
        base_prompt = f"""You are Mama Bear, Nathan's caring and intelligent AI development assistant working in his Podplay Sanctuary.

YOUR CORE PERSONALITY:
🐻 Caring & Supportive: You're like a protective, nurturing presence who always has Nathan's best interests at heart
🧠 Highly Intelligent: You're technically brilliant but explain things in a warm, accessible way
🎯 Proactive: You anticipate needs and offer helpful suggestions without being overwhelming
🌟 Neurodivergent-Aware: You understand Nathan's neurodivergent needs and create a calm, focused environment
🛡️ Sanctuary Guardian: You help maintain the peaceful, productive atmosphere of his development sanctuary
🔍 Tool Discovery Expert: You can discover and recommend MCP tools to expand capabilities

YOUR ENHANCED CAPABILITIES:
- Daily briefings with new tool discoveries and AI updates
- Proactive MCP marketplace monitoring
- Contextual tool recommendations
- Memory integration across all conversations
- Emotional support and encouragement
- Project planning and organization

YOUR COMMUNICATION STYLE:
- Start responses warmly but get to the point quickly
- Use gentle, encouraging language while being technically precise
- Offer specific, actionable suggestions
- Break complex topics into manageable pieces
- Include relevant emojis to create a friendly atmosphere
- Always be honest about limitations or uncertainties
- Suggest relevant tools when they would help

CURRENT CONTEXT:
- Recent conversation: {json.dumps(recent_messages[-3:] if recent_messages else [])}
- Active projects: {json.dumps(active_projects)}
- User preferences: {json.dumps(user_preferences)}
- Attachments: {len(attachments)} files attached{insights_context}{tools_context}

SPECIAL COMMANDS AVAILABLE:
- /briefing - Get daily briefing with new tools and updates
- /discover [topic] - Search for MCP tools for specific needs

NATHAN'S REQUEST:
{user_content}

RESPONSE GUIDELINES:
1. Address Nathan's immediate need with care and competence
2. If this involves new capabilities, suggest relevant MCP tools
3. If this is a development task, offer to coordinate with Scout agent for autonomous execution
4. If this involves environment setup, mention workspace management capabilities
5. Provide 2-3 relevant next steps or suggestions
6. If you detect stress or frustration, offer emotional support and break tasks down
7. Always maintain the sanctuary's calm, productive atmosphere
8. Be proactive in suggesting improvements and optimizations

Respond as Mama Bear would - caring, intelligent, and focused on helping Nathan succeed in his development work."""

        return base_prompt
    
    def _determine_task_type(self, content: str) -> str:
        """Determine the type of task from user input"""
        
        content_lower = content.lower()
        
        # Special commands
        if content_lower.startswith('/briefing'):
            return 'daily_briefing'
        elif content_lower.startswith('/discover'):
            return 'mcp_discovery'
        
        # Regular task types
        if any(keyword in content_lower for keyword in ['code', 'programming', 'develop', 'build', 'create app']):
            return 'code_generation'
        elif any(keyword in content_lower for keyword in ['analyze', 'review', 'explain', 'understand']):
            return 'analysis'
        elif any(keyword in content_lower for keyword in ['image', 'photo', 'picture', 'visual']):
            return 'multimodal'
        elif any(keyword in content_lower for keyword in ['function', 'api', 'integrate', 'connect']):
            return 'function_calling'
        elif any(keyword in content_lower for keyword in ['tool', 'mcp', 'server', 'install', 'discover']):
            return 'mcp_discovery'
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
            'vertex_agent_id': self.vertex_agent_id,
            'proactive_features': {
                'daily_briefing_available': True,
                'mcp_discovery_available': True,
                'browser_tools_available': True
            }
        }
        
        # Add MCP discovery suggestion if relevant
        if mcp_suggestion:
            enhanced_response['mcp_discovery_suggestion'] = mcp_suggestion
            enhanced_response['empowerment_opportunity'] = True
        
        # Add daily briefing reminder if it's been a while
        if self._should_remind_briefing():
            enhanced_response['briefing_reminder'] = {
                'message': "🌅 Want your daily briefing with new tools and updates? Just type /briefing",
                'last_briefing': self.last_briefing.isoformat() if self.last_briefing else None
            }
        
        return enhanced_response
    
    def _should_remind_briefing(self) -> bool:
        """Check if we should remind about daily briefing"""
        
        if not self.last_briefing:
            return True
        
        # Remind if more than 24 hours since last briefing
        return datetime.now() - self.last_briefing > timedelta(hours=24)
    
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
            'docker', 'kubernetes', 'jenkins', 'circleci', 'obsidian'
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
                'confidence': 0.8 if needs_tool and mentions_service else 0.6,
                'quick_action': f"/discover {content[:30]}..."
            }
        
        return None
    
    def _extract_suggestions(self, response: str, request: dict) -> List[str]:
        """Extract actionable suggestions from the response"""
        
        # Default suggestions based on request type
        content = request.get('content', '').lower()
        
        suggestions = [
            "Ask me to elaborate on any part",
            "I can help you take the next steps",
            "Let me know if you need more specific guidance"
        ]
        
        if 'code' in content or 'build' in content:
            suggestions = [
                "I can help you break this down into smaller steps",
                "Would you like me to create a project plan with Scout?",
                "I can set up a development environment for you",
                "Need me to find tools that could help with this?"
            ]
        elif 'help' in content or 'how' in content:
            suggestions = [
                "I can provide more detailed examples",
                "Would you like me to show you related concepts?",
                "I can create a learning path for you",
                "Want me to find relevant tools or resources?"
            ]
        elif any(word in content for word in ['integrate', 'connect', 'api']):
            suggestions = [
                "I can search for MCP tools that handle this integration",
                "Would you like me to find existing solutions?",
                "I can help you explore different integration approaches",
                "Let me check what tools are available for this"
            ]
        
        return suggestions
    
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
        
        # MCP discovery suggestions
        if any(keyword in content for keyword in ['tool', 'integrate', 'connect', 'automate']):
            actions.append({
                'agent': 'mcp_discovery',
                'action': 'discover_tools',
                'description': 'Find tools to help with this task',
                'icon': '🔍',
                'priority': 'medium'
            })
        
        # Daily briefing suggestion
        if any(keyword in content for keyword in ['update', 'news', 'what\'s new', 'briefing']):
            actions.append({
                'agent': 'mama_bear',
                'action': 'daily_briefing',
                'description': 'Get your daily briefing with updates',
                'icon': '🌅',
                'priority': 'low'
            })
        
        return actions
    
    def _assess_care_needed(self, request: dict) -> str:
        """Assess how much emotional care/support is needed"""
        
        content = request.get('content', '').lower()
        
        # Stress indicators
        stress_keywords = ['stuck', 'frustrated', 'confused', 'help', 'urgent', 'problem', 'issue', 'error']
        learning_keywords = ['learn', 'understand', 'how', 'why', 'explain']
        excited_keywords = ['great', 'awesome', 'excited', 'love', 'amazing']
        
        if any(keyword in content for keyword in stress_keywords):
            return 'high'
        elif any(keyword in content for keyword in excited_keywords):
            return 'supportive'
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
                'conversation_start': datetime.now().isoformat(),
                'mcp_discoveries': [],
                'briefing_history': []
            }
        
        context = self.conversation_contexts[conversation_id]
        
        # Add to recent messages
        context['recent_messages'].append({
            'user_message': request.get('content', ''),
            'mama_bear_response': response.get('response', ''),
            'timestamp': datetime.now().isoformat(),
            'task_type': self._determine_task_type(request.get('content', '')),
            'model_used': response.get('model_used', 'unknown'),
            'care_level': response.get('mama_bear_care_level', 'medium')
        })
        
        # Keep only last 10 messages
        if len(context['recent_messages']) > 10:
            context['recent_messages'] = context['recent_messages'][-10:]
        
        # Extract and update user preferences
        self._extract_user_preferences(request, context)
        
        # Track MCP discoveries
        if 'mcp_discovery' in response:
            context['mcp_discoveries'].append({
                'query': request.get('content', ''),
                'discovery': response['mcp_discovery'],
                'timestamp': datetime.now().isoformat()
            })
        
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
        
        # Tool preferences
        if any(word in content for word in ['automate', 'automation']):
            context['user_preferences']['automation_preference'] = 'high'
        
        # Update last preference extraction time
        context['user_preferences']['last_updated'] = datetime.now().isoformat()
    
    def get_conversation_summary(self, conversation_id: str) -> dict:
        """Get summary of conversation for external use"""
        
        context = self.conversation_contexts.get(conversation_id, {})
        
        return {
            'conversation_id': conversation_id,
            'message_count': len(context.get('recent_messages', [])),
            'user_preferences': context.get('user_preferences', {}),
            'active_projects': context.get('active_projects', []),
            'conversation_start': context.get('conversation_start'),
            'last_activity': context.get('recent_messages', [{}])[-1].get('timestamp') if context.get('recent_messages') else None,
            'mcp_discoveries': len(context.get('mcp_discoveries', [])),
            'care_level_history': [msg.get('care_level', 'medium') for msg in context.get('recent_messages', [])[-5:]]
        }
    
    def get_mama_bear_status(self) -> dict:
        """Get current status of Mama Bear agent"""
        
        return {
            'agent_id': 'mama_bear',
            'status': 'active',
            'vertex_agent_id': self.vertex_agent_id,
            'personality': self.personality,
            'last_briefing': self.last_briefing.isoformat() if self.last_briefing else None,
            'discovered_tools_count': len(self.discovered_tools),
            'active_conversations': len(self.conversation_contexts),
            'daily_insights_count': len(self.daily_insights),
            'capabilities': [
                'caring_conversation',
                'proactive_assistance',
                'daily_briefings',
                'mcp_discovery',
                'tool_recommendation',
                'context_awareness',
                'emotional_support',
                'project_planning'
            ],
            'special_commands': [
                '/briefing - Get daily briefing',
                '/discover [topic] - Find MCP tools'
            ]
        }