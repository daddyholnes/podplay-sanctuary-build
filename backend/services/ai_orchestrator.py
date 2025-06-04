"""
AI Orchestrator - Central coordination for multiple AI models and agents
Handles model routing, fallback strategies, and multi-provider integration
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import openai
import google.generativeai as genai
from anthropic import Anthropic
import requests

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for an AI model"""
    name: str
    provider: str
    endpoint: str
    capabilities: List[str]
    cost_per_1k_tokens: float
    rate_limit: str
    best_for: List[str]
    quota_limit: int = 1000000
    current_usage: int = 0

class AIOrchestrator:
    """Central coordination for multiple AI models and agents"""
    
    def __init__(self):
        self.models = self._initialize_models()
        self.usage_tracker = {}
        self.fallback_chain = ['gemini-2.5-pro', 'claude-3.5-sonnet', 'gpt-4o']
        
        # Initialize API clients
        self._initialize_clients()
    
    def _initialize_models(self) -> Dict[str, ModelConfig]:
        """Initialize available AI models configuration"""
        return {
            'gemini-2.5-pro': ModelConfig(
                name='gemini-2.5-pro',
                provider='gemini',
                endpoint='https://generativelanguage.googleapis.com/v1beta/models',
                capabilities=['text', 'image', 'code', 'reasoning'],
                cost_per_1k_tokens=0.002,
                rate_limit='60/minute',
                best_for=['complex_reasoning', 'code_generation', 'multimodal'],
                quota_limit=1000000
            ),
            'gemini-2.5-flash': ModelConfig(
                name='gemini-2.5-flash',
                provider='gemini',
                endpoint='https://generativelanguage.googleapis.com/v1beta/models',
                capabilities=['text', 'code', 'fast_reasoning'],
                cost_per_1k_tokens=0.001,
                rate_limit='1000/minute',
                best_for=['chat', 'quick_tasks', 'code_completion'],
                quota_limit=2000000
            ),
            'claude-3.5-sonnet': ModelConfig(
                name='claude-3.5-sonnet',
                provider='anthropic',
                endpoint='https://api.anthropic.com/v1/messages',
                capabilities=['text', 'reasoning', 'code', 'analysis'],
                cost_per_1k_tokens=0.003,
                rate_limit='50/minute',
                best_for=['analysis', 'writing', 'complex_reasoning'],
                quota_limit=1000000
            ),
            'gpt-4o': ModelConfig(
                name='gpt-4o',
                provider='openai',
                endpoint='https://api.openai.com/v1/chat/completions',
                capabilities=['text', 'image', 'code', 'function_calling'],
                cost_per_1k_tokens=0.005,
                rate_limit='40/minute',
                best_for=['function_calling', 'structured_output'],
                quota_limit=1000000
            )
        }
    
    def _initialize_clients(self):
        """Initialize API clients for different providers"""
        try:
            # Initialize Gemini
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            self.gemini_client = genai.GenerativeModel('gemini-2.0-flash-exp')
            logger.info("✅ Gemini client initialized")
            
            # Initialize Anthropic
            self.anthropic_client = Anthropic(
                api_key=os.getenv('ANTHROPIC_API_KEY')
            )
            logger.info("✅ Anthropic client initialized")
            
            # Initialize OpenAI
            self.openai_client = openai.OpenAI(
                api_key=os.getenv('OPENAI_API_KEY')
            )
            logger.info("✅ OpenAI client initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing AI clients: {e}")
    
    def select_optimal_model(self, task_type: str = 'general', complexity: str = 'medium', agent_preference: str = 'mama_bear') -> ModelConfig:
        """Select optimal model based on task requirements and availability"""
        
        # Define task type preferences
        task_preferences = {
            'code_generation': ['gemini-2.5-pro', 'claude-3.5-sonnet'],
            'chat': ['gemini-2.5-flash', 'claude-3.5-sonnet'],
            'analysis': ['claude-3.5-sonnet', 'gemini-2.5-pro'],
            'multimodal': ['gemini-2.5-pro', 'gpt-4o'],
            'function_calling': ['gpt-4o', 'gemini-2.5-pro'],
            'general': ['gemini-2.5-flash', 'gemini-2.5-pro', 'claude-3.5-sonnet']
        }
        
        preferred_models = task_preferences.get(task_type, task_preferences['general'])
        
        # Filter by availability and quota
        available_models = []
        for model_name in preferred_models:
            model = self.models.get(model_name)
            if model and self._check_quota(model):
                available_models.append(model)
        
        if not available_models:
            # Fallback to any available model
            for model_name in self.fallback_chain:
                model = self.models.get(model_name)
                if model and self._check_quota(model):
                    available_models.append(model)
                    break
        
        if not available_models:
            raise Exception("No available AI models with sufficient quota")
        
        selected_model = available_models[0]
        logger.info(f"🎯 Selected model: {selected_model.name} for task: {task_type}")
        
        return selected_model
    
    def _check_quota(self, model: ModelConfig) -> bool:
        """Check if model has sufficient quota remaining"""
        remaining = model.quota_limit - model.current_usage
        return remaining > 1000  # Require at least 1000 tokens remaining
    
    async def process_request(self, agent_type: str, request_data: dict) -> dict:
        """Route request to appropriate model with optimal selection"""
        
        try:
            # Determine task type from request
            task_type = request_data.get('task_type', 'chat')
            complexity = request_data.get('complexity', 'medium')
            
            # Select optimal model
            model = self.select_optimal_model(task_type, complexity, agent_type)
            
            # Process with selected model
            response = await self._process_with_model(model, request_data)
            
            # Update usage tracking
            self._update_usage(model, response.get('usage', {}))
            
            return {
                'response': response.get('content', ''),
                'model_used': model.name,
                'usage': response.get('usage', {}),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing request: {e}")
            
            # Try fallback models
            for fallback_model_name in self.fallback_chain:
                try:
                    fallback_model = self.models.get(fallback_model_name)
                    if fallback_model and self._check_quota(fallback_model):
                        logger.info(f"🔄 Trying fallback model: {fallback_model_name}")
                        response = await self._process_with_model(fallback_model, request_data)
                        self._update_usage(fallback_model, response.get('usage', {}))
                        
                        return {
                            'response': response.get('content', ''),
                            'model_used': fallback_model.name,
                            'usage': response.get('usage', {}),
                            'fallback': True,
                            'timestamp': datetime.now().isoformat()
                        }
                except Exception as fallback_error:
                    logger.error(f"❌ Fallback model {fallback_model_name} failed: {fallback_error}")
                    continue
            
            # If all models fail, return error
            return {
                'response': 'I apologize, but I\'m experiencing technical difficulties right now. Please try again in a moment.',
                'error': str(e),
                'model_used': 'none',
                'timestamp': datetime.now().isoformat()
            }
    
    async def _process_with_model(self, model: ModelConfig, request_data: dict) -> dict:
        """Process request with specific model"""
        
        content = request_data.get('content', '')
        
        if model.provider == 'gemini':
            return await self._process_with_gemini(content, model)
        elif model.provider == 'anthropic':
            return await self._process_with_anthropic(content, model)
        elif model.provider == 'openai':
            return await self._process_with_openai(content, model)
        else:
            raise Exception(f"Unsupported model provider: {model.provider}")
    
    async def _process_with_gemini(self, content: str, model: ModelConfig) -> dict:
        """Process request with Gemini model"""
        try:
            response = self.gemini_client.generate_content(content)
            
            return {
                'content': response.text,
                'usage': {
                    'prompt_tokens': 0,  # Gemini doesn't provide token counts in free API
                    'completion_tokens': len(response.text.split()),
                    'total_tokens': len(content.split()) + len(response.text.split())
                }
            }
        except Exception as e:
            logger.error(f"❌ Gemini processing error: {e}")
            raise
    
    async def _process_with_anthropic(self, content: str, model: ModelConfig) -> dict:
        """Process request with Anthropic Claude model"""
        try:
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                messages=[{"role": "user", "content": content}]
            )
            
            return {
                'content': message.content[0].text,
                'usage': {
                    'prompt_tokens': message.usage.input_tokens,
                    'completion_tokens': message.usage.output_tokens,
                    'total_tokens': message.usage.input_tokens + message.usage.output_tokens
                }
            }
        except Exception as e:
            logger.error(f"❌ Anthropic processing error: {e}")
            raise
    
    async def _process_with_openai(self, content: str, model: ModelConfig) -> dict:
        """Process request with OpenAI model"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": content}],
                max_tokens=4000
            )
            
            return {
                'content': response.choices[0].message.content,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            }
        except Exception as e:
            logger.error(f"❌ OpenAI processing error: {e}")
            raise
    
    def _update_usage(self, model: ModelConfig, usage: dict):
        """Update model usage tracking"""
        tokens_used = usage.get('total_tokens', 0)
        model.current_usage += tokens_used
        
        # Log usage
        if model.name not in self.usage_tracker:
            self.usage_tracker[model.name] = {
                'total_tokens': 0,
                'requests': 0,
                'last_used': None
            }
        
        self.usage_tracker[model.name]['total_tokens'] += tokens_used
        self.usage_tracker[model.name]['requests'] += 1
        self.usage_tracker[model.name]['last_used'] = datetime.now().isoformat()
        
        logger.info(f"📊 {model.name} usage: {tokens_used} tokens, total: {self.usage_tracker[model.name]['total_tokens']}")
    
    def get_usage_stats(self) -> dict:
        """Get usage statistics for all models"""
        return {
            'models': self.usage_tracker,
            'total_requests': sum(stats['requests'] for stats in self.usage_tracker.values()),
            'total_tokens': sum(stats['total_tokens'] for stats in self.usage_tracker.values()),
            'timestamp': datetime.now().isoformat()
        }