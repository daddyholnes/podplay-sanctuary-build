import React, { useState, useEffect } from 'react';
import { Socket } from 'socket.io-client';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { 
  Monitor,
  Play,
  Square,
  Trash2,
  ExternalLink,
  Cloud,
  Settings,
  Plus,
  RefreshCw,
  CheckCircle,
  AlertCircle,
  Clock,
  Cpu,
  HardDrive,
  Download,
  Code,
  Puzzle,
  Globe
} from 'lucide-react';

interface ConnectionStatus {
  connected: boolean;
  user_id?: string;
  message?: string;
}

interface CodeServerManagerProps {
  socket: Socket | null;
  connectionStatus: ConnectionStatus;
}

interface CodeServerInstance {
  id: string;
  name: string;
  status: 'starting' | 'running' | 'stopped' | 'error';
  port: number;
  access_url?: string;
  cloud_url?: string;
  created_at: string;
  last_accessed: string;
  environment_id?: string;
  extensions_count: number;
}

interface Extension {
  id: string;
  name: string;
  description: string;
  category: string;
}

const CodeServerManager: React.FC<CodeServerManagerProps> = ({ socket, connectionStatus }) => {
  const [instances, setInstances] = useState<CodeServerInstance[]>([]);
  const [extensionCatalog, setExtensionCatalog] = useState<{[key: string]: Extension[]}>({});
  const [activeTab, setActiveTab] = useState('instances');
  const [isCreatingInstance, setIsCreatingInstance] = useState(false);
  const [selectedExtensions, setSelectedExtensions] = useState<string[]>([]);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [createConfig, setCreateConfig] = useState({
    name: '',
    project_description: '',
    project_type: 'web_development',
    theme: 'Default Dark+',
    fontSize: 14
  });

  useEffect(() => {
    fetchInstances();
    fetchExtensionCatalog();
  }, []);

  const fetchInstances = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}/api/code-server/instances`);
      if (response.ok) {
        const data = await response.json();
        setInstances(data.instances || []);
      }
    } catch (error) {
      console.error('Error fetching instances:', error);
    }
  };

  const fetchExtensionCatalog = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}/api/code-server/extensions`);
      if (response.ok) {
        const data = await response.json();
        setExtensionCatalog(data.catalog?.categories || {});
      }
    } catch (error) {
      console.error('Error fetching extension catalog:', error);
    }
  };

  const createInstance = async () => {
    if (!createConfig.name) {
      return;
    }

    setIsCreatingInstance(true);

    try {
      const payload = {
        name: createConfig.name,
        project_description: createConfig.project_description,
        project_type: createConfig.project_type,
        extensions: selectedExtensions,
        settings: {
          'workbench.colorTheme': createConfig.theme,
          'editor.fontSize': createConfig.fontSize
        },
        user_id: connectionStatus.user_id
      };

      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}/api/code-server/instances`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      const result = await response.json();
      
      if (result.success) {
        // Refresh instances list
        fetchInstances();
        
        // Reset form
        setCreateConfig({
          name: '',
          project_description: '',
          project_type: 'web_development',
          theme: 'Default Dark+',
          fontSize: 14
        });
        setSelectedExtensions([]);
        setShowCreateDialog(false);
        
        // Switch to instances tab
        setActiveTab('instances');
      } else {
        console.error('Instance creation failed:', result.error);
      }
    } catch (error) {
      console.error('Error creating instance:', error);
    } finally {
      setIsCreatingInstance(false);
    }
  };

  const stopInstance = async (instanceId: string) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}/api/code-server/instances/${instanceId}/stop`, {
        method: 'POST'
      });

      if (response.ok) {
        fetchInstances();
      }
    } catch (error) {
      console.error('Error stopping instance:', error);
    }
  };

  const deleteInstance = async (instanceId: string) => {
    if (!confirm('Are you sure you want to delete this code-server instance?')) {
      return;
    }

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}/api/code-server/instances/${instanceId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        fetchInstances();
      }
    } catch (error) {
      console.error('Error deleting instance:', error);
    }
  };

  const deployToCloud = async (instanceId: string) => {
    if (!confirm('Deploy this instance to Google Cloud? This may take several minutes.')) {
      return;
    }

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}/api/code-server/instances/${instanceId}/deploy-cloud`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          region: 'us-central1',
          memory: '2Gi',
          cpu: '1000m'
        })
      });

      const result = await response.json();
      
      if (result.success) {
        fetchInstances();
        alert(`Successfully deployed to: ${result.service_url}`);
      } else {
        alert(`Deployment failed: ${result.error}`);
      }
    } catch (error) {
      console.error('Error deploying to cloud:', error);
      alert('Deployment failed. Check console for details.');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'starting':
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
      case 'running':
        return 'bg-green-500 text-white';
      case 'starting':
        return 'bg-blue-500 text-white';
      case 'stopped':
        return 'bg-gray-500 text-white';
      case 'error':
        return 'bg-red-500 text-white';
      default:
        return 'bg-gray-400 text-white';
    }
  };

  const InstanceCard: React.FC<{ instance: CodeServerInstance }> = ({ instance }) => (
    <Card className="sanctuary-card">
      <CardContent className="p-6">
        <div className="space-y-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-2">
                <Monitor className="w-5 h-5 text-blue-500" />
                <h3 className="font-semibold">{instance.name}</h3>
                <Badge className={`text-xs ${getStatusColor(instance.status)}`}>
                  {getStatusIcon(instance.status)}
                  <span className="ml-1">{instance.status}</span>
                </Badge>
              </div>
              <div className="text-sm text-muted-foreground space-y-1">
                <p>Port: {instance.port}</p>
                {instance.environment_id && (
                  <p>Environment: {instance.environment_id}</p>
                )}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 text-xs text-muted-foreground">
            <div className="flex items-center space-x-1">
              <Puzzle className="w-3 h-3" />
              <span>{instance.extensions_count} extensions</span>
            </div>
            <div className="flex items-center space-x-1">
              <Clock className="w-3 h-3" />
              <span>Created: {new Date(instance.created_at).toLocaleDateString()}</span>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {instance.access_url && (
                <Button
                  size="sm"
                  onClick={() => window.open(instance.access_url, '_blank')}
                  className="text-xs"
                >
                  <ExternalLink className="w-3 h-3 mr-1" />
                  Open Local
                </Button>
              )}
              {instance.cloud_url && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => window.open(instance.cloud_url, '_blank')}
                  className="text-xs"
                >
                  <Globe className="w-3 h-3 mr-1" />
                  Open Cloud
                </Button>
              )}
            </div>

            <div className="flex items-center space-x-2">
              {instance.status === 'running' && !instance.cloud_url && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => deployToCloud(instance.id)}
                  className="text-xs"
                >
                  <Cloud className="w-3 h-3 mr-1" />
                  Deploy
                </Button>
              )}
              {instance.status === 'running' && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => stopInstance(instance.id)}
                  className="text-xs"
                >
                  <Square className="w-3 h-3 mr-1" />
                  Stop
                </Button>
              )}
              <Button
                size="sm"
                variant="outline"
                onClick={() => deleteInstance(instance.id)}
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

  const ExtensionSelector: React.FC<{ category: string; extensions: Extension[] }> = ({ category, extensions }) => (
    <div className="space-y-2">
      <h4 className="font-medium text-sm capitalize">{category.replace('_', ' ')}</h4>
      <div className="grid grid-cols-2 gap-2">
        {extensions.map((extension) => (
          <div key={extension.id} className="flex items-center space-x-2">
            <Checkbox
              id={extension.id}
              checked={selectedExtensions.includes(extension.id)}
              onCheckedChange={(checked) => {
                if (checked) {
                  setSelectedExtensions(prev => [...prev, extension.id]);
                } else {
                  setSelectedExtensions(prev => prev.filter(id => id !== extension.id));
                }
              }}
            />
            <label htmlFor={extension.id} className="text-sm">
              {extension.name}
            </label>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="sanctuary-card">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <div className="text-2xl">💻</div>
            <div>
              <span className="text-xl">Code-Server Manager</span>
              <p className="text-sm text-muted-foreground font-normal">
                Full VSCode in your browser with Docker and cloud deployment
              </p>
            </div>
          </CardTitle>
        </CardHeader>
      </Card>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3 lg:w-[400px]">
          <TabsTrigger value="instances">
            Instances ({instances.length})
          </TabsTrigger>
          <TabsTrigger value="extensions">Extensions</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        {/* Instances Tab */}
        <TabsContent value="instances">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Your Code Servers</h3>
              <div className="flex items-center space-x-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={fetchInstances}
                >
                  <RefreshCw className="w-3 h-3 mr-1" />
                  Refresh
                </Button>
                <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
                  <DialogTrigger asChild>
                    <Button size="sm">
                      <Plus className="w-3 h-3 mr-1" />
                      Create Instance
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-2xl">
                    <DialogHeader>
                      <DialogTitle>Create Code-Server Instance</DialogTitle>
                      <DialogDescription>
                        Set up a new browser-based VSCode environment
                      </DialogDescription>
                    </DialogHeader>
                    
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="text-sm font-medium">Instance Name</label>
                          <Input
                            value={createConfig.name}
                            onChange={(e) => setCreateConfig({...createConfig, name: e.target.value})}
                            placeholder="My Code Server"
                            className="mt-1"
                          />
                        </div>
                        <div>
                          <label className="text-sm font-medium">Project Type</label>
                          <Select 
                            value={createConfig.project_type} 
                            onValueChange={(value) => setCreateConfig({...createConfig, project_type: value})}
                          >
                            <SelectTrigger className="mt-1">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="web_development">Web Development</SelectItem>
                              <SelectItem value="data_science">Data Science</SelectItem>
                              <SelectItem value="mobile_development">Mobile Development</SelectItem>
                              <SelectItem value="devops">DevOps</SelectItem>
                              <SelectItem value="general">General</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>

                      <div>
                        <label className="text-sm font-medium">Project Description</label>
                        <Textarea
                          value={createConfig.project_description}
                          onChange={(e) => setCreateConfig({...createConfig, project_description: e.target.value})}
                          placeholder="Describe your project to get tailored extension recommendations..."
                          className="mt-1"
                        />
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="text-sm font-medium">Theme</label>
                          <Select 
                            value={createConfig.theme} 
                            onValueChange={(value) => setCreateConfig({...createConfig, theme: value})}
                          >
                            <SelectTrigger className="mt-1">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="Default Dark+">Default Dark+</SelectItem>
                              <SelectItem value="Default Light+">Default Light+</SelectItem>
                              <SelectItem value="Monokai">Monokai</SelectItem>
                              <SelectItem value="Solarized Dark">Solarized Dark</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <label className="text-sm font-medium">Font Size</label>
                          <Input
                            type="number"
                            value={createConfig.fontSize}
                            onChange={(e) => setCreateConfig({...createConfig, fontSize: parseInt(e.target.value)})}
                            min="10"
                            max="24"
                            className="mt-1"
                          />
                        </div>
                      </div>

                      {Object.keys(extensionCatalog).length > 0 && (
                        <div>
                          <label className="text-sm font-medium mb-2 block">Extensions</label>
                          <div className="max-h-60 overflow-y-auto space-y-4 border rounded p-4">
                            {Object.entries(extensionCatalog).map(([category, extensions]) => (
                              <ExtensionSelector 
                                key={category} 
                                category={category} 
                                extensions={extensions} 
                              />
                            ))}
                          </div>
                          <p className="text-xs text-muted-foreground mt-2">
                            Selected: {selectedExtensions.length} extensions
                          </p>
                        </div>
                      )}

                      <div className="flex justify-end space-x-2">
                        <Button 
                          variant="outline" 
                          onClick={() => setShowCreateDialog(false)}
                        >
                          Cancel
                        </Button>
                        <Button 
                          onClick={createInstance}
                          disabled={isCreatingInstance || !createConfig.name}
                        >
                          {isCreatingInstance ? (
                            <>
                              <Settings className="w-4 h-4 mr-2 animate-spin" />
                              Creating...
                            </>
                          ) : (
                            <>
                              <Plus className="w-4 h-4 mr-2" />
                              Create Instance
                            </>
                          )}
                        </Button>
                      </div>
                    </div>
                  </DialogContent>
                </Dialog>
              </div>
            </div>
            
            {instances.length > 0 ? (
              <div className="grid gap-4">
                {instances.map((instance) => (
                  <InstanceCard key={instance.id} instance={instance} />
                ))}
              </div>
            ) : (
              <Card className="sanctuary-card">
                <CardContent className="p-12 text-center">
                  <Monitor className="w-16 h-16 mx-auto mb-4 text-muted-foreground/50" />
                  <h3 className="text-lg font-medium mb-2">No code servers yet</h3>
                  <p className="text-muted-foreground mb-4">
                    Create your first browser-based VSCode environment
                  </p>
                  <Button onClick={() => setShowCreateDialog(true)}>
                    <Plus className="w-4 h-4 mr-2" />
                    Create Code Server
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Extensions Tab */}
        <TabsContent value="extensions">
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Available Extensions</h3>
            
            {Object.keys(extensionCatalog).length > 0 ? (
              <div className="grid gap-6">
                {Object.entries(extensionCatalog).map(([category, extensions]) => (
                  <Card key={category} className="sanctuary-card">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-base capitalize">
                        {category.replace('_', ' ')}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid gap-3 md:grid-cols-2">
                        {extensions.map((extension) => (
                          <div key={extension.id} className="p-3 border rounded">
                            <h4 className="font-medium text-sm">{extension.name}</h4>
                            <p className="text-xs text-muted-foreground mt-1">
                              {extension.description}
                            </p>
                            <Badge variant="outline" className="text-xs mt-2">
                              {extension.id}
                            </Badge>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <Card className="sanctuary-card">
                <CardContent className="p-8 text-center">
                  <Puzzle className="w-12 h-12 mx-auto mb-4 text-muted-foreground/50" />
                  <h3 className="font-medium mb-2">Loading extensions...</h3>
                  <p className="text-sm text-muted-foreground">
                    Extension catalog is being loaded
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings">
          <div className="space-y-4">
            <Card className="sanctuary-card border-mama-bear/20">
              <CardContent className="p-6">
                <div className="flex items-start space-x-4">
                  <div className="text-3xl">🐻</div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-mama-bear mb-2">
                      Mama Bear Smart Workspace Creation
                    </h3>
                    <p className="text-sm text-muted-foreground mb-4">
                      I can analyze your project requirements and automatically set up the perfect development environment with the right extensions and settings.
                    </p>
                    <div className="flex space-x-2">
                      <Button 
                        size="sm" 
                        className="mama-bear-gradient text-white"
                        onClick={() => setShowCreateDialog(true)}
                      >
                        <Code className="w-3 h-3 mr-1" />
                        Create Smart Workspace
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="sanctuary-card">
              <CardHeader>
                <CardTitle>Cloud Deployment</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center space-x-2 text-sm">
                  <Cloud className="w-4 h-4" />
                  <span>Deploy instances to Google Cloud Run</span>
                </div>
                <div className="flex items-center space-x-2 text-sm">
                  <Globe className="w-4 h-4" />
                  <span>Access your code server from anywhere</span>
                </div>
                <div className="flex items-center space-x-2 text-sm">
                  <Settings className="w-4 h-4" />
                  <span>Automatic scaling and resource management</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CodeServerManager;