import React, { useState, useEffect } from 'react';
import { Socket } from 'socket.io-client';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { 
  Search, 
  Package, 
  Download, 
  CheckCircle, 
  ExternalLink, 
  Github,
  Star,
  Zap,
  Settings,
  RefreshCw,
  AlertCircle
} from 'lucide-react';

interface ConnectionStatus {
  connected: boolean;
  user_id?: string;
  message?: string;
}

interface MCPMarketplaceProps {
  socket: Socket | null;
  connectionStatus: ConnectionStatus;
}

interface MCPServer {
  id: string;
  name: string;
  description: string;
  url: string;
  capabilities: string[];
  installation_method: string;
  status: 'available' | 'installing' | 'installed' | 'error';
  github_repo?: string;
  stars?: number;
  language?: string;
  confidence?: number;
  source: string;
}

interface SearchResult {
  query: string;
  results: MCPServer[];
  total_found: number;
}

const MCPMarketplace: React.FC<MCPMarketplaceProps> = ({ socket, connectionStatus }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult | null>(null);
  const [installedMCPs, setInstalledMCPs] = useState<MCPServer[]>([]);
  const [availableMCPs, setAvailableMCPs] = useState<MCPServer[]>([]);
  const [activeTab, setActiveTab] = useState('discover');
  const [isSearching, setIsSearching] = useState(false);
  const [installProgress, setInstallProgress] = useState<{ [key: string]: number }>({});

  useEffect(() => {
    if (!socket) return;

    // Listen for MCP-related events
    socket.on('mcp_search_results', (data) => {
      console.log('MCP search results:', data);
      setSearchResults(data);
      setIsSearching(false);
    });

    socket.on('mcp_installation_progress', (data) => {
      setInstallProgress(prev => ({ ...prev, [data.mcp_id]: data.progress }));
    });

    socket.on('mcp_installation_complete', (data) => {
      if (data.success) {
        // Move from available to installed
        setAvailableMCPs(prev => 
          prev.map(mcp => 
            mcp.id === data.mcp_id 
              ? { ...mcp, status: 'installed' }
              : mcp
          )
        );
        fetchInstalledMCPs();
      } else {
        setAvailableMCPs(prev => 
          prev.map(mcp => 
            mcp.id === data.mcp_id 
              ? { ...mcp, status: 'error' }
              : mcp
          )
        );
      }
      setInstallProgress(prev => {
        const newProgress = { ...prev };
        delete newProgress[data.mcp_id];
        return newProgress;
      });
    });

    return () => {
      socket.off('mcp_search_results');
      socket.off('mcp_installation_progress');
      socket.off('mcp_installation_complete');
    };
  }, [socket]);

  useEffect(() => {
    // Fetch initial data
    fetchInstalledMCPs();
    fetchAvailableMCPs();
  }, []);

  const fetchInstalledMCPs = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}/api/mcp/installed`);
      if (response.ok) {
        const data = await response.json();
        setInstalledMCPs(data.installed_mcps || []);
      }
    } catch (error) {
      console.error('Error fetching installed MCPs:', error);
    }
  };

  const fetchAvailableMCPs = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}/api/mcp/available`);
      if (response.ok) {
        const data = await response.json();
        setAvailableMCPs(data.available_mcps || []);
      } else {
        // Mock data if API not available
        setAvailableMCPs([
          {
            id: 'github-mcp',
            name: 'GitHub MCP',
            description: 'GitHub repository management and code analysis',
            url: 'https://github.com/modelcontextprotocol/servers/tree/main/src/github',
            capabilities: ['github_api', 'repo_management', 'code_analysis'],
            installation_method: 'npm',
            status: 'available',
            github_repo: 'modelcontextprotocol/servers',
            stars: 1250,
            language: 'TypeScript',
            source: 'official'
          },
          {
            id: 'docker-mcp',
            name: 'Docker MCP',
            description: 'Docker container management and operations',
            url: 'https://github.com/modelcontextprotocol/servers/tree/main/src/docker',
            capabilities: ['docker_api', 'container_management', 'image_operations'],
            installation_method: 'npm',
            status: 'available',
            github_repo: 'modelcontextprotocol/servers',
            stars: 1250,
            language: 'TypeScript',
            source: 'official'
          },
          {
            id: 'browser-mcp',
            name: 'Browser MCP',
            description: 'Web browsing and automation capabilities',
            url: 'https://github.com/modelcontextprotocol/servers/tree/main/src/puppeteer',
            capabilities: ['web_browsing', 'automation', 'data_extraction'],
            installation_method: 'npm',
            status: 'available',
            github_repo: 'modelcontextprotocol/servers',
            stars: 1250,
            language: 'TypeScript',
            source: 'official'
          },
          {
            id: 'filesystem-mcp',
            name: 'Filesystem MCP',
            description: 'File system operations and management',
            url: 'https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem',
            capabilities: ['file_operations', 'directory_management', 'file_search'],
            installation_method: 'npm',
            status: 'available',
            github_repo: 'modelcontextprotocol/servers',
            stars: 1250,
            language: 'TypeScript',
            source: 'official'
          }
        ]);
      }
    } catch (error) {
      console.error('Error fetching available MCPs:', error);
    }
  };

  const searchMCPs = () => {
    if (!searchQuery.trim() || !socket) return;

    setIsSearching(true);
    socket.emit('search_mcp_marketplace', {
      query: searchQuery,
      user_id: connectionStatus.user_id
    });
  };

  const installMCP = (mcp: MCPServer) => {
    if (!socket) return;

    // Update status to installing
    setAvailableMCPs(prev => 
      prev.map(item => 
        item.id === mcp.id 
          ? { ...item, status: 'installing' }
          : item
      )
    );

    // Start installation
    socket.emit('install_mcp_server', {
      mcp_data: mcp,
      user_id: connectionStatus.user_id
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'installed':
        return 'bg-green-500';
      case 'installing':
        return 'bg-blue-500';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getSourceBadgeColor = (source: string) => {
    switch (source) {
      case 'official':
        return 'bg-blue-500 text-white';
      case 'github':
        return 'bg-gray-700 text-white';
      case 'community':
        return 'bg-green-500 text-white';
      default:
        return 'bg-gray-500 text-white';
    }
  };

  const MCPCard: React.FC<{ mcp: MCPServer; showInstallButton?: boolean }> = ({ 
    mcp, 
    showInstallButton = false 
  }) => (
    <Card className="sanctuary-card">
      <CardContent className="p-6">
        <div className="space-y-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-2">
                <Package className="w-5 h-5 text-muted-foreground" />
                <h3 className="font-semibold">{mcp.name}</h3>
                <Badge 
                  variant="secondary" 
                  className={`text-xs ${getStatusColor(mcp.status)} text-white`}
                >
                  {mcp.status}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground mb-3">{mcp.description}</p>
            </div>
          </div>

          <div className="flex flex-wrap gap-1 mb-3">
            {mcp.capabilities.map((capability, index) => (
              <Badge key={index} variant="outline" className="text-xs">
                {capability.replace('_', ' ')}
              </Badge>
            ))}
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4 text-xs text-muted-foreground">
              <Badge className={getSourceBadgeColor(mcp.source)}>
                {mcp.source}
              </Badge>
              {mcp.github_repo && (
                <div className="flex items-center space-x-1">
                  <Github className="w-3 h-3" />
                  <span>{mcp.github_repo}</span>
                </div>
              )}
              {mcp.stars && (
                <div className="flex items-center space-x-1">
                  <Star className="w-3 h-3" />
                  <span>{mcp.stars}</span>
                </div>
              )}
              {mcp.language && (
                <span>{mcp.language}</span>
              )}
            </div>

            <div className="flex items-center space-x-2">
              {mcp.url && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => window.open(mcp.url, '_blank')}
                >
                  <ExternalLink className="w-3 h-3" />
                </Button>
              )}
              {showInstallButton && mcp.status === 'available' && (
                <Button
                  size="sm"
                  onClick={() => installMCP(mcp)}
                  className="text-xs"
                >
                  <Download className="w-3 h-3 mr-1" />
                  Install
                </Button>
              )}
              {mcp.status === 'installing' && mcp.id in installProgress && (
                <div className="flex items-center space-x-2">
                  <Progress value={installProgress[mcp.id]} className="w-16 h-2" />
                  <span className="text-xs">{installProgress[mcp.id]}%</span>
                </div>
              )}
              {mcp.status === 'installed' && (
                <div className="flex items-center space-x-1 text-green-600">
                  <CheckCircle className="w-4 h-4" />
                  <span className="text-xs">Installed</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="sanctuary-card">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <div className="text-2xl">🔌</div>
            <div>
              <span className="text-xl">MCP Marketplace</span>
              <p className="text-sm text-muted-foreground font-normal">
                Discover and install Model Context Protocol servers to empower Mama Bear
              </p>
            </div>
          </CardTitle>
        </CardHeader>
      </Card>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4 lg:w-[500px]">
          <TabsTrigger value="discover">Discover</TabsTrigger>
          <TabsTrigger value="installed">
            Installed ({installedMCPs.length})
          </TabsTrigger>
          <TabsTrigger value="available">Available</TabsTrigger>
          <TabsTrigger value="search">Search</TabsTrigger>
        </TabsList>

        {/* Discover Tab */}
        <TabsContent value="discover">
          <div className="space-y-6">
            <Card className="sanctuary-card border-mama-bear/20">
              <CardContent className="p-6">
                <div className="flex items-start space-x-4">
                  <div className="text-3xl">🐻</div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-mama-bear mb-2">
                      Empower Mama Bear with New Capabilities
                    </h3>
                    <p className="text-sm text-muted-foreground mb-4">
                      MCP servers extend Mama Bear's abilities by connecting her to external tools and services. 
                      Each server adds new capabilities like GitHub integration, Docker management, or web browsing.
                    </p>
                    <div className="flex space-x-2">
                      <Button 
                        size="sm" 
                        onClick={() => setActiveTab('available')}
                        className="mama-bear-gradient text-white"
                      >
                        <Package className="w-3 h-3 mr-1" />
                        Browse Available Tools
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => setActiveTab('search')}
                      >
                        <Search className="w-3 h-3 mr-1" />
                        Search Marketplace
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Quick Install Recommendations */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Recommended for Getting Started</h3>
              <div className="grid gap-4 md:grid-cols-2">
                {availableMCPs.slice(0, 4).map((mcp) => (
                  <MCPCard key={mcp.id} mcp={mcp} showInstallButton={true} />
                ))}
              </div>
            </div>
          </div>
        </TabsContent>

        {/* Installed Tab */}
        <TabsContent value="installed">
          <div className="space-y-4">
            {installedMCPs.length > 0 ? (
              <div className="grid gap-4">
                {installedMCPs.map((mcp) => (
                  <MCPCard key={mcp.id} mcp={mcp} />
                ))}
              </div>
            ) : (
              <Card className="sanctuary-card">
                <CardContent className="p-12 text-center">
                  <Package className="w-16 h-16 mx-auto mb-4 text-muted-foreground/50" />
                  <h3 className="text-lg font-medium mb-2">No MCP servers installed yet</h3>
                  <p className="text-muted-foreground mb-4">
                    Install your first MCP server to extend Mama Bear's capabilities
                  </p>
                  <Button onClick={() => setActiveTab('available')}>
                    <Download className="w-4 h-4 mr-2" />
                    Browse Available Servers
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Available Tab */}
        <TabsContent value="available">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Available MCP Servers</h3>
              <Button
                size="sm"
                variant="outline"
                onClick={fetchAvailableMCPs}
              >
                <RefreshCw className="w-3 h-3 mr-1" />
                Refresh
              </Button>
            </div>
            
            <div className="grid gap-4">
              {availableMCPs.map((mcp) => (
                <MCPCard key={mcp.id} mcp={mcp} showInstallButton={true} />
              ))}
            </div>
          </div>
        </TabsContent>

        {/* Search Tab */}
        <TabsContent value="search">
          <div className="space-y-6">
            <Card className="sanctuary-card">
              <CardContent className="p-6">
                <div className="flex space-x-2">
                  <div className="flex-1">
                    <Input
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="Search for MCP servers... e.g., 'github', 'docker', 'slack'"
                      onKeyPress={(e) => e.key === 'Enter' && searchMCPs()}
                      disabled={isSearching}
                    />
                  </div>
                  <Button
                    onClick={searchMCPs}
                    disabled={!searchQuery.trim() || isSearching}
                  >
                    {isSearching ? (
                      <Settings className="w-4 h-4 animate-spin" />
                    ) : (
                      <Search className="w-4 h-4" />
                    )}
                  </Button>
                </div>
                
                {isSearching && (
                  <div className="mt-4 text-center text-sm text-muted-foreground">
                    🔍 Searching GitHub and MCP ecosystem for "{searchQuery}"...
                  </div>
                )}
              </CardContent>
            </Card>

            {searchResults && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold">
                    Search Results for "{searchResults.query}"
                  </h3>
                  <Badge variant="secondary">
                    {searchResults.total_found} found
                  </Badge>
                </div>
                
                {searchResults.results.length > 0 ? (
                  <div className="grid gap-4">
                    {searchResults.results.map((mcp) => (
                      <MCPCard key={mcp.id} mcp={mcp} showInstallButton={true} />
                    ))}
                  </div>
                ) : (
                  <Card className="sanctuary-card">
                    <CardContent className="p-8 text-center">
                      <AlertCircle className="w-12 h-12 mx-auto mb-4 text-muted-foreground/50" />
                      <h3 className="font-medium mb-2">No results found</h3>
                      <p className="text-sm text-muted-foreground">
                        Try searching with different keywords or browse available servers
                      </p>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default MCPMarketplace;