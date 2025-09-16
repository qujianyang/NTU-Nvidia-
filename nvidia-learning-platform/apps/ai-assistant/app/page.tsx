'use client';

import { useState, useRef, useEffect } from 'react';
import { MessageCircle, Send, User, Bot, Sparkles, Calendar, DollarSign } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  recommendations?: any[];
}

interface UserContext {
  role?: string;
  currentSkills?: string[];
  goals?: string;
  budget?: string;
  timeAvailable?: string;
}

export default function ChatAssistant() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: `👋 Hello! I'm your NVIDIA Learning Path Assistant.

I can help you:
- Find the perfect learning path based on your goals
- Recommend courses that match your skill level
- Create custom learning schedules within your time constraints
- Suggest budget-friendly options

What would you like to achieve with NVIDIA technologies?`,
      timestamp: new Date(),
    },
  ]);

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [context, setContext] = useState<UserContext>({});
  const [showContext, setShowContext] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input, context }),
      });

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.message,
        timestamp: new Date(),
        recommendations: data.recommendations,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      }]);
    } finally {
      setLoading(false);
    }
  };

  const quickPrompts = [
    "I want to become an AI engineer",
    "What's the best path for beginners?",
    "I have 20 hours per month to learn",
    "Show me courses under $100",
    "I want to learn LLMs and RAG"
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-green-900 to-emerald-900">
      <header className="bg-black/30 backdrop-blur-md border-b border-green-500/20 p-4">
        <div className="container mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <Sparkles className="w-8 h-8 text-green-500" />
            <h1 className="text-2xl font-bold text-white">NVIDIA Learning Assistant</h1>
          </div>
          <button
            onClick={() => setShowContext(!showContext)}
            className="px-4 py-2 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30 transition"
          >
            Set Context
          </button>
        </div>
      </header>

      <div className="container mx-auto p-4 max-w-5xl">
        <div className="grid grid-cols-12 gap-4">
          {/* Main Chat Area */}
          <div className="col-span-8">
            <div className="bg-black/30 backdrop-blur-md rounded-xl border border-green-500/20 h-[600px] flex flex-col">
              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`flex max-w-[80%] ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'} gap-3`}>
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        message.role === 'user' ? 'bg-blue-500' : 'bg-green-500'
                      }`}>
                        {message.role === 'user' ? <User size={18} /> : <Bot size={18} />}
                      </div>
                      <div className={`rounded-lg p-4 ${
                        message.role === 'user'
                          ? 'bg-blue-500/20 border border-blue-500/30'
                          : 'bg-green-500/10 border border-green-500/20'
                      }`}>
                        <ReactMarkdown className="text-white prose prose-invert prose-sm max-w-none">
                          {message.content}
                        </ReactMarkdown>
                        {message.recommendations && message.recommendations.length > 0 && (
                          <div className="mt-4 space-y-2">
                            <p className="text-green-400 font-semibold text-sm">Recommended:</p>
                            {message.recommendations.map((rec, idx) => (
                              <div key={idx} className="bg-black/30 p-2 rounded border border-green-500/30">
                                <p className="text-white text-sm font-medium">{rec.title}</p>
                                <p className="text-gray-400 text-xs">{rec.reason}</p>
                              </div>
                            ))}
                          </div>
                        )}
                        <p className="text-gray-500 text-xs mt-2">
                          {message.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="flex justify-start">
                    <div className="flex gap-3">
                      <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center">
                        <Bot size={18} />
                      </div>
                      <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
                        <div className="flex space-x-2">
                          <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                          <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                          <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="border-t border-green-500/20 p-4">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Ask about learning paths, courses, or career goals..."
                    className="flex-1 bg-black/30 border border-green-500/30 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-green-500"
                  />
                  <button
                    onClick={handleSend}
                    disabled={loading || !input.trim()}
                    className="px-4 py-2 bg-green-500 text-black rounded-lg hover:bg-green-400 transition disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Send size={20} />
                  </button>
                </div>
              </div>
            </div>

            {/* Quick Prompts */}
            <div className="mt-4">
              <p className="text-gray-400 text-sm mb-2">Quick prompts:</p>
              <div className="flex flex-wrap gap-2">
                {quickPrompts.map((prompt, idx) => (
                  <button
                    key={idx}
                    onClick={() => setInput(prompt)}
                    className="px-3 py-1 bg-black/30 border border-green-500/30 rounded-lg text-green-400 text-sm hover:bg-green-500/20 transition"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Context Panel */}
          <div className="col-span-4">
            <div className="bg-black/30 backdrop-blur-md rounded-xl border border-green-500/20 p-6">
              <h3 className="text-white font-semibold mb-4">Your Profile</h3>

              <div className="space-y-4">
                <div>
                  <label className="text-gray-400 text-sm">Role</label>
                  <select
                    value={context.role || ''}
                    onChange={(e) => setContext({ ...context, role: e.target.value })}
                    className="w-full mt-1 bg-black/30 border border-green-500/30 rounded px-3 py-2 text-white"
                  >
                    <option value="">Select role...</option>
                    <option value="developer">Developer</option>
                    <option value="administrator">Administrator</option>
                    <option value="both">Both</option>
                  </select>
                </div>

                <div>
                  <label className="text-gray-400 text-sm">Learning Goals</label>
                  <textarea
                    value={context.goals || ''}
                    onChange={(e) => setContext({ ...context, goals: e.target.value })}
                    placeholder="e.g., Become an AI engineer, Learn LLMs..."
                    className="w-full mt-1 bg-black/30 border border-green-500/30 rounded px-3 py-2 text-white placeholder-gray-600"
                    rows={3}
                  />
                </div>

                <div>
                  <label className="text-gray-400 text-sm flex items-center gap-2">
                    <Calendar size={16} />
                    Time Available
                  </label>
                  <input
                    type="text"
                    value={context.timeAvailable || ''}
                    onChange={(e) => setContext({ ...context, timeAvailable: e.target.value })}
                    placeholder="e.g., 10 hours/week"
                    className="w-full mt-1 bg-black/30 border border-green-500/30 rounded px-3 py-2 text-white placeholder-gray-600"
                  />
                </div>

                <div>
                  <label className="text-gray-400 text-sm flex items-center gap-2">
                    <DollarSign size={16} />
                    Budget
                  </label>
                  <input
                    type="text"
                    value={context.budget || ''}
                    onChange={(e) => setContext({ ...context, budget: e.target.value })}
                    placeholder="e.g., $500/month"
                    className="w-full mt-1 bg-black/30 border border-green-500/30 rounded px-3 py-2 text-white placeholder-gray-600"
                  />
                </div>

                <div>
                  <label className="text-gray-400 text-sm">Current Skills</label>
                  <input
                    type="text"
                    placeholder="Python, Machine Learning, Docker..."
                    onChange={(e) => setContext({
                      ...context,
                      currentSkills: e.target.value.split(',').map(s => s.trim())
                    })}
                    className="w-full mt-1 bg-black/30 border border-green-500/30 rounded px-3 py-2 text-white placeholder-gray-600"
                  />
                </div>
              </div>

              <button className="w-full mt-6 px-4 py-2 bg-green-500 text-black font-semibold rounded-lg hover:bg-green-400 transition">
                Update Context
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}