import React from 'react';
import { RefreshCw, Sparkles, Calendar, Users, MapPin } from 'lucide-react';

const Sidebar = ({ onReset }) => {
  return (
    <div className="w-64 bg-gradient-to-b from-gray-800 to-gray-900 border-r border-gray-700 p-6 hidden md:block flex flex-col h-full">
      {/* Header */}
      <div className="mb-12">
        <h1 className="text-3xl font-bold text-white mb-4 flex items-center gap-2">
          SocialSync
          <span className="text-3xl">🤝</span>
        </h1>
        <p className="text-gray-300 text-base leading-relaxed mb-6">
          Your AI-powered companion for discovering meaningful local experiences and building real-world connections.
        </p>
        
        {/* Feature highlights */}
        <div className="space-y-4">
          <div className="flex items-start gap-3 text-sm text-gray-400">
            <Sparkles size={18} className="mt-0.5 text-blue-400 flex-shrink-0" />
            <span>Intelligent event matching based on your interests</span>
          </div>
          <div className="flex items-start gap-3 text-sm text-gray-400">
            <MapPin size={18} className="mt-0.5 text-purple-400 flex-shrink-0" />
            <span>Hyper-local recommendations in your area</span>
          </div>
          <div className="flex items-start gap-3 text-sm text-gray-400">
            <Users size={18} className="mt-0.5 text-green-400 flex-shrink-0" />
            <span>Connect with like-minded people nearby</span>
          </div>
          <div className="flex items-start gap-3 text-sm text-gray-400">
            <Calendar size={18} className="mt-0.5 text-orange-400 flex-shrink-0" />
            <span>Real-time updates on upcoming events</span>
          </div>
        </div>
      </div>

      {/* Spacer to push button to a nice position */}
      <div className="flex-grow"></div>
      
      {/* Reset Button */}
      <div className="mt-auto pt-8 border-t border-gray-700">
        <button 
          onClick={onReset}
          className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-blue-700 to-blue-800 text-white py-3 rounded-lg hover:from-blue-800 hover:to-blue-900 transition-all shadow-lg hover:shadow-xl transform hover:scale-105 active:scale-95"
        >
          <RefreshCw size={20} /> 
          <span className="font-medium text-base">Reset Chat</span>
        </button>
        <p className="text-sm text-gray-500 text-center mt-3">
          Start fresh with a new conversation
        </p>
      </div>
    </div>
  );
};

export default Sidebar;