import React from 'react';
import { Calendar, MapPin, DollarSign, ExternalLink } from 'lucide-react';

const EventCard = ({ event }) => {
  return (
    <div className="bg-gray-800 border-l-4 border-red-500 rounded-lg p-4 shadow-lg hover:shadow-2xl transition-all flex-1 min-w-[300px] mb-4 text-white">
      <h3 className="text-lg font-bold text-gray-100 mb-2">🏆 {event.title}</h3>
      
      <div className="space-y-2 text-sm text-gray-300">
        <div className="flex items-center gap-2">
          <Calendar size={16} className="text-red-400" />
          <span className="font-semibold text-gray-200">When:</span> {event.date}
        </div>
        
        <div className="flex items-center gap-2">
          <MapPin size={16} className="text-red-400" />
          <span className="font-semibold text-gray-200">Where:</span> {event.location}
        </div>

        <div className="flex items-center gap-2">
          <DollarSign size={16} className="text-red-400" />
          <span className="font-semibold text-gray-200">Cost:</span> {event.cost}
        </div>
      </div>

      <p className="mt-3 text-gray-400 italic text-sm border-t pt-2 border-gray-700">
        "{event.description}"
      </p>

      <a 
        href={event.url} 
        target="_blank" 
        rel="noopener noreferrer"
        className="mt-4 inline-flex items-center gap-2 text-red-400 font-bold hover:text-red-300 hover:underline transition-colors"
      >
        <ExternalLink size={16} />
        View Event Details
      </a>
    </div>
  );
};

export default EventCard;