import React, { useState } from 'react';
import { 
  ShieldCheck, AlertTriangle, Plane, Train, Building, Clock, DollarSign, 
  Sparkles, CheckCircle2, ChevronRight, MessageSquare, Send, ArrowRight, X, RefreshCw, Calendar, MapPin, Compass, Plus, ArrowLeft
} from 'lucide-react';

export default function CustomerView({ itinerary, allItineraries = [], onApprovePlan, onSelectItinerary, loading }) {
  const [pageView, setPageView] = useState('BOOKINGS'); // 'BOOKINGS' or 'DETAILS'
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [chatOpen, setChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState([
    { sender: 'AI', text: "Hello! I'm your Travel Guardian AI Assistant. I'm actively monitoring your flight radar, weather, and rail lines across Indian hubs." }
  ]);
  const [inputMsg, setInputMsg] = useState('');

  // Trip planner form state
  const [originCity, setOriginCity] = useState('Delhi (DEL)');
  const [destCity, setDestCity] = useState('Mumbai (BOM)');
  const [travelDate, setTravelDate] = useState('2026-08-15');
  const [bookedNotice, setBookedNotice] = useState(null);

  if (!itinerary && allItineraries.length === 0) {
    return (
      <div className="p-8 text-center text-slate-400">
        <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-brand-400" />
        <p>Loading your protected itinerary...</p>
      </div>
    );
  }

  const legs = itinerary?.legs || [];
  const incidents = itinerary?.incidents || [];
  const activeIncident = incidents.find(i => i.status === 'RECOVERY_PROPOSED' || i.status === 'OPEN');
  const recoveryPlans = activeIncident ? activeIncident.recovery_plans : [];

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!inputMsg.trim()) return;

    const userText = inputMsg;
    setChatMessages(prev => [...prev, { sender: 'USER', text: userText }]);
    setInputMsg('');

    setTimeout(() => {
      let reply = "I am analyzing your query with our Recovery Planning Agent. Your itinerary is protected with 100% VIP layover coverage.";
      if (userText.toLowerCase().includes("why") || userText.toLowerCase().includes("delay") || userText.toLowerCase().includes("rain")) {
        reply = "Mumbai Airport (BOM) experienced monsoon torrential rain. Our Disruption Detection Agent flagged this 2 hours ahead of airport check-in.";
      } else if (userText.toLowerCase().includes("hotel") || userText.toLowerCase().includes("taj") || userText.toLowerCase().includes("check")) {
        reply = "We automatically notified Taj Mahal Palace & Leela Palace of your updated arrival time. Your room reservation is guaranteed with late check-out.";
      }
      setChatMessages(prev => [...prev, { sender: 'AI', text: reply }]);
    }, 600);
  };

  const handleBookTripSubmit = (e) => {
    e.preventDefault();
    setBookedNotice(`New trip from ${originCity} to ${destCity} booked! Protection active.`);
    setTimeout(() => setBookedNotice(null), 4000);
  };

  const openItineraryDetails = (it) => {
    if (onSelectItinerary) {
      onSelectItinerary(it.id);
    }
    setPageView('DETAILS');
  };

  return (
    <div className="space-y-6">
      {/* Navigation breadcrumb between Bookings and Details */}
      <div className="flex items-center justify-between border-b dark:border-slate-800 border-slate-200 pb-3">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setPageView('BOOKINGS')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all ${
              pageView === 'BOOKINGS'
                ? 'bg-brand-600 text-white shadow-md'
                : 'dark:bg-slate-900 bg-slate-100 text-slate-400 hover:text-slate-200'
            }`}
          >
            <Compass className="w-3.5 h-3.5" />
            <span>Book & My Bookings</span>
          </button>

          {itinerary && (
            <button
              onClick={() => setPageView('DETAILS')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all ${
                pageView === 'DETAILS'
                  ? 'bg-brand-600 text-white shadow-md'
                  : 'dark:bg-slate-900 bg-slate-100 text-slate-400 hover:text-slate-200'
              }`}
            >
              <Clock className="w-3.5 h-3.5" />
              <span>Detailed Itinerary View ({itinerary.customer.name})</span>
            </button>
          )}
        </div>

        {pageView === 'DETAILS' && (
          <button
            onClick={() => setPageView('BOOKINGS')}
            className="text-xs text-brand-400 hover:text-brand-300 font-semibold flex items-center space-x-1"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to My Bookings</span>
          </button>
        )}
      </div>

      {/* PAGE A: BOOK TRIP PLAN & MY BOOKED TRIPS */}
      {pageView === 'BOOKINGS' && (
        <div className="space-y-6">
          {/* 1. Attractive UI Card: "Book Your Trip Plan" with AI Assistant Icon */}
          <div className="glass-panel rounded-2xl p-6 border border-brand-500/40 relative overflow-hidden bg-gradient-to-r from-brand-900/40 via-slate-900 to-emerald-950/40">
            <div className="absolute top-0 right-0 p-8 opacity-10 pointer-events-none">
              <Sparkles className="w-72 h-72 text-brand-400" />
            </div>

            <div className="relative z-10 space-y-4">
              <div className="flex items-center space-x-3">
                <div className="p-3 rounded-2xl bg-gradient-to-tr from-brand-600 to-emerald-500 text-white shadow-lg shadow-brand-500/30">
                  <Sparkles className="w-7 h-7 animate-pulse" />
                </div>
                <div>
                  <h2 className="text-xl font-extrabold dark:text-slate-100 text-slate-800">
                    Book Your Trip Plan with AI Protection
                  </h2>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Autonomous 7-Agent protection built-in. Monitored continuously across Open-Meteo weather radar & Indian transit lines.
                  </p>
                </div>
              </div>

              {bookedNotice && (
                <div className="p-3 rounded-xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs font-semibold flex items-center space-x-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span>{bookedNotice}</span>
                </div>
              )}

              {/* Booking Planner Form */}
              <form onSubmit={handleBookTripSubmit} className="grid grid-cols-1 sm:grid-cols-4 gap-3 bg-slate-950/80 p-4 rounded-xl border border-slate-800/80 text-xs">
                <div>
                  <label className="text-[11px] font-semibold text-slate-400 block mb-1">Origin City</label>
                  <div className="relative">
                    <MapPin className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5" />
                    <input
                      type="text"
                      value={originCity}
                      onChange={(e) => setOriginCity(e.target.value)}
                      className="w-full bg-slate-900 text-slate-100 rounded-lg pl-8 pr-2 py-2 border border-slate-800 focus:outline-none focus:border-brand-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-slate-400 block mb-1">Destination City</label>
                  <div className="relative">
                    <MapPin className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5" />
                    <input
                      type="text"
                      value={destCity}
                      onChange={(e) => setDestCity(e.target.value)}
                      className="w-full bg-slate-900 text-slate-100 rounded-lg pl-8 pr-2 py-2 border border-slate-800 focus:outline-none focus:border-brand-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-slate-400 block mb-1">Travel Date</label>
                  <div className="relative">
                    <Calendar className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5" />
                    <input
                      type="date"
                      value={travelDate}
                      onChange={(e) => setTravelDate(e.target.value)}
                      className="w-full bg-slate-900 text-slate-100 rounded-lg pl-8 pr-2 py-2 border border-slate-800 focus:outline-none focus:border-brand-500"
                    />
                  </div>
                </div>

                <div className="flex items-end">
                  <button
                    type="submit"
                    className="w-full py-2 rounded-lg bg-gradient-to-r from-brand-600 to-emerald-600 hover:from-brand-500 hover:to-emerald-500 text-white font-bold text-xs flex items-center justify-center space-x-1.5 shadow-lg shadow-brand-600/30 transition-all"
                  >
                    <Plus className="w-4 h-4" />
                    <span>Book Protected Trip</span>
                  </button>
                </div>
              </form>
            </div>
          </div>

          {/* 2. My Booked Travel Plans Section */}
          <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-extrabold text-base dark:text-slate-100 text-slate-800 flex items-center space-x-2">
                  <ShieldCheck className="w-5 h-5 text-emerald-400" />
                  <span>My Booked Travel Plans</span>
                </h3>
                <p className="text-xs text-slate-400">Click on any booked plan below to open the full detailed itinerary view page</p>
              </div>
              <span className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
                {allItineraries.length} Active Bookings
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {allItineraries.map((it) => {
                const isSelected = itinerary?.id === it.id;
                const hasIncident = it.risk_score >= 60;

                return (
                  <div
                    key={it.id}
                    onClick={() => openItineraryDetails(it)}
                    className={`cursor-pointer p-5 rounded-2xl border transition-all flex flex-col justify-between ${
                      isSelected
                        ? 'bg-slate-900/90 border-brand-500 ring-2 ring-brand-500/50 shadow-xl'
                        : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-brand-500/20 text-brand-400 border border-brand-500/30">
                          {it.customer.tier} Protection
                        </span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          hasIncident ? 'bg-red-500/20 text-red-400 border border-red-500/30 animate-pulse' : 'bg-emerald-500/10 text-emerald-400'
                        }`}>
                          {hasIncident ? `DISRUPTED (${it.risk_score}% Risk)` : 'GUARDIAN PROTECTED'}
                        </span>
                      </div>

                      <h4 className="font-extrabold text-sm text-slate-100">{it.title}</h4>
                      <p className="text-xs text-slate-400 mt-1">Traveler: <strong className="text-slate-200">{it.customer.name}</strong></p>

                      <div className="flex items-center space-x-4 mt-3 text-xs text-slate-400 font-mono bg-slate-950 p-2.5 rounded-xl border border-slate-800/80">
                        <div>Legs: <strong className="text-slate-200">{it.leg_count} Legs</strong></div>
                        <div>Start: <strong className="text-slate-200">{new Date(it.start_date).toLocaleDateString()}</strong></div>
                      </div>
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
                      <span className="text-slate-400 italic text-[11px]">Click to view full plan & AI recovery options</span>
                      <span className="font-bold text-brand-400 flex items-center space-x-1">
                        <span>Open Details</span>
                        <ChevronRight className="w-4 h-4" />
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* PAGE B: DETAILED ITINERARY VIEW PAGE */}
      {pageView === 'DETAILS' && (
        <div className="space-y-6">
          {/* Guardian Shield Header */}
          <div className="glass-panel rounded-2xl p-6 border border-emerald-500/30 relative overflow-hidden bg-gradient-to-r from-slate-900 via-slate-900 to-emerald-950/40">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-start space-x-4">
                <div className="p-3.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 animate-pulse-glow">
                  <ShieldCheck className="w-8 h-8" />
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <h2 className="text-xl font-bold text-slate-100">{itinerary.title}</h2>
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-brand-500/20 text-brand-400 border border-brand-500/30">
                      {itinerary.customer.tier} Tier Protected
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    Traveler: <span className="text-slate-200 font-medium">{itinerary.customer.name}</span> • 
                    Continuous Protection: <span className="text-emerald-400 font-semibold">Active Monitoring</span>
                  </p>
                </div>
              </div>

              <button
                onClick={() => setChatOpen(true)}
                className="px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold flex items-center space-x-2 shadow-lg shadow-brand-600/30 transition-all self-start md:self-auto"
              >
                <Sparkles className="w-4 h-4" />
                <span>AI Guardian Assistant</span>
              </button>
            </div>
          </div>

          {/* Active Disruption Alert & Recovery Options Modal */}
          {activeIncident && (
            <div className="glass-panel rounded-2xl p-6 border border-amber-500/40 bg-gradient-to-r from-amber-950/30 via-slate-900 to-slate-900 animate-alert-pulse">
              <div className="flex items-start space-x-3 mb-4">
                <div className="p-2.5 rounded-xl bg-amber-500/20 text-amber-400 border border-amber-500/30">
                  <AlertTriangle className="w-6 h-6 animate-bounce" />
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-0.5 rounded bg-red-500/20 text-red-400 text-[10px] font-bold uppercase tracking-wider">
                      {activeIncident.severity} Severity Disruption
                    </span>
                    <span className="text-xs text-slate-400">Detected live</span>
                  </div>
                  <h3 className="text-lg font-bold text-slate-100 mt-0.5">{activeIncident.title}</h3>
                  <p className="text-xs text-slate-300 mt-1">{activeIncident.description}</p>
                </div>
              </div>

              {/* Recovery Options Cards */}
              <div className="mt-4 space-y-3">
                <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center space-x-2">
                  <Sparkles className="w-4 h-4 text-emerald-400" />
                  <span>AI Guardian Alternate Recovery Plans (Select to Approve)</span>
                </h4>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {recoveryPlans.map((plan) => {
                    const isSelected = selectedPlan === plan.id;
                    const isOptionA = plan.option_code === 'OPTION_A';

                    return (
                      <div
                        key={plan.id}
                        onClick={() => setSelectedPlan(plan.id)}
                        className={`cursor-pointer p-4 rounded-xl border flex flex-col justify-between transition-all ${
                          isSelected
                            ? 'bg-slate-800 border-emerald-500 ring-2 ring-emerald-500 shadow-xl'
                            : isOptionA
                              ? 'bg-slate-800/80 border-emerald-500/40 hover:border-emerald-400'
                              : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                        }`}
                      >
                        <div>
                          <div className="flex items-center justify-between mb-2">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              isOptionA ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-slate-700 text-slate-300'
                            }`}>
                              {plan.option_code.replace('_', ' ')}
                              {isOptionA && ' ★ Recommended'}
                            </span>
                            <span className="text-xs font-bold text-emerald-400">
                              {Math.round(plan.confidence_score * 100)}% Confidence
                            </span>
                          </div>

                          <h5 className="font-bold text-xs text-slate-100 mb-1">{plan.title}</h5>
                          <p className="text-[11px] text-slate-400 mb-3">{plan.summary}</p>

                          <div className="space-y-1 text-[11px] bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/60 font-mono mb-3">
                            <div className="flex justify-between">
                              <span className="text-slate-500">Cost Impact:</span>
                              <span className={plan.cost_delta > 0 ? 'text-amber-400' : 'text-emerald-400'}>
                                {plan.cost_delta === 0 ? '₹0 (VIP Covered)' : (plan.cost_delta > 0 ? `+₹${plan.cost_delta}` : `-₹${Math.abs(plan.cost_delta)} Credit`)}
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-slate-500">ETA Delta:</span>
                              <span className="text-slate-300">+{plan.eta_delta_minutes} mins</span>
                            </div>
                          </div>

                          <div className="text-[10px] text-slate-400 italic">
                            <span className="font-semibold text-slate-300">Reasoning:</span> {plan.reasoning}
                          </div>
                        </div>

                        <button
                          disabled={loading}
                          onClick={(e) => {
                            e.stopPropagation();
                            onApprovePlan(activeIncident.id, plan.id);
                          }}
                          className={`mt-4 w-full py-2 px-3 rounded-lg text-xs font-bold flex items-center justify-center space-x-1.5 transition-all ${
                            isOptionA
                              ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/30'
                              : 'bg-brand-600 hover:bg-brand-500 text-white'
                          }`}
                        >
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>Approve & Rebook Plan</span>
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* Itinerary Legs Timeline */}
          <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
            <h3 className="text-sm font-bold text-slate-200 flex items-center space-x-2">
              <Clock className="w-4 h-4 text-brand-400" />
              <span>Full Detailed Travel Itinerary Timeline</span>
            </h3>

            <div className="space-y-3">
              {legs.map((leg, index) => {
                const isFlight = leg.leg_type === 'FLIGHT';
                const isTrain = leg.leg_type === 'TRAIN';
                const isHotel = leg.leg_type === 'HOTEL';

                return (
                  <div
                    key={leg.id}
                    className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4 transition-all hover:border-slate-700"
                  >
                    <div className="flex items-start space-x-3">
                      <div className={`p-3 rounded-xl ${
                        isFlight ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' :
                        isTrain ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20' :
                        'bg-purple-500/10 text-purple-400 border border-purple-500/20'
                      }`}>
                        {isFlight && <Plane className="w-5 h-5" />}
                        {isTrain && <Train className="w-5 h-5" />}
                        {isHotel && <Building className="w-5 h-5" />}
                      </div>

                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="text-xs font-mono text-slate-400">Leg #{index + 1}</span>
                          <h4 className="font-bold text-sm text-slate-100">{leg.title}</h4>
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                            leg.status === 'DELAYED' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                            leg.status === 'REBOOKED' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                            'bg-emerald-500/10 text-emerald-400'
                          }`}>
                            {leg.status}
                          </span>
                        </div>

                        <p className="text-xs text-slate-400 mt-1">
                          {leg.origin} <ArrowRight className="w-3 h-3 inline mx-1" /> {leg.destination}
                        </p>

                        <div className="flex items-center space-x-4 mt-2 text-[11px] text-slate-400">
                          <span>Operator: <strong className="text-slate-300">{leg.operator || 'Standard'}</strong></span>
                          <span>Code: <strong className="text-slate-300 font-mono">{leg.code || 'N/A'}</strong></span>
                        </div>
                      </div>
                    </div>

                    <div className="text-right text-xs text-slate-400 space-y-1 border-t md:border-t-0 md:border-l border-slate-800 pt-2 md:pt-0 md:pl-4">
                      <div>Departure: <span className="text-slate-200 font-mono">{new Date(leg.departure_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span></div>
                      <div>Arrival: <span className="text-slate-200 font-mono">{new Date(leg.arrival_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Guardian AI Assistant Chat Drawer */}
      {chatOpen && (
        <div className="fixed bottom-6 right-6 w-96 glass-panel rounded-2xl border border-brand-500/40 shadow-2xl z-50 overflow-hidden flex flex-col h-[480px]">
          <div className="bg-slate-900 p-3.5 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-emerald-400 animate-pulse" />
              <span className="font-bold text-xs text-slate-100">Travel Guardian AI Assistant</span>
            </div>
            <button onClick={() => setChatOpen(false)} className="text-slate-400 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="flex-1 p-3 overflow-y-auto space-y-3">
            {chatMessages.map((msg, i) => (
              <div key={i} className={`flex ${msg.sender === 'USER' ? 'justify-end' : 'justify-start'}`}>
                <div className={`p-3 rounded-xl text-xs max-w-[80%] ${
                  msg.sender === 'USER'
                    ? 'bg-brand-600 text-white rounded-br-none'
                    : 'bg-slate-800 text-slate-200 border border-slate-700 rounded-bl-none'
                }`}>
                  {msg.text}
                </div>
              </div>
            ))}
          </div>

          <form onSubmit={handleSendMessage} className="p-2.5 bg-slate-900 border-t border-slate-800 flex items-center space-x-2">
            <input
              type="text"
              value={inputMsg}
              onChange={(e) => setInputMsg(e.target.value)}
              placeholder="Ask about your trip protection, weather, or hotel..."
              className="flex-1 bg-slate-950 text-xs text-slate-100 rounded-lg px-3 py-2 border border-slate-800 focus:outline-none focus:border-brand-500"
            />
            <button type="submit" className="p-2 rounded-lg bg-brand-600 text-white hover:bg-brand-500">
              <Send className="w-3.5 h-3.5" />
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
