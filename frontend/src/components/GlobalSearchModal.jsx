import React, { useState } from 'react';
import { Search, X, User, Plane, MapPin, AlertTriangle, FileText, ChevronRight } from 'lucide-react';

export default function GlobalSearchModal({ itineraries = [], incidents = [], onClose, onSelectResult }) {
  const [query, setQuery] = useState('');

  const q = query.toLowerCase().strip ? query.toLowerCase().strip() : query.toLowerCase();

  const matchingItineraries = itineraries.filter(it => 
    it.title.toLowerCase().includes(q) ||
    it.id.toLowerCase().includes(q) ||
    it.customer.name.toLowerCase().includes(q) ||
    it.customer.email.toLowerCase().includes(q)
  );

  const matchingIncidents = incidents.filter(inc =>
    inc.title.toLowerCase().includes(q) ||
    inc.type.toLowerCase().includes(q) ||
    (inc.customer_name && inc.customer_name.toLowerCase().includes(q))
  );

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-start justify-center pt-20 p-4">
      <div className="glass-panel w-full max-w-2xl rounded-2xl border dark:border-slate-800 border-slate-200 shadow-2xl overflow-hidden flex flex-col max-h-[80vh]">
        
        {/* Search Input Bar */}
        <div className="p-4 bg-slate-900 border-b border-slate-800 flex items-center space-x-3">
          <Search className="w-5 h-5 text-brand-400" />
          <input
            type="text"
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search across Customers, Bookings, Flights, Hotels, Incidents, Agents..."
            className="flex-1 bg-transparent text-sm text-slate-100 placeholder-slate-500 focus:outline-none"
          />
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-slate-800 text-slate-400">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Results Stream */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
          {!query ? (
            <div className="text-center py-8 text-slate-500 italic">
              Type anything above to search across customer profiles, bookings, flights, hotels, weather disruptions, and agents...
            </div>
          ) : (
            <>
              {matchingItineraries.length > 0 && (
                <div>
                  <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Bookings & Customers ({matchingItineraries.length})</div>
                  <div className="space-y-1.5">
                    {matchingItineraries.map((it) => (
                      <div
                        key={it.id}
                        onClick={() => {
                          onSelectResult('BOOKING', it.id);
                          onClose();
                        }}
                        className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 hover:border-brand-500 cursor-pointer flex items-center justify-between text-slate-200"
                      >
                        <div className="flex items-center space-x-3">
                          <Plane className="w-4 h-4 text-brand-400" />
                          <div>
                            <div className="font-bold text-slate-100">{it.title}</div>
                            <div className="text-[11px] text-slate-400">ID: {it.id} • Traveler: {it.customer.name}</div>
                          </div>
                        </div>
                        <ChevronRight className="w-4 h-4 text-slate-500" />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {matchingIncidents.length > 0 && (
                <div>
                  <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Active Disruption Alerts ({matchingIncidents.length})</div>
                  <div className="space-y-1.5">
                    {matchingIncidents.map((inc) => (
                      <div
                        key={inc.id}
                        onClick={() => {
                          onSelectResult('INCIDENT', inc.itinerary_id);
                          onClose();
                        }}
                        className="p-3 rounded-xl bg-slate-950/60 border border-amber-500/40 hover:border-amber-400 cursor-pointer flex items-center justify-between text-slate-200"
                      >
                        <div className="flex items-center space-x-3">
                          <AlertTriangle className="w-4 h-4 text-amber-400" />
                          <div>
                            <div className="font-bold text-slate-100">{inc.title}</div>
                            <div className="text-[11px] text-slate-400">Severity: {inc.severity} • {inc.type}</div>
                          </div>
                        </div>
                        <ChevronRight className="w-4 h-4 text-slate-500" />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {matchingItineraries.length === 0 && matchingIncidents.length === 0 && (
                <div className="text-center py-8 text-slate-500">
                  No matching items found for "{query}". Try searching by customer name, city, or booking ID.
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
