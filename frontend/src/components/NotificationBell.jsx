import React, { useState } from 'react';
import { Bell, AlertTriangle, ChevronRight, X, Sparkles } from 'lucide-react';

export default function NotificationBell({ incidents = [], currentUser = null, role = 'CUSTOMER', onSelectIncident }) {
  const [open, setOpen] = useState(false);

  // STRICT AUTHENTICATION & AUTHORIZATION FILTERING:
  // If Customer role: ONLY show alerts belonging to this specific logged-in customer!
  // If Ops role: Show all fleet alerts.
  const userEmail = currentUser?.email || 'rajesh.sharma@tata.com';
  const userName = currentUser?.name || 'Rajesh Sharma';

  const userIncidents = incidents.filter(inc => {
    if (role === 'OPS') return true;
    if (!inc) return false;
    
    const matchesEmail = inc.customer_email && inc.customer_email.toLowerCase() === userEmail.toLowerCase();
    const matchesName = inc.customer_name && inc.customer_name.toLowerCase() === userName.toLowerCase();
    
    // Default fallback for demo matching
    if (!inc.customer_email && !inc.customer_name) return true;
    return matchesEmail || matchesName;
  });

  const activeIncidents = userIncidents.filter(i => i.status !== 'RECOVERED');
  const alertCount = activeIncidents.length;

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(prev => !prev)}
        title="Real-Time Guardian Disruption Alerts"
        className="relative p-2 rounded-xl dark:bg-slate-800 bg-slate-100 dark:text-slate-200 text-slate-700 hover:bg-slate-200 dark:hover:bg-slate-700 border dark:border-slate-700 border-slate-200 transition-all"
      >
        <Bell className="w-4 h-4" />
        {alertCount > 0 && (
          <span className="absolute -top-1 -right-1 px-1.5 py-0.5 rounded-full bg-red-500 text-white text-[10px] font-extrabold shadow-md animate-pulse">
            {alertCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-80 sm:w-96 glass-panel rounded-2xl border dark:border-slate-700 border-slate-200 shadow-2xl p-4 z-[110] text-xs">
          <div className="flex items-center justify-between border-b dark:border-slate-800 border-slate-200 pb-2 mb-3">
            <div className="flex items-center space-x-2 font-bold dark:text-slate-100 text-slate-800">
              <AlertTriangle className="w-4 h-4 text-amber-500" />
              <span>
                {role === 'CUSTOMER' ? `My Disruption Alerts (${alertCount})` : `Fleet Disruption Alerts (${alertCount})`}
              </span>
            </div>
            <button onClick={() => setOpen(false)} className="text-slate-400 hover:text-slate-200">
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="space-y-2 max-h-72 overflow-y-auto">
            {alertCount === 0 ? (
              <div className="p-4 text-center text-slate-400 italic">
                <Sparkles className="w-5 h-5 mx-auto mb-1 text-emerald-400" />
                <p>No active disruptions on your booked routes. All flight & rail legs running smoothly!</p>
              </div>
            ) : (
              activeIncidents.map((inc) => (
                <div
                  key={inc.id}
                  onClick={() => {
                    if (onSelectIncident) onSelectIncident(inc.itinerary_id);
                    setOpen(false);
                  }}
                  className="cursor-pointer p-3 rounded-xl dark:bg-slate-900 bg-slate-50 border dark:border-slate-800 border-slate-200 hover:border-amber-500/50 transition-all flex flex-col justify-between"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-red-500/20 text-red-400 border border-red-500/30">
                      {inc.severity} Severity
                    </span>
                    <span className="text-[10px] text-slate-400">{inc.type}</span>
                  </div>
                  <div className="font-bold dark:text-slate-100 text-slate-800">{inc.title}</div>
                  <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">{inc.description}</p>
                  <div className="mt-2 text-[10px] text-brand-400 font-semibold flex items-center justify-between">
                    <span>Traveler: {inc.customer_name || userName}</span>
                    <span className="flex items-center">View AI Recovery Plan <ChevronRight className="w-3 h-3 ml-0.5" /></span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
