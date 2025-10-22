import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, X, Send, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { ScrollArea } from '@/components/ui/scroll-area';
import { API_BASE_URL } from '@/lib/api';

interface Message {
  id: string;
  message: string;
  sender: 'user' | 'bot';
  timestamp: string;
}

interface ChatSession {
  id: string;
  user_name: string;
  user_email: string;
}


const ChatBot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [session, setSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [userName, setUserName] = useState('');
  const [userEmail, setUserEmail] = useState('');
  const [showUserForm, setShowUserForm] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load session from localStorage on mount
  useEffect(() => {
    const savedSession = localStorage.getItem('chatbot_session');
    if (savedSession) {
      const parsedSession = JSON.parse(savedSession);
      setSession(parsedSession);
      setShowUserForm(false);
      loadMessages(parsedSession.id);
    }
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadMessages = async (sessionId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/messages/${sessionId}`);
      if (response.ok) {
        const data = await response.json();
        setMessages(data);
      }
    } catch (error) {
      console.error('Error loading messages:', error);
    }
  };

  const handleCreateSession = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userName.trim() || !userEmail.trim()) return;

    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_name: userName,
          user_email: userEmail,
        }),
      });

      if (response.ok) {
        const newSession = await response.json();
        setSession(newSession);
        localStorage.setItem('chatbot_session', JSON.stringify(newSession));
        setShowUserForm(false);
        
        // Add welcome message
        const welcomeMsg: Message = {
          id: 'welcome',
          message: `Hello ${userName}! 👋 I'm here to help you with BBQ catering questions, menu items, pricing, holiday specials, and bookings. How can I assist you today?`,
          sender: 'bot',
          timestamp: new Date().toISOString(),
        };
        setMessages([welcomeMsg]);
      }
    } catch (error) {
      console.error('Error creating session:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || !session || isLoading) return;

    const userMsg: Message = {
      id: `temp-${Date.now()}`,
      message: inputMessage,
      sender: 'user',
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: session.id,
          message: inputMessage,
        }),
      });

      if (response.ok) {
        const botMessage = await response.json();
        setMessages((prev) => [...prev, botMessage]);
      } else {
        throw new Error('Failed to send message');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMsg: Message = {
        id: `error-${Date.now()}`,
        message: 'Sorry, I encountered an error. Please try again.',
        sender: 'bot',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    localStorage.removeItem('chatbot_session');
    setSession(null);
    setMessages([]);
    setShowUserForm(true);
    setUserName('');
    setUserEmail('');
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      {/* Floating Chat Button */}
      {!isOpen && (
        <button
          onClick={toggleChat}
          className="fixed bottom-20 right-8 z-50 group"
          aria-label="Open chat"
        >
          <div className="relative">
            {/* Pulsing background effect */}
            <div className="absolute inset-0 bg-amber-600 rounded-full animate-ping opacity-75"></div>
            
            {/* Main button */}
            <div className="relative bg-gradient-to-br from-amber-700 via-amber-600 to-yellow-700 text-faded-mustard rounded-full p-5 shadow-2xl hover:shadow-amber-600/60 transition-all duration-300 hover:scale-110 border-2 border-faded-mustard/30">
              <MessageCircle className="w-8 h-8" strokeWidth={2.5} />
            </div>
            
            {/* Glow effect */}
            <div className="absolute inset-0 rounded-full bg-amber-600/40 blur-2xl group-hover:bg-amber-600/60 transition-all duration-300"></div>
          </div>
          
          {/* Tooltip */}
          <div className="absolute bottom-full right-0 mb-3 px-4 py-2 bg-gradient-to-r from-gray-900 to-gray-800 text-white text-sm rounded-xl shadow-2xl opacity-0 group-hover:opacity-100 transition-all duration-300 whitespace-nowrap border border-white/10">
            <span className="font-medium">Chat with us!</span>
            <div className="absolute top-full right-6 -mt-1 w-0 h-0 border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-gray-900"></div>
          </div>
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-20 right-8 z-50 w-[420px] h-[650px] bg-cream-white rounded shadow-card flex flex-col overflow-hidden border border-amber-600/30">
          {/* Header */}
          <div className="bg-gradient-to-r from-amber-700 via-amber-600 to-yellow-700 text-cream-white p-6 flex items-center justify-between relative overflow-hidden">
            {/* Subtle texture */}
            <div className="absolute inset-0 opacity-10">
              <div className="absolute top-0 left-0 w-32 h-32 bg-faded-mustard rounded-full -translate-x-1/2 -translate-y-1/2"></div>
              <div className="absolute bottom-0 right-0 w-24 h-24 bg-faded-mustard rounded-full translate-x-1/2 translate-y-1/2"></div>
            </div>
            
            <div className="flex items-center gap-4 relative z-10">
              <div className="bg-faded-mustard/40 backdrop-blur-sm p-2.5 rounded">
                <MessageCircle className="w-6 h-6 text-faded-mustard" strokeWidth={2.5} />
              </div>
              <div>
                <h3 className="font-serif font-bold text-lg tracking-wide text-faded-mustard">BBQ Catering Chat</h3>
                <p className="text-xs text-cream-white/90 font-light">Real help, real quick 🍖</p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleChat}
              className="text-faded-mustard hover:bg-faded-mustard/20 rounded relative z-10 transition-all duration-200"
            >
              <X className="w-5 h-5" strokeWidth={2.5} />
            </Button>
          </div>

          {/* User Info Form */}
          {showUserForm && (
            <div className="flex-1 p-8 flex flex-col justify-center bg-gradient-to-br from-cream-white to-amber-50">
              <div className="text-center mb-8">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-amber-700 to-amber-600 rounded mb-4 shadow-soft">
                  <MessageCircle className="w-8 h-8 text-faded-mustard" strokeWidth={2.5} />
                </div>
                <h4 className="text-2xl font-serif mb-2 text-charcoal-gray">
                  Welcome!
                </h4>
                <p className="text-sm text-charcoal-gray/70 font-light">
                  Let's get started with your BBQ catering journey
                </p>
              </div>
              <form onSubmit={handleCreateSession} className="space-y-5">
                <div>
                  <Label htmlFor="name" className="text-sm font-medium text-charcoal-gray">Your Name</Label>
                  <Input
                    id="name"
                    type="text"
                    placeholder="John Doe"
                    value={userName}
                    onChange={(e) => setUserName(e.target.value)}
                    required
                    className="mt-2 h-11 rounded border border-amber-600/20 focus:border-amber-600 focus:ring-2 focus:ring-faded-mustard/20 transition-all duration-200 bg-white text-charcoal-gray"
                  />
                </div>
                <div>
                  <Label htmlFor="email" className="text-sm font-medium text-charcoal-gray">Your Email</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="john@example.com"
                    value={userEmail}
                    onChange={(e) => setUserEmail(e.target.value)}
                    required
                    className="mt-2 h-11 rounded border border-amber-600/20 focus:border-amber-600 focus:ring-2 focus:ring-faded-mustard/20 transition-all duration-200 bg-white text-charcoal-gray"
                  />
                </div>
                <Button
                  type="submit"
                  className="w-full h-11 bg-gradient-to-r from-amber-700 via-amber-600 to-yellow-700 hover:shadow-lg hover:shadow-amber-600/50 transition-all duration-250 rounded font-medium text-faded-mustard border border-faded-mustard/30"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Starting Chat...
                    </>
                  ) : (
                    'Start Chat'
                  )}
                </Button>
              </form>
            </div>
          )}

          {/* Chat Messages */}
          {!showUserForm && session && (
            <>
              <ScrollArea className="flex-1 p-6 bg-gradient-to-br from-cream-white to-amber-50">
                <div className="space-y-4">
                  {messages.map((msg, index) => (
                    <div
                      key={msg.id || index}
                      className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'} animate-in slide-in-from-bottom-2 duration-300`}
                    >
                      <div
                        className={`max-w-[85%] rounded px-4 py-3 shadow-soft ${
                          msg.sender === 'user'
                            ? 'bg-gradient-to-r from-amber-700 to-amber-600 text-faded-mustard border border-faded-mustard/30'
                            : 'bg-white text-charcoal-gray border border-amber-600/20'
                        }`}
                      >
                        <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.message}</p>
                        <p className={`text-xs mt-2 ${msg.sender === 'user' ? 'text-cream-white/70' : 'text-charcoal-gray/60'}`}>
                          {new Date(msg.timestamp).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </p>
                      </div>
                    </div>
                  ))}
                  {isLoading && (
                    <div className="flex justify-start animate-in slide-in-from-bottom-2 duration-300">
                      <div className="bg-white rounded px-4 py-3 shadow-soft border border-amber-600/20">
                        <div className="flex items-center gap-2">
                          <Loader2 className="w-4 h-4 animate-spin text-amber-600" />
                          <span className="text-sm text-charcoal-gray">Typing...</span>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              </ScrollArea>

              {/* Input Area */}
              <div className="p-5 border-t border-amber-600/20 bg-cream-white">
                <form onSubmit={handleSendMessage} className="flex gap-3">
                  <Input
                    type="text"
                    placeholder="Type your message..."
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    disabled={isLoading}
                    className="flex-1 h-11 rounded border border-amber-600/20 focus:border-amber-600 focus:ring-2 focus:ring-faded-mustard/20 transition-all duration-200 bg-white text-charcoal-gray placeholder:text-charcoal-gray/40"
                  />
                  <Button
                    type="submit"
                    size="icon"
                    disabled={isLoading || !inputMessage.trim()}
                    className="h-11 w-11 bg-gradient-to-r from-amber-700 to-amber-600 hover:shadow-lg hover:shadow-amber-600/50 transition-all duration-250 rounded text-faded-mustard border border-faded-mustard/30"
                  >
                    <Send className="w-5 h-5" strokeWidth={2.5} />
                  </Button>
                </form>
                <div className="mt-3 flex justify-center">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleNewChat}
                    className="text-xs text-charcoal-gray/60 hover:text-amber-600 transition-colors duration-200 rounded font-normal"
                  >
                    Start New Chat
                  </Button>
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </>
  );
};

export default ChatBot;
