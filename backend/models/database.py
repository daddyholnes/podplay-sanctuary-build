"""
Database models and operations for Podplay Sanctuary
SQLite-based data storage with potential PostgreSQL migration
"""

import os
import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import json

logger = logging.getLogger(__name__)

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'sanctuary.db')

def init_database():
    """Initialize database tables"""
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                agent_type TEXT NOT NULL,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                model_used TEXT,
                tokens_used INTEGER,
                attachments TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        ''')
        
        # Projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                type TEXT,
                language TEXT,
                framework TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                config TEXT,
                file_structure TEXT
            )
        ''')
        
        # Workspaces table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workspaces (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                access_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                config TEXT,
                resources TEXT
            )
        ''')
        
        # MCP servers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mcp_servers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                url TEXT,
                capabilities TEXT,
                installation_method TEXT,
                status TEXT DEFAULT 'available',
                installed_at TIMESTAMP,
                config TEXT
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT PRIMARY KEY,
                preferences TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Agent sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                agent_type TEXT NOT NULL,
                session_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Usage analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                agent_type TEXT,
                action_type TEXT,
                model_used TEXT,
                tokens_used INTEGER,
                execution_time REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Database initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        raise

class ConversationManager:
    """Manage conversation history and context"""
    
    @staticmethod
    def create_conversation(user_id: str, agent_type: str, title: str = None) -> str:
        """Create a new conversation"""
        
        conversation_id = f"conv_{user_id}_{agent_type}_{int(datetime.now().timestamp())}"
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO conversations (id, user_id, agent_type, title, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (conversation_id, user_id, agent_type, title, json.dumps({})))
            
            conn.commit()
            conn.close()
            
            logger.info(f"📝 Created conversation: {conversation_id}")
            return conversation_id
            
        except Exception as e:
            logger.error(f"❌ Error creating conversation: {e}")
            raise
    
    @staticmethod
    def add_message(conversation_id: str, role: str, content: str, model_used: str = None, 
                   tokens_used: int = None, attachments: List[dict] = None) -> int:
        """Add message to conversation"""
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO messages (conversation_id, role, content, model_used, tokens_used, attachments)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (conversation_id, role, content, model_used, tokens_used, 
                  json.dumps(attachments) if attachments else None))
            
            message_id = cursor.lastrowid
            
            # Update conversation timestamp
            cursor.execute('''
                UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?
            ''', (conversation_id,))
            
            conn.commit()
            conn.close()
            
            return message_id
            
        except Exception as e:
            logger.error(f"❌ Error adding message: {e}")
            raise
    
    @staticmethod
    def get_conversation_history(conversation_id: str, limit: int = 50) -> List[dict]:
        """Get conversation message history"""
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT role, content, timestamp, model_used, tokens_used, attachments
                FROM messages
                WHERE conversation_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (conversation_id, limit))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'role': row[0],
                    'content': row[1],
                    'timestamp': row[2],
                    'model_used': row[3],
                    'tokens_used': row[4],
                    'attachments': json.loads(row[5]) if row[5] else None
                })
            
            conn.close()
            
            # Reverse to get chronological order
            return list(reversed(messages))
            
        except Exception as e:
            logger.error(f"❌ Error getting conversation history: {e}")
            return []
    
    @staticmethod
    def get_user_conversations(user_id: str, agent_type: str = None) -> List[dict]:
        """Get user's conversations"""
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            if agent_type:
                cursor.execute('''
                    SELECT id, agent_type, title, created_at, updated_at
                    FROM conversations
                    WHERE user_id = ? AND agent_type = ?
                    ORDER BY updated_at DESC
                ''', (user_id, agent_type))
            else:
                cursor.execute('''
                    SELECT id, agent_type, title, created_at, updated_at
                    FROM conversations
                    WHERE user_id = ?
                    ORDER BY updated_at DESC
                ''', (user_id,))
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append({
                    'id': row[0],
                    'agent_type': row[1],
                    'title': row[2],
                    'created_at': row[3],
                    'updated_at': row[4]
                })
            
            conn.close()
            return conversations
            
        except Exception as e:
            logger.error(f"❌ Error getting user conversations: {e}")
            return []

class ProjectManager:
    """Manage development projects"""
    
    @staticmethod
    def create_project(name: str, description: str, project_type: str, 
                      language: str, framework: str, config: dict = None) -> str:
        """Create a new project"""
        
        project_id = f"proj_{int(datetime.now().timestamp())}"
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO projects (id, name, description, type, language, framework, config)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (project_id, name, description, project_type, language, framework,
                  json.dumps(config) if config else None))
            
            conn.commit()
            conn.close()
            
            logger.info(f"📁 Created project: {project_id}")
            return project_id
            
        except Exception as e:
            logger.error(f"❌ Error creating project: {e}")
            raise
    
    @staticmethod
    def get_project(project_id: str) -> Optional[dict]:
        """Get project details"""
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, description, type, language, framework, status, 
                       created_at, updated_at, config, file_structure
                FROM projects WHERE id = ?
            ''', (project_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'type': row[3],
                    'language': row[4],
                    'framework': row[5],
                    'status': row[6],
                    'created_at': row[7],
                    'updated_at': row[8],
                    'config': json.loads(row[9]) if row[9] else None,
                    'file_structure': json.loads(row[10]) if row[10] else None
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting project: {e}")
            return None
    
    @staticmethod
    def list_projects(status: str = None) -> List[dict]:
        """List all projects"""
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            if status:
                cursor.execute('''
                    SELECT id, name, description, type, language, framework, status, created_at
                    FROM projects WHERE status = ?
                    ORDER BY updated_at DESC
                ''', (status,))
            else:
                cursor.execute('''
                    SELECT id, name, description, type, language, framework, status, created_at
                    FROM projects
                    ORDER BY updated_at DESC
                ''')
            
            projects = []
            for row in cursor.fetchall():
                projects.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'type': row[3],
                    'language': row[4],
                    'framework': row[5],
                    'status': row[6],
                    'created_at': row[7]
                })
            
            conn.close()
            return projects
            
        except Exception as e:
            logger.error(f"❌ Error listing projects: {e}")
            return []

