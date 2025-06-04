import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import ResourceMonitor from './ResourceMonitor';
import { 
  Play, 
  Square, 
  Trash2, 
  Plus, 
  Settings, 
  MonitorSpeaker, 
  Cloud, 
  Container,
  Cpu,
  HardDrive,
  Activity,
  Users,
  Clock,
  DollarSign,
  BarChart3,
  AlertTriangle,
  CheckCircle,
  Loader2
} from 'lucide-react';

interface Template {
  id: string;
  name: string;
  description: string;
  type: string;
  tags: string[];
  required_resources: {
    memory: string;
    cpu: string;
    storage: string;
  };
}

interface Environment {
  id: string;
  name: string;
  status: string;
  type: string;
  template_id: string;
  endpoints: Record<string, string>;
  owner: string;
  collaborators: string[];
  created_at: string;
  last_accessed: string;
  resources: {
    memory: string;
    cpu: string;
    storage: string;
  };
  health_status: {
    status: string;
    last_check: string;
  };
}

interface ResourceUsage {
  total_environments: number;
  running_environments: number;
  total_memory_gb: number;
  total_cpu_cores: number;
  resource_utilization: string;
}

const EnvironmentOrchestrator: React.FC = () => {
  const [environments, setEnvironments] = useState<Environment[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [resourceUsage, setResourceUsage] = useState<ResourceUsage | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedEnvironment, setSelectedEnvironment] = useState<Environment | null>(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [activeTab, setActiveTab] = useState('environments');

  // Load data on component mount
  useEffect(() => {
    loadData();
    
    // Set up periodic refresh
    const interval = setInterval(loadData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      await Promise.all([
        loadEnvironments(),
        loadTemplates(),
        loadResourceUsage()
      ]);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadEnvironments = async () => {
    try {
      const response = await fetch('/api/orchestrator/environments');
      const data = await response.json();
      
      if (data.success) {
        setEnvironments(data.environments);
      }
    } catch (error) {
      console.error('Failed to load environments:', error);
    }
  };

  const loadTemplates = async () => {
    try {
      const response = await fetch('/api/orchestrator/templates');
      const data = await response.json();
      
      if (data.success) {
        setTemplates(data.templates);
      }
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  const loadResourceUsage = async () => {
    try {
      const response = await fetch('/api/orchestrator/resource-usage');
      const data = await response.json();
      
      if (data.success) {
        setResourceUsage(data.resource_usage);
      }
    } catch (error) {
      console.error('Failed to load resource usage:', error);
    }
  };

  const createEnvironment = async (templateId: string, name: string, config: any = {}) => {
    try {
      const response = await fetch('/api/orchestrator/environments', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          template_id: templateId,
          name,
          config,
          owner: 'mama_bear'
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        await loadEnvironments();
        setShowCreateDialog(false);
      } else {
        alert(`Failed to create environment: ${data.error}`);
      }
    } catch (error) {
      console.error('Failed to create environment:', error);
      alert('Failed to create environment');
    }
  };

  const stopEnvironment = async (envId: string) => {
    try {
      const response = await fetch(`/api/orchestrator/environments/${envId}/stop`, {
        method: 'POST',
      });

      const data = await response.json();
      
      if (data.success) {
        await loadEnvironments();
      } else {
        alert(`Failed to stop environment: ${data.error}`);
      }
    } catch (error) {
      console.error('Failed to stop environment:', error);
      alert('Failed to stop environment');
    }
  };

  const deleteEnvironment = async (envId: string) => {
    if (!confirm('Are you sure you want to delete this environment? This action cannot be undone.')) {
      return;
    }

    try {
      const response = await fetch(`/api/orchestrator/environments/${envId}`, {
        method: 'DELETE',
      });

      const data = await response.json();
      
      if (data.success) {
        await loadEnvironments();
        setSelectedEnvironment(null);
      } else {
        alert(`Failed to delete environment: ${data.error}`);
      }
    } catch (error) {
      console.error('Failed to delete environment:', error);
      alert('Failed to delete environment');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'ready': return 'bg-green-500';
      case 'provisioning': return 'bg-yellow-500';
      case 'pending': return 'bg-blue-500';
      case 'stopping': return 'bg-orange-500';
      case 'stopped': return 'bg-gray-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-400';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'docker': return <Container className="h-4 w-4" />;
      case 'cloud': return <Cloud className="h-4 w-4" />;
      case 'nixos': return <MonitorSpeaker className="h-4 w-4" />;
      case 'hybrid': return <Settings className="h-4 w-4" />;
      default: return <Activity className="h-4 w-4" />;
    }
  };

  const formatUptime = (createdAt: string) => {
    const created = new Date(createdAt);
    const now = new Date();
    const diffMs = now.getTime() - created.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    
    if (diffHours > 0) {
      return `${diffHours}h ${diffMinutes}m`;
    }
    return `${diffMinutes}m`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-2">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span>Loading Environment Orchestrator...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">Environment Orchestrator</h2>
          <p className="text-muted-foreground">
            Mama Bear's development environment management system
          </p>
        </div>
        <Button onClick={() => setShowCreateDialog(true)} className="bg-gradient-to-r from-purple-600 to-pink-600">
          <Plus className="h-4 w-4 mr-2" />
          Create Environment
        </Button>
      </div>

      {/* Resource Overview */}
      {resourceUsage && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Activity className="h-5 w-5 text-blue-500" />
                <div>
                  <p className="text-sm text-muted-foreground">Total Environments</p>
                  <p className="text-2xl font-bold">{resourceUsage.total_environments}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <div>
                  <p className="text-sm text-muted-foreground">Running</p>
                  <p className="text-2xl font-bold">{resourceUsage.running_environments}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Cpu className="h-5 w-5 text-orange-500" />
                <div>
                  <p className="text-sm text-muted-foreground">CPU Cores</p>
                  <p className="text-2xl font-bold">{resourceUsage.total_cpu_cores.toFixed(1)}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <HardDrive className="h-5 w-5 text-purple-500" />
                <div>
                  <p className="text-sm text-muted-foreground">Memory (GB)</p>
                  <p className="text-2xl font-bold">{resourceUsage.total_memory_gb.toFixed(1)}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="environments">Environments</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
          <TabsTrigger value="monitoring">Monitoring</TabsTrigger>
        </TabsList>

        <TabsContent value="environments" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
            {environments.map((env) => (
              <Card key={env.id} className="hover:shadow-lg transition-shadow cursor-pointer"
                    onClick={() => setSelectedEnvironment(env)}>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {getTypeIcon(env.type)}
                      <CardTitle className="text-lg">{env.name}</CardTitle>
                    </div>
                    <Badge className={`${getStatusColor(env.status)} text-white`}>
                      {env.status}
                    </Badge>
                  </div>
                  <CardDescription className="flex items-center space-x-4 text-sm">
                    <span className="flex items-center space-x-1">
                      <Clock className="h-3 w-3" />
                      <span>{formatUptime(env.created_at)}</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <Users className="h-3 w-3" />
                      <span>{env.collaborators.length + 1}</span>
                    </span>
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-muted-foreground">
                      <p>{env.resources.memory} • {env.resources.cpu}</p>
                    </div>
                    <div className="flex space-x-1">
                      {env.status === 'ready' && (
                        <Button size="sm" variant="outline" onClick={(e) => {
                          e.stopPropagation();
                          stopEnvironment(env.id);
                        }}>
                          <Square className="h-3 w-3" />
                        </Button>
                      )}
                      <Button size="sm" variant="outline" onClick={(e) => {
                        e.stopPropagation();
                        deleteEnvironment(env.id);
                      }}>
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                  
                  {/* Access Links */}
                  {Object.keys(env.endpoints).length > 0 && (
                    <div className="mt-3 space-y-1">
                      {Object.entries(env.endpoints).map(([name, url]) => (
                        url && (
                          <a
                            key={name}
                            href={url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block text-sm text-blue-600 hover:text-blue-800 underline"
                            onClick={(e) => e.stopPropagation()}
                          >
                            Open {name}
                          </a>
                        )
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>

          {environments.length === 0 && (
            <div className="text-center py-12">
              <Activity className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No environments yet</h3>
              <p className="text-muted-foreground mb-4">Create your first development environment to get started</p>
              <Button onClick={() => setShowCreateDialog(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Create Environment
              </Button>
            </div>
          )}
        </TabsContent>

        <TabsContent value="templates" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {templates.map((template) => (
              <Card key={template.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center space-x-2">
                      {getTypeIcon(template.type)}
                      <span>{template.name}</span>
                    </CardTitle>
                    <Badge variant="outline">{template.type}</Badge>
                  </div>
                  <CardDescription>{template.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex flex-wrap gap-1">
                      {template.tags.map((tag) => (
                        <Badge key={tag} variant="secondary" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                    
                    <div className="text-sm text-muted-foreground">
                      <p>{template.required_resources.memory} • {template.required_resources.cpu}</p>
                    </div>
                    
                    <Button 
                      className="w-full" 
                      onClick={() => {
                        const name = prompt('Enter environment name:');
                        if (name) {
                          createEnvironment(template.id, name);
                        }
                      }}
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      Create from Template
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="monitoring" className="space-y-4">
          <ResourceMonitor />
        </TabsContent>
      </Tabs>

      {/* Environment Details Modal */}
      {selectedEnvironment && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold">{selectedEnvironment.name}</h3>
                <Button variant="outline" onClick={() => setSelectedEnvironment(null)}>
                  Close
                </Button>
              </div>
              
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="font-medium">Status</p>
                    <Badge className={`${getStatusColor(selectedEnvironment.status)} text-white`}>
                      {selectedEnvironment.status}
                    </Badge>
                  </div>
                  <div>
                    <p className="font-medium">Type</p>
                    <div className="flex items-center space-x-1">
                      {getTypeIcon(selectedEnvironment.type)}
                      <span>{selectedEnvironment.type}</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <p className="font-medium mb-2">Resources</p>
                  <div className="bg-gray-50 p-3 rounded text-sm">
                    <p>Memory: {selectedEnvironment.resources.memory}</p>
                    <p>CPU: {selectedEnvironment.resources.cpu}</p>
                    <p>Storage: {selectedEnvironment.resources.storage}</p>
                  </div>
                </div>
                
                <div>
                  <p className="font-medium mb-2">Endpoints</p>
                  <div className="space-y-2">
                    {Object.entries(selectedEnvironment.endpoints).map(([name, url]) => (
                      url && (
                        <div key={name} className="flex items-center justify-between bg-gray-50 p-2 rounded">
                          <span className="text-sm">{name}</span>
                          <a
                            href={url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-800 text-sm underline"
                          >
                            Open
                          </a>
                        </div>
                      )
                    ))}
                  </div>
                </div>
                
                <div>
                  <p className="font-medium mb-2">Collaborators</p>
                  <div className="flex flex-wrap gap-2">
                    <Badge variant="outline">{selectedEnvironment.owner} (Owner)</Badge>
                    {selectedEnvironment.collaborators.map((collaborator) => (
                      <Badge key={collaborator} variant="secondary">{collaborator}</Badge>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create Environment Dialog */}
      {showCreateDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full">
            <div className="p-6">
              <h3 className="text-xl font-bold mb-4">Create New Environment</h3>
              
              <div className="space-y-4">
                <p className="text-muted-foreground">
                  Choose a template to create your new development environment:
                </p>
                
                <div className="space-y-2">
                  {templates.map((template) => (
                    <Button
                      key={template.id}
                      variant="outline"
                      className="w-full justify-start h-auto p-3"
                      onClick={() => {
                        const name = prompt(`Enter name for ${template.name} environment:`);
                        if (name) {
                          createEnvironment(template.id, name);
                        }
                      }}
                    >
                      <div className="text-left">
                        <div className="flex items-center space-x-2 mb-1">
                          {getTypeIcon(template.type)}
                          <span className="font-medium">{template.name}</span>
                        </div>
                        <p className="text-sm text-muted-foreground">{template.description}</p>
                      </div>
                    </Button>
                  ))}
                </div>
                
                <div className="flex justify-end space-x-2">
                  <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                    Cancel
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnvironmentOrchestrator;