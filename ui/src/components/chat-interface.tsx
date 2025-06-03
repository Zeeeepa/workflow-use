import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Settings, Download, Trash2, Square, Loader2 } from 'lucide-react';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  metadata?: any;
}

interface ChatSession {
  id: string;
  messages: ChatMessage[];
  created_at: string;
  updated_at: string;
  status: string;
}

interface ChatInterfaceProps {
  onClose?: () => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ onClose }) => {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [providers, setProviders] = useState<Record<string, string[]>>({});
  const [selectedProvider, setSelectedProvider] = useState('openai');
  const [selectedModel, setSelectedModel] = useState('');
  const [showSettings, setShowSettings] = useState(false);
  const [browserConfig, setBrowserConfig] = useState({
    headless: false,
    disable_security: true,
  });
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const API_BASE = 'http://localhost:8000/api/chat';

  useEffect(() => {
    loadProviders();
    loadSessions();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [currentSession?.messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadProviders = async () => {
    try {
      const response = await fetch(`${API_BASE}/providers`);
      const data = await response.json();
      setProviders(data.providers);
      
      // Set default model for selected provider
      if (data.providers[selectedProvider]?.length > 0) {
        setSelectedModel(data.providers[selectedProvider][0]);
      }
    } catch (error) {
      console.error('Failed to load providers:', error);
    }
  };

  const loadSessions = async () => {
    try {
      const response = await fetch(`${API_BASE}/sessions`);
      const data = await response.json();
      setSessions(data.sessions);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
  };

  const createNewSession = async () => {
    try {
      const response = await fetch(`${API_BASE}/sessions`, {
        method: 'POST',
      });
      const data = await response.json();
      
      const newSession: ChatSession = {
        id: data.session_id,
        messages: [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        status: 'active',
      };
      
      setSessions(prev => [newSession, ...prev]);
      setCurrentSession(newSession);
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  const sendMessage = async () => {
    if (!message.trim() || !currentSession || isLoading) return;

    const userMessage = message;
    setMessage('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/sessions/${currentSession.id}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          provider: selectedProvider,
          model: selectedModel || undefined,
          browser_config: browserConfig,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const assistantMessage = await response.json();
      
      // Reload the session to get both user and assistant messages
      const sessionResponse = await fetch(`${API_BASE}/sessions/${currentSession.id}`);
      const updatedSession = await sessionResponse.json();
      
      setCurrentSession(updatedSession);
      setSessions(prev => 
        prev.map(s => s.id === updatedSession.id ? updatedSession : s)
      );
    } catch (error) {
      console.error('Failed to send message:', error);
      // Add error message to chat
      const errorMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `Error: ${error instanceof Error ? error.message : 'Failed to process message'}`,
        timestamp: new Date().toISOString(),
      };
      
      if (currentSession) {
        const updatedSession = {
          ...currentSession,
          messages: [...currentSession.messages, errorMessage],
        };
        setCurrentSession(updatedSession);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const cancelSession = async (sessionId: string) => {
    try {
      await fetch(`${API_BASE}/sessions/${sessionId}/cancel`, {
        method: 'POST',
      });
      loadSessions();
    } catch (error) {
      console.error('Failed to cancel session:', error);
    }
  };

  const deleteSession = async (sessionId: string) => {
    try {
      await fetch(`${API_BASE}/sessions/${sessionId}`, {
        method: 'DELETE',
      });
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      if (currentSession?.id === sessionId) {
        setCurrentSession(null);
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  };

  const downloadSession = async (sessionId: string) => {
    try {
      const response = await fetch(`${API_BASE}/sessions/${sessionId}/download`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `chat_session_${sessionId}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to download session:', error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <div className="flex h-full bg-gray-50">
      {/* Sidebar */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Browser Chat</h2>
            <div className="flex gap-2">
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
              >
                <Settings size={18} />
              </button>
              {onClose && (
                <button
                  onClick={onClose}
                  className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
                >
                  ×
                </button>
              )}
            </div>
          </div>
          
          <button
            onClick={createNewSession}
            className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            New Chat Session
          </button>
        </div>

        {/* Settings Panel */}
        {showSettings && (
          <div className="p-4 border-b border-gray-200 bg-gray-50">
            <h3 className="font-medium text-gray-900 mb-3">Settings</h3>
            
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  LLM Provider
                </label>
                <select
                  value={selectedProvider}
                  onChange={(e) => {
                    setSelectedProvider(e.target.value);
                    setSelectedModel(providers[e.target.value]?.[0] || '');
                  }}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                >
                  {Object.keys(providers).map(provider => (
                    <option key={provider} value={provider}>
                      {provider.charAt(0).toUpperCase() + provider.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Model
                </label>
                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                >
                  {providers[selectedProvider]?.map(model => (
                    <option key={model} value={model}>
                      {model}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={!browserConfig.headless}
                    onChange={(e) => setBrowserConfig(prev => ({
                      ...prev,
                      headless: !e.target.checked
                    }))}
                    className="mr-2"
                  />
                  <span className="text-sm text-gray-700">Show Browser</span>
                </label>
              </div>
            </div>
          </div>
        )}

        {/* Sessions List */}
        <div className="flex-1 overflow-y-auto">
          {sessions.map(session => (
            <div
              key={session.id}
              className={`p-3 border-b border-gray-100 cursor-pointer hover:bg-gray-50 ${
                currentSession?.id === session.id ? 'bg-blue-50 border-blue-200' : ''
              }`}
              onClick={() => setCurrentSession(session)}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-900 truncate">
                    Session {session.id.slice(0, 8)}
                  </div>
                  <div className="text-xs text-gray-500">
                    {session.messages.length} messages • {session.status}
                  </div>
                </div>
                <div className="flex gap-1 ml-2">
                  {session.status === 'active' && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        cancelSession(session.id);
                      }}
                      className="p-1 text-gray-400 hover:text-red-600"
                      title="Cancel"
                    >
                      <Square size={14} />
                    </button>
                  )}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      downloadSession(session.id);
                    }}
                    className="p-1 text-gray-400 hover:text-blue-600"
                    title="Download"
                  >
                    <Download size={14} />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteSession(session.id);
                    }}
                    className="p-1 text-gray-400 hover:text-red-600"
                    title="Delete"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {currentSession ? (
          <>
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {currentSession.messages.map(msg => (
                <div
                  key={msg.id}
                  className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {msg.role === 'assistant' && (
                    <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
                      <Bot size={16} className="text-white" />
                    </div>
                  )}
                  
                  <div
                    className={`max-w-3xl px-4 py-2 rounded-lg ${
                      msg.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-white border border-gray-200 text-gray-900'
                    }`}
                  >
                    <div className="whitespace-pre-wrap">{msg.content}</div>
                    <div
                      className={`text-xs mt-1 ${
                        msg.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                      }`}
                    >
                      {formatTimestamp(msg.timestamp)}
                      {msg.metadata?.provider && (
                        <span className="ml-2">• {msg.metadata.provider}</span>
                      )}
                    </div>
                  </div>
                  
                  {msg.role === 'user' && (
                    <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center flex-shrink-0">
                      <User size={16} className="text-white" />
                    </div>
                  )}
                </div>
              ))}
              
              {isLoading && (
                <div className="flex gap-3 justify-start">
                  <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
                    <Bot size={16} className="text-white" />
                  </div>
                  <div className="bg-white border border-gray-200 text-gray-900 px-4 py-2 rounded-lg">
                    <div className="flex items-center gap-2">
                      <Loader2 size={16} className="animate-spin" />
                      <span>Processing your request...</span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t border-gray-200 p-4">
              <div className="flex gap-3">
                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me to automate any browser task..."
                  className="flex-1 border border-gray-300 rounded-lg px-4 py-2 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={3}
                  disabled={isLoading}
                />
                <button
                  onClick={sendMessage}
                  disabled={!message.trim() || isLoading}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                >
                  <Send size={16} />
                  Send
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            <div className="text-center">
              <Bot size={48} className="mx-auto mb-4 text-gray-400" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Welcome to Browser Chat
              </h3>
              <p className="text-gray-600 mb-4">
                Create a new chat session to start automating browser tasks with AI
              </p>
              <button
                onClick={createNewSession}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Start New Chat
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatInterface;

