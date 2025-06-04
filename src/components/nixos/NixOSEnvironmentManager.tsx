import React, { useState, useEffect } from 'react';
import { Socket } from 'socket.io-client';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { 
  Snowflake, 
  Play, 
  Square, 
  Trash2, 
  Package, 
  Terminal,
  Settings,
  Plus,
  RefreshCw,
  CheckCircle,
  AlertCircle,
  Clock,
  Cpu,
  HardDrive,
  Database
} from 'lucide-react';

interface ConnectionStatus {
  connected: boolean;
  user_id?: string;
  message?: string;
}

interface NixOSEnvironmentManagerProps {
  socket: Socket | null;
  connectionStatus: ConnectionStatus;
}

interface NixEnvironment {
  id: string;
  name: string;
  description: string;
  status: 'creating' | 'active' | 'stopped' | 'error';
  created_at: string;
  last_updated: string;
  packages_count: number;
  resource_limits: {
    memory: string;
    cpu: string;
    disk: string;
  };
}

interface Template {
  name: string;
  description: string;
  packages: string[];
  environment_variables: Record<string, string>;
  shell_hooks: string[];
  resource_limits: {
    memory: string;
    cpu: string;
    disk: string;
  };
}

const NixOSEnvironmentManager: React.FC<NixOSEnvironmentManagerProps> = ({ socket, connectionStatus }) => {
  const [environments, setEnvironments] = useState<NixEnvironment[]>([]);
  const [templates, setTemplates] = useState<Record<string, Template>>({});
  const [activeTab, setActiveTab] = useState('environments');
  const [isCreatingEnvironment, setIsCreatingEnvironment] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [customConfig, setCustomConfig] = useState({
    name: '',
    description: '',
    packages: '',
    environment_variables: '',
    shell_hooks: ''
  });

  useEffect(() => {
    fetchEnvironments();
    fetchTemplates();
  }, []);

  const fetchEnvironments = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}/api/nixos/environments`);
      if (response.ok) {
        const data = await response.json();
        setEnvironments(data.environments || []);
      }
    } catch (error) {
      console.error('Error fetching environments:', error);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}/api/nixos/templates`);
      if (response.ok) {
        const data = await response.json();
        setTemplates(data.templates || {});
      }
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const createEnvironment = async () => {
    if (!selectedTemplate && !customConfig.name) {
      return;
    }

    setIsCreatingEnvironment(true);

    try {
      const payload: any = {
        user_id: connectionStatus.user_id
      };

      if (selectedTemplate) {
        payload.template_name = selectedTemplate;
      }

      if (customConfig.name) {
        payload.custom_config = {
          name: customConfig.name,
          description: customConfig.description,
          packages: customConfig.packages.split(',').map(p => p.trim()).filter(p => p),
          environment_variables: customConfig.environment_variables ? 
            JSON.parse(customConfig.environment_variables) : {},
          shell_hooks: customConfig.shell_hooks.split('\n').filter(h => h.trim())
        };
      }

      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}/api/nixos/environments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      const result = await response.json();
      
      if (result.success) {
        // Refresh environments list
        fetchEnvironments();
        
        // Reset form
        setSelectedTemplate('');
        setCustomConfig({
          name: '',
          description: '',
          packages: '',
          environment_variables: '',
          shell_hooks: ''
        });
        
        // Switch to environments tab
        setActiveTab('environments');
      } else {
        console.error('Environment creation failed:', result.error);
      }
    } catch (error) {
      console.error('Error creating environment:', error);
    } finally {
      setIsCreatingEnvironment(false);
    }
  };

  const startEnvironment = async (environmentId: string) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}/api/nixos/environments/${environmentId}/start`, {
        method: 'POST'
      });

      if (response.ok) {
        fetchEnvironments();
      }
    } catch (error) {
      console.error('Error starting environment:', error);
    }
  };

  const stopEnvironment = async (environmentId: string) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}/api/nixos/environments/${environmentId}/stop`, {
        method: 'POST'
      });

      if (response.ok) {
        fetchEnvironments();
      }
    } catch (error) {
      console.error('Error stopping environment:', error);
    }
  };

  const deleteEnvironment = async (environmentId: string) => {
    if (!confirm('Are you sure you want to delete this environment?')) {
      return;
    }

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}/api/nixos/environments/${environmentId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        fetchEnvironments();
      }
    } catch (error) {
      console.error('Error deleting environment:', error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'creating':
        return <Clock className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'stopped':
        return <Square className="w-4 h-4 text-gray-500" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-500 text-white';
      case 'creating':
        return 'bg-blue-500 text-white';
      case 'stopped':
        return 'bg-gray-500 text-white';
      case 'error':
        return 'bg-red-500 text-white';
      default:
        return 'bg-gray-400 text-white';
    }
  };

  const EnvironmentCard: React.FC<{ environment: NixEnvironment }> = ({ environment }) => (
    <Card className="sanctuary-card">
      <CardContent className="p-6">
        <div className="space-y-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-2">
                <Snowflake className="w-5 h-5 text-blue-500" />
                <h3 className="font-semibold">{environment.name}</h3>
                <Badge className={`text-xs ${getStatusColor(environment.status)}`}>
                  {getStatusIcon(environment.status)}
                  <span className="ml-1">{environment.status}</span>
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground mb-3">{environment.description}</p>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4 text-xs text-muted-foreground">
            <div className="flex items-center space-x-1">
              <Package className="w-3 h-3" />
              <span>{environment.packages_count} packages</span>
            </div>
            <div className="flex items-center space-x-1">
              <Database className="w-3 h-3" />
              <span>{environment.resource_limits.memory}</span>
            </div>
            <div className="flex items-center space-x-1">
              <Cpu className="w-3 h-3" />
              <span>{environment.resource_limits.cpu} CPU</span>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="text-xs text-muted-foreground">
              Created: {new Date(environment.created_at).toLocaleDateString()}
            </div>

            <div className="flex items-center space-x-2">
              {environment.status === 'stopped' && (
                <Button
                  size="sm"
                  onClick={() => startEnvironment(environment.id)}
                  className="text-xs"
                >
                  <Play className="w-3 h-3 mr-1" />
                  Start
                </Button>
              )}
              {environment.status === 'active' && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => stopEnvironment(environment.id)}
                  className="text-xs"
                >
                  <Square className="w-3 h-3 mr-1" />
                  Stop
                </Button>
              )}
              <Button
                size="sm"
                variant="outline"
                onClick={() => deleteEnvironment(environment.id)}
                className="text-xs text-red-600 hover:text-red-700"
              >
                <Trash2 className="w-3 h-3" />
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const TemplateCard: React.FC<{ templateId: string; template: Template }> = ({ templateId, template }) => (
    <Card 
      className={`sanctuary-card cursor-pointer transition-all ${
        selectedTemplate === templateId ? 'ring-2 ring-mama-bear' : 'hover:shadow-md'
      }`}
      onClick={() => setSelectedTemplate(selectedTemplate === templateId ? '' : templateId)}
    >
      <CardContent className="p-4">
        <div className="space-y-3">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h4 className="font-medium">{template.name}</h4>
              <p className="text-sm text-muted-foreground mt-1">{template.description}</p>
            </div>
            {selectedTemplate === templateId && (
              <CheckCircle className="w-5 h-5 text-mama-bear" />
            )}
          </div>

          <div className="grid grid-cols-3 gap-2 text-xs text-muted-foreground">
            <div className="flex items-center space-x-1">
              <Package className="w-3 h-3" />
              <span>{template.packages.length} packages</span>
            </div>
            <div className="flex items-center space-x-1">
              <Database className="w-3 h-3" />
              <span>{template.resource_limits.memory}</span>
            </div>
            <div className="flex items-center space-x-1">
              <Cpu className="w-3 h-3" />
              <span>{template.resource_limits.cpu} CPU</span>
            </div>
          </div>

          <div className="flex flex-wrap gap-1">
            {template.packages.slice(0, 4).map((pkg, index) => (
              <Badge key={index} variant="outline" className="text-xs">
                {pkg}
              </Badge>
            ))}
            {template.packages.length > 4 && (
              <Badge variant="outline" className="text-xs">
                +{template.packages.length - 4} more
              </Badge>
            )}
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
            <div className="text-2xl">❄️</div>
            <div>
              <span className="text-xl">NixOS Environment Manager</span>
              <p className="text-sm text-muted-foreground font-normal">
                Create and manage reproducible development environments with NixOS
              </p>
            </div>
          </CardTitle>
        </CardHeader>
      </Card>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3 lg:w-[400px]">
          <TabsTrigger value="environments">
            Environments ({environments.length})
          </TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
          <TabsTrigger value="create">Create New</TabsTrigger>
        </TabsList>

        {/* Environments Tab */}
        <TabsContent value="environments">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Your Environments</h3>
              <Button
                size="sm"
                variant="outline"
                onClick={fetchEnvironments}
              >
                <RefreshCw className="w-3 h-3 mr-1" />
                Refresh
              </Button>
            </div>
            
            {environments.length > 0 ? (
              <div className="grid gap-4">
                {environments.map((environment) => (
                  <EnvironmentCard key={environment.id} environment={environment} />
                ))}
              </div>
            ) : (
              <Card className="sanctuary-card">
                <CardContent className="p-12 text-center">
                  <Snowflake className="w-16 h-16 mx-auto mb-4 text-muted-foreground/50" />
                  <h3 className="text-lg font-medium mb-2">No environments yet</h3>
                  <p className="text-muted-foreground mb-4">
                    Create your first NixOS environment to get started
                  </p>
                  <Button onClick={() => setActiveTab('create')}>
                    <Plus className="w-4 h-4 mr-2" />
                    Create Environment
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Templates Tab */}
        <TabsContent value="templates">
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Available Templates</h3>
            
            <div className="grid gap-4 md:grid-cols-2">
              {Object.entries(templates).map(([templateId, template]) => (
                <TemplateCard key={templateId} templateId={templateId} template={template} />
              ))}
            </div>
            
            {selectedTemplate && (
              <Card className="sanctuary-card border-mama-bear/20">
                <CardContent className="p-6">
                  <div className="flex items-start space-x-4">
                    <div className="text-3xl">🐻</div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-mama-bear mb-2">
                        Ready to Create Environment
                      </h3>
                      <p className="text-sm text-muted-foreground mb-4">
                        I'll create the "{templates[selectedTemplate]?.name}" environment for you with all the tools you need.
                      </p>
                      <Button 
                        onClick={createEnvironment}
                        disabled={isCreatingEnvironment}
                        className="mama-bear-gradient text-white"
                      >
                        {isCreatingEnvironment ? (
                          <>
                            <Settings className="w-4 h-4 mr-2 animate-spin" />
                            Creating Environment...
                          </>
                        ) : (
                          <>
                            <Plus className="w-4 h-4 mr-2" />
                            Create Environment
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Create New Tab */}
        <TabsContent value="create">
          <div className="space-y-6">
            <Card className="sanctuary-card">
              <CardHeader>
                <CardTitle>Custom Environment Configuration</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Environment Name</label>
                    <Input
                      value={customConfig.name}
                      onChange={(e) => setCustomConfig({...customConfig, name: e.target.value})}
                      placeholder="My Custom Environment"
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Description</label>
                    <Input
                      value={customConfig.description}
                      onChange={(e) => setCustomConfig({...customConfig, description: e.target.value})}
                      placeholder="Environment description"
                      className="mt-1"
                    />
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium">Packages (comma-separated)</label>
                  <Textarea
                    value={customConfig.packages}
                    onChange={(e) => setCustomConfig({...customConfig, packages: e.target.value})}
                    placeholder="git, nodejs, python3, docker, ..."
                    className="mt-1"
                  />
                </div>

                <div>
                  <label className="text-sm font-medium">Environment Variables (JSON)</label>
                  <Textarea
                    value={customConfig.environment_variables}
                    onChange={(e) => setCustomConfig({...customConfig, environment_variables: e.target.value})}
                    placeholder='{"NODE_ENV": "development", "EDITOR": "vim"}'
                    className="mt-1"
                  />
                </div>

                <div>
                  <label className="text-sm font-medium">Shell Hooks (one per line)</label>
                  <Textarea
                    value={customConfig.shell_hooks}
                    onChange={(e) => setCustomConfig({...customConfig, shell_hooks: e.target.value})}
                    placeholder="echo 'Welcome to your environment'"
                    className="mt-1"
                  />
                </div>

                <Button 
                  onClick={createEnvironment}
                  disabled={isCreatingEnvironment || !customConfig.name}
                  className="w-full"
                >
                  {isCreatingEnvironment ? (
                    <>
                      <Settings className="w-4 h-4 mr-2 animate-spin" />
                      Creating Custom Environment...
                    </>
                  ) : (
                    <>
                      <Plus className="w-4 h-4 mr-2" />
                      Create Custom Environment
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default NixOSEnvironmentManager;