import React, { useState, useCallback, useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';
import WindowManager, { WindowState } from './window-manager';
import MultiTerminal from './multi-terminal';
import { DragDropPanel, DropZone } from './drag-drop-panel';
import { Button } from './button';
import { Badge } from './badge';
import {
  Layout,
  Monitor,
  Terminal,
  Code,
  Globe,
  FileText,
  Settings,
  Grid3X3,
  Maximize2,
  Minimize2,
  Plus,
  RotateCcw,
  Save,
  FolderOpen,
  Palette,
  MousePointer2,
  Eye,
  EyeOff,
  Lock,
  Unlock
} from 'lucide-react';

interface WorkspacePanel {
  id: string;
  title: string;
  type: 'terminal' | 'monitor' | 'editor' | 'browser' | 'custom';
  component: React.ComponentType<any>;
  props?: any;
  position: { x: number; y: number };
  size: { width: number; height: number };
  visible: boolean;
  locked: boolean;
  collapsed: boolean;
}

interface WorkspaceTheme {
  name: string;
  background: string;
  panelBg: string;
  headerBg: string;
  accent: string;
  text: string;
}

interface WorkspaceLayout {
  id: string;
  name: string;
  panels: WorkspacePanel[];
  theme: string;
  windowLayout?: WindowState[];
}

const AdvancedWorkspace: React.FC = () => {
  const [panels, setPanels] = useState<WorkspacePanel[]>([]);
  const [showWindowManager, setShowWindowManager] = useState(false);
  const [currentTheme, setCurrentTheme] = useState<string>('dark');
  const [isLayoutMode, setIsLayoutMode] = useState(false);
  const [savedLayouts, setSavedLayouts] = useState<WorkspaceLayout[]>([]);
  const [showThemeSelector, setShowThemeSelector] = useState(false);
  
  const workspaceRef = useRef<HTMLDivElement>(null);

  // Available themes
  const themes: Record<string, WorkspaceTheme> = {
    dark: {
      name: 'Dark',
      background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
      panelBg: 'rgba(30, 41, 59, 0.95)',
      headerBg: 'rgba(15, 23, 42, 0.95)',
      accent: '#3b82f6',
      text: '#f1f5f9'
    },
    light: {
      name: 'Light',
      background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
      panelBg: 'rgba(248, 250, 252, 0.95)',
      headerBg: 'rgba(226, 232, 240, 0.95)',
      accent: '#3b82f6',
      text: '#1e293b'
    },
    ocean: {
      name: 'Ocean',
      background: 'linear-gradient(135deg, #0ea5e9 0%, #0284c7 50%, #0369a1 100%)',
      panelBg: 'rgba(14, 165, 233, 0.1)',
      headerBg: 'rgba(2, 132, 199, 0.2)',
      accent: '#06b6d4',
      text: '#f0f9ff'
    },
    forest: {
      name: 'Forest',
      background: 'linear-gradient(135deg, #059669 0%, #047857 50%, #065f46 100%)',
      panelBg: 'rgba(5, 150, 105, 0.1)',
      headerBg: 'rgba(4, 120, 87, 0.2)',
      accent: '#10b981',
      text: '#ecfdf5'
    },
    sunset: {
      name: 'Sunset',
      background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 50%, #b45309 100%)',
      panelBg: 'rgba(245, 158, 11, 0.1)',
      headerBg: 'rgba(217, 119, 6, 0.2)',
      accent: '#f97316',
      text: '#fffbeb'
    }
  };

  // Create panel
  const createPanel = useCallback((
    type: WorkspacePanel['type'],
    title: string,
    component: React.ComponentType<any>,
    props: any = {}
  ) => {
    const id = `panel-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    // Calculate position (cascade new panels)
    const baseX = 50 + panels.length * 30;
    const baseY = 50 + panels.length * 30;
    
    const newPanel: WorkspacePanel = {
      id,
      title,
      type,
      component,
      props,
      position: { x: baseX, y: baseY },
      size: { width: 400, height: 300 },
      visible: true,
      locked: false,
      collapsed: false
    };

    setPanels(prev => [...prev, newPanel]);
    return id;
  }, [panels.length]);

  // Update panel
  const updatePanel = useCallback((id: string, updates: Partial<WorkspacePanel>) => {
    setPanels(prev => prev.map(panel => 
      panel.id === id ? { ...panel, ...updates } : panel
    ));
  }, []);

  // Remove panel
  const removePanel = useCallback((id: string) => {
    setPanels(prev => prev.filter(panel => panel.id !== id));
  }, []);

  // Toggle panel visibility
  const togglePanelVisibility = useCallback((id: string) => {
    updatePanel(id, { visible: false });
  }, [updatePanel]);

  // Save current layout
  const saveLayout = useCallback(() => {
    const layoutName = prompt('Enter layout name:');
    if (!layoutName) return;

    const layout: WorkspaceLayout = {
      id: `layout-${Date.now()}`,
      name: layoutName,
      panels: panels.map(panel => ({ ...panel })),
      theme: currentTheme
    };

    setSavedLayouts(prev => [...prev, layout]);
  }, [panels, currentTheme]);

  // Load layout
  const loadLayout = useCallback((layout: WorkspaceLayout) => {
    setPanels(layout.panels);
    setCurrentTheme(layout.theme);
  }, []);

  // Clear workspace
  const clearWorkspace = useCallback(() => {
    if (confirm('Clear all panels? This action cannot be undone.')) {
      setPanels([]);
    }
  }, []);

  // Quick panel creators
  const createTerminalPanel = useCallback(() => {
    createPanel('terminal', 'Terminal', MultiTerminal);
  }, [createPanel]);

  const createMonitorPanel = useCallback(() => {
    createPanel('monitor', 'System Monitor', ({ children }: any) => (
      <div className="p-4 h-full">
        <div className="flex items-center justify-center h-full bg-gray-900 text-green-400 rounded">
          <div className="text-center">
            <Monitor className="h-12 w-12 mx-auto mb-4" />
            <h3 className="text-lg font-bold mb-2">System Monitor</h3>
            <p className="text-sm">CPU, Memory, Network monitoring</p>
          </div>
        </div>
      </div>
    ));
  }, [createPanel]);

  const createCodeEditorPanel = useCallback(() => {
    createPanel('editor', 'Code Editor', ({ children }: any) => (
      <div className="p-4 h-full">
        <div className="flex items-center justify-center h-full bg-gray-800 text-white rounded">
          <div className="text-center">
            <Code className="h-12 w-12 mx-auto mb-4" />
            <h3 className="text-lg font-bold mb-2">Code Editor</h3>
            <p className="text-sm">Integrated development environment</p>
          </div>
        </div>
      </div>
    ));
  }, [createPanel]);

  const createBrowserPanel = useCallback(() => {
    createPanel('browser', 'Browser', ({ children }: any) => (
      <div className="p-4 h-full">
        <div className="flex items-center justify-center h-full bg-blue-50 text-blue-800 rounded">
          <div className="text-center">
            <Globe className="h-12 w-12 mx-auto mb-4" />
            <h3 className="text-lg font-bold mb-2">Browser</h3>
            <p className="text-sm">Embedded web browser</p>
          </div>
        </div>
      </div>
    ));
  }, [createPanel]);

  // Predefined layouts
  const createDevelopmentLayout = useCallback(() => {
    setPanels([]);
    setTimeout(() => {
      createPanel('editor', 'Code Editor', ({ children }: any) => (
        <div className="p-4 h-full">
          <div className="flex items-center justify-center h-full bg-gray-800 text-white rounded">
            <div className="text-center">
              <Code className="h-12 w-12 mx-auto mb-4" />
              <h3 className="text-lg font-bold mb-2">Code Editor</h3>
              <p className="text-sm">Main development interface</p>
            </div>
          </div>
        </div>
      ));
      
      setTimeout(() => {
        const terminalId = createPanel('terminal', 'Terminal', MultiTerminal);
        updatePanel(terminalId, { 
          position: { x: 50, y: 350 },
          size: { width: 600, height: 250 }
        });
      }, 100);
      
      setTimeout(() => {
        const browserId = createPanel('browser', 'Preview', ({ children }: any) => (
          <div className="p-4 h-full">
            <div className="flex items-center justify-center h-full bg-blue-50 text-blue-800 rounded">
              <div className="text-center">
                <Globe className="h-12 w-12 mx-auto mb-4" />
                <h3 className="text-lg font-bold mb-2">Live Preview</h3>
                <p className="text-sm">Application preview</p>
              </div>
            </div>
          </div>
        ));
        updatePanel(browserId, { 
          position: { x: 670, y: 50 },
          size: { width: 400, height: 500 }
        });
      }, 200);
    }, 100);
  }, [createPanel, updatePanel]);

  const createMonitoringLayout = useCallback(() => {
    setPanels([]);
    setTimeout(() => {
      // System monitor
      createPanel('monitor', 'System Monitor', ({ children }: any) => (
        <div className="p-4 h-full">
          <div className="flex items-center justify-center h-full bg-gray-900 text-green-400 rounded">
            <div className="text-center">
              <Monitor className="h-12 w-12 mx-auto mb-4" />
              <h3 className="text-lg font-bold mb-2">System Resources</h3>
              <p className="text-sm">CPU, Memory, Disk usage</p>
            </div>
          </div>
        </div>
      ));
      
      setTimeout(() => {
        const networkId = createPanel('monitor', 'Network Monitor', ({ children }: any) => (
          <div className="p-4 h-full">
            <div className="flex items-center justify-center h-full bg-purple-900 text-purple-200 rounded">
              <div className="text-center">
                <Globe className="h-12 w-12 mx-auto mb-4" />
                <h3 className="text-lg font-bold mb-2">Network Activity</h3>
                <p className="text-sm">Traffic, connections, latency</p>
              </div>
            </div>
          </div>
        ));
        updatePanel(networkId, { 
          position: { x: 450, y: 50 },
          size: { width: 400, height: 300 }
        });
      }, 100);
      
      setTimeout(() => {
        const logsId = createPanel('terminal', 'Logs', MultiTerminal);
        updatePanel(logsId, { 
          position: { x: 50, y: 370 },
          size: { width: 800, height: 200 }
        });
      }, 200);
    }, 100);
  }, [createPanel, updatePanel]);

  // Get current theme
  const theme = themes[currentTheme];

  // Handle drop
  const handleDrop = useCallback((panelId: string, zoneId: string) => {
    console.log(`Panel ${panelId} dropped on zone ${zoneId}`);
    // Implement panel docking logic here
  }, []);

  return (
    <div 
      ref={workspaceRef}
      className="relative w-full h-full overflow-hidden"
      style={{ 
        background: theme.background,
        color: theme.text
      }}
    >
      {/* Workspace Toolbar */}
      <div className="absolute top-4 left-4 right-4 z-50 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {/* Workspace Controls */}
          <div 
            className="backdrop-blur-sm border border-white/20 rounded-lg shadow-lg p-2"
            style={{ backgroundColor: theme.panelBg }}
          >
            <div className="flex items-center space-x-2">
              <Layout className="h-5 w-5" style={{ color: theme.accent }} />
              <span className="text-sm font-medium">Advanced Workspace</span>
              <Badge variant="secondary" className="text-xs">
                {panels.filter(p => p.visible).length} panels
              </Badge>
            </div>
          </div>

          {/* Quick Actions */}
          <div 
            className="backdrop-blur-sm border border-white/20 rounded-lg shadow-lg p-2"
            style={{ backgroundColor: theme.panelBg }}
          >
            <div className="flex items-center space-x-1">
              <Button
                size="sm"
                variant="ghost"
                onClick={createTerminalPanel}
                title="New Terminal"
                className="h-8 w-8 p-0"
              >
                <Terminal className="h-4 w-4" />
              </Button>
              
              <Button
                size="sm"
                variant="ghost"
                onClick={createCodeEditorPanel}
                title="New Code Editor"
                className="h-8 w-8 p-0"
              >
                <Code className="h-4 w-4" />
              </Button>
              
              <Button
                size="sm"
                variant="ghost"
                onClick={createMonitorPanel}
                title="New Monitor"
                className="h-8 w-8 p-0"
              >
                <Monitor className="h-4 w-4" />
              </Button>
              
              <Button
                size="sm"
                variant="ghost"
                onClick={createBrowserPanel}
                title="New Browser"
                className="h-8 w-8 p-0"
              >
                <Globe className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Layout Presets */}
          <div 
            className="backdrop-blur-sm border border-white/20 rounded-lg shadow-lg p-2"
            style={{ backgroundColor: theme.panelBg }}
          >
            <div className="flex items-center space-x-1">
              <Button
                size="sm"
                variant="ghost"
                onClick={createDevelopmentLayout}
                title="Development Layout"
                className="h-8 px-3 text-xs"
              >
                <Code className="h-3 w-3 mr-1" />
                Dev
              </Button>
              
              <Button
                size="sm"
                variant="ghost"
                onClick={createMonitoringLayout}
                title="Monitoring Layout"
                className="h-8 px-3 text-xs"
              >
                <Monitor className="h-3 w-3 mr-1" />
                Monitor
              </Button>
            </div>
          </div>
        </div>

        {/* Right Side Controls */}
        <div className="flex items-center space-x-2">
          {/* Theme Selector */}
          <div className="relative">
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setShowThemeSelector(!showThemeSelector)}
              className="h-8 w-8 p-0"
              title="Change Theme"
              style={{ 
                backgroundColor: showThemeSelector ? theme.accent : 'transparent',
                color: showThemeSelector ? 'white' : theme.text
              }}
            >
              <Palette className="h-4 w-4" />
            </Button>
            
            {showThemeSelector && (
              <div 
                className="absolute top-full right-0 mt-1 backdrop-blur-sm border border-white/20 rounded-lg shadow-lg p-2 min-w-32 z-10"
                style={{ backgroundColor: theme.panelBg }}
              >
                {Object.entries(themes).map(([key, themeOption]) => (
                  <button
                    key={key}
                    onClick={() => {
                      setCurrentTheme(key);
                      setShowThemeSelector(false);
                    }}
                    className={cn(
                      'w-full flex items-center space-x-2 px-2 py-1 text-sm rounded transition-colors',
                      key === currentTheme 
                        ? 'bg-blue-500 text-white' 
                        : 'hover:bg-white/10'
                    )}
                  >
                    <div 
                      className="w-3 h-3 rounded-full border border-white/20"
                      style={{ background: themeOption.accent }}
                    />
                    <span>{themeOption.name}</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Window Manager Toggle */}
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setShowWindowManager(!showWindowManager)}
            className="h-8 w-8 p-0"
            title="Toggle Window Manager"
            style={{ 
              backgroundColor: showWindowManager ? theme.accent : 'transparent',
              color: showWindowManager ? 'white' : theme.text
            }}
          >
            <Grid3X3 className="h-4 w-4" />
          </Button>

          {/* Layout Mode Toggle */}
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setIsLayoutMode(!isLayoutMode)}
            className="h-8 w-8 p-0"
            title="Layout Mode"
            style={{ 
              backgroundColor: isLayoutMode ? theme.accent : 'transparent',
              color: isLayoutMode ? 'white' : theme.text
            }}
          >
            <MousePointer2 className="h-4 w-4" />
          </Button>

          {/* Save/Load */}
          <div 
            className="backdrop-blur-sm border border-white/20 rounded-lg shadow-lg p-1"
            style={{ backgroundColor: theme.panelBg }}
          >
            <div className="flex items-center space-x-1">
              <Button
                size="sm"
                variant="ghost"
                onClick={saveLayout}
                title="Save Layout"
                className="h-6 w-6 p-0"
              >
                <Save className="h-3 w-3" />
              </Button>
              
              <Button
                size="sm"
                variant="ghost"
                onClick={clearWorkspace}
                title="Clear Workspace"
                className="h-6 w-6 p-0"
              >
                <RotateCcw className="h-3 w-3" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Window Manager Overlay */}
      {showWindowManager && (
        <div className="absolute inset-0 z-30">
          <WindowManager />
        </div>
      )}

      {/* Drop Zones */}
      {isLayoutMode && (
        <>
          <DropZone
            id="left"
            onDrop={handleDrop}
            className="absolute left-4 top-20 bottom-4 w-32"
          >
            <div className="h-full flex items-center justify-center">
              <span className="text-xs opacity-60">Left Zone</span>
            </div>
          </DropZone>
          
          <DropZone
            id="right"
            onDrop={handleDrop}
            className="absolute right-4 top-20 bottom-4 w-32"
          >
            <div className="h-full flex items-center justify-center">
              <span className="text-xs opacity-60">Right Zone</span>
            </div>
          </DropZone>
          
          <DropZone
            id="bottom"
            onDrop={handleDrop}
            className="absolute left-40 right-40 bottom-4 h-32"
          >
            <div className="h-full flex items-center justify-center">
              <span className="text-xs opacity-60">Bottom Zone</span>
            </div>
          </DropZone>
        </>
      )}

      {/* Panels */}
      {panels
        .filter(panel => panel.visible)
        .map(panel => {
          const PanelComponent = panel.component;
          
          return (
            <div
              style={{
                position: 'absolute',
                left: panel.position.x,
                top: panel.position.y,
                width: panel.size.width,
                height: panel.size.height,
              }}
            >
              <DragDropPanel
                key={panel.id}
                id={panel.id}
                title={panel.title}
                className={cn(
                  "w-full h-full border-white/20",
                  panel.locked && "border-2"
                )}
                headerClassName="backdrop-blur-sm border-white/20"
                contentClassName="backdrop-blur-sm"
                locked={panel.locked}
                onClose={removePanel}
                onCollapse={(id, collapsed) => updatePanel(id, { collapsed })}
                onLock={(id, locked) => updatePanel(id, { locked })}
                onResize={(id, size) => updatePanel(id, { size })}
                onDragEnd={(id, position) => updatePanel(id, { position })}
              >
                <PanelComponent {...panel.props} />
              </DragDropPanel>
            </div>
          );
        })}

      {/* Empty State */}
      {panels.filter(p => p.visible).length === 0 && !showWindowManager && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center max-w-lg">
            <div 
              className="backdrop-blur-sm border border-white/20 rounded-xl p-12 shadow-2xl"
              style={{ backgroundColor: theme.panelBg }}
            >
              <Layout className="h-20 w-20 mx-auto mb-6 opacity-50" />
              <h2 className="text-3xl font-bold mb-4">Advanced Workspace</h2>
              <p className="text-lg opacity-80 mb-8">
                Create resizable panels, organize your workflow, and customize your development environment.
              </p>
              <div className="flex flex-wrap justify-center gap-3">
                <Button 
                  onClick={createDevelopmentLayout}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700"
                >
                  <Code className="h-4 w-4 mr-2" />
                  Development Layout
                </Button>
                <Button 
                  onClick={createMonitoringLayout}
                  variant="outline"
                  style={{ borderColor: theme.accent, color: theme.accent }}
                >
                  <Monitor className="h-4 w-4 mr-2" />
                  Monitoring Layout
                </Button>
                <Button 
                  onClick={() => setShowWindowManager(true)}
                  variant="outline"
                  style={{ borderColor: theme.accent, color: theme.accent }}
                >
                  <Grid3X3 className="h-4 w-4 mr-2" />
                  Window Manager
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Layout Mode Indicator */}
      {isLayoutMode && (
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 z-50">
          <div 
            className="backdrop-blur-sm border border-white/20 rounded-lg shadow-lg px-4 py-2"
            style={{ backgroundColor: theme.panelBg }}
          >
            <div className="flex items-center space-x-2">
              <MousePointer2 className="h-4 w-4" style={{ color: theme.accent }} />
              <span className="text-sm font-medium">Layout Mode Active</span>
              <span className="text-xs opacity-60">Drag panels to drop zones</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdvancedWorkspace;