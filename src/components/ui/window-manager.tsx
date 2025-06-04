import React, { useState, useCallback, useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';
import ResizableWindow, { WindowProps } from './resizable-window';
import { 
  Plus, 
  Grid3X3, 
  Maximize, 
  Monitor,
  Square,
  Minimize2,
  Layout,
  Settings,
  ChevronDown,
  Terminal,
  Globe,
  FileText,
  Code
} from 'lucide-react';
import { Button } from './button';
import { Badge } from './badge';

export interface WindowState {
  id: string;
  title: string;
  component: React.ComponentType<any>;
  props?: any;
  position: { x: number; y: number };
  size: { width: number; height: number };
  isMinimized: boolean;
  isMaximized: boolean;
  zIndex: number;
  icon?: React.ReactNode;
  type: 'terminal' | 'browser' | 'editor' | 'monitor' | 'custom';
}

interface WindowManagerProps {
  children?: React.ReactNode;
  className?: string;
}

interface LayoutPreset {
  name: string;
  icon: React.ReactNode;
  windows: Partial<WindowState>[];
}

const WindowManager: React.FC<WindowManagerProps> = ({ children, className }) => {
  const [windows, setWindows] = useState<WindowState[]>([]);
  const [nextZIndex, setNextZIndex] = useState(1);
  const [showLayoutMenu, setShowLayoutMenu] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Layout presets
  const layoutPresets: LayoutPreset[] = [
    {
      name: 'Development',
      icon: <Code className="h-4 w-4" />,
      windows: [
        {
          title: 'Code Editor',
          size: { width: 800, height: 600 },
          position: { x: 50, y: 50 },
          type: 'editor',
          icon: <FileText className="h-4 w-4" />
        },
        {
          title: 'Terminal',
          size: { width: 600, height: 300 },
          position: { x: 50, y: 670 },
          type: 'terminal',
          icon: <Terminal className="h-4 w-4" />
        },
        {
          title: 'Globe',
          size: { width: 500, height: 600 },
          position: { x: 870, y: 50 },
          type: 'browser',
          icon: <Globe className="h-4 w-4" />
        }
      ]
    },
    {
      name: 'Monitoring',
      icon: <Monitor className="h-4 w-4" />,
      windows: [
        {
          title: 'System Monitor',
          size: { width: 600, height: 400 },
          position: { x: 50, y: 50 },
          type: 'monitor',
          icon: <Monitor className="h-4 w-4" />
        },
        {
          title: 'Environment Status',
          size: { width: 600, height: 400 },
          position: { x: 670, y: 50 },
          type: 'monitor',
          icon: <Monitor className="h-4 w-4" />
        },
        {
          title: 'Logs',
          size: { width: 1220, height: 300 },
          position: { x: 50, y: 470 },
          type: 'terminal',
          icon: <Terminal className="h-4 w-4" />
        }
      ]
    },
    {
      name: 'Tiled',
      icon: <Grid3X3 className="h-4 w-4" />,
      windows: [
        {
          title: 'Top Left',
          size: { width: 640, height: 360 },
          position: { x: 50, y: 50 },
          type: 'custom'
        },
        {
          title: 'Top Right',
          size: { width: 640, height: 360 },
          position: { x: 710, y: 50 },
          type: 'custom'
        },
        {
          title: 'Bottom Left',
          size: { width: 640, height: 360 },
          position: { x: 50, y: 430 },
          type: 'custom'
        },
        {
          title: 'Bottom Right',
          size: { width: 640, height: 360 },
          position: { x: 710, y: 430 },
          type: 'custom'
        }
      ]
    }
  ];

  // Create a new window
  const createWindow = useCallback((
    title: string,
    component: React.ComponentType<any>,
    options: Partial<WindowState> = {}
  ) => {
    const id = `window-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    // Calculate initial position (cascade windows)
    const cascade = windows.length * 30;
    const defaultPosition = { 
      x: 100 + cascade, 
      y: 100 + cascade 
    };
    
    const newWindow: WindowState = {
      id,
      title,
      component,
      position: options.position || defaultPosition,
      size: options.size || { width: 600, height: 400 },
      isMinimized: false,
      isMaximized: false,
      zIndex: nextZIndex,
      type: options.type || 'custom',
      icon: options.icon,
      props: options.props,
      ...options
    };

    setWindows(prev => [...prev, newWindow]);
    setNextZIndex(prev => prev + 1);
    
    return id;
  }, [windows.length, nextZIndex]);

  // Focus window (bring to front)
  const focusWindow = useCallback((id: string) => {
    setWindows(prev => prev.map(window => ({
      ...window,
      zIndex: window.id === id ? nextZIndex : window.zIndex
    })));
    setNextZIndex(prev => prev + 1);
  }, [nextZIndex]);

  // Close window
  const closeWindow = useCallback((id: string) => {
    setWindows(prev => prev.filter(window => window.id !== id));
  }, []);

  // Minimize window
  const minimizeWindow = useCallback((id: string) => {
    setWindows(prev => prev.map(window => ({
      ...window,
      isMinimized: window.id === id ? !window.isMinimized : window.isMinimized
    })));
  }, []);

  // Maximize window
  const maximizeWindow = useCallback((id: string) => {
    setWindows(prev => prev.map(window => ({
      ...window,
      isMaximized: window.id === id ? !window.isMaximized : window.isMaximized
    })));
  }, []);

  // Update window position
  const updateWindowPosition = useCallback((id: string, position: { x: number; y: number }) => {
    setWindows(prev => prev.map(window => ({
      ...window,
      position: window.id === id ? position : window.position
    })));
  }, []);

  // Update window size
  const updateWindowSize = useCallback((id: string, size: { width: number; height: number }) => {
    setWindows(prev => prev.map(window => ({
      ...window,
      size: window.id === id ? size : window.size
    })));
  }, []);

  // Apply layout preset
  const applyLayoutPreset = useCallback((preset: LayoutPreset) => {
    // Clear existing windows
    setWindows([]);
    
    // Create windows from preset
    setTimeout(() => {
      preset.windows.forEach((windowConfig, index) => {
        createWindow(
          windowConfig.title || `Window ${index + 1}`,
          ({ children }: { children?: React.ReactNode }) => (
            <div className="flex items-center justify-center h-full bg-gray-50 text-gray-500">
              <div className="text-center">
                {windowConfig.icon}
                <p className="mt-2 text-sm">{windowConfig.title}</p>
                <p className="text-xs text-gray-400">Content placeholder</p>
              </div>
            </div>
          ),
          windowConfig
        );
      });
      setShowLayoutMenu(false);
    }, 100);
  }, [createWindow]);

  // Arrange windows
  const arrangeWindows = useCallback((arrangement: 'cascade' | 'tile' | 'stack') => {
    const visibleWindows = windows.filter(w => !w.isMinimized);
    
    if (arrangement === 'cascade') {
      setWindows(prev => prev.map((window, index) => ({
        ...window,
        position: { x: 50 + index * 30, y: 50 + index * 30 },
        size: { width: 600, height: 400 },
        isMaximized: false
      })));
    } else if (arrangement === 'tile') {
      const containerWidth = window.innerWidth - 100;
      const containerHeight = window.innerHeight - 150;
      const cols = Math.ceil(Math.sqrt(visibleWindows.length));
      const rows = Math.ceil(visibleWindows.length / cols);
      const windowWidth = containerWidth / cols;
      const windowHeight = containerHeight / rows;
      
      setWindows(prev => prev.map((window, index) => {
        if (window.isMinimized) return window;
        
        const visibleIndex = visibleWindows.findIndex(w => w.id === window.id);
        const col = visibleIndex % cols;
        const row = Math.floor(visibleIndex / cols);
        
        return {
          ...window,
          position: { x: 50 + col * windowWidth, y: 50 + row * windowHeight },
          size: { width: windowWidth - 10, height: windowHeight - 10 },
          isMaximized: false
        };
      }));
    } else if (arrangement === 'stack') {
      setWindows(prev => prev.map((window, index) => ({
        ...window,
        position: { x: 100, y: 100 },
        size: { width: 800, height: 600 },
        isMaximized: false,
        zIndex: index + 1
      })));
    }
  }, [windows]);

  // Get window icon
  const getWindowIcon = (type: string) => {
    switch (type) {
      case 'terminal': return <Terminal className="h-4 w-4" />;
      case 'browser': return <Globe className="h-4 w-4" />;
      case 'editor': return <FileText className="h-4 w-4" />;
      case 'monitor': return <Monitor className="h-4 w-4" />;
      default: return <Square className="h-4 w-4" />;
    }
  };

  return (
    <div ref={containerRef} className={cn('relative w-full h-full overflow-hidden', className)}>
      {/* Window Manager Toolbar */}
      <div className="absolute top-4 left-4 z-50 flex items-center space-x-2">
        <div className="bg-white/90 backdrop-blur-sm border border-gray-200 rounded-lg shadow-lg p-2">
          <div className="flex items-center space-x-2">
            {/* New Window Button */}
            <Button
              size="sm"
              variant="ghost"
              onClick={() => createWindow(
                'New Window',
                ({ children }: { children?: React.ReactNode }) => (
                  <div className="flex items-center justify-center h-full bg-gray-50 text-gray-500">
                    <div className="text-center">
                      <Plus className="h-8 w-8 mx-auto mb-2" />
                      <p>New Window</p>
                    </div>
                  </div>
                )
              )}
              title="Create New Window"
            >
              <Plus className="h-4 w-4" />
            </Button>

            {/* Layout Presets */}
            <div className="relative">
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setShowLayoutMenu(!showLayoutMenu)}
                title="Layout Presets"
              >
                <Layout className="h-4 w-4" />
                <ChevronDown className="h-3 w-3 ml-1" />
              </Button>
              
              {showLayoutMenu && (
                <div className="absolute top-full left-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg min-w-48 z-10">
                  <div className="p-2">
                    <p className="text-xs font-medium text-gray-600 mb-2">Layout Presets</p>
                    {layoutPresets.map((preset) => (
                      <button
                        key={preset.name}
                        onClick={() => applyLayoutPreset(preset)}
                        className="w-full flex items-center space-x-2 px-2 py-1 text-sm hover:bg-gray-100 rounded"
                      >
                        {preset.icon}
                        <span>{preset.name}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Arrange Windows */}
            <Button
              size="sm"
              variant="ghost"
              onClick={() => arrangeWindows('cascade')}
              title="Cascade Windows"
            >
              <Grid3X3 className="h-4 w-4" />
            </Button>

            <Button
              size="sm"
              variant="ghost"
              onClick={() => arrangeWindows('tile')}
              title="Tile Windows"
            >
              <Maximize className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Active Windows Count */}
        {windows.length > 0 && (
          <Badge variant="secondary" className="bg-white/90 backdrop-blur-sm">
            {windows.filter(w => !w.isMinimized).length} active
          </Badge>
        )}
      </div>

      {/* Taskbar for Minimized Windows */}
      {windows.some(w => w.isMinimized) && (
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 z-50">
          <div className="bg-white/90 backdrop-blur-sm border border-gray-200 rounded-lg shadow-lg p-2">
            <div className="flex items-center space-x-2">
              {windows
                .filter(window => window.isMinimized)
                .map(window => (
                  <button
                    key={window.id}
                    onClick={() => minimizeWindow(window.id)}
                    className="flex items-center space-x-2 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
                    title={`Restore ${window.title}`}
                  >
                    {window.icon || getWindowIcon(window.type)}
                    <span className="text-sm font-medium">{window.title}</span>
                    <Minimize2 className="h-3 w-3 text-gray-500" />
                  </button>
                ))}
            </div>
          </div>
        </div>
      )}

      {/* Background Children */}
      {children}

      {/* Render Windows */}
      {windows
        .filter(window => !window.isMinimized)
        .map(window => {
          const WindowComponent = window.component;
          
          return (
            <ResizableWindow
              key={window.id}
              id={window.id}
              title={window.title}
              initialPosition={window.position}
              initialSize={window.size}
              isMaximized={window.isMaximized}
              zIndex={window.zIndex}
              onClose={closeWindow}
              onMinimize={minimizeWindow}
              onMaximize={maximizeWindow}
              onMove={updateWindowPosition}
              onResize={updateWindowSize}
              onFocus={focusWindow}
            >
              <WindowComponent {...(window.props || {})} />
            </ResizableWindow>
          );
        })}

      {/* Empty State */}
      {windows.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50">
          <div className="text-center">
            <div className="bg-white/80 backdrop-blur-sm rounded-xl p-8 shadow-xl border border-white/20">
              <Layout className="h-16 w-16 mx-auto mb-4 text-gray-400" />
              <h2 className="text-2xl font-bold text-gray-700 mb-2">Advanced Workspace</h2>
              <p className="text-gray-600 mb-6 max-w-md">
                Create resizable windows, organize your workspace, and boost your productivity with our advanced window management system.
              </p>
              <div className="flex flex-wrap justify-center gap-2">
                <Button
                  onClick={() => createWindow(
                    'Terminal',
                    ({ children }: { children?: React.ReactNode }) => (
                      <div className="flex items-center justify-center h-full bg-black text-green-400 font-mono">
                        <div className="text-center">
                          <Terminal className="h-8 w-8 mx-auto mb-2" />
                          <p>Terminal Window</p>
                          <p className="text-xs">$ Ready for commands...</p>
                        </div>
                      </div>
                    ),
                    { type: 'terminal', icon: <Terminal className="h-4 w-4" /> }
                  )}
                  variant="outline"
                >
                  <Terminal className="h-4 w-4 mr-2" />
                  Terminal
                </Button>
                
                <Button
                  onClick={() => createWindow(
                    'Globe',
                    ({ children }: { children?: React.ReactNode }) => (
                      <div className="flex items-center justify-center h-full bg-gray-100">
                        <div className="text-center text-gray-600">
                          <Globe className="h-8 w-8 mx-auto mb-2" />
                          <p>Globe Window</p>
                          <p className="text-xs">Ready to browse...</p>
                        </div>
                      </div>
                    ),
                    { type: 'browser', icon: <Globe className="h-4 w-4" /> }
                  )}
                  variant="outline"
                >
                  <Globe className="h-4 w-4 mr-2" />
                  Globe
                </Button>
                
                <Button
                  onClick={() => applyLayoutPreset(layoutPresets[0])}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 text-white"
                >
                  <Code className="h-4 w-4 mr-2" />
                  Development Layout
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WindowManager;