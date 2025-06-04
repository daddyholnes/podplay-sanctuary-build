import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Progress } from '../ui/progress';
import { Badge } from '../ui/badge';
import { 
  Activity, 
  Cpu, 
  HardDrive, 
  MemoryStick, 
  Network,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Clock,
  DollarSign,
  Zap
} from 'lucide-react';

interface ResourceMetrics {
  cpu: {
    usage: number;
    cores: number;
    temperature?: number;
  };
  memory: {
    used: number;
    total: number;
    usage_percent: number;
  };
  storage: {
    used: number;
    total: number;
    usage_percent: number;
  };
  network: {
    incoming: number;
    outgoing: number;
    connections: number;
  };
  environments: {
    total: number;
    running: number;
    stopped: number;
    error: number;
  };
  costs: {
    current_hour: number;
    daily_estimate: number;
    monthly_estimate: number;
  };
}

interface PerformanceAlert {
  id: string;
  type: 'warning' | 'error' | 'info';
  message: string;
  timestamp: string;
  resolved: boolean;
}

const ResourceMonitor: React.FC = () => {
  const [metrics, setMetrics] = useState<ResourceMetrics | null>(null);
  const [alerts, setAlerts] = useState<PerformanceAlert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMetrics();
    
    // Set up real-time monitoring
    const interval = setInterval(loadMetrics, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const loadMetrics = async () => {
    try {
      // In a real implementation, this would fetch from the orchestrator API
      // For now, we'll generate realistic mock data
      const mockMetrics: ResourceMetrics = {
        cpu: {
          usage: Math.random() * 100,
          cores: 8,
          temperature: 45 + Math.random() * 15
        },
        memory: {
          used: 8.5 + Math.random() * 3,
          total: 16,
          usage_percent: (8.5 + Math.random() * 3) / 16 * 100
        },
        storage: {
          used: 45 + Math.random() * 10,
          total: 100,
          usage_percent: (45 + Math.random() * 10)
        },
        network: {
          incoming: Math.random() * 100,
          outgoing: Math.random() * 50,
          connections: Math.floor(Math.random() * 20) + 5
        },
        environments: {
          total: 8,
          running: 5,
          stopped: 2,
          error: 1
        },
        costs: {
          current_hour: 0.15 + Math.random() * 0.1,
          daily_estimate: 3.5 + Math.random() * 1,
          monthly_estimate: 105 + Math.random() * 30
        }
      };

      setMetrics(mockMetrics);
      
      // Generate alerts based on metrics
      generateAlerts(mockMetrics);
      
    } catch (error) {
      console.error('Failed to load metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateAlerts = (metrics: ResourceMetrics) => {
    const newAlerts: PerformanceAlert[] = [];

    // CPU alert
    if (metrics.cpu.usage > 85) {
      newAlerts.push({
        id: 'cpu-high',
        type: 'warning',
        message: `High CPU usage detected: ${metrics.cpu.usage.toFixed(1)}%`,
        timestamp: new Date().toISOString(),
        resolved: false
      });
    }

    // Memory alert
    if (metrics.memory.usage_percent > 90) {
      newAlerts.push({
        id: 'memory-high',
        type: 'error',
        message: `Critical memory usage: ${metrics.memory.usage_percent.toFixed(1)}%`,
        timestamp: new Date().toISOString(),
        resolved: false
      });
    }

    // Storage alert
    if (metrics.storage.usage_percent > 80) {
      newAlerts.push({
        id: 'storage-high',
        type: 'warning',
        message: `Storage space running low: ${metrics.storage.usage_percent.toFixed(1)}% used`,
        timestamp: new Date().toISOString(),
        resolved: false
      });
    }

    // Environment errors
    if (metrics.environments.error > 0) {
      newAlerts.push({
        id: 'env-errors',
        type: 'error',
        message: `${metrics.environments.error} environment(s) in error state`,
        timestamp: new Date().toISOString(),
        resolved: false
      });
    }

    setAlerts(newAlerts);
  };

  const getUsageColor = (percentage: number) => {
    if (percentage < 50) return 'bg-green-500';
    if (percentage < 75) return 'bg-yellow-500';
    if (percentage < 90) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'error': return <AlertTriangle className="h-4 w-4 text-red-500" />;
      case 'warning': return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      default: return <CheckCircle className="h-4 w-4 text-blue-500" />;
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 GB';
    const k = 1024;
    const sizes = ['GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const formatNetworkSpeed = (speed: number) => {
    return `${speed.toFixed(1)} MB/s`;
  };

  if (loading || !metrics) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-2">
          <Activity className="h-6 w-6 animate-pulse" />
          <span>Loading resource metrics...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl font-bold">Resource Monitor</h3>
          <p className="text-muted-foreground">Real-time system performance and resource usage</p>
        </div>
        <Badge className="bg-green-500 text-white">
          <Activity className="h-3 w-3 mr-1" />
          Live
        </Badge>
      </div>

      {/* Alerts */}
      {alerts.length > 0 && (
        <Card className="border-yellow-200 bg-yellow-50">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-yellow-500" />
              <span>Performance Alerts</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {alerts.map((alert) => (
                <div key={alert.id} className="flex items-center space-x-2 p-2 bg-white rounded border">
                  {getAlertIcon(alert.type)}
                  <span className="text-sm">{alert.message}</span>
                  <Badge variant="secondary" className="ml-auto text-xs">
                    {new Date(alert.timestamp).toLocaleTimeString()}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Resource Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* CPU Usage */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center space-x-2 text-sm">
              <Cpu className="h-4 w-4" />
              <span>CPU Usage</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-2xl font-bold">{metrics.cpu.usage.toFixed(1)}%</span>
                <Badge variant="outline">{metrics.cpu.cores} cores</Badge>
              </div>
              <Progress 
                value={metrics.cpu.usage} 
                className={`h-2 ${getUsageColor(metrics.cpu.usage)}`}
              />
              {metrics.cpu.temperature && (
                <p className="text-xs text-muted-foreground">
                  Temperature: {metrics.cpu.temperature.toFixed(1)}°C
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Memory Usage */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center space-x-2 text-sm">
              <MemoryStick className="h-4 w-4" />
              <span>Memory Usage</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-2xl font-bold">{metrics.memory.usage_percent.toFixed(1)}%</span>
                <span className="text-sm text-muted-foreground">
                  {formatBytes(metrics.memory.used)} / {formatBytes(metrics.memory.total)}
                </span>
              </div>
              <Progress 
                value={metrics.memory.usage_percent} 
                className={`h-2 ${getUsageColor(metrics.memory.usage_percent)}`}
              />
            </div>
          </CardContent>
        </Card>

        {/* Storage Usage */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center space-x-2 text-sm">
              <HardDrive className="h-4 w-4" />
              <span>Storage Usage</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-2xl font-bold">{metrics.storage.usage_percent.toFixed(1)}%</span>
                <span className="text-sm text-muted-foreground">
                  {formatBytes(metrics.storage.used)} / {formatBytes(metrics.storage.total)}
                </span>
              </div>
              <Progress 
                value={metrics.storage.usage_percent} 
                className={`h-2 ${getUsageColor(metrics.storage.usage_percent)}`}
              />
            </div>
          </CardContent>
        </Card>

        {/* Network Activity */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center space-x-2 text-sm">
              <Network className="h-4 w-4" />
              <span>Network Activity</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-1">
                  <TrendingDown className="h-3 w-3 text-green-500" />
                  <span className="text-sm">{formatNetworkSpeed(metrics.network.incoming)}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <TrendingUp className="h-3 w-3 text-blue-500" />
                  <span className="text-sm">{formatNetworkSpeed(metrics.network.outgoing)}</span>
                </div>
              </div>
              <p className="text-xs text-muted-foreground">
                {metrics.network.connections} active connections
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Environment Status and Cost Tracking */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Environment Status */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="h-5 w-5" />
              <span>Environment Status</span>
            </CardTitle>
            <CardDescription>Current state of all managed environments</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center">
                <p className="text-3xl font-bold text-green-600">{metrics.environments.running}</p>
                <p className="text-sm text-muted-foreground">Running</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold text-gray-600">{metrics.environments.stopped}</p>
                <p className="text-sm text-muted-foreground">Stopped</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold text-blue-600">{metrics.environments.total}</p>
                <p className="text-sm text-muted-foreground">Total</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold text-red-600">{metrics.environments.error}</p>
                <p className="text-sm text-muted-foreground">Errors</p>
              </div>
            </div>
            
            <div className="mt-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm">Environment Health</span>
                <span className="text-sm">
                  {((metrics.environments.running / metrics.environments.total) * 100).toFixed(1)}%
                </span>
              </div>
              <Progress 
                value={(metrics.environments.running / metrics.environments.total) * 100}
                className="h-2"
              />
            </div>
          </CardContent>
        </Card>

        {/* Cost Tracking */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <DollarSign className="h-5 w-5" />
              <span>Cost Tracking</span>
            </CardTitle>
            <CardDescription>Resource usage costs and estimates</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Clock className="h-4 w-4 text-blue-500" />
                  <span className="text-sm">Current Hour</span>
                </div>
                <span className="font-bold">${metrics.costs.current_hour.toFixed(2)}</span>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Zap className="h-4 w-4 text-yellow-500" />
                  <span className="text-sm">Daily Estimate</span>
                </div>
                <span className="font-bold">${metrics.costs.daily_estimate.toFixed(2)}</span>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <TrendingUp className="h-4 w-4 text-green-500" />
                  <span className="text-sm">Monthly Estimate</span>
                </div>
                <span className="font-bold">${metrics.costs.monthly_estimate.toFixed(2)}</span>
              </div>
              
              <div className="pt-2 border-t">
                <p className="text-xs text-muted-foreground">
                  Costs calculated based on current resource usage and running environments
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Performance Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <CheckCircle className="h-5 w-5" />
            <span>Performance Recommendations</span>
          </CardTitle>
          <CardDescription>AI-powered suggestions for optimization</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {metrics.cpu.usage > 80 && (
              <div className="flex items-start space-x-2 p-3 bg-yellow-50 rounded border">
                <AlertTriangle className="h-4 w-4 text-yellow-500 mt-0.5" />
                <div>
                  <p className="text-sm font-medium">High CPU Usage Detected</p>
                  <p className="text-xs text-muted-foreground">
                    Consider scaling down non-critical environments or upgrading resources
                  </p>
                </div>
              </div>
            )}
            
            {metrics.storage.usage_percent > 75 && (
              <div className="flex items-start space-x-2 p-3 bg-blue-50 rounded border">
                <HardDrive className="h-4 w-4 text-blue-500 mt-0.5" />
                <div>
                  <p className="text-sm font-medium">Storage Cleanup Recommended</p>
                  <p className="text-xs text-muted-foreground">
                    Clean up unused environments and temporary files to free up space
                  </p>
                </div>
              </div>
            )}
            
            {metrics.environments.error > 0 && (
              <div className="flex items-start space-x-2 p-3 bg-red-50 rounded border">
                <AlertTriangle className="h-4 w-4 text-red-500 mt-0.5" />
                <div>
                  <p className="text-sm font-medium">Environment Errors Need Attention</p>
                  <p className="text-xs text-muted-foreground">
                    Check failed environments and restart or delete them to improve stability
                  </p>
                </div>
              </div>
            )}
            
            {alerts.length === 0 && (
              <div className="flex items-start space-x-2 p-3 bg-green-50 rounded border">
                <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
                <div>
                  <p className="text-sm font-medium">System Running Optimally</p>
                  <p className="text-xs text-muted-foreground">
                    All resources are within normal ranges. Great work!
                  </p>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ResourceMonitor;