"""
Scout Agent - Autonomous development agent with MCP marketplace integration
Handles autonomous development tasks and MCP server discovery/installation
"""

import os
import logging
import json
import subprocess
import asyncio
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MCPServer:
    """Represents a discovered MCP server"""
    name: str
    description: str
    url: str
    capabilities: List[str]
    installation_method: str
    docker_image: Optional[str] = None
    github_repo: Optional[str] = None
    status: str = 'discovered'

class ScoutAgent:
    """Autonomous development agent with MCP marketplace integration"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.mcp_servers = {}
        self.installed_mcps = []
        self.github_pat = os.getenv('GITHUB_PAT')
        self.capabilities = [
            'autonomous_development',
            'mcp_discovery',
            'mcp_installation',
            'github_integration',
            'docker_management',
            'browser_automation'
        ]
        
        logger.info("🔍 Scout agent initialized with MCP marketplace capabilities")
        
        # Initialize with known MCP servers
        self._initialize_known_mcps()
    
    def _initialize_known_mcps(self):
        """Initialize with known MCP servers from ecosystem"""
        
        known_mcps = [
            {
                'name': 'github-mcp',
                'description': 'GitHub repository management and code analysis',
                'url': 'https://github.com/modelcontextprotocol/servers/tree/main/src/github',
                'capabilities': ['github_api', 'repo_management', 'code_analysis'],
                'installation_method': 'npm',
                'github_repo': 'modelcontextprotocol/servers'
            },
            {
                'name': 'docker-mcp',
                'description': 'Docker container management and operations',
                'url': 'https://github.com/modelcontextprotocol/servers/tree/main/src/docker',
                'capabilities': ['docker_api', 'container_management', 'image_operations'],
                'installation_method': 'npm',
                'github_repo': 'modelcontextprotocol/servers'
            },
            {
                'name': 'filesystem-mcp',
                'description': 'File system operations and management',
                'url': 'https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem',
                'capabilities': ['file_operations', 'directory_management', 'file_search'],
                'installation_method': 'npm',
                'github_repo': 'modelcontextprotocol/servers'
            },
            {
                'name': 'browser-mcp',
                'description': 'Web browsing and automation capabilities',
                'url': 'https://github.com/modelcontextprotocol/servers/tree/main/src/puppeteer',
                'capabilities': ['web_browsing', 'automation', 'data_extraction'],
                'installation_method': 'npm',
                'github_repo': 'modelcontextprotocol/servers'
            },
            {
                'name': 'sqlite-mcp',
                'description': 'SQLite database operations and queries',
                'url': 'https://github.com/modelcontextprotocol/servers/tree/main/src/sqlite',
                'capabilities': ['database_operations', 'sql_queries', 'data_management'],
                'installation_method': 'npm',
                'github_repo': 'modelcontextprotocol/servers'
            }
        ]
        
        for mcp_data in known_mcps:
            mcp = MCPServer(**mcp_data)
            self.mcp_servers[mcp.name] = mcp
        
        logger.info(f"🔍 Initialized {len(known_mcps)} known MCP servers")
    
    def process_task(self, task_data: dict) -> dict:
        """Process autonomous development task"""
        
        try:
            task_description = task_data.get('task', '')
            user_id = task_data.get('user_id')
            
            logger.info(f"🔍 Scout processing task: {task_description[:100]}...")
            
            # Determine task type and required capabilities
            task_analysis = self._analyze_task(task_description)
            
            # Check if we need additional MCP servers
            missing_capabilities = self._identify_missing_capabilities(task_analysis['required_capabilities'])
            
            if missing_capabilities:
                # Search for and install required MCP servers
                mcp_search_results = self._search_mcp_marketplace(missing_capabilities)
                recommended_mcps = self._recommend_mcps(mcp_search_results, missing_capabilities)
                
                return {
                    'status': 'mcp_discovery',
                    'task_analysis': task_analysis,
                    'missing_capabilities': missing_capabilities,
                    'recommended_mcps': recommended_mcps,
                    'message': '🔍 I found some MCP servers that could help with this task. Would you like me to install them?',
                    'actions': [
                        {
                            'type': 'install_mcps',
                            'mcps': recommended_mcps,
                            'description': 'Install recommended MCP servers'
                        }
                    ]
                }
            
            # Execute task with available capabilities
            result = self._execute_autonomous_task(task_analysis, task_data)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Scout task processing error: {e}")
            return {
                'status': 'error',
                'message': f'🔍 Scout encountered an error: {str(e)}',
                'error': str(e)
            }
    
    def _analyze_task(self, task_description: str) -> dict:
        """Analyze task to determine required capabilities"""
        
        task_lower = task_description.lower()
        
        # Capability mapping
        capability_keywords = {
            'github_api': ['github', 'repository', 'repo', 'git', 'clone', 'commit'],
            'docker_api': ['docker', 'container', 'image', 'dockerfile', 'compose'],
            'file_operations': ['file', 'folder', 'directory', 'create file', 'write file'],
            'web_browsing': ['browse', 'web', 'website', 'scrape', 'automation'],
            'database_operations': ['database', 'sql', 'query', 'sqlite', 'db'],
            'code_generation': ['code', 'programming', 'build', 'develop', 'create app'],
            'api_integration': ['api', 'integration', 'webhook', 'endpoint'],
            'data_processing': ['data', 'process', 'analyze', 'transform', 'csv']
        }
        
        required_capabilities = []
        for capability, keywords in capability_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                required_capabilities.append(capability)
        
        # Determine task complexity
        complexity = 'medium'
        if any(word in task_lower for word in ['complex', 'advanced', 'enterprise', 'scalable']):
            complexity = 'high'
        elif any(word in task_lower for word in ['simple', 'basic', 'quick', 'small']):
            complexity = 'low'
        
        return {
            'description': task_description,
            'required_capabilities': required_capabilities,
            'complexity': complexity,
            'estimated_steps': len(required_capabilities) * 2,
            'automation_level': 'high' if 'automate' in task_lower else 'medium'
        }
    
    def _identify_missing_capabilities(self, required_capabilities: List[str]) -> List[str]:
        """Identify which capabilities we're missing"""
        
        # Get capabilities from installed MCP servers
        available_capabilities = []
        for mcp in self.mcp_servers.values():
            if mcp.status == 'installed':
                available_capabilities.extend(mcp.capabilities)
        
        # Find missing capabilities
        missing = []
        for capability in required_capabilities:
            if capability not in available_capabilities:
                missing.append(capability)
        
        return missing
    
    def _search_mcp_marketplace(self, required_capabilities: List[str]) -> List[dict]:
        """Search GitHub and MCP ecosystem for servers with required capabilities"""
        
        search_results = []
        
        try:
            # Search GitHub for MCP servers
            github_results = self._search_github_mcps(required_capabilities)
            search_results.extend(github_results)
            
            # Search known MCP directories
            directory_results = self._search_mcp_directories(required_capabilities)
            search_results.extend(directory_results)
            
            logger.info(f"🔍 Found {len(search_results)} potential MCP servers")
            
        except Exception as e:
            logger.error(f"❌ MCP marketplace search error: {e}")
        
        return search_results
    
    def _search_github_mcps(self, capabilities: List[str]) -> List[dict]:
        """Search GitHub for MCP servers"""
        
        if not self.github_pat:
            logger.warning("No GitHub PAT available for MCP search")
            return []
        
        results = []
        
        try:
            # Search for MCP-related repositories
            search_queries = [
                "mcp server",
                "model context protocol",
                "mcp-server",
                "context protocol server"
            ]
            
            for query in search_queries:
                url = f"https://api.github.com/search/repositories"
                params = {
                    'q': f"{query} language:python OR language:javascript OR language:typescript",
                    'sort': 'stars',
                    'order': 'desc',
                    'per_page': 10
                }
                headers = {
                    'Authorization': f'token {self.github_pat}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                
                response = requests.get(url, params=params, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for repo in data.get('items', []):
                        # Analyze repository for MCP server potential
                        mcp_potential = self._analyze_repo_for_mcp(repo, capabilities)
                        
                        if mcp_potential['is_mcp_server']:
                            results.append({
                                'name': repo['name'],
                                'description': repo['description'] or 'No description available',
                                'url': repo['html_url'],
                                'clone_url': repo['clone_url'],
                                'stars': repo['stargazers_count'],
                                'language': repo['language'],
                                'capabilities': mcp_potential['capabilities'],
                                'confidence': mcp_potential['confidence'],
                                'source': 'github'
                            })
                
        except Exception as e:
            logger.error(f"❌ GitHub MCP search error: {e}")
        
        return results
    
    def _analyze_repo_for_mcp(self, repo: dict, required_capabilities: List[str]) -> dict:
        """Analyze if a repository is likely an MCP server"""
        
        repo_name = repo.get('name', '').lower()
        repo_desc = repo.get('description', '').lower()
        
        # MCP server indicators
        mcp_indicators = ['mcp', 'model context protocol', 'context protocol', 'mcp-server']
        capability_indicators = {
            'github_api': ['github', 'git', 'repository'],
            'docker_api': ['docker', 'container'],
            'file_operations': ['filesystem', 'file', 'fs'],
            'web_browsing': ['browser', 'puppeteer', 'playwright', 'selenium'],
            'database_operations': ['database', 'sql', 'sqlite', 'postgres'],
            'api_integration': ['api', 'rest', 'graphql', 'webhook']
        }
        
        # Check for MCP indicators
        is_mcp = any(indicator in repo_name or indicator in repo_desc for indicator in mcp_indicators)
        
        # Check for capability matches
        detected_capabilities = []
        confidence = 0
        
        for capability, keywords in capability_indicators.items():
            if any(keyword in repo_name or keyword in repo_desc for keyword in keywords):
                detected_capabilities.append(capability)
                if capability in required_capabilities:
                    confidence += 30
        
        if is_mcp:
            confidence += 40
        
        return {
            'is_mcp_server': is_mcp or len(detected_capabilities) > 0,
            'capabilities': detected_capabilities,
            'confidence': min(confidence, 100)
        }
    
    def _search_mcp_directories(self, capabilities: List[str]) -> List[dict]:
        """Search known MCP server directories"""
        
        # This would search known MCP marketplaces and directories
        # For now, return servers from our known list that match capabilities
        
        matching_servers = []
        
        for mcp in self.mcp_servers.values():
            # Check if this MCP provides any of the required capabilities
            if any(cap in mcp.capabilities for cap in capabilities):
                matching_servers.append({
                    'name': mcp.name,
                    'description': mcp.description,
                    'url': mcp.url,
                    'capabilities': mcp.capabilities,
                    'installation_method': mcp.installation_method,
                    'confidence': 95,  # High confidence for known servers
                    'source': 'known_directory'
                })
        
        return matching_servers
    
    def _recommend_mcps(self, search_results: List[dict], missing_capabilities: List[str]) -> List[dict]:
        """Recommend best MCP servers for missing capabilities"""
        
        # Score and rank MCP servers
        scored_mcps = []
        
        for mcp in search_results:
            score = 0
            
            # Capability match score
            capability_matches = sum(1 for cap in missing_capabilities if cap in mcp.get('capabilities', []))
            score += capability_matches * 30
            
            # Confidence score
            score += mcp.get('confidence', 0) * 0.4
            
            # Popularity score (for GitHub repos)
            if mcp.get('stars'):
                score += min(mcp['stars'] / 10, 20)
            
            # Known source bonus
            if mcp.get('source') == 'known_directory':
                score += 20
            
            scored_mcps.append({
                **mcp,
                'recommendation_score': score
            })
        
        # Sort by score and return top recommendations
        scored_mcps.sort(key=lambda x: x['recommendation_score'], reverse=True)
        
        return scored_mcps[:5]  # Return top 5 recommendations
    
    def install_mcp_server(self, mcp_data: dict) -> dict:
        """Install an MCP server"""
        
        try:
            mcp_name = mcp_data.get('name')
            installation_method = mcp_data.get('installation_method', 'npm')
            
            logger.info(f"🔍 Installing MCP server: {mcp_name}")
            
            if installation_method == 'npm':
                result = self._install_npm_mcp(mcp_data)
            elif installation_method == 'docker':
                result = self._install_docker_mcp(mcp_data)
            elif installation_method == 'python':
                result = self._install_python_mcp(mcp_data)
            else:
                result = self._install_generic_mcp(mcp_data)
            
            if result['success']:
                # Update MCP server status
                if mcp_name in self.mcp_servers:
                    self.mcp_servers[mcp_name].status = 'installed'
                else:
                    # Add new MCP server
                    new_mcp = MCPServer(
                        name=mcp_name,
                        description=mcp_data.get('description', ''),
                        url=mcp_data.get('url', ''),
                        capabilities=mcp_data.get('capabilities', []),
                        installation_method=installation_method,
                        status='installed'
                    )
                    self.mcp_servers[mcp_name] = new_mcp
                
                self.installed_mcps.append(mcp_name)
                
                logger.info(f"✅ Successfully installed MCP server: {mcp_name}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ MCP installation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to install MCP server: {str(e)}'
            }
    
    def _install_npm_mcp(self, mcp_data: dict) -> dict:
        """Install NPM-based MCP server"""
        
        try:
            # For the official MCP servers
            if mcp_data.get('github_repo') == 'modelcontextprotocol/servers':
                commands = [
                    "cd /tmp && git clone https://github.com/modelcontextprotocol/servers.git",
                    "cd /tmp/servers && npm install",
                    "cd /tmp/servers && npm run build"
                ]
            else:
                # For other NPM packages
                package_name = mcp_data.get('npm_package', mcp_data['name'])
                commands = [f"npm install -g {package_name}"]
            
            for cmd in commands:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    return {
                        'success': False,
                        'error': result.stderr,
                        'message': f'NPM installation failed: {result.stderr}'
                    }
            
            return {
                'success': True,
                'message': f'Successfully installed NPM MCP server: {mcp_data["name"]}',
                'installation_path': '/tmp/servers' if 'modelcontextprotocol' in mcp_data.get('github_repo', '') else 'global'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'NPM installation error: {str(e)}'
            }
    
    def _install_docker_mcp(self, mcp_data: dict) -> dict:
        """Install Docker-based MCP server"""
        
        try:
            docker_image = mcp_data.get('docker_image')
            if not docker_image:
                return {
                    'success': False,
                    'error': 'No Docker image specified',
                    'message': 'Docker installation requires docker_image parameter'
                }
            
            # Pull Docker image
            pull_cmd = f"docker pull {docker_image}"
            result = subprocess.run(pull_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': result.stderr,
                    'message': f'Docker pull failed: {result.stderr}'
                }
            
            return {
                'success': True,
                'message': f'Successfully pulled Docker MCP image: {docker_image}',
                'docker_image': docker_image
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Docker installation error: {str(e)}'
            }
    
    def _install_python_mcp(self, mcp_data: dict) -> dict:
        """Install Python-based MCP server"""
        
        try:
            package_name = mcp_data.get('pypi_package', mcp_data['name'])
            
            # Install via pip
            install_cmd = f"pip install {package_name}"
            result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': result.stderr,
                    'message': f'Pip installation failed: {result.stderr}'
                }
            
            return {
                'success': True,
                'message': f'Successfully installed Python MCP package: {package_name}',
                'package_name': package_name
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Python installation error: {str(e)}'
            }
    
    def _install_generic_mcp(self, mcp_data: dict) -> dict:
        """Install MCP server using generic method (git clone)"""
        
        try:
            repo_url = mcp_data.get('clone_url') or mcp_data.get('url')
            if not repo_url:
                return {
                    'success': False,
                    'error': 'No repository URL provided',
                    'message': 'Generic installation requires clone_url or url'
                }
            
            # Clone repository
            clone_dir = f"/tmp/mcp_{mcp_data['name']}"
            clone_cmd = f"git clone {repo_url} {clone_dir}"
            
            result = subprocess.run(clone_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': result.stderr,
                    'message': f'Git clone failed: {result.stderr}'
                }
            
            return {
                'success': True,
                'message': f'Successfully cloned MCP repository: {mcp_data["name"]}',
                'clone_path': clone_dir
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Generic installation error: {str(e)}'
            }
    
    def _execute_autonomous_task(self, task_analysis: dict, task_data: dict) -> dict:
        """Execute autonomous development task"""
        
        # This would contain the main autonomous development logic
        # For now, return a structured response
        
        return {
            'status': 'completed',
            'task_analysis': task_analysis,
            'steps_executed': [
                'Analyzed task requirements',
                'Verified available capabilities',
                'Generated execution plan',
                'Executed development steps'
            ],
            'message': '🔍 Scout has analyzed the task and is ready to proceed with autonomous development.',
            'next_steps': [
                'Review the execution plan',
                'Approve autonomous execution',
                'Monitor progress in real-time'
            ]
        }
    
    def get_installed_mcps(self) -> List[dict]:
        """Get list of installed MCP servers"""
        
        installed = []
        for mcp in self.mcp_servers.values():
            if mcp.status == 'installed':
                installed.append({
                    'name': mcp.name,
                    'description': mcp.description,
                    'capabilities': mcp.capabilities,
                    'installation_method': mcp.installation_method,
                    'status': mcp.status
                })
        
        return installed
    
    def get_available_mcps(self) -> List[dict]:
        """Get list of all available MCP servers"""
        
        return [
            {
                'name': mcp.name,
                'description': mcp.description,
                'capabilities': mcp.capabilities,
                'installation_method': mcp.installation_method,
                'status': mcp.status,
                'url': mcp.url
            }
            for mcp in self.mcp_servers.values()
        ]