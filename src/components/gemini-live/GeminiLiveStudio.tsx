import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  Mic, MicOff, Video, VideoOff, Monitor, Settings, MessageCircle, 
  Brain, Zap, Pause, Play, Volume2, VolumeX, Sparkles, 
  Activity, Users, Clock, Wifi, WifiOff, Send, Loader2 
} from 'lucide-react';

interface GeminiModel {
  id: string;
  name: string;
  description: string;
  type: string;
  badge: string;
  features: string[];
  cost: string;
  rpm: string;
  recommended?: boolean;
}

interface ConversationHistory {
  preview: string;
  timestamp: string;
  session_id: string;
  model?: string;
}

interface MemoryContext {
  content: string;
  timestamp: string;
}

const GeminiLiveStudio: React.FC = () => {
  // Connection & Session State
  const [isConnected, setIsConnected] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected' | 'error'>('disconnected');
  
  // Media State
  const [isRecording, setIsRecording] = useState(false);
  const [isVideoEnabled, setIsVideoEnabled] = useState(false);
  const [videoMode, setVideoMode] = useState<'camera' | 'screen' | 'none'>('none');
  const [audioLevel, setAudioLevel] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolume] = useState(80);
  
  // Model & Conversation State
  const [selectedModel, setSelectedModel] = useState('gemini-2.5-flash-preview-native-audio-dialog');
  const [conversations, setConversations] = useState<ConversationHistory[]>([]);
  const [currentConversation, setCurrentConversation] = useState('');
  const [memoryContext, setMemoryContext] = useState<MemoryContext[]>([]);
  const [textInput, setTextInput] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  
  // Refs for media handling
  const audioStreamRef = useRef<MediaStream | null>(null);
  const videoStreamRef = useRef<MediaStream | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const websocketRef = useRef<WebSocket | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  // Hardcoded Gemini Live models as specified by user requirements
  const availableModels: GeminiModel[] = [
    {
      id: 'gemini-2.5-flash-preview-native-audio-dialog',
      name: 'Gemini 2.5 Flash Audio',
      description: 'Native audio dialog with real-time streaming - perfect for natural conversations',
      type: 'AUDIO_DIALOG',
      badge: 'RECOMMENDED',
      features: ['Real-time audio', 'Live conversation', 'Fast response', 'Memory integration'],
      cost: '$0.075/1K tokens',
      rpm: '2000 RPM',
      recommended: true
    },
    {
      id: 'gemini-2.5-flash-exp-native-audio-thinking-dialog',
      name: 'Gemini 2.5 Flash Thinking',
      description: 'Audio dialog with advanced reasoning - shows thinking process',
      type: 'THINKING_DIALOG',
      badge: 'EXPERIMENTAL',
      features: ['Advanced reasoning', 'Thinking process', 'Audio dialog', 'Deep analysis'],
      cost: '$0.075/1K tokens',
      rpm: '1500 RPM',
      recommended: false
    },
    {
      id: 'gemini-2.0-flash-live-001',
      name: 'Gemini 2.0 Flash Live',
      description: 'Latest live model with enhanced multimodal capabilities',
      type: 'LIVE',
      badge: 'LATEST',
      features: ['Latest model', 'Enhanced live features', 'Multimodal', 'Tool integration'],
      cost: '$0.10/1K tokens',
      rpm: '1000 RPM',
      recommended: false
    }
  ];

  // Initialize session with persistent memory
  const initializeSession = useCallback(async () => {
    try {
      setConnectionStatus('connecting');
      
      const response = await fetch('/api/gemini-live/session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: selectedModel,
          user_id: 'nathan',
          load_memory: true
        })
      });
      
      const data = await response.json();
      if (data.success) {
        setSessionId(data.session_id);
        setMemoryContext(data.memory_context || []);
        setConversations(data.recent_conversations || []);
        setConnectionStatus('disconnected'); // Ready to connect
        
        // Auto-connect if this is the recommended model
        if (selectedModel === 'gemini-2.5-flash-preview-native-audio-dialog') {
          setTimeout(() => connectToGemini(), 1000);
        }
      } else {
        setConnectionStatus('error');
        console.error('Failed to initialize session:', data.error);
      }
    } catch (error) {
      setConnectionStatus('error');
      console.error('Failed to initialize session:', error);
    }
  }, [selectedModel]);

  // Connect to Gemini Live with WebSocket
  const connectToGemini = useCallback(async () => {
    if (!sessionId) {
      await initializeSession();
      return;
    }

    try {
      setConnectionStatus('connecting');
      
      // First connect the session
      const connectResponse = await fetch(`/api/gemini-live/session/${sessionId}/connect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (!connectResponse.ok) {
        throw new Error('Failed to connect session');
      }
      
      // Then establish WebSocket connection
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/api/gemini-live/stream?session_id=${sessionId}`;
      
      websocketRef.current = new WebSocket(wsUrl);
      
      websocketRef.current.onopen = () => {
        setIsConnected(true);
        setConnectionStatus('connected');
        console.log('🎤 Connected to Gemini Live');
      };
      
      websocketRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleGeminiMessage(data);
      };
      
      websocketRef.current.onclose = () => {
        setIsConnected(false);
        setConnectionStatus('disconnected');
        console.log('🔌 Disconnected from Gemini Live');
      };
      
      websocketRef.current.onerror = (error) => {
        setConnectionStatus('error');
        console.error('WebSocket error:', error);
      };
      
    } catch (error) {
      setConnectionStatus('error');
      console.error('Failed to connect to Gemini Live:', error);
    }
  }, [sessionId, initializeSession]);

  // Handle incoming messages from Gemini
  const handleGeminiMessage = (data: any) => {
    switch (data.type) {
      case 'audio_response':
        playAudioResponse(data.audio_data);
        break;
        
      case 'text_response':
        setCurrentConversation(prev => prev + (prev ? '\n\n' : '') + data.text);
        setIsThinking(false);
        
        // Show thinking indicator for thinking models
        if (data.thinking_model) {
          setIsThinking(true);
          setTimeout(() => setIsThinking(false), 2000);
        }
        break;
        
      case 'connection_status':
        if (data.status === 'connected') {
          setIsConnected(true);
          setConnectionStatus('connected');
        }
        break;
        
      case 'connection_error':
        setConnectionStatus('error');
        setIsConnected(false);
        break;
        
      case 'memory_update':
        setMemoryContext(data.memory_context || []);
        break;
        
      default:
        console.log('Unknown message type:', data.type);
    }
  };

  // Start audio recording with enhanced audio processing
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: { 
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        } 
      });
      
      audioStreamRef.current = stream;
      setIsRecording(true);
      
      // Set up enhanced audio processing
      const audioContext = new AudioContext({ sampleRate: 16000 });
      const source = audioContext.createMediaStreamSource(stream);
      const processor = audioContext.createScriptProcessor(4096, 1, 1);
      
      processor.onaudioprocess = (event) => {
        const audioData = event.inputBuffer.getChannelData(0);
        
        // Calculate audio level for visualization
        const level = Math.sqrt(audioData.reduce((sum, sample) => sum + sample * sample, 0) / audioData.length);
        setAudioLevel(Math.min(level * 200, 100)); // Enhanced sensitivity
        
        // Send audio to Gemini if connected
        if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
          const audioBuffer = new Int16Array(audioData.length);
          for (let i = 0; i < audioData.length; i++) {
            audioBuffer[i] = audioData[i] * 32767;
          }
          
          websocketRef.current.send(JSON.stringify({
            type: 'audio_input',
            data: Array.from(audioBuffer),
            timestamp: Date.now()
          }));
        }
      };
      
      source.connect(processor);
      processor.connect(audioContext.destination);
      audioContextRef.current = audioContext;
      
    } catch (error) {
      console.error('Failed to start recording:', error);
      alert('Failed to access microphone. Please check permissions.');
    }
  };

  // Stop audio recording
  const stopRecording = () => {
    if (audioStreamRef.current) {
      audioStreamRef.current.getTracks().forEach(track => track.stop());
      audioStreamRef.current = null;
    }
    
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    
    setIsRecording(false);
    setAudioLevel(0);
  };

  // Start video capture
  const startVideo = async () => {
    try {
      let stream: MediaStream;
      
      if (videoMode === 'camera') {
        stream = await navigator.mediaDevices.getUserMedia({ 
          video: { 
            width: { ideal: 1024 }, 
            height: { ideal: 768 },
            facingMode: 'user'
          } 
        });
      } else if (videoMode === 'screen') {
        stream = await navigator.mediaDevices.getDisplayMedia({ 
          video: { 
            width: { ideal: 1024 }, 
            height: { ideal: 768 }
          } 
        });
      } else {
        return;
      }
      
      videoStreamRef.current = stream;
      setIsVideoEnabled(true);
      
      // Set up video element
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
      
    } catch (error) {
      console.error('Failed to start video:', error);
      alert('Failed to access camera/screen. Please check permissions.');
    }
  };

  // Stop video capture
  const stopVideo = () => {
    if (videoStreamRef.current) {
      videoStreamRef.current.getTracks().forEach(track => track.stop());
      videoStreamRef.current = null;
    }
    
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    
    setIsVideoEnabled(false);
  };

  // Send text message
  const sendTextMessage = async () => {
    if (!textInput.trim() || !sessionId) return;
    
    try {
      const response = await fetch(`/api/gemini-live/session/${sessionId}/send-text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: textInput })
      });
      
      if (response.ok) {
        setCurrentConversation(prev => prev + (prev ? '\n\n' : '') + `You: ${textInput}`);
        setTextInput('');
        setIsThinking(true);
      }
    } catch (error) {
      console.error('Failed to send text message:', error);
    }
  };

  // Play audio response from Gemini
  const playAudioResponse = (audioData: number[]) => {
    try {
      const audioContext = new AudioContext();
      const audioBuffer = audioContext.createBuffer(1, audioData.length, 24000);
      const channelData = audioBuffer.getChannelData(0);
      
      for (let i = 0; i < audioData.length; i++) {
        channelData[i] = audioData[i] / 32767;
      }
      
      const source = audioContext.createBufferSource();
      const gainNode = audioContext.createGain();
      
      gainNode.gain.value = volume / 100;
      source.buffer = audioBuffer;
      source.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      source.start();
      setIsPlaying(true);
      
      source.onended = () => {
        setIsPlaying(false);
      };
      
    } catch (error) {
      console.error('Failed to play audio:', error);
    }
  };

  // Disconnect from Gemini
  const disconnect = async () => {
    try {
      if (websocketRef.current) {
        websocketRef.current.close();
      }
      
      if (sessionId) {
        await fetch(`/api/gemini-live/session/${sessionId}/disconnect`, {
          method: 'POST'
        });
      }
      
      stopRecording();
      stopVideo();
      setIsConnected(false);
      setConnectionStatus('disconnected');
      
    } catch (error) {
      console.error('Failed to disconnect:', error);
    }
  };

  // Initialize on mount
  useEffect(() => {
    initializeSession();
    return () => {
      disconnect();
    };
  }, [initializeSession]);

  // Handle video mode changes
  useEffect(() => {
    if (isVideoEnabled) {
      stopVideo();
      if (videoMode !== 'none') {
        setTimeout(() => startVideo(), 100);
      }
    }
  }, [videoMode]);

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'bg-green-500/20 text-green-300 border-green-500/30';
      case 'connecting': return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30';
      case 'error': return 'bg-red-500/20 text-red-300 border-red-500/30';
      default: return 'bg-gray-500/20 text-gray-300 border-gray-500/30';
    }
  };

  const getConnectionStatusText = () => {
    switch (connectionStatus) {
      case 'connected': return 'Connected';
      case 'connecting': return 'Connecting...';
      case 'error': return 'Error';
      default: return 'Disconnected';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-800 to-pink-800 text-white">
      {/* Enhanced Header with Gemini Branding */}
      <div className="border-b border-white/10 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 flex items-center justify-center relative p-2">
              <img src="/gemini-icon.png" alt="Gemini" className="w-8 h-8 object-contain" />
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full animate-pulse" 
                   style={{ display: isConnected ? 'block' : 'none' }} />
            </div>
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                  Gemini Live Studio
                </span>
                {isThinking && <Loader2 className="w-5 h-5 animate-spin text-purple-400" />}
              </h1>
              <p className="text-purple-200">Real-time AI conversation with Mama Bear's persistent memory</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <div className={`px-4 py-2 rounded-full text-sm border transition-all ${getConnectionStatusColor()}`}>
              <div className="flex items-center gap-2">
                {connectionStatus === 'connecting' ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : isConnected ? (
                  <Wifi className="w-4 h-4" />
                ) : (
                  <WifiOff className="w-4 h-4" />
                )}
                {getConnectionStatusText()}
              </div>
            </div>
            
            {sessionId && (
              <div className="text-xs text-purple-300 bg-purple-500/20 px-3 py-1 rounded-lg">
                Session: {sessionId.slice(-8)}
              </div>
            )}
            
            <button className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors">
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6 p-6 h-[calc(100vh-140px)]">
        {/* Enhanced Model Selection Sidebar */}
        <div className="col-span-3 space-y-4 overflow-y-auto">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Brain className="w-5 h-5 text-blue-400" />
            <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Gemini Models
            </span>
          </h3>
          
          {availableModels.map((model) => (
            <div
              key={model.id}
              onClick={() => setSelectedModel(model.id)}
              className={`p-4 rounded-xl border transition-all cursor-pointer group ${
                selectedModel === model.id
                  ? 'bg-gradient-to-r from-blue-600/30 via-purple-600/30 to-pink-600/30 border-purple-400/50 shadow-lg shadow-purple-500/20'
                  : 'bg-white/5 border-white/10 hover:bg-white/10 hover:border-purple-400/30'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <h4 className="font-semibold text-sm text-white">{model.name}</h4>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  model.badge === 'RECOMMENDED' ? 'bg-green-500/20 text-green-300 border border-green-500/30' :
                  model.badge === 'EXPERIMENTAL' ? 'bg-orange-500/20 text-orange-300 border border-orange-500/30' :
                  model.badge === 'LATEST' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' :
                  'bg-gray-500/20 text-gray-300'
                }`}>
                  {model.badge}
                </span>
              </div>
              
              <p className="text-xs text-purple-200 mb-3 leading-relaxed">{model.description}</p>
              
              <div className="flex flex-wrap gap-1 mb-3">
                {model.features.map((feature, idx) => (
                  <span key={idx} className="px-2 py-1 bg-purple-500/20 text-purple-200 rounded text-xs">
                    {feature}
                  </span>
                ))}
              </div>
              
              <div className="flex justify-between text-xs text-purple-300">
                <span>{model.cost}</span>
                <span>{model.rpm}</span>
              </div>
              
              {model.recommended && (
                <div className="mt-2 text-xs text-green-300 flex items-center gap-1">
                  <Sparkles className="w-3 h-3" />
                  Recommended for Mama Bear
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Enhanced Main Live Interface */}
        <div className="col-span-6 flex flex-col">
          {/* Video/Visual Interface */}
          <div className="flex-1 bg-black/20 rounded-xl border border-white/10 mb-4 relative overflow-hidden">
            {/* Video Element */}
            <video
              ref={videoRef}
              className={`w-full h-full object-cover ${isVideoEnabled ? 'block' : 'hidden'}`}
              muted
              playsInline
            />
            
            {/* Canvas for processing */}
            <canvas
              ref={canvasRef}
              className="hidden"
            />
            
            {/* Default State */}
            {!isVideoEnabled && (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <div className="w-24 h-24 rounded-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 flex items-center justify-center mb-4 mx-auto relative p-4">
                    <img src="/gemini-icon.png" alt="Gemini" className="w-16 h-16 object-contain" />
                    {isConnected && (
                      <div className="absolute -bottom-2 -right-2 w-6 h-6 bg-green-400 rounded-full flex items-center justify-center">
                        <Activity className="w-3 h-3 text-green-900" />
                      </div>
                    )}
                  </div>
                  <h3 className="text-xl font-semibold mb-2 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                    Talk to Gemini Live
                  </h3>
                  <p className="text-purple-200">Start a real-time conversation with voice and vision</p>
                </div>
              </div>
            )}
            
            {/* Enhanced Audio Level Indicator */}
            {isRecording && (
              <div className="absolute bottom-4 left-4 right-4">
                <div className="bg-black/60 backdrop-blur-md rounded-lg p-4">
                  <div className="flex items-center gap-3">
                    <div className="relative">
                      <Mic className="w-5 h-5 text-green-400" />
                      <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-pulse" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs text-green-300 font-medium">Recording</span>
                        <span className="text-xs text-purple-300">{Math.round(audioLevel)}%</span>
                      </div>
                      <div className="bg-gray-700 rounded-full h-2 overflow-hidden">
                        <div
                          className="bg-gradient-to-r from-green-400 to-blue-400 h-full rounded-full transition-all duration-100"
                          style={{ width: `${Math.min(audioLevel, 100)}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {/* Thinking Indicator */}
            {isThinking && (
              <div className="absolute top-4 left-4">
                <div className="bg-black/60 backdrop-blur-md rounded-lg px-3 py-2 flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin text-purple-400" />
                  <span className="text-sm text-purple-300">Mama Bear is thinking...</span>
                </div>
              </div>
            )}
          </div>

          {/* Enhanced Controls */}
          <div className="space-y-4">
            {/* Main Controls */}
            <div className="flex items-center justify-center gap-4 p-4 bg-white/5 rounded-xl border border-white/10">
              {/* Audio Controls */}
              <button
                onClick={isRecording ? stopRecording : startRecording}
                disabled={!isConnected}
                className={`p-4 rounded-full transition-all transform hover:scale-105 active:scale-95 ${
                  isRecording
                    ? 'bg-red-500 hover:bg-red-600 shadow-lg shadow-red-500/30'
                    : isConnected
                    ? 'bg-purple-600 hover:bg-purple-700 shadow-lg shadow-purple-500/30'
                    : 'bg-gray-600 cursor-not-allowed'
                }`}
              >
                {isRecording ? <MicOff className="w-6 h-6" /> : <Mic className="w-6 h-6" />}
              </button>

              {/* Video Controls */}
              <div className="flex items-center gap-2">
                <button
                  onClick={isVideoEnabled ? stopVideo : startVideo}
                  disabled={!isConnected || videoMode === 'none'}
                  className={`p-3 rounded-full transition-all ${
                    isVideoEnabled
                      ? 'bg-blue-500 hover:bg-blue-600 shadow-lg shadow-blue-500/30'
                      : 'bg-white/10 hover:bg-white/20'
                  } ${(!isConnected || videoMode === 'none') ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  {isVideoEnabled ? <VideoOff className="w-5 h-5" /> : <Video className="w-5 h-5" />}
                </button>
                
                <select
                  value={videoMode}
                  onChange={(e) => setVideoMode(e.target.value as 'camera' | 'screen' | 'none')}
                  className="bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-sm"
                >
                  <option value="none">No Video</option>
                  <option value="camera">Camera</option>
                  <option value="screen">Screen Share</option>
                </select>
              </div>

              {/* Connection Control */}
              <button
                onClick={isConnected ? disconnect : connectToGemini}
                disabled={connectionStatus === 'connecting'}
                className={`px-6 py-3 rounded-lg font-semibold transition-all transform hover:scale-105 active:scale-95 ${
                  connectionStatus === 'connecting'
                    ? 'bg-yellow-500 cursor-not-allowed'
                    : isConnected
                    ? 'bg-red-500 hover:bg-red-600 text-white'
                    : 'bg-green-500 hover:bg-green-600 text-white'
                } shadow-lg`}
              >
                {connectionStatus === 'connecting' ? (
                  <div className="flex items-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Connecting...
                  </div>
                ) : isConnected ? (
                  'Disconnect'
                ) : (
                  'Connect'
                )}
              </button>

              {/* Volume Control */}
              <div className="flex items-center gap-2">
                {volume > 0 ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={volume}
                  onChange={(e) => setVolume(parseInt(e.target.value))}
                  className="w-20 accent-purple-500"
                />
                <span className="text-xs text-purple-300 w-8">{volume}%</span>
              </div>
            </div>
            
            {/* Text Input */}
            <div className="flex gap-2 p-3 bg-white/5 rounded-xl border border-white/10">
              <input
                type="text"
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendTextMessage()}
                placeholder="Type a message to Mama Bear..."
                disabled={!isConnected}
                className="flex-1 bg-transparent border-none outline-none text-white placeholder-purple-300"
              />
              <button
                onClick={sendTextMessage}
                disabled={!isConnected || !textInput.trim()}
                className="p-2 rounded-lg bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Enhanced Memory & Context Sidebar */}
        <div className="col-span-3 space-y-4 overflow-y-auto">
          {/* Session Info */}
          <div className="bg-white/5 rounded-xl border border-white/10 p-4">
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <Brain className="w-4 h-4 text-purple-400" />
              Memory Context
            </h3>
            
            <div className="space-y-2">
              {memoryContext.slice(0, 3).map((memory, idx) => (
                <div key={idx} className="p-3 bg-purple-500/10 rounded-lg border border-purple-500/20">
                  <p className="text-xs text-purple-200 leading-relaxed">{memory.content}</p>
                  <p className="text-xs text-purple-400 mt-2 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {memory.timestamp}
                  </p>
                </div>
              ))}
              
              {memoryContext.length === 0 && (
                <div className="text-center py-4">
                  <Brain className="w-8 h-8 text-purple-400 mx-auto mb-2 opacity-50" />
                  <p className="text-sm text-purple-300">Building memory context...</p>
                </div>
              )}
            </div>
          </div>

          {/* Recent Conversations */}
          <div className="bg-white/5 rounded-xl border border-white/10 p-4">
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <MessageCircle className="w-4 h-4 text-blue-400" />
              Recent Conversations
            </h3>
            
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {conversations.map((conv, idx) => (
                <div key={idx} className="p-3 bg-white/5 rounded-lg cursor-pointer hover:bg-white/10 transition-colors border border-white/10">
                  <p className="text-xs text-white truncate mb-1">{conv.preview}</p>
                  <div className="flex items-center justify-between text-xs text-purple-400">
                    <span>{conv.timestamp}</span>
                    {conv.model && (
                      <span className="px-2 py-1 bg-purple-500/20 rounded text-xs">
                        {conv.model.includes('thinking') ? '🧠' : '💬'}
                      </span>
                    )}
                  </div>
                </div>
              ))}
              
              {conversations.length === 0 && (
                <div className="text-center py-4">
                  <MessageCircle className="w-8 h-8 text-blue-400 mx-auto mb-2 opacity-50" />
                  <p className="text-sm text-purple-300">No recent conversations</p>
                </div>
              )}
            </div>
          </div>

          {/* Current Conversation */}
          {currentConversation && (
            <div className="bg-white/5 rounded-xl border border-white/10 p-4">
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <Activity className="w-4 h-4 text-green-400" />
                Live Conversation
              </h3>
              <div className="text-sm text-purple-200 max-h-60 overflow-y-auto leading-relaxed whitespace-pre-wrap">
                {currentConversation}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GeminiLiveStudio;