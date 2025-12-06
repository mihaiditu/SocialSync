import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import EventCard from './components/EventCard';
import Sidebar from './components/Sidebar';
import { Send, Bot, User } from 'lucide-react';

const SESSION_ID = "user-session-1";

function App() {
  // 1. STATE: Initialize from LocalStorage
  const [messages, setMessages] = useState(() => {
    const saved = localStorage.getItem("chat_history");
    if (saved) {
      return JSON.parse(saved);
    } else {
      return [
        { 
          role: 'assistant', 
          text: "Hey there! 👋 I'm SocialSync. I'm here to help you find your people. No pressure — just tell me, what’s your vibe lately?", 
          events: [] 
        }
      ];
    }
  });

  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  
  // REFS
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // 2. EFFECT: Save to LocalStorage
  useEffect(() => {
    localStorage.setItem("chat_history", JSON.stringify(messages));
  }, [messages]);

  // SCROLL TO BOTTOM
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  useEffect(scrollToBottom, [messages]);

  // AUTO-FOCUS
  useEffect(() => {
    if (!isLoading && !isComplete) {
      inputRef.current?.focus();
    }
  }, [isLoading, isComplete]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg = { role: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg.text, session_id: SESSION_ID })
      });

      const data = await response.json();
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        text: data.text,
        events: data.events
      }]);

      if (data.mission_complete) setIsComplete(true);

    } catch (error) {
      console.error("Error:", error);
      setMessages(prev => [...prev, { role: 'assistant', text: "Sorry, I'm having trouble connecting to the brain." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = async () => {
    localStorage.removeItem("chat_history");

    await fetch('http://localhost:8000/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: "", session_id: SESSION_ID })
    });
    
    setMessages([{ 
      role: 'assistant', 
      text: "Hey there! 👋 I'm SocialSync. I'm here to help you find your people. No pressure — just tell me, what’s your vibe lately?", 
      events: [] 
    }]);
    
    setIsComplete(false);
    setIsLoading(false);
  };

  return (
    <div className="flex h-screen bg-gray-900 font-sans text-gray-100">
      
      {/* --- SIDEBAR COMPONENT --- */}
      <Sidebar onReset={handleReset} />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col max-w-5xl mx-auto w-full bg-gray-900 h-screen relative">
        
        {/* Messages List */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
          {messages.map((msg, idx) => {
            const isEventMessage = msg.role === 'assistant' && msg.events && msg.events.length > 0;
            
            return (
              <div key={idx} className={`flex w-full ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                
                <div className={`flex max-w-[85%] gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                  
                  {/* --- AVATARS --- */}
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                    msg.role === 'user' 
                      ? 'bg-blue-600' 
                      : isEventMessage ? 'bg-emerald-600' : 'bg-gray-700' 
                  }`}>
                    {msg.role === 'user' ? (
                      <User size={18} className="text-white" />
                    ) : (
                      <Bot size={18} className="text-white" />
                    )}
                  </div>

                  {/* --- BUBBLE --- */}
                  {/* UPDATE: Changed p-4 to py-2 px-4 for shorter height */}
                  <div className={`rounded-2xl py-2 px-4 shadow-md border ${
                    msg.role === 'user' 
                      ? 'bg-blue-600 text-white border-blue-500' 
                      : isEventMessage
                        ? 'bg-gray-800 text-gray-100 border-2 border-emerald-600/50 shadow-[0_0_15px_-3px_rgba(16,185,129,0.15)]' 
                        : 'bg-gray-800 text-gray-100 border border-gray-700' 
                    }`}
                  >
                    
                    {/* Text Content */}
                    <div className="prose prose-invert prose-sm max-w-none mb-1">
                      <ReactMarkdown>{msg.text}</ReactMarkdown>
                    </div>

                    {/* Event Cards Grid */}
                    {msg.events && msg.events.length > 0 && (
                      <div className="flex flex-wrap gap-4 mt-3">
                        {msg.events.map((event, i) => (
                          <EventCard key={i} event={event} />
                        ))}
                      </div>
                    )}
                  </div>

                </div>
              </div>
            );
          })}

          {/* LOADING STATE */}
          {isLoading && (
            <div className="flex justify-start w-full">
               <div className="flex gap-3 max-w-[85%]">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center">
                    <Bot size={18} className="text-gray-400 animate-pulse" />
                  </div>
                  {/* UPDATE: Changed p-4 to py-2 px-4 */}
                  <div className="bg-gray-800 border border-gray-700 text-gray-400 rounded-2xl py-2 px-4 flex items-center gap-2">
                      <span className="animate-pulse">Checking the airwaves...</span>
                  </div>
               </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-gray-800 bg-gray-800">
          {!isComplete ? (
            <div className="flex items-center gap-3">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Type your answer..."
                // UPDATE: Changed py-3 to py-2 for slimmer input
                className="flex-1 py-2 px-6 bg-gray-900 border border-gray-700 text-white rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-gray-500 shadow-inner transition-all"
                disabled={isLoading}
                autoFocus
              />
              
              <button 
                onClick={handleSend}
                disabled={isLoading}
                // UPDATE: Changed w-12 h-12 to w-10 h-10 to match new input height better
                className="flex-shrink-0 w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center hover:bg-blue-700 hover:scale-110 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none transition-all shadow-lg"
              >
                <Send size={18} className="-ml-0.5 mt-0.5" />
              </button>
            </div>
          ) : (
            <div className="text-center p-4">
              <div className="text-emerald-400 font-bold text-xl mb-3">🎉 Mission Complete!</div>
              <button 
                onClick={handleReset}
                className="bg-emerald-600 text-white px-8 py-3 rounded-full font-semibold hover:bg-emerald-500 hover:scale-105 shadow-lg transition-all"
              >
                Start New Search
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;