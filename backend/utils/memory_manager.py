"""
Memory Manager - Integrates with Mem0.ai for persistent conversation context
Handles memory storage, retrieval, and context management
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import asyncio
import requests

logger = logging.getLogger(__name__)

class MemoryManager:
    """Integrates with Mem0.ai for persistent conversation context"""
    
    def __init__(self):
        self.mem0_api_key = os.getenv('MEM0_API_KEY')
        self.mem0_user_id = os.getenv('MEM0_USER_ID', 'nathan_sanctuary')
        self.memory_enabled = os.getenv('MEM0_MEMORY_ENABLED', 'True').lower() == 'true'
        self.rag_enabled = os.getenv('MEM0_RAG_ENABLED', 'True').lower() == 'true'
        self.context_window = int(os.getenv('MEM0_CONTEXT_WINDOW', '100'))
        
        self.base_url = "https://api.mem0.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.mem0_api_key}",
            "Content-Type": "application/json"
        }
        
        # Local memory cache
        self.local_memory = {}
        
        logger.info(f"🧠 Memory Manager initialized - Mem0: {self.memory_enabled}, RAG: {self.rag_enabled}")
    
    async def get_relevant_context(self, user_id: str, conversation_id: str, query: str) -> dict:
        """Retrieve relevant context from memory stores"""
        
        if not self.memory_enabled or not self.mem0_api_key:
            logger.warning("⚠️ Mem0.ai not configured, using local memory only")
            return self._get_local_context(conversation_id, query)
        
        try:
            # Search Mem0.ai for relevant memories
            context = await self._search_mem0_memories(user_id, query, conversation_id)
            
            # Enhance with local context
            local_context = self._get_local_context(conversation_id, query)
            
            # Merge contexts
            merged_context = self._merge_contexts(context, local_context)
            
            logger.info(f"🧠 Retrieved {len(merged_context.get('memories', []))} memories for context")
            
            return merged_context
            
        except Exception as e:
            logger.error(f"❌ Memory retrieval error: {e}")
            # Fallback to local memory
            return self._get_local_context(conversation_id, query)
    
    async def _search_mem0_memories(self, user_id: str, query: str, conversation_id: str) -> dict:
        """Search Mem0.ai for relevant memories"""
        
        try:
            # Search for conversation-specific memories
            conversation_memories = await self._mem0_search_request(
                user_id=user_id,
                query=query,
                filters={"conversation_id": conversation_id},
                limit=10
            )
            
            # Search for project-related memories
            project_memories = await self._mem0_search_request(
                user_id=user_id,
                query=query,
                filters={"type": "project_context"},
                limit=5
            )
            
            # Search for user preferences and patterns
            preference_memories = await self._mem0_search_request(
                user_id=user_id,
                query=query,
                filters={"type": "user_preference"},
                limit=5
            )
            
            # Search for tool/MCP related memories
            tool_memories = await self._mem0_search_request(
                user_id=user_id,
                query=query,
                filters={"type": "tool_usage"},
                limit=5
            )
            
            return {
                'conversation_memories': conversation_memories,
                'project_memories': project_memories,
                'preference_memories': preference_memories,
                'tool_memories': tool_memories,
                'total_context_items': len(conversation_memories) + len(project_memories) + 
                                     len(preference_memories) + len(tool_memories)
            }
            
        except Exception as e:
            logger.error(f"❌ Mem0.ai search error: {e}")
            return {'conversation_memories': [], 'project_memories': [], 
                   'preference_memories': [], 'tool_memories': [], 'total_context_items': 0}
    
    async def _mem0_search_request(self, user_id: str, query: str, filters: dict = None, limit: int = 10) -> List[dict]:
        """Make search request to Mem0.ai API"""
        
        try:
            payload = {
                "query": query,
                "user_id": user_id,
                "limit": limit
            }
            
            if filters:
                payload["filters"] = filters
            
            # Make async request (simulated with requests for now)
            response = requests.post(
                f"{self.base_url}/memories/search",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('memories', [])
            else:
                logger.error(f"❌ Mem0.ai search failed: {response.status_code} - {response.text}")
                return []
                
        except requests.RequestException as e:
            logger.error(f"❌ Mem0.ai request error: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Mem0.ai search error: {e}")
            return []
    
    def _get_local_context(self, conversation_id: str, query: str) -> dict:
        """Get context from local memory cache"""
        
        local_memories = self.local_memory.get(conversation_id, {})
        
        # Simple keyword matching for local context
        query_words = query.lower().split()
        relevant_memories = []
        
        for memory_type, memories in local_memories.items():
            for memory in memories:
                content = memory.get('content', '').lower()
                if any(word in content for word in query_words):
                    relevant_memories.append({
                        'type': memory_type,
                        'content': memory.get('content'),
                        'timestamp': memory.get('timestamp'),
                        'relevance_score': 0.8
                    })
        
        return {
            'conversation_memories': relevant_memories,
            'project_memories': [],
            'preference_memories': [],
            'tool_memories': [],
            'total_context_items': len(relevant_memories),
            'source': 'local_cache'
        }
    
    def _merge_contexts(self, mem0_context: dict, local_context: dict) -> dict:
        """Merge Mem0.ai and local contexts"""
        
        merged = {
            'conversation_memories': (mem0_context.get('conversation_memories', []) + 
                                    local_context.get('conversation_memories', [])),
            'project_memories': mem0_context.get('project_memories', []),
            'preference_memories': mem0_context.get('preference_memories', []),
            'tool_memories': mem0_context.get('tool_memories', []),
            'sources': ['mem0', 'local_cache']
        }
        
        merged['total_context_items'] = (len(merged['conversation_memories']) + 
                                       len(merged['project_memories']) + 
                                       len(merged['preference_memories']) + 
                                       len(merged['tool_memories']))
        
        return merged
    
    async def store_interaction(self, user_id: str, agent_type: str, request: dict, response: dict, model_used: str):
        """Store interaction for future context"""
        
        try:
            # Prepare interaction data
            interaction_data = {
                'request': request.get('content'),
                'response': response.get('response'),
                'agent': agent_type,
                'model': model_used,
                'timestamp': datetime.now().isoformat(),
                'conversation_id': request.get('conversation_id'),
                'task_type': request.get('task_type', 'chat')
            }
            
            # Store in Mem0.ai if enabled
            if self.memory_enabled and self.mem0_api_key:
                await self._store_mem0_memory(user_id, interaction_data)
            
            # Store in local cache
            self._store_local_memory(request.get('conversation_id', 'default'), interaction_data)
            
            # Extract and store patterns
            await self._extract_and_store_patterns(user_id, interaction_data)
            
        except Exception as e:
            logger.error(f"❌ Error storing interaction: {e}")
    
    async def _store_mem0_memory(self, user_id: str, interaction_data: dict):
        """Store memory in Mem0.ai"""
        
        try:
            payload = {
                "messages": [
                    {"role": "user", "content": interaction_data['request']},
                    {"role": "assistant", "content": interaction_data['response']}
                ],
                "user_id": user_id,
                "metadata": {
                    "agent": interaction_data['agent'],
                    "model": interaction_data['model'],
                    "conversation_id": interaction_data['conversation_id'],
                    "task_type": interaction_data['task_type'],
                    "timestamp": interaction_data['timestamp'],
                    "type": "chat_interaction"
                }
            }
            
            response = requests.post(
                f"{self.base_url}/memories",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 201:
                logger.info("🧠 Memory stored in Mem0.ai successfully")
            else:
                logger.error(f"❌ Mem0.ai storage failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Mem0.ai storage error: {e}")
    
    def _store_local_memory(self, conversation_id: str, interaction_data: dict):
        """Store memory in local cache"""
        
        if conversation_id not in self.local_memory:
            self.local_memory[conversation_id] = {
                'interactions': [],
                'patterns': [],
                'preferences': []
            }
        
        # Add interaction
        self.local_memory[conversation_id]['interactions'].append({
            'content': f"User: {interaction_data['request']} | Assistant: {interaction_data['response']}",
            'timestamp': interaction_data['timestamp'],
            'agent': interaction_data['agent'],
            'model': interaction_data['model']
        })
        
        # Keep only recent interactions
        if len(self.local_memory[conversation_id]['interactions']) > self.context_window:
            self.local_memory[conversation_id]['interactions'] = \
                self.local_memory[conversation_id]['interactions'][-self.context_window:]
    
    async def _extract_and_store_patterns(self, user_id: str, interaction_data: dict):
        """Extract and store user patterns and preferences"""
        
        try:
            request_content = interaction_data['request'].lower()
            
            # Extract programming language preferences
            languages = ['python', 'javascript', 'typescript', 'react', 'vue', 'angular', 'flask', 'django']
            for lang in languages:
                if lang in request_content:
                    await self._store_preference(user_id, 'programming_language', lang)
            
            # Extract framework preferences
            frameworks = ['react', 'vue', 'angular', 'flask', 'fastapi', 'express', 'nextjs']
            for framework in frameworks:
                if framework in request_content:
                    await self._store_preference(user_id, 'framework', framework)
            
            # Extract development patterns
            if any(word in request_content for word in ['simple', 'minimal', 'clean']):
                await self._store_preference(user_id, 'development_style', 'minimal')
            elif any(word in request_content for word in ['advanced', 'complex', 'enterprise']):
                await self._store_preference(user_id, 'development_style', 'advanced')
            
            # Extract tool usage patterns
            tools = ['docker', 'git', 'vscode', 'jupyter', 'npm', 'pip']
            for tool in tools:
                if tool in request_content:
                    await self._store_tool_usage(user_id, tool, interaction_data['timestamp'])
                    
        except Exception as e:
            logger.error(f"❌ Pattern extraction error: {e}")
    
    async def _store_preference(self, user_id: str, preference_type: str, preference_value: str):
        """Store user preference in Mem0.ai"""
        
        if not self.memory_enabled or not self.mem0_api_key:
            return
        
        try:
            payload = {
                "messages": [
                    {"role": "user", "content": f"I prefer to use {preference_value} for {preference_type}"}
                ],
                "user_id": user_id,
                "metadata": {
                    "type": "user_preference",
                    "preference_type": preference_type,
                    "preference_value": preference_value,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            requests.post(
                f"{self.base_url}/memories",
                headers=self.headers,
                json=payload,
                timeout=5
            )
            
        except Exception as e:
            logger.warning(f"⚠️ Preference storage warning: {e}")
    
    async def _store_tool_usage(self, user_id: str, tool: str, timestamp: str):
        """Store tool usage pattern"""
        
        if not self.memory_enabled or not self.mem0_api_key:
            return
        
        try:
            payload = {
                "messages": [
                    {"role": "user", "content": f"I used {tool} for development"}
                ],
                "user_id": user_id,
                "metadata": {
                    "type": "tool_usage",
                    "tool": tool,
                    "timestamp": timestamp
                }
            }
            
            requests.post(
                f"{self.base_url}/memories",
                headers=self.headers,
                json=payload,
                timeout=5
            )
            
        except Exception as e:
            logger.warning(f"⚠️ Tool usage storage warning: {e}")
    
    async def get_user_preferences(self, user_id: str) -> dict:
        """Get user preferences from memory"""
        
        if not self.memory_enabled or not self.mem0_api_key:
            return {}
        
        try:
            # Search for preference memories
            preferences = await self._mem0_search_request(
                user_id=user_id,
                query="preferences programming language framework style",
                filters={"type": "user_preference"},
                limit=20
            )
            
            # Process preferences
            processed_preferences = {}
            for pref in preferences:
                metadata = pref.get('metadata', {})
                pref_type = metadata.get('preference_type')
                pref_value = metadata.get('preference_value')
                
                if pref_type and pref_value:
                    if pref_type not in processed_preferences:
                        processed_preferences[pref_type] = []
                    processed_preferences[pref_type].append(pref_value)
            
            return processed_preferences
            
        except Exception as e:
            logger.error(f"❌ Error getting user preferences: {e}")
            return {}
    
    async def get_project_context(self, user_id: str, project_name: str) -> dict:
        """Get project-specific context"""
        
        try:
            project_memories = await self._mem0_search_request(
                user_id=user_id,
                query=f"project {project_name}",
                filters={"type": "project_context"},
                limit=15
            )
            
            return {
                'project_memories': project_memories,
                'project_name': project_name,
                'memory_count': len(project_memories)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting project context: {e}")
            return {'project_memories': [], 'memory_count': 0}
    
    def get_memory_stats(self) -> dict:
        """Get memory usage statistics"""
        
        local_stats = {
            'conversations': len(self.local_memory),
            'total_interactions': sum(len(conv.get('interactions', [])) 
                                   for conv in self.local_memory.values()),
            'memory_enabled': self.memory_enabled,
            'rag_enabled': self.rag_enabled,
            'context_window': self.context_window
        }
        
        return local_stats
    
    def clear_local_memory(self, conversation_id: str = None):
        """Clear local memory cache"""
        
        if conversation_id:
            if conversation_id in self.local_memory:
                del self.local_memory[conversation_id]
                logger.info(f"🧠 Cleared local memory for conversation: {conversation_id}")
        else:
            self.local_memory.clear()
            logger.info("🧠 Cleared all local memory cache")