import React, { useState, useEffect } from 'react';
import { io, Socket } from 'socket.io-client';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Heart, Sparkles, Zap, Settings, Snowflake, Monitor, Activity, Layout } from 'lucide-react';
import MamaBearChat from '@/components/mama-bear/MamaBearChat';
import ScoutWorkspace from '@/components/scout/ScoutWorkspace';
import WorkspaceManager from '@/components/workspace/WorkspaceManager';
import MCPMarketplace from '@/components/mcp/MCPMarketplace';
import NixOSEnvironmentManager from '@/components/nixos/NixOSEnvironmentManager';
import CodeServerManager from '@/components/code-server/CodeServerManager';
import EnvironmentOrchestrator from '@/components/orchestrator/EnvironmentOrchestrator';
import AdvancedWorkspace from '@/components/ui/advanced-workspace';
import { GeminiLiveStudio } from '@/components/gemini-live';

interface Agent {
  id: string;
  name: string;
  description: string;
  emoji: string;
  status: 'active' | 'inactive';
  capabilities: string[];
}

interface ConnectionStatus {
  connected: boolean;
  user_id?: string;
  message?: string;
}

function App() {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({ connected: false });
  const [agents, setAgents] = useState<Agent[]>([]);
  const [activeTab, setActiveTab] = useState('mama-bear');
  const [showWelcome, setShowWelcome] = useState(true);

  useEffect(() => {
    // Initialize Socket.IO connection
    const newSocket = io(import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000', {
      transports: ['websocket', 'polling'],
      autoConnect: true
    });

    setSocket(newSocket);

    // Connection event handlers
    newSocket.on('connect', () => {
      console.log('🔌 Connected to Podplay Sanctuary');
      setConnectionStatus({ connected: true });
    });

    newSocket.on('disconnect', () => {
      console.log('🔌 Disconnected from Podplay Sanctuary');
      setConnectionStatus({ connected: false });
    });

    newSocket.on('connection_established', (data) => {
      console.log('🐻 Sanctuary connection established:', data);
      setConnectionStatus({
        connected: true,
        user_id: data.user_id,
        message: data.message
      });
      
      // Hide welcome message after connection
      setTimeout(() => setShowWelcome(false), 3000);
    });

    // Cleanup on unmount
    return () => {
      newSocket.disconnect();
    };
  }, []);

  useEffect(() => {
    // Fetch available agents
    const fetchAgents = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}/api/agents`);
        if (response.ok) {
          const data = await response.json();
          setAgents(data.agents);
        }
      } catch (error) {
        console.error('Error fetching agents:', error);
      }
    };

    fetchAgents();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-500';
      case 'inactive':
        return 'bg-gray-400';
      default:
        return 'bg-yellow-500';
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between px-4">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 sanctuary-gradient rounded-lg flex items-center justify-center">
                <Heart className="w-4 h-4 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-sanctuary to-mama-bear bg-clip-text text-transparent">
                  Podplay Sanctuary
                </h1>
                <p className="text-xs text-muted-foreground">Nathan's AI Development Environment</p>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {/* Connection Status */}
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${connectionStatus.connected ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-sm text-muted-foreground">
                {connectionStatus.connected ? 'Connected' : 'Disconnected'}
              </span>
            </div>

            {/* Agent Status */}
            <div className="hidden md:flex items-center space-x-2">
              {agents.map((agent) => (
                <div key={agent.id} className="flex items-center space-x-1">
                  <span className="text-lg">{agent.emoji}</span>
                  <div className={`w-2 h-2 rounded-full ${getStatusColor(agent.status)}`} />
                </div>
              ))}
            </div>
          </div>
        </div>
      </header>

      {/* Welcome Message */}
      {showWelcome && connectionStatus.message && (
        <div className="container mt-4 px-4">
          <Card className="sanctuary-card border-mama-bear/20">
            <CardContent className="pt-6">
              <div className="flex items-center space-x-3">
                <div className="text-2xl float-animation">🐻</div>
                <div>
                  <p className="font-medium text-mama-bear">{connectionStatus.message}</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    Your caring AI development sanctuary is ready. Choose an agent below to start building!
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content */}
      <main className="container mt-6 pb-8 px-4">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-9 lg:w-[1100px]">
            <TabsTrigger value="mama-bear" className="flex items-center space-x-2">
              <span>🐻</span>
              <span className="hidden sm:inline">Mama Bear</span>
            </TabsTrigger>
            <TabsTrigger value="scout" className="flex items-center space-x-2">
              <span>🔍</span>
              <span className="hidden sm:inline">Scout</span>
            </TabsTrigger>
            <TabsTrigger value="workspace" className="flex items-center space-x-2">
              <span>🛠️</span>
              <span className="hidden sm:inline">Workspace</span>
            </TabsTrigger>
            <TabsTrigger value="nixos" className="flex items-center space-x-2">
              <span>❄️</span>
              <span className="hidden sm:inline">NixOS</span>
            </TabsTrigger>
            <TabsTrigger value="code-server" className="flex items-center space-x-2">
              <span>💻</span>
              <span className="hidden sm:inline">VSCode</span>
            </TabsTrigger>
            <TabsTrigger value="mcp" className="flex items-center space-x-2">
              <span>🔌</span>
              <span className="hidden sm:inline">Tools</span>
            </TabsTrigger>
            <TabsTrigger value="orchestrator" className="flex items-center space-x-2">
              <Activity className="h-4 w-4" />
              <span className="hidden sm:inline">Orchestrator</span>
            </TabsTrigger>
            <TabsTrigger value="advanced-workspace" className="flex items-center space-x-2">
              <Layout className="h-4 w-4" />
              <span className="hidden sm:inline">Workspace</span>
            </TabsTrigger>
            <TabsTrigger value="gemini-live" className="flex items-center space-x-2">
              <Sparkles className="h-4 w-4 text-blue-400" />
              <span className="hidden sm:inline">Gemini Live</span>
            </TabsTrigger>
          </TabsList>

          {/* Mama Bear Chat */}
          <TabsContent value="mama-bear" className="mt-6">
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              <div className="lg:col-span-3">
                <MamaBearChat socket={socket} connectionStatus={connectionStatus} />
              </div>
              <div className="space-y-4">
                <Card className="sanctuary-card">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg flex items-center space-x-2">
                      <span>🐻</span>
                      <span>Mama Bear</span>
                    </CardTitle>
                    <CardDescription>
                      Your caring AI development assistant
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex flex-wrap gap-1">
                      <Badge variant="secondary" className="text-xs">Caring</Badge>
                      <Badge variant="secondary" className="text-xs">Intelligent</Badge>
                      <Badge variant="secondary" className="text-xs">Proactive</Badge>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      <p className="mb-2">Mama Bear can help you with:</p>
                      <ul className="space-y-1 text-xs">
                        <li>• Code assistance & debugging</li>
                        <li>• Project planning & architecture</li>
                        <li>• Learning new technologies</li>
                        <li>• Emotional support & encouragement</li>
                      </ul>
                    </div>
                  </CardContent>
                </Card>

                <Card className="sanctuary-card">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm">Quick Actions</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <Button 
                      size="sm" 
                      variant="outline" 
                      className="w-full justify-start text-xs"
                      onClick={() => {
                        // This would send a predefined message
                      }}
                    >
                      <Sparkles className="w-3 h-3 mr-2" />
                      Start a new project
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline" 
                      className="w-full justify-start text-xs"
                      onClick={() => setActiveTab('workspace')}
                    >
                      <Zap className="w-3 h-3 mr-2" />
                      Create workspace
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline" 
                      className="w-full justify-start text-xs"
                      onClick={() => setActiveTab('nixos')}
                    >
                      <Snowflake className="w-3 h-3 mr-2" />
                      Create NixOS environment
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline" 
                      className="w-full justify-start text-xs"
                      onClick={() => setActiveTab('code-server')}
                    >
                      <Monitor className="w-3 h-3 mr-2" />
                      Create VSCode instance
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline" 
                      className="w-full justify-start text-xs"
                      onClick={() => setActiveTab('mcp')}
                    >
                      <Settings className="w-3 h-3 mr-2" />
                      Browse tools
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* Scout Autonomous Development */}
          <TabsContent value="scout" className="mt-6">
            <ScoutWorkspace socket={socket} connectionStatus={connectionStatus} />
          </TabsContent>

          {/* Workspace Manager */}
          <TabsContent value="workspace" className="mt-6">
            <WorkspaceManager socket={socket} connectionStatus={connectionStatus} />
          </TabsContent>

          {/* NixOS Environment Manager */}
          <TabsContent value="nixos" className="mt-6">
            <NixOSEnvironmentManager socket={socket} connectionStatus={connectionStatus} />
          </TabsContent>

          {/* Code-Server Manager */}
          <TabsContent value="code-server" className="mt-6">
            <CodeServerManager socket={socket} connectionStatus={connectionStatus} />
          </TabsContent>

          {/* MCP Marketplace */}
          <TabsContent value="mcp" className="mt-6">
            <MCPMarketplace socket={socket} connectionStatus={connectionStatus} />
          </TabsContent>

          {/* Environment Orchestrator */}
          <TabsContent value="orchestrator" className="mt-6">
            <EnvironmentOrchestrator />
          </TabsContent>

          {/* Advanced Workspace */}
          <TabsContent value="advanced-workspace" className="mt-6 h-[calc(100vh-200px)]">
            <AdvancedWorkspace />
          </TabsContent>

          {/* Gemini Live Studio */}
          <TabsContent value="gemini-live" className="mt-6 h-[calc(100vh-200px)]">
            <GeminiLiveStudio />
          </TabsContent>
        </Tabs>
      </main>

      {/* Footer */}
      <footer className="border-t bg-background/95 backdrop-blur">
        <div className="container py-4 px-4">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <div className="flex items-center space-x-4">
              <span>🏠 Nathan's Sanctuary</span>
              <span>•</span>
              <span>AI-Powered Development Environment</span>
            </div>
            <div className="flex items-center space-x-2">
              <span>Made with</span>
              <Heart className="w-3 h-3 fill-red-500 text-red-500" />
              <span>by Mama Bear & Scout</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;