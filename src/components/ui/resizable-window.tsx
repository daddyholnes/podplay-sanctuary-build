import React, { useState, useRef, useEffect, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { 
  X, 
  Minus, 
  Square, 
  Maximize2, 
  Minimize2,
  Move3D,
  GripVertical,
  MoreHorizontal
} from 'lucide-react';

export interface WindowProps {
  id: string;
  title: string;
  children: React.ReactNode;
  initialPosition?: { x: number; y: number };
  initialSize?: { width: number; height: number };
  minSize?: { width: number; height: number };
  maxSize?: { width: number; height: number };
  resizable?: boolean;
  draggable?: boolean;
  closable?: boolean;
  minimizable?: boolean;
  maximizable?: boolean;
  className?: string;
  onClose?: (id: string) => void;
  onMinimize?: (id: string) => void;
  onMaximize?: (id: string) => void;
  onResize?: (id: string, size: { width: number; height: number }) => void;
  onMove?: (id: string, position: { x: number; y: number }) => void;
  onFocus?: (id: string) => void;
  isMinimized?: boolean;
  isMaximized?: boolean;
  zIndex?: number;
}

const ResizableWindow: React.FC<WindowProps> = ({
  id,
  title,
  children,
  initialPosition = { x: 50, y: 50 },
  initialSize = { width: 600, height: 400 },
  minSize = { width: 300, height: 200 },
  maxSize = { width: window.innerWidth - 100, height: window.innerHeight - 100 },
  resizable = true,
  draggable = true,
  closable = true,
  minimizable = true,
  maximizable = true,
  className,
  onClose,
  onMinimize,
  onMaximize,
  onResize,
  onMove,
  onFocus,
  isMinimized = false,
  isMaximized = false,
  zIndex = 1
}) => {
  const [position, setPosition] = useState(initialPosition);
  const [size, setSize] = useState(initialSize);
  const [isDragging, setIsDragging] = useState(false);
  const [isResizing, setIsResizing] = useState(false);
  const [resizeDirection, setResizeDirection] = useState('');
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [resizeStart, setResizeStart] = useState({ x: 0, y: 0, width: 0, height: 0 });

  const windowRef = useRef<HTMLDivElement>(null);
  const headerRef = useRef<HTMLDivElement>(null);

  // Handle window focus
  const handleFocus = useCallback(() => {
    onFocus?.(id);
  }, [id, onFocus]);

  // Drag functionality
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (!draggable || isMaximized) return;
    
    e.preventDefault();
    setIsDragging(true);
    setDragStart({
      x: e.clientX - position.x,
      y: e.clientY - position.y
    });
    handleFocus();
  }, [draggable, isMaximized, position, handleFocus]);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (isDragging && !isMaximized) {
      const newPosition = {
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      };
      
      // Keep window within viewport
      newPosition.x = Math.max(0, Math.min(newPosition.x, window.innerWidth - size.width));
      newPosition.y = Math.max(0, Math.min(newPosition.y, window.innerHeight - size.height));
      
      setPosition(newPosition);
      onMove?.(id, newPosition);
    }
    
    if (isResizing) {
      const deltaX = e.clientX - resizeStart.x;
      const deltaY = e.clientY - resizeStart.y;
      
      let newWidth = resizeStart.width;
      let newHeight = resizeStart.height;
      let newX = position.x;
      let newY = position.y;
      
      if (resizeDirection.includes('right')) {
        newWidth = Math.max(minSize.width, Math.min(maxSize.width, resizeStart.width + deltaX));
      }
      if (resizeDirection.includes('left')) {
        newWidth = Math.max(minSize.width, Math.min(maxSize.width, resizeStart.width - deltaX));
        newX = resizeStart.x + deltaX;
      }
      if (resizeDirection.includes('bottom')) {
        newHeight = Math.max(minSize.height, Math.min(maxSize.height, resizeStart.height + deltaY));
      }
      if (resizeDirection.includes('top')) {
        newHeight = Math.max(minSize.height, Math.min(maxSize.height, resizeStart.height - deltaY));
        newY = resizeStart.y + deltaY;
      }
      
      setSize({ width: newWidth, height: newHeight });
      setPosition({ x: newX, y: newY });
      onResize?.(id, { width: newWidth, height: newHeight });
      onMove?.(id, { x: newX, y: newY });
    }
  }, [isDragging, isResizing, isMaximized, dragStart, resizeStart, resizeDirection, position, size, minSize, maxSize, id, onMove, onResize]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
    setIsResizing(false);
    setResizeDirection('');
  }, []);

  // Resize functionality
  const handleResizeStart = useCallback((e: React.MouseEvent, direction: string) => {
    if (!resizable || isMaximized) return;
    
    e.preventDefault();
    e.stopPropagation();
    setIsResizing(true);
    setResizeDirection(direction);
    setResizeStart({
      x: e.clientX,
      y: e.clientY,
      width: size.width,
      height: size.height
    });
    handleFocus();
  }, [resizable, isMaximized, size, handleFocus]);

  // Window controls
  const handleClose = () => onClose?.(id);
  const handleMinimize = () => onMinimize?.(id);
  const handleMaximize = () => onMaximize?.(id);

  // Global mouse events
  useEffect(() => {
    if (isDragging || isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = isDragging ? 'move' : 'resize';
      document.body.style.userSelect = 'none';
      
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
        document.body.style.cursor = 'auto';
        document.body.style.userSelect = 'auto';
      };
    }
  }, [isDragging, isResizing, handleMouseMove, handleMouseUp]);

  // Handle maximized state
  const windowStyle = isMaximized 
    ? { 
        position: 'fixed' as const,
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        zIndex: zIndex + 1000
      }
    : {
        position: 'fixed' as const,
        left: position.x,
        top: position.y,
        width: size.width,
        height: size.height,
        zIndex
      };

  if (isMinimized) {
    return null; // Minimized windows are handled by the window manager
  }

  return (
    <div
      ref={windowRef}
      className={cn(
        'bg-white border border-gray-300 rounded-lg shadow-lg overflow-hidden',
        'focus:outline-none focus:ring-2 focus:ring-blue-500',
        className
      )}
      style={windowStyle}
      onMouseDown={handleFocus}
      tabIndex={0}
    >
      {/* Window Header */}
      <div
        ref={headerRef}
        className={cn(
          'flex items-center justify-between px-4 py-2 bg-gradient-to-r from-gray-50 to-gray-100',
          'border-b border-gray-200 select-none',
          draggable && !isMaximized && 'cursor-move'
        )}
        onMouseDown={handleMouseDown}
      >
        <div className="flex items-center space-x-2">
          <Move3D className="h-4 w-4 text-gray-400" />
          <h3 className="text-sm font-medium text-gray-900 truncate">{title}</h3>
        </div>
        
        <div className="flex items-center space-x-1">
          {minimizable && (
            <button
              onClick={handleMinimize}
              className="p-1 hover:bg-gray-200 rounded transition-colors"
              title="Minimize"
            >
              <Minus className="h-3 w-3 text-gray-600" />
            </button>
          )}
          {maximizable && (
            <button
              onClick={handleMaximize}
              className="p-1 hover:bg-gray-200 rounded transition-colors"
              title={isMaximized ? "Restore" : "Maximize"}
            >
              {isMaximized ? (
                <Minimize2 className="h-3 w-3 text-gray-600" />
              ) : (
                <Maximize2 className="h-3 w-3 text-gray-600" />
              )}
            </button>
          )}
          {closable && (
            <button
              onClick={handleClose}
              className="p-1 hover:bg-red-100 hover:text-red-600 rounded transition-colors"
              title="Close"
            >
              <X className="h-3 w-3" />
            </button>
          )}
        </div>
      </div>

      {/* Window Content */}
      <div className="flex-1 overflow-hidden">
        {children}
      </div>

      {/* Resize Handles */}
      {resizable && !isMaximized && (
        <>
          {/* Corner handles */}
          <div
            className="absolute top-0 left-0 w-2 h-2 cursor-nw-resize"
            onMouseDown={(e) => handleResizeStart(e, 'top-left')}
          />
          <div
            className="absolute top-0 right-0 w-2 h-2 cursor-ne-resize"
            onMouseDown={(e) => handleResizeStart(e, 'top-right')}
          />
          <div
            className="absolute bottom-0 left-0 w-2 h-2 cursor-sw-resize"
            onMouseDown={(e) => handleResizeStart(e, 'bottom-left')}
          />
          <div
            className="absolute bottom-0 right-0 w-2 h-2 cursor-se-resize"
            onMouseDown={(e) => handleResizeStart(e, 'bottom-right')}
          />
          
          {/* Edge handles */}
          <div
            className="absolute top-0 left-2 right-2 h-1 cursor-n-resize"
            onMouseDown={(e) => handleResizeStart(e, 'top')}
          />
          <div
            className="absolute bottom-0 left-2 right-2 h-1 cursor-s-resize"
            onMouseDown={(e) => handleResizeStart(e, 'bottom')}
          />
          <div
            className="absolute left-0 top-2 bottom-2 w-1 cursor-w-resize"
            onMouseDown={(e) => handleResizeStart(e, 'left')}
          />
          <div
            className="absolute right-0 top-2 bottom-2 w-1 cursor-e-resize"
            onMouseDown={(e) => handleResizeStart(e, 'right')}
          />
        </>
      )}
    </div>
  );
};

export default ResizableWindow;