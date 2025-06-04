import React, { useState, useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { 
  Terminal, 
  Code, 
  Monitor, 
  Globe, 
  Settings, 
  Play, 
  Pause, 
  Square, 
  RotateCw,
  Zap,
  Heart,
  Star,
  Sparkles,
  Activity
} from 'lucide-react';

interface AnimatedIconProps {
  icon: React.ComponentType<any>;
  animation?: 'pulse' | 'bounce' | 'spin' | 'scale' | 'glow' | 'fade' | 'slide';
  duration?: number;
  size?: number;
  color?: string;
  className?: string;
  active?: boolean;
  onClick?: () => void;
  hoverEffect?: boolean;
}

interface FloatingIconProps {
  icon: React.ComponentType<any>;
  startPosition: { x: number; y: number };
  endPosition: { x: number; y: number };
  duration?: number;
  onComplete?: () => void;
}

interface IconBadgeProps {
  icon: React.ComponentType<any>;
  count?: number;
  pulse?: boolean;
  color?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const AnimatedIcon: React.FC<AnimatedIconProps> = ({
  icon: Icon,
  animation = 'pulse',
  duration = 1000,
  size = 24,
  color = 'currentColor',
  className,
  active = false,
  onClick,
  hoverEffect = true
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isClicked, setIsClicked] = useState(false);

  const getAnimationClass = () => {
    const baseClass = 'transition-all duration-300';
    
    switch (animation) {
      case 'pulse':
        return `${baseClass} ${active ? 'animate-pulse' : ''}`;
      case 'bounce':
        return `${baseClass} ${active ? 'animate-bounce' : ''}`;
      case 'spin':
        return `${baseClass} ${active ? 'animate-spin' : ''}`;
      case 'scale':
        return `${baseClass} ${active || isHovered ? 'scale-110' : 'scale-100'}`;
      case 'glow':
        return `${baseClass} ${active ? 'drop-shadow-lg' : ''}`;
      case 'fade':
        return `${baseClass} ${active ? 'opacity-100' : 'opacity-60'}`;
      case 'slide':
        return `${baseClass} ${active ? 'translate-x-1' : 'translate-x-0'}`;
      default:
        return baseClass;
    }
  };

  const handleClick = () => {
    setIsClicked(true);
    setTimeout(() => setIsClicked(false), 150);
    onClick?.();
  };

  return (
    <div
      className={cn(
        'inline-flex items-center justify-center cursor-pointer',
        hoverEffect && 'hover:scale-110',
        isClicked && 'scale-95',
        getAnimationClass(),
        className
      )}
      style={{ 
        width: size, 
        height: size,
        color: active ? color : undefined
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleClick}
    >
      <Icon 
        width={size * 0.7}
        height={size * 0.7}
        className={cn(
          getAnimationClass(),
          isHovered && hoverEffect && 'drop-shadow-md'
        )}
        style={{ color }}
      />
    </div>
  );
};

const FloatingIcon: React.FC<FloatingIconProps> = ({
  icon: Icon,
  startPosition,
  endPosition,
  duration = 2000,
  onComplete
}) => {
  const [position, setPosition] = useState(startPosition);
  const [isVisible, setIsVisible] = useState(true);
  const animationFrameRef = useRef<number>();
  const startTimeRef = useRef<number>();

  useEffect(() => {
    const animate = (timestamp: number) => {
      if (!startTimeRef.current) {
        startTimeRef.current = timestamp;
      }

      const elapsed = timestamp - startTimeRef.current;
      const progress = Math.min(elapsed / duration, 1);

      // Easing function (ease-out)
      const easeOut = 1 - Math.pow(1 - progress, 3);

      setPosition({
        x: startPosition.x + (endPosition.x - startPosition.x) * easeOut,
        y: startPosition.y + (endPosition.y - startPosition.y) * easeOut
      });

      if (progress < 1) {
        animationFrameRef.current = requestAnimationFrame(animate);
      } else {
        setIsVisible(false);
        onComplete?.();
      }
    };

    animationFrameRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [startPosition, endPosition, duration, onComplete]);

  if (!isVisible) return null;

  return (
    <div
      className="fixed pointer-events-none z-50 transition-opacity duration-300"
      style={{
        left: position.x,
        top: position.y,
        opacity: isVisible ? 1 : 0
      }}
    >
      <div className="animate-pulse">
        <Icon width={24} height={24} className="text-blue-500 drop-shadow-lg" />
      </div>
    </div>
  );
};

const IconBadge: React.FC<IconBadgeProps> = ({
  icon: Icon,
  count,
  pulse = false,
  color = 'blue',
  size = 'md',
  className
}) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12'
  };

  const iconSizes = {
    sm: 16,
    md: 20,
    lg: 24
  };

  return (
    <div className={cn('relative inline-flex', className)}>
      <div
        className={cn(
          'flex items-center justify-center rounded-full transition-all duration-300',
          sizeClasses[size],
          pulse && 'animate-pulse',
          `bg-${color}-100 text-${color}-600 hover:bg-${color}-200`
        )}
      >
        <Icon width={iconSizes[size]} height={iconSizes[size]} />
      </div>
      
      {count !== undefined && count > 0 && (
        <div
          className={cn(
            'absolute -top-1 -right-1 flex items-center justify-center',
            'min-w-5 h-5 text-xs font-bold text-white rounded-full',
            'animate-pulse',
            `bg-${color}-500`
          )}
        >
          {count > 99 ? '99+' : count}
        </div>
      )}
    </div>
  );
};

// Predefined animated icon sets
const StatusIcons = {
  Running: () => (
    <AnimatedIcon
      icon={Play}
      animation="glow"
      color="#10b981"
      active={true}
    />
  ),
  Stopped: () => (
    <AnimatedIcon
      icon={Square}
      animation="fade"
      color="#6b7280"
      active={false}
    />
  ),
  Loading: () => (
    <AnimatedIcon
      icon={RotateCw}
      animation="spin"
      color="#3b82f6"
      active={true}
    />
  ),
  Error: () => (
    <AnimatedIcon
      icon={Zap}
      animation="pulse"
      color="#ef4444"
      active={true}
    />
  ),
  Success: () => (
    <AnimatedIcon
      icon={Star}
      animation="bounce"
      color="#10b981"
      active={true}
    />
  )
};

const ToolIcons = {
  Terminal: (active = false) => (
    <AnimatedIcon
      icon={Terminal}
      animation="scale"
      color="#10b981"
      active={active}
    />
  ),
  Code: (active = false) => (
    <AnimatedIcon
      icon={Code}
      animation="scale"
      color="#3b82f6"
      active={active}
    />
  ),
  Monitor: (active = false) => (
    <AnimatedIcon
      icon={Monitor}
      animation="scale"
      color="#8b5cf6"
      active={active}
    />
  ),
  Browser: (active = false) => (
    <AnimatedIcon
      icon={Globe}
      animation="scale"
      color="#f59e0b"
      active={active}
    />
  ),
  Settings: (active = false) => (
    <AnimatedIcon
      icon={Settings}
      animation="spin"
      color="#6b7280"
      active={active}
      duration={2000}
    />
  )
};

// Icon Button with multiple states
interface IconButtonProps {
  icon: React.ComponentType<any>;
  state?: 'default' | 'active' | 'loading' | 'success' | 'error';
  size?: 'sm' | 'md' | 'lg';
  onClick?: () => void;
  className?: string;
  disabled?: boolean;
}

const IconButton: React.FC<IconButtonProps> = ({
  icon: Icon,
  state = 'default',
  size = 'md',
  onClick,
  className,
  disabled = false
}) => {
  const [isPressed, setIsPressed] = useState(false);

  const getStateStyle = () => {
    switch (state) {
      case 'active':
        return 'bg-blue-500 text-white shadow-lg';
      case 'loading':
        return 'bg-yellow-500 text-white animate-pulse';
      case 'success':
        return 'bg-green-500 text-white';
      case 'error':
        return 'bg-red-500 text-white animate-pulse';
      default:
        return 'bg-gray-100 text-gray-700 hover:bg-gray-200';
    }
  };

  const getSizeClass = () => {
    switch (size) {
      case 'sm': return 'w-8 h-8';
      case 'lg': return 'w-12 h-12';
      default: return 'w-10 h-10';
    }
  };

  const getIconSize = () => {
    switch (size) {
      case 'sm': return 16;
      case 'lg': return 24;
      default: return 20;
    }
  };

  return (
    <button
      className={cn(
        'flex items-center justify-center rounded-lg transition-all duration-200',
        'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
        getSizeClass(),
        getStateStyle(),
        isPressed && 'scale-95',
        disabled && 'opacity-50 cursor-not-allowed',
        className
      )}
      onClick={onClick}
      disabled={disabled}
      onMouseDown={() => setIsPressed(true)}
      onMouseUp={() => setIsPressed(false)}
      onMouseLeave={() => setIsPressed(false)}
    >
      <Icon 
        width={getIconSize()}
        height={getIconSize()}
        className={cn(
          'transition-transform duration-200',
          state === 'loading' && 'animate-spin'
        )}
      />
    </button>
  );
};

export {
  AnimatedIcon,
  FloatingIcon,
  IconBadge,
  IconButton,
  StatusIcons,
  ToolIcons
};

export default AnimatedIcon;