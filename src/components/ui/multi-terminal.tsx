import React, { useState, useRef, useEffect, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { Button } from './button';
import { Badge } from './badge';
import { 
  Plus, 
  X, 
  Terminal, 
  SplitSquareHorizontal,
  SplitSquareVertical,
  Maximize2,
  Minimize2,
  Copy,
  Download,
  Settings,
  MoreHorizontal,
  ChevronDown,
  Play,
  Square,
  RotateCcw
} from 'lucide-react';

interface TerminalSession {
  id: string;
  title: string;
  command?: string;
  workingDirectory: string;
  isActive: boolean;
  output: string[];
  isRunning: boolean;
  lastActivity: Date;
}

interface TerminalPane {
  id: string;
  sessions: TerminalSession[];
  activeSessionId: string;
  position: 'full' | 'left' | 'right' | 'top' | 'bottom';
  size: number; // percentage
}

interface MultiTerminalProps {
  className?: string;
  onSessionCreate?: (session: TerminalSession) => void;
  onSessionClose?: (sessionId: string) => void;
  onCommand?: (sessionId: string, command: string) => void;
}

const MultiTerminal: React.FC<MultiTerminalProps> = ({
  className,
  onSessionCreate,
  onSessionClose,
  onCommand
}) => {
  const [panes, setPanes] = useState<TerminalPane[]>([
    {
      id: 'main',
      sessions: [{
        id: 'session-1',
        title: 'Main Terminal',
        workingDirectory: '/home/user',
        isActive: true,
        output: [
          '$ Welcome to Podplay Sanctuary Terminal',
          '$ Current directory: /home/user',
          '$ Type commands to interact with your environment...',
          ''
        ],
        isRunning: false,
        lastActivity: new Date()
      }],
      activeSessionId: 'session-1',
      position: 'full',
      size: 100
    }
  ]);

  const [splitOrientation, setSplitOrientation] = useState<'horizontal' | 'vertical'>('horizontal');
  const [showSettings, setShowSettings] = useState(false);
  const [fontSize, setFontSize] = useState(14);
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  
  const inputRefs = useRef<Map<string, HTMLInputElement>>(new Map());
  const outputRefs = useRef<Map<string, HTMLDivElement>>(new Map());

  // Create new session
  const createSession = useCallback((paneId: string, title?: string) => {
    const sessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const newSession: TerminalSession = {
      id: sessionId,
      title: title || `Terminal ${Date.now()}`,
      workingDirectory: '/home/user',
      isActive: false,
      output: [
        '$ New terminal session started',
        `$ Session ID: ${sessionId}`,
        '$ Ready for commands...',
        ''
      ],
      isRunning: false,
      lastActivity: new Date()
    };

    setPanes(prev => prev.map(pane => {
      if (pane.id === paneId) {
        return {
          ...pane,
          sessions: [...pane.sessions, newSession],
          activeSessionId: sessionId
        };
      }
      return pane;
    }));

    onSessionCreate?.(newSession);
  }, [onSessionCreate]);

  // Close session
  const closeSession = useCallback((paneId: string, sessionId: string) => {
    setPanes(prev => prev.map(pane => {
      if (pane.id === paneId) {
        const remainingSessions = pane.sessions.filter(s => s.id !== sessionId);
        const activeSession = remainingSessions.length > 0 
          ? remainingSessions[remainingSessions.length - 1].id 
          : '';
        
        return {
          ...pane,
          sessions: remainingSessions,
          activeSessionId: activeSession
        };
      }
      return pane;
    }));

    onSessionClose?.(sessionId);
  }, [onSessionClose]);

  // Switch to session
  const switchSession = useCallback((paneId: string, sessionId: string) => {
    setPanes(prev => prev.map(pane => ({
      ...pane,
      activeSessionId: pane.id === paneId ? sessionId : pane.activeSessionId
    })));
  }, []);

  // Split pane
  const splitPane = useCallback((paneId: string, orientation: 'horizontal' | 'vertical') => {
    const newPaneId = `pane-${Date.now()}`;
    const newSessionId = `session-${Date.now()}`;
    
    const newSession: TerminalSession = {
      id: newSessionId,
      title: 'Split Terminal',
      workingDirectory: '/home/user',
      isActive: true,
      output: [
        '$ Split terminal created',
        '$ Ready for commands...',
        ''
      ],
      isRunning: false,
      lastActivity: new Date()
    };

    setPanes(prev => {
      // Update existing panes to make room
      const updatedPanes = prev.map(pane => ({
        ...pane,
        size: pane.size / 2
      }));

      // Add new pane
      const newPane: TerminalPane = {
        id: newPaneId,
        sessions: [newSession],
        activeSessionId: newSessionId,
        position: orientation === 'horizontal' ? 'right' : 'bottom',
        size: 50
      };

      return [...updatedPanes, newPane];
    });

    setSplitOrientation(orientation);
  }, []);

  // Execute command
  const executeCommand = useCallback((sessionId: string, command: string) => {
    const trimmedCommand = command.trim();
    if (!trimmedCommand) return;

    setPanes(prev => prev.map(pane => ({
      ...pane,
      sessions: pane.sessions.map(session => {
        if (session.id === sessionId) {
          const newOutput = [
            ...session.output,
            `$ ${trimmedCommand}`,
            ...simulateCommandOutput(trimmedCommand),
            ''
          ];

          return {
            ...session,
            output: newOutput,
            lastActivity: new Date(),
            isRunning: trimmedCommand.includes('install') || trimmedCommand.includes('build')
          };
        }
        return session;
      })
    })));

    onCommand?.(sessionId, trimmedCommand);

    // Clear input
    const inputElement = inputRefs.current.get(sessionId);
    if (inputElement) {
      inputElement.value = '';
    }

    // Scroll to bottom
    setTimeout(() => {
      const outputElement = outputRefs.current.get(sessionId);
      if (outputElement) {
        outputElement.scrollTop = outputElement.scrollHeight;
      }
    }, 100);
  }, [onCommand]);

  // Simulate command output
  const simulateCommandOutput = (command: string): string[] => {
    const lowerCommand = command.toLowerCase();
    
    if (lowerCommand.startsWith('ls')) {
      return [
        'Documents  Downloads  Pictures  Projects',
        'Desktop    Music      Videos    workspace'
      ];
    } else if (lowerCommand.startsWith('pwd')) {
      return ['/home/user'];
    } else if (lowerCommand.startsWith('whoami')) {
      return ['user'];
    } else if (lowerCommand.startsWith('date')) {
      return [new Date().toString()];
    } else if (lowerCommand.startsWith('echo')) {
      return [command.substring(5)];
    } else if (lowerCommand.includes('install')) {
      return [
        'Installing packages...',
        'Reading package lists... Done',
        'Building dependency tree... Done',
        'The following packages will be installed:',
        '  package-name (1.0.0)',
        'Do you want to continue? [Y/n] Y',
        'Fetching packages...',
        'Installing...',
        'Successfully installed!'
      ];
    } else if (lowerCommand.includes('git')) {
      return [
        'On branch main',
        'Your branch is up to date with \'origin/main\'.',
        'nothing to commit, working tree clean'
      ];
    } else if (lowerCommand.startsWith('clear')) {
      return ['[2J[H']; // ANSI clear screen codes
    } else if (lowerCommand.startsWith('help')) {
      return [
        'Available commands:',
        '  ls       - List directory contents',
        '  pwd      - Print working directory',
        '  cd       - Change directory',
        '  echo     - Display text',
        '  git      - Git version control',
        '  npm      - Node package manager',
        '  python   - Python interpreter',
        '  clear    - Clear terminal',
        '  help     - Show this help message'
      ];
    } else {
      return [
        `${command}: command not found`,
        'Type "help" for available commands'
      ];
    }
  };

  // Handle key press
  const handleKeyPress = (e: React.KeyboardEvent, sessionId: string) => {
    if (e.key === 'Enter') {
      const input = (e.target as HTMLInputElement).value;
      executeCommand(sessionId, input);
    }
  };

  // Get active session for a pane
  const getActiveSession = (pane: TerminalPane): TerminalSession | undefined => {
    return pane.sessions.find(s => s.id === pane.activeSessionId);
  };

  // Render terminal content
  const renderTerminalContent = (pane: TerminalPane) => {
    const activeSession = getActiveSession(pane);
    if (!activeSession) return null;

    return (
      <div className="flex flex-col h-full">
        {/* Session tabs */}
        {pane.sessions.length > 1 && (
          <div className="flex items-center bg-gray-800 border-b border-gray-700 px-2 py-1">
            <div className="flex items-center space-x-1 flex-1 overflow-x-auto">
              {pane.sessions.map(session => (
                <button
                  key={session.id}
                  onClick={() => switchSession(pane.id, session.id)}
                  className={cn(
                    'flex items-center space-x-2 px-3 py-1 rounded text-xs transition-colors',
                    session.id === activeSession.id
                      ? 'bg-gray-700 text-white'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-gray-700/50'
                  )}
                >
                  <Terminal className="h-3 w-3" />
                  <span className="truncate max-w-20">{session.title}</span>
                  {pane.sessions.length > 1 && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        closeSession(pane.id, session.id);
                      }}
                      className="text-gray-500 hover:text-red-400"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  )}
                </button>
              ))}
            </div>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => createSession(pane.id)}
              className="text-gray-400 hover:text-white h-6 w-6 p-0"
            >
              <Plus className="h-3 w-3" />
            </Button>
          </div>
        )}

        {/* Terminal output */}
        <div className="flex-1 flex flex-col">
          <div
            ref={el => { if (el) outputRefs.current.set(activeSession.id, el); }}
            className={cn(
              'flex-1 p-4 font-mono text-sm overflow-y-auto',
              theme === 'dark' ? 'bg-black text-green-400' : 'bg-white text-black'
            )}
            style={{ fontSize: `${fontSize}px` }}
          >
            {activeSession.output.map((line, index) => (
              <div key={index} className="whitespace-pre-wrap">
                {line === '[2J[H]' ? '' : line}
              </div>
            ))}
            
            {/* Command input */}
            <div className="flex items-center">
              <span className="text-blue-400 mr-2">$</span>
              <input
                ref={el => { if (el) inputRefs.current.set(activeSession.id, el); }}
                type="text"
                className={cn(
                  'flex-1 bg-transparent border-none outline-none font-mono',
                  theme === 'dark' ? 'text-green-400' : 'text-black'
                )}
                style={{ fontSize: `${fontSize}px` }}
                onKeyPress={(e) => handleKeyPress(e, activeSession.id)}
                placeholder="Type command and press Enter..."
                autoFocus
              />
            </div>
            
            {activeSession.isRunning && (
              <div className="flex items-center mt-2 text-yellow-400">
                <div className="animate-spin mr-2">⟳</div>
                <span>Command running...</span>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className={cn('flex flex-col h-full bg-gray-900', className)}>
      {/* Terminal toolbar */}
      <div className="flex items-center justify-between bg-gray-800 border-b border-gray-700 px-4 py-2">
        <div className="flex items-center space-x-2">
          <Terminal className="h-4 w-4 text-green-400" />
          <span className="text-sm font-medium text-white">Multi-Terminal</span>
          <Badge variant="secondary" className="text-xs">
            {panes.reduce((acc, pane) => acc + pane.sessions.length, 0)} sessions
          </Badge>
        </div>

        <div className="flex items-center space-x-2">
          {/* Split controls */}
          <Button
            size="sm"
            variant="ghost"
            onClick={() => splitPane(panes[0]?.id, 'horizontal')}
            title="Split Horizontally"
            className="text-gray-400 hover:text-white"
          >
            <SplitSquareHorizontal className="h-4 w-4" />
          </Button>
          
          <Button
            size="sm"
            variant="ghost"
            onClick={() => splitPane(panes[0]?.id, 'vertical')}
            title="Split Vertically"
            className="text-gray-400 hover:text-white"
          >
            <SplitSquareVertical className="h-4 w-4" />
          </Button>

          {/* New session */}
          <Button
            size="sm"
            variant="ghost"
            onClick={() => createSession(panes[0]?.id)}
            title="New Session"
            className="text-gray-400 hover:text-white"
          >
            <Plus className="h-4 w-4" />
          </Button>

          {/* Settings */}
          <div className="relative">
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setShowSettings(!showSettings)}
              title="Settings"
              className="text-gray-400 hover:text-white"
            >
              <Settings className="h-4 w-4" />
            </Button>

            {showSettings && (
              <div className="absolute top-full right-0 mt-1 bg-gray-800 border border-gray-700 rounded-lg shadow-lg p-3 min-w-48 z-10">
                <div className="space-y-3">
                  <div>
                    <label className="text-xs text-gray-400 block mb-1">Font Size</label>
                    <input
                      type="range"
                      min="10"
                      max="20"
                      value={fontSize}
                      onChange={(e) => setFontSize(parseInt(e.target.value))}
                      className="w-full"
                    />
                    <span className="text-xs text-gray-500">{fontSize}px</span>
                  </div>
                  
                  <div>
                    <label className="text-xs text-gray-400 block mb-1">Theme</label>
                    <select
                      value={theme}
                      onChange={(e) => setTheme(e.target.value as 'dark' | 'light')}
                      className="w-full bg-gray-700 text-white text-xs rounded px-2 py-1"
                    >
                      <option value="dark">Dark</option>
                      <option value="light">Light</option>
                    </select>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Terminal panes */}
      <div className={cn(
        'flex-1 flex',
        splitOrientation === 'horizontal' ? 'flex-row' : 'flex-col'
      )}>
        {panes.map((pane, index) => (
          <div
            key={pane.id}
            className="relative border-gray-700"
            style={{ 
              width: splitOrientation === 'horizontal' ? `${pane.size}%` : '100%',
              height: splitOrientation === 'vertical' ? `${pane.size}%` : '100%'
            }}
          >
            {index > 0 && (
              <div className={cn(
                'absolute bg-gray-700 hover:bg-gray-600 transition-colors',
                splitOrientation === 'horizontal'
                  ? 'left-0 top-0 w-1 h-full cursor-col-resize'
                  : 'top-0 left-0 w-full h-1 cursor-row-resize'
              )} />
            )}
            
            {renderTerminalContent(pane)}
          </div>
        ))}
      </div>

      {/* Status bar */}
      <div className="bg-gray-800 border-t border-gray-700 px-4 py-1">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <div className="flex items-center space-x-4">
            <span>Sessions: {panes.reduce((acc, pane) => acc + pane.sessions.length, 0)}</span>
            <span>Panes: {panes.length}</span>
            <span>Theme: {theme}</span>
          </div>
          <div className="flex items-center space-x-2">
            <span>Ready</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MultiTerminal;