class MCPServerManager:
    """Manage MCP server registry"""
    
    @staticmethod
    def register_mcp_server(name: str, description: str, url: str, 
                          capabilities: List[str], installation_method: str, 
                          config: dict = None) -> str:
        """Register a new MCP server"""
        
        server_id = f"mcp_{name}_{int(datetime.now().timestamp())}"
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO mcp_servers (id, name, description, url, capabilities, 
                                       installation_method, config)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (server_id, name, description, url, json.dumps(capabilities),
                  installation_method, json.dumps(config) if config else None))
            
            conn.commit()
            conn.close()
            
            logger.info(f"🔌 Registered MCP server: {server_id}")
            return server_id
            
        except Exception as e:
            logger.error(f"❌ Error registering MCP server: {e}")
            raise
    
    @staticmethod
    def update_mcp_status(server_id: str, status: str, installed_at: str = None):
        """Update MCP server status"""
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            if installed_at:
                cursor.execute('''
                    UPDATE mcp_servers 
                    SET status = ?, installed_at = ?
                    WHERE id = ?
                ''', (status, installed_at, server_id))
            else:
                cursor.execute('''
                    UPDATE mcp_servers 
                    SET status = ?
                    WHERE id = ?
                ''', (status, server_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error updating MCP status: {e}")
    
    @staticmethod
    def get_installed_mcps() -> List[dict]:
        """Get list of installed MCP servers"""
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, description, url, capabilities, installation_method, installed_at
                FROM mcp_servers 
                WHERE status = 'installed'
                ORDER BY installed_at DESC
            ''')
            
            mcps = []
            for row in cursor.fetchall():
                mcps.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'url': row[3],
                    'capabilities': json.loads(row[4]) if row[4] else [],
                    'installation_method': row[5],
                    'installed_at': row[6]
                })
            
            conn.close()
            return mcps
            
        except Exception as e:
            logger.error(f"❌ Error getting installed MCPs: {e}")
            return []

class AnalyticsManager:
    """Manage usage analytics and metrics"""
    
    @staticmethod
    def track_usage(user_id: str, agent_type: str, action_type: str, 
                   model_used: str = None, tokens_used: int = None, 
                   execution_time: float = None, metadata: dict = None):
        """Track usage analytics"""
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO usage_analytics (user_id, agent_type, action_type, model_used,
                                           tokens_used, execution_time, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, agent_type, action_type, model_used, tokens_used, 
                  execution_time, json.dumps(metadata) if metadata else None))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error tracking usage: {e}")
    
    @staticmethod
    def get_usage_stats(days: int = 7) -> dict:
        """Get usage statistics"""
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Total usage in last N days
            cursor.execute('''
                SELECT COUNT(*), SUM(tokens_used), agent_type, model_used
                FROM usage_analytics
                WHERE timestamp >= datetime('now', '-{} days')
                GROUP BY agent_type, model_used
            '''.format(days))
            
            usage_data = []
            for row in cursor.fetchall():
                usage_data.append({
                    'requests': row[0],
                    'tokens': row[1] or 0,
                    'agent_type': row[2],
                    'model_used': row[3]
                })
            
            conn.close()
            
            return {
                'period_days': days,
                'usage_data': usage_data,
                'total_requests': sum(item['requests'] for item in usage_data),
                'total_tokens': sum(item['tokens'] for item in usage_data)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting usage stats: {e}")
            return {'usage_data': [], 'total_requests': 0, 'total_tokens': 0}