import React, { useState, useEffect } from 'react';
import { Socket } from 'socket.io-client';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { 
  Play, 
  Square, 
  Trash2, 
  ExternalLink, 
  Server, 
  Container, 
  Cloud,
  Settings,
  Plus,
  Monitor
} from 'lucide-react';

interface ConnectionStatus {
  connected: boolean;
  user_id?: string;
  message?: string;
}

interface WorkspaceManagerProps {
  socket: Socket | null;
  connectionStatus: ConnectionStatus;
}

interface Workspace {
  id: string;
  name: string;
  type: string;
  status: string;
  access_url?: string;
  created_at: string;
  last_used?: string;
}

interface WorkspaceTemplate {
  id: string;
  name: string;
  description: string;
  language: string;
  framework: string;
  tools: string[];
}

const WorkspaceManager: React.FC<WorkspaceManagerProps> = ({ socket, connectionStatus }) => {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [templates, setTemplates] = useState<WorkspaceTemplate[]>([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [isCreating, setIsCreating] = useState(false);
  const [newWorkspaceConfig, setNewWorkspaceConfig] = useState({
    name: '',
    type: 'docker',
    template: '',
    description: '',
    customTools: ''
  });

  useEffect(() => {
    if (!socket) return;

    // Listen for workspace events
    socket.on('workspace_created', (data) => {
      console.log('Workspace created:', data);
      setIsCreating(false);
      if (data.success) {
        fetchWorkspaces();
        setActiveTab('overview');
        // Reset form
        setNewWorkspaceConfig({
          name: '',
          type: 'docker',
          template: '',
          description: '',
          customTools: ''
        });
      }
    });

    socket.on('workspace_status_updated', (data) => {
      setWorkspaces(prev => 
        prev.map(ws => 
          ws.id === data.workspace_id 
            ? { ...ws, status: data.status }
            : ws
        )
      );
    });

    return () => {
      socket.off('workspace_created');
      socket.off('workspace_status_updated');
    };
  }, [socket]);

  useEffect(() => {
    // Fetch initial data
    fetchWorkspaces();
    fetchTemplates();
  }, []);

  const fetchWorkspaces = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}/api/workspaces`);
      if (response.ok) {
        const data = await response.json();
        setWorkspaces(data.workspaces || []);
      }
    } catch (error) {
      console.error('Error fetching workspaces:', error);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}/api/workspace-templates`);
      if (response.ok) {
        const data = await response.json();
        setTemplates(data.templates || []);
      } else {
        // Mock templates if API not available
        setTemplates([
          {
            id: 'react_typescript',
            name: 'React + TypeScript',
            description: 'Modern React application with TypeScript',
            language: 'typescript',
            framework: 'react',
            tools: ['node', 'npm', 'vite', 'eslint', 'prettier']
          },
          {
            id: 'python_flask',
            name: 'Python + Flask',
            description: 'Flask web application with Python',
            language: 'python',
            framework: 'flask',
            tools: ['python3', 'pip', 'flask', 'pytest']
          },
          {
            id: 'full_stack',
            name: 'Full Stack (React + Flask)',
            description: 'Complete full-stack development environment',
            language: 'multiple',
            framework: 'full_stack',
            tools: ['node', 'python3', 'docker', 'postgres']
          },
          {
            id: 'ai_development',
            name: 'AI/ML Development',
            description: 'Machine learning and AI development environment',
            language: 'python',
            framework: 'pytorch',
            tools: ['python3', 'jupyter', 'pytorch', 'transformers', 'pandas']
          }
        ]);
      }
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const createWorkspace = () => {
    if (!socket || !newWorkspaceConfig.name.trim()) return;

    setIsCreating(true);

    const config = {
      name: newWorkspaceConfig.name,
      type: newWorkspaceConfig.type,
      template: newWorkspaceConfig.template || undefined,
      description: newWorkspaceConfig.description || undefined,
      tools: newWorkspaceConfig.customTools ? newWorkspaceConfig.customTools.split(',').map(t => t.trim()) : undefined
    };

    socket.emit('create_workspace', { config });
  };

  const stopWorkspace = (workspaceId: string) => {
    if (!socket) return;
    
    socket.emit('stop_workspace', { workspace_id: workspaceId });
  };

  const deleteWorkspace = (workspaceId: string) => {
    if (!socket) return;
    
    if (window.confirm('Are you sure you want to delete this workspace? This action cannot be undone.')) {
      socket.emit('delete_workspace', { workspace_id: workspaceId });
      setWorkspaces(prev => prev.filter(ws => ws.id !== workspaceId));
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'bg-green-500';
      case 'stopped':
        return 'bg-gray-500';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-yellow-500';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'docker':
        return <Container className="w-4 h-4" />;
      case 'nixos':
        return <Server className="w-4 h-4" />;
      case 'cloud':
        return <Cloud className="w-4 h-4" />;
      default:
        return <Monitor className="w-4 h-4" />;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="sanctuary-card">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <div className="text-2xl">🛠️</div>
            <div>
              <span className="text-xl">Workspace Manager</span>
              <p className="text-sm text-muted-foreground font-normal">
                Create and manage development environments
              </p>
            </div>
          </CardTitle>
        </CardHeader>
      </Card>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3 lg:w-[400px]">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="create">Create New</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
        </TabsList>

        {/* Workspaces Overview */}
        <TabsContent value="overview">
          <div className="space-y-4">
            {workspaces.length > 0 ? (
              <div className="grid gap-4">
                {workspaces.map((workspace) => (
                  <Card key={workspace.id} className="sanctuary-card">
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            {getTypeIcon(workspace.type)}
                            <h3 className="font-semibold">{workspace.name}</h3>
                            <Badge 
                              variant="secondary" 
                              className={`text-xs ${getStatusColor(workspace.status)} text-white`}
                            >
                              {workspace.status}
                            </Badge>
                            <Badge variant="outline" className="text-xs">
                              {workspace.type}
                            </Badge>
                          </div>
                          <div className="text-sm text-muted-foreground space-y-1">
                            <p>Created: {formatDate(workspace.created_at)}</p>
                            {workspace.last_used && (
                              <p>Last used: {formatDate(workspace.last_used)}</p>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          {workspace.access_url && workspace.status === 'running' && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => window.open(workspace.access_url, '_blank')}
                            >
                              <ExternalLink className="w-3 h-3 mr-1" />
                              Open
                            </Button>
                          )}
                          {workspace.status === 'running' ? (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => stopWorkspace(workspace.id)}
                            >
                              <Square className="w-3 h-3 mr-1" />
                              Stop
                            </Button>
                          ) : (
                            <Button
                              size="sm"
                              onClick={() => {
                                // Start workspace logic would go here
                              }}
                            >
                              <Play className="w-3 h-3 mr-1" />
                              Start
                            </Button>
                          )}
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => deleteWorkspace(workspace.id)}
                          >
                            <Trash2 className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <Card className="sanctuary-card">
                <CardContent className="p-12 text-center">
                  <Monitor className="w-16 h-16 mx-auto mb-4 text-muted-foreground/50" />
                  <h3 className="text-lg font-medium mb-2">No workspaces yet</h3>
                  <p className="text-muted-foreground mb-4">
                    Create your first development environment to get started
                  </p>
                  <Button onClick={() => setActiveTab('create')}>
                    <Plus className="w-4 h-4 mr-2" />
                    Create Workspace
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Create New Workspace */}
        <TabsContent value="create">
          <Card className="sanctuary-card">
            <CardHeader>
              <CardTitle className="text-lg">Create New Workspace</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid gap-4">
                <div>
                  <Label htmlFor="workspace-name">Workspace Name</Label>
                  <Input
                    id="workspace-name"
                    value={newWorkspaceConfig.name}
                    onChange={(e) => setNewWorkspaceConfig(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="My Development Environment"
                    disabled={isCreating}
                  />
                </div>

                <div>
                  <Label htmlFor="workspace-type">Environment Type</Label>
                  <Select 
                    value={newWorkspaceConfig.type} 
                    onValueChange={(value) => setNewWorkspaceConfig(prev => ({ ...prev, type: value }))}
                    disabled={isCreating}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="docker">
                        <div className="flex items-center space-x-2">
                          <Container className="w-4 h-4" />
                          <span>Docker Container</span>
                        </div>
                      </SelectItem>
                      <SelectItem value="nixos" disabled>
                        <div className="flex items-center space-x-2">
                          <Server className="w-4 h-4" />
                          <span>NixOS VM (Coming Soon)</span>
                        </div>
                      </SelectItem>
                      <SelectItem value="cloud" disabled>
                        <div className="flex items-center space-x-2">
                          <Cloud className="w-4 h-4" />
                          <span>Cloud Environment (Coming Soon)</span>
                        </div>
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="workspace-template">Template (Optional)</Label>
                  <Select 
                    value={newWorkspaceConfig.template} 
                    onValueChange={(value) => setNewWorkspaceConfig(prev => ({ ...prev, template: value }))}
                    disabled={isCreating}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Choose a template or leave blank for custom" />
                    </SelectTrigger>
                    <SelectContent>
                      {templates.map((template) => (
                        <SelectItem key={template.id} value={template.id}>
                          <div>
                            <div className="font-medium">{template.name}</div>
                            <div className="text-xs text-muted-foreground">{template.description}</div>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="workspace-description">Description (Optional)</Label>
                  <Textarea
                    id="workspace-description"
                    value={newWorkspaceConfig.description}
                    onChange={(e) => setNewWorkspaceConfig(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Brief description of this workspace..."
                    disabled={isCreating}
                  />
                </div>

                <div>
                  <Label htmlFor="custom-tools">Custom Tools (Optional)</Label>
                  <Input
                    id="custom-tools"
                    value={newWorkspaceConfig.customTools}
                    onChange={(e) => setNewWorkspaceConfig(prev => ({ ...prev, customTools: e.target.value }))}
                    placeholder="git, vim, curl (comma-separated)"
                    disabled={isCreating}
                  />
                </div>
              </div>

              <div className="flex space-x-2">
                <Button
                  onClick={createWorkspace}
                  disabled={!newWorkspaceConfig.name.trim() || isCreating || !connectionStatus.connected}
                  className="flex-1"
                >
                  {isCreating ? (
                    <>
                      <Settings className="w-4 h-4 mr-2 animate-spin" />
                      Creating Workspace...
                    </>
                  ) : (
                    <>
                      <Plus className="w-4 h-4 mr-2" />
                      Create Workspace
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Templates */}
        <TabsContent value="templates">
          <div className="grid gap-4 md:grid-cols-2">
            {templates.map((template) => (
              <Card key={template.id} className="sanctuary-card">
                <CardContent className="p-6">
                  <div className="space-y-3">
                    <div>
                      <h3 className="font-semibold">{template.name}</h3>
                      <p className="text-sm text-muted-foreground">{template.description}</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className="text-xs">
                        {template.language}
                      </Badge>
                      <Badge variant="outline" className="text-xs">
                        {template.framework}
                      </Badge>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {template.tools.map((tool, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {tool}
                        </Badge>
                      ))}
                    </div>
                    <Button
                      size="sm"
                      className="w-full"
                      onClick={() => {
                        setNewWorkspaceConfig(prev => ({ 
                          ...prev, 
                          template: template.id,
                          name: `${template.name} Workspace`
                        }));
                        setActiveTab('create');
                      }}
                    >
                      Use This Template
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default WorkspaceManager;