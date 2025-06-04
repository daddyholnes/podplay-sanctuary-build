import React, { useState, useEffect, useRef } from 'react';
import { Socket } from 'socket.io-client';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Send, Paperclip, Sparkles, Heart, Zap, Package } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  model_used?: string;
  suggestions?: string[];
  suggested_actions?: any[];
  mcp_discovery_suggestion?: any;
  empowerment_opportunity?: boolean;
}

interface ConnectionStatus {
  connected: boolean;
  user_id?: string;
  message?: string;
}

interface MamaBearChatProps {
  socket: Socket | null;
  connectionStatus: ConnectionStatus;
}

const MamaBearChat: React.FC<MamaBearChatProps> = ({ socket, connectionStatus }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!socket) return;

    // Listen for Mama Bear responses
    socket.on('mama_bear_response', (data) => {
      const newMessage: Message = {
        id: `msg_${Date.now()}`,
        role: 'assistant',
        content: data.response,
        timestamp: data.timestamp || new Date().toISOString(),
        model_used: data.model_used,
        suggestions: data.suggestions,
        suggested_actions: data.actions,
        mcp_discovery_suggestion: data.mcp_discovery_suggestion,
        empowerment_opportunity: data.empowerment_opportunity
      };

      setMessages(prev => [...prev, newMessage]);
      setIsTyping(false);
      setIsSending(false);
    });

    // Listen for typing indicator
    socket.on('mama_bear_typing', (data) => {
      setIsTyping(data.is_typing);
    });

    // Listen for errors
    socket.on('error', (data) => {
      console.error('Mama Bear error:', data);
      setIsTyping(false);
      setIsSending(false);
    });

    // Cleanup
    return () => {
      socket.off('mama_bear_response');
      socket.off('mama_bear_typing');
      socket.off('error');
    };
  }, [socket]);

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // Add welcome message when connected
  useEffect(() => {
    if (connectionStatus.connected && connectionStatus.message && messages.length === 0) {
      const welcomeMessage: Message = {
        id: 'welcome',
        role: 'assistant',
        content: connectionStatus.message,
        timestamp: new Date().toISOString()
      };
      setMessages([welcomeMessage]);
    }
  }, [connectionStatus, messages.length]);

  const sendMessage = () => {
    if (!inputValue.trim() || !socket || !connectionStatus.connected || isSending) return;

    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: inputValue,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsSending(true);

    // Send to backend
    socket.emit('mama_bear_chat', {
      content: inputValue,
      conversation_id: `conv_${connectionStatus.user_id}`,
      timestamp: new Date().toISOString()
    });

    setInputValue('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleSuggestedAction = (action: any) => {
    if (action.agent === 'scout') {
      // This would trigger Scout agent
      console.log('Triggering Scout agent:', action);
    } else if (action.agent === 'workspace') {
      // This would switch to workspace tab
      console.log('Switching to workspace:', action);
    } else if (action.agent === 'integration') {
      // This would trigger MCP marketplace
      console.log('Opening MCP marketplace:', action);
    }
  };

  const handleMCPDiscovery = (suggestion: any) => {
    if (!socket) return;

    // Send MCP discovery request to Mama Bear
    socket.emit('mama_bear_chat', {
      content: `Please search the MCP marketplace for: ${suggestion.suggested_search}`,
      conversation_id: `conv_${connectionStatus.user_id}`,
      mcp_discovery_request: true,
      timestamp: new Date().toISOString()
    });
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <Card className="sanctuary-card h-[600px] flex flex-col">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="text-2xl float-animation">🐻</div>
            <div>
              <span className="text-lg">Mama Bear Chat</span>
              <p className="text-sm text-muted-foreground font-normal">
                Your caring AI development assistant
              </p>
            </div>
          </div>
          {connectionStatus.connected && (
            <Badge variant="secondary" className="mama-bear-gradient text-white">
              <Heart className="w-3 h-3 mr-1" />
              Active
            </Badge>
          )}
        </CardTitle>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col space-y-4 p-4">
        {/* Messages Area */}
        <ScrollArea className="flex-1 pr-4">
          <div className="space-y-4">
            {messages.map((message) => (
              <div key={message.id} className="space-y-3">
                {/* Message */}
                <div className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`flex space-x-2 max-w-[80%] ${message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                    <Avatar className="w-8 h-8">
                      <AvatarFallback className={message.role === 'user' ? 'bg-scout text-white' : 'mama-bear-gradient text-white'}>
                        {message.role === 'user' ? '👤' : '🐻'}
                      </AvatarFallback>
                    </Avatar>
                    <div className={`rounded-lg p-3 ${
                      message.role === 'user' 
                        ? 'bg-scout text-scout-foreground' 
                        : 'bg-muted'
                    }`}>
                      <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                      <div className="flex items-center justify-between mt-2 text-xs text-muted-foreground">
                        <span>{formatTimestamp(message.timestamp)}</span>
                        {message.model_used && (
                          <span className="text-xs opacity-60">{message.model_used}</span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Suggestions */}
                {message.suggestions && message.suggestions.length > 0 && (
                  <div className="flex flex-wrap gap-2 ml-10">
                    {message.suggestions.map((suggestion, index) => (
                      <Button
                        key={index}
                        variant="outline"
                        size="sm"
                        className="text-xs h-7"
                        onClick={() => {
                          setInputValue(suggestion);
                        }}
                      >
                        <Sparkles className="w-3 h-3 mr-1" />
                        {suggestion}
                      </Button>
                    ))}
                  </div>
                )}

                {/* Suggested Actions */}
                {message.suggested_actions && message.suggested_actions.length > 0 && (
                  <div className="ml-10 space-y-2">
                    <p className="text-xs text-muted-foreground">🐻 I can help you with:</p>
                    <div className="flex flex-wrap gap-2">
                      {message.suggested_actions.map((action, index) => (
                        <Button
                          key={index}
                          variant="outline"
                          size="sm"
                          className="text-xs h-8"
                          onClick={() => handleSuggestedAction(action)}
                        >
                          <span className="mr-1">{action.icon}</span>
                          {action.description}
                        </Button>
                      ))}
                    </div>
                  </div>
                )}

                {/* MCP Discovery Suggestion */}
                {message.mcp_discovery_suggestion && (
                  <div className="ml-10">
                    <Card className="border-mama-bear/20 bg-mama-bear/5">
                      <CardContent className="p-3">
                        <div className="flex items-start space-x-2">
                          <Package className="w-4 h-4 text-mama-bear mt-0.5" />
                          <div>
                            <p className="text-xs text-mama-bear font-medium">Tool Discovery Opportunity</p>
                            <p className="text-xs text-muted-foreground mt-1">
                              {message.mcp_discovery_suggestion.message}
                            </p>
                            <Button
                              size="sm"
                              className="mt-2 h-7 mama-bear-gradient text-white"
                              onClick={() => handleMCPDiscovery(message.mcp_discovery_suggestion)}
                            >
                              <Zap className="w-3 h-3 mr-1" />
                              Search MCP Marketplace
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                )}
              </div>
            ))}

            {/* Typing Indicator */}
            {isTyping && (
              <div className="flex justify-start">
                <div className="flex space-x-2 max-w-[80%]">
                  <Avatar className="w-8 h-8">
                    <AvatarFallback className="mama-bear-gradient text-white">🐻</AvatarFallback>
                  </Avatar>
                  <div className="bg-muted rounded-lg p-3">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>

        {/* Input Area */}
        <div className="border-t pt-4">
          <div className="flex space-x-2">
            <div className="flex-1 relative">
              <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask Mama Bear anything - she's here to help! 🐻"
                disabled={!connectionStatus.connected || isSending}
                className="pr-10"
              />
              <Button
                size="sm"
                variant="ghost"
                className="absolute right-1 top-1/2 transform -translate-y-1/2 h-6 w-6 p-0"
              >
                <Paperclip className="w-3 h-3" />
              </Button>
            </div>
            <Button
              onClick={sendMessage}
              disabled={!inputValue.trim() || !connectionStatus.connected || isSending}
              className="mama-bear-gradient text-white"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
          
          {!connectionStatus.connected && (
            <p className="text-xs text-muted-foreground mt-2 text-center">
              Connecting to your sanctuary...
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default MamaBearChat;