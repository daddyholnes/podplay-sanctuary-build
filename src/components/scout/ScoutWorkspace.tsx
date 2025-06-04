import React, { useState, useEffect } from 'react';
import { Socket } from 'socket.io-client';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Play, Search, Package, GitBranch, Settings, Zap } from 'lucide-react';

interface ConnectionStatus {
  connected: boolean;
  user_id?: string;
  message?: string;
}

interface ScoutWorkspaceProps {
  socket: Socket | null;
  connectionStatus: ConnectionStatus;
}

interface MCPServer {
  name: string;
  description: string;
  capabilities: string[];
  confidence: number;
  source: string;
}

interface WorkflowStage {
  name: string;
  status: 'pending' | 'active' | 'completed' | 'error';
  description: string;
}

const ScoutWorkspace: React.FC<ScoutWorkspaceProps> = ({ socket, connectionStatus }) => {
  const [taskDescription, setTaskDescription] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [workflowStages, setWorkflowStages] = useState<WorkflowStage[]>([
    { name: 'Analysis', status: 'pending', description: 'Analyzing task requirements' },
    { name: 'MCP Discovery', status: 'pending', description: 'Searching for required tools' },
    { name: 'Environment Setup', status: 'pending', description: 'Preparing development environment' },
    { name: 'Implementation', status: 'pending', description: 'Autonomous development execution' },
    { name: 'Testing', status: 'pending', description: 'Validating implementation' },
    { name: 'Deployment', status: 'pending', description: 'Deploying the solution' }
  ]);
  const [discoveredMCPs, setDiscoveredMCPs] = useState<MCPServer[]>([]);
  const [taskResult, setTaskResult] = useState<any>(null);
  const [activeTab, setActiveTab] = useState('task');

  useEffect(() => {
    if (!socket) return;

    // Listen for Scout responses
    socket.on('scout_response', (data) => {
      console.log('Scout response:', data);
      setTaskResult(data);
      setIsProcessing(false);

      if (data.status === 'mcp_discovery' && data.recommended_mcps) {
        setDiscoveredMCPs(data.recommended_mcps);
        setActiveTab('mcps');
      }
    });

    return () => {
      socket.off('scout_response');
    };
  }, [socket]);

  const handleTaskSubmit = () => {
    if (!taskDescription.trim() || !socket || !connectionStatus.connected || isProcessing) return;

    setIsProcessing(true);
    setTaskResult(null);
    setDiscoveredMCPs([]);

    // Reset workflow stages
    setWorkflowStages(stages => stages.map(stage => ({ ...stage, status: 'pending' })));

    // Simulate workflow progress
    simulateWorkflowProgress();

    // Send task to Scout agent
    socket.emit('scout_request', {
      task: taskDescription,
      user_id: connectionStatus.user_id,
      timestamp: new Date().toISOString()
    });
  };

  const simulateWorkflowProgress = () => {
    let currentStageIndex = 0;
    
    const progressInterval = setInterval(() => {
      if (currentStageIndex < workflowStages.length) {
        setWorkflowStages(stages => 
          stages.map((stage, index) => {
            if (index === currentStageIndex) {
              return { ...stage, status: 'active' };
            } else if (index < currentStageIndex) {
              return { ...stage, status: 'completed' };
            }
            return stage;
          })
        );
        currentStageIndex++;
      } else {
        clearInterval(progressInterval);
        setWorkflowStages(stages => 
          stages.map(stage => ({ ...stage, status: 'completed' }))
        );
      }
    }, 2000);

    // Clear interval if component unmounts or processing stops
    setTimeout(() => clearInterval(progressInterval), 15000);
  };

  const installMCP = (mcp: MCPServer) => {
    if (!socket) return;

    socket.emit('install_mcp', {
      mcp_data: mcp,
      user_id: connectionStatus.user_id
    });

    console.log('Installing MCP:', mcp.name);
  };

  const getStageIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return '✅';
      case 'active':
        return '⏳';
      case 'error':
        return '❌';
      default:
        return '⚪';
    }
  };

  const getProgressPercentage = () => {
    const completedStages = workflowStages.filter(stage => stage.status === 'completed').length;
    return (completedStages / workflowStages.length) * 100;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="sanctuary-card">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <div className="text-2xl">🔍</div>
            <div>
              <span className="text-xl">Scout Autonomous Workspace</span>
              <p className="text-sm text-muted-foreground font-normal">
                Autonomous development agent with MCP marketplace integration
              </p>
            </div>
          </CardTitle>
        </CardHeader>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Workspace */}
        <div className="lg:col-span-2 space-y-6">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="task">Task Definition</TabsTrigger>
              <TabsTrigger value="mcps">MCP Discovery</TabsTrigger>
              <TabsTrigger value="execution">Execution</TabsTrigger>
            </TabsList>

            {/* Task Definition Tab */}
            <TabsContent value="task">
              <Card className="sanctuary-card">
                <CardHeader>
                  <CardTitle className="text-lg">Define Your Development Task</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Textarea
                    value={taskDescription}
                    onChange={(e) => setTaskDescription(e.target.value)}
                    placeholder="Describe what you want Scout to build... e.g., 'Create a React app with user authentication and integrate it with GitHub'"
                    className="min-h-[100px]"
                    disabled={isProcessing}
                  />
                  <div className="flex space-x-2">
                    <Button
                      onClick={handleTaskSubmit}
                      disabled={!taskDescription.trim() || isProcessing || !connectionStatus.connected}
                      className="scout-gradient text-white"
                    >
                      <Play className="w-4 h-4 mr-2" />
                      {isProcessing ? 'Processing...' : 'Start Autonomous Development'}
                    </Button>
                    <Button variant="outline" size="sm">
                      <Settings className="w-4 h-4 mr-2" />
                      Advanced Options
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* MCP Discovery Tab */}
            <TabsContent value="mcps">
              <Card className="sanctuary-card">
                <CardHeader>
                  <CardTitle className="text-lg flex items-center space-x-2">
                    <Package className="w-5 h-5" />
                    <span>Discovered MCP Servers</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {discoveredMCPs.length > 0 ? (
                    <div className="space-y-3">
                      {discoveredMCPs.map((mcp, index) => (
                        <Card key={index} className="border border-scout/20">
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <h4 className="font-medium">{mcp.name}</h4>
                                <p className="text-sm text-muted-foreground mt-1">
                                  {mcp.description}
                                </p>
                                <div className="flex flex-wrap gap-1 mt-2">
                                  {mcp.capabilities.map((capability, capIndex) => (
                                    <Badge key={capIndex} variant="secondary" className="text-xs">
                                      {capability.replace('_', ' ')}
                                    </Badge>
                                  ))}
                                </div>
                                <div className="flex items-center space-x-2 mt-2">
                                  <Badge variant="outline" className="text-xs">
                                    {mcp.source}
                                  </Badge>
                                  <span className="text-xs text-muted-foreground">
                                    Confidence: {mcp.confidence}%
                                  </span>
                                </div>
                              </div>
                              <Button
                                size="sm"
                                onClick={() => installMCP(mcp)}
                                className="scout-gradient text-white"
                              >
                                <Zap className="w-3 h-3 mr-1" />
                                Install
                              </Button>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      <Package className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>No MCP servers discovered yet.</p>
                      <p className="text-sm">Submit a task to discover relevant tools.</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* Execution Tab */}
            <TabsContent value="execution">
              <Card className="sanctuary-card">
                <CardHeader>
                  <CardTitle className="text-lg">Execution Results</CardTitle>
                </CardHeader>
                <CardContent>
                  {taskResult ? (
                    <div className="space-y-4">
                      <div className="flex items-center space-x-2">
                        <Badge 
                          variant={taskResult.status === 'completed' ? 'default' : 'secondary'}
                          className={taskResult.status === 'completed' ? 'scout-gradient text-white' : ''}
                        >
                          {taskResult.status}
                        </Badge>
                        <span className="text-sm text-muted-foreground">
                          {taskResult.timestamp}
                        </span>
                      </div>
                      
                      {taskResult.message && (
                        <p className="text-sm">{taskResult.message}</p>
                      )}

                      {taskResult.steps_executed && (
                        <div>
                          <h4 className="font-medium mb-2">Steps Executed:</h4>
                          <ul className="space-y-1 text-sm">
                            {taskResult.steps_executed.map((step: string, index: number) => (
                              <li key={index} className="flex items-center space-x-2">
                                <span className="text-green-500">✓</span>
                                <span>{step}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {taskResult.next_steps && (
                        <div>
                          <h4 className="font-medium mb-2">Next Steps:</h4>
                          <ul className="space-y-1 text-sm">
                            {taskResult.next_steps.map((step: string, index: number) => (
                              <li key={index} className="flex items-center space-x-2">
                                <span className="text-blue-500">→</span>
                                <span>{step}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      <GitBranch className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>No execution results yet.</p>
                      <p className="text-sm">Submit a task to see autonomous development in action.</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        {/* Workflow Progress Sidebar */}
        <div className="space-y-4">
          <Card className="sanctuary-card">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">Workflow Progress</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Overall Progress</span>
                  <span className="text-sm text-muted-foreground">
                    {Math.round(getProgressPercentage())}%
                  </span>
                </div>
                <Progress value={getProgressPercentage()} className="h-2" />
              </div>

              <div className="space-y-3">
                {workflowStages.map((stage, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <div className="text-lg mt-0.5">
                      {getStageIcon(stage.status)}
                    </div>
                    <div className="flex-1">
                      <h4 className={`text-sm font-medium ${
                        stage.status === 'active' ? 'text-scout' : ''
                      }`}>
                        {stage.name}
                      </h4>
                      <p className="text-xs text-muted-foreground">
                        {stage.description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="sanctuary-card">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Scout Capabilities</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="space-y-2">
                {[
                  'Autonomous Development',
                  'MCP Server Discovery',
                  'GitHub Integration',
                  'Docker Management',
                  'Environment Setup',
                  'Code Generation',
                  'Testing & Validation'
                ].map((capability, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <div className="w-2 h-2 scout-gradient rounded-full" />
                    <span className="text-xs">{capability}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default ScoutWorkspace;