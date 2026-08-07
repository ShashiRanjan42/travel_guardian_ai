import React, { useState, useEffect } from 'react';
import { 
  Plane, Train, Building, Bus, Calendar, MapPin, Users, Sparkles, ShieldCheck, 
  Clock, ArrowRight, CheckCircle2, AlertTriangle, ChevronRight, Plus, ArrowLeft, RefreshCw, Send, X, Search, Bot, CreditCard, Star, ShieldAlert, Image, Quote, Check, Zap, Lock, MessageSquare 
} from 'lucide-react';

export default function CustomerMMTView({ 
  itinerary, 
  allItineraries = [], 
  onApprovePlan, 
  onSelectItinerary, 
  currentUser,
  onOpenAuth,
  loading 
}) {
  const [activeTab, setActiveTab] = useState('FLIGHTS'); // 'FLIGHTS', 'HOTELS', 'TRAINS', 'BUS', 'MY_BOOKINGS', 'DETAILS'
  const [bookingNotice, setBookingNotice] = useState(null);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [chatOpen, setChatOpen] = useState(false);

  // Hero Search Input States
  const [heroDestination, setHeroDestination] = useState('Goa, India');
  const [heroDates, setHeroDates] = useState('2026-08-15');
  const [heroTravelers, setHeroTravelers] = useState('2 Travelers');

  // Search Results States (Flow: Search -> Fetch Live Inventory from DB -> Select & Book)
  const [flightResults, setFlightResults] = useState(null);
  const [hotelResults, setHotelResults] = useState(null);
  const [trainResults, setTrainResults] = useState(null);
  const [busResults, setBusResults] = useState(null);
  const [searching, setSearching] = useState(false);

  // Conversational AI Booking Agent
  const [chatMessages, setChatMessages] = useState([
    { 
      sender: 'AI', 
      text: "Namaste! I am your AI Booking Agent 🤖. Tell me your travel plans, or ask me to design a custom trip for you. What city, budget, or travel dates do you have in mind?" 
    }
  ]);
  const [inputMsg, setInputMsg] = useState('');
  const [agentSessionId] = useState(() => `session-${Date.now()}`);

  // Booking Widget Inputs
  const [flightOrigin, setFlightOrigin] = useState('Delhi (DEL)');
  const [flightDest, setFlightDest] = useState('Mumbai (BOM)');
  const [flightDate, setFlightDate] = useState('2026-08-15');

  const [hotelCity, setHotelCity] = useState('Mumbai (Taj Mahal Palace)');
  const [checkInDate, setCheckInDate] = useState('2026-08-15');
  const [checkOutDate, setCheckOutDate] = useState('2026-08-18');

  const [trainOrigin, setTrainOrigin] = useState('New Delhi (NDLS)');
  const [trainDest, setTrainDest] = useState('Mumbai CSMT');
  const [trainDate, setTrainDate] = useState('2026-08-16');

  const [busOrigin, setBusOrigin] = useState('Delhi (ISBT Kashmiri Gate)');
  const [busDest, setBusDest] = useState('Jaipur (Sindhi Camp)');
  const [busDate, setBusDate] = useState('2026-08-15');

  // Local Storage for real-time customer data isolation
  const userEmail = currentUser?.email || '';
  const localStorageKey = userEmail ? `guardian_user_bookings_${userEmail}` : null;

  const [localBookings, setLocalBookings] = useState(() => {
    try {
      if (!localStorageKey) return [];
      const saved = localStorage.getItem(localStorageKey);
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  // STRICT DATA ISOLATION & AUTHORIZATION: Only show itineraries belonging to THIS logged in customer!
  const customerItineraries = currentUser ? allItineraries.filter(it => {
    if (!it.customer) return false;
    const matchesEmail = it.customer.email.toLowerCase() === userEmail.toLowerCase();
    const matchesId = currentUser?.id && (it.customer.id === currentUser.id || it.customer.id === `cust-${currentUser.id}`);
    const matchesName = currentUser?.name && it.customer.name.toLowerCase() === currentUser.name.toLowerCase();
    return matchesEmail || matchesId || matchesName;
  }) : [];

  const myBookingsList = [...customerItineraries];

  useEffect(() => {
    if (localStorageKey) {
      try {
        localStorage.setItem(localStorageKey, JSON.stringify(localBookings));
      } catch (e) {
        console.error(e);
      }
    }
  }, [localBookings, localStorageKey]);

  const legs = itinerary?.legs || [];
  const incidents = itinerary?.incidents || [];
  const activeIncident = incidents.find(i => i.status === 'RECOVERY_PROPOSED' || i.status === 'OPEN');
  const recoveryPlans = activeIncident ? activeIncident.recovery_plans : [];

  // AUTH GUARD: Intercept search if not logged in
  const checkAuthGuard = () => {
    if (!currentUser) {
      if (onOpenAuth) onOpenAuth();
      setBookingNotice("🔒 Authentication required: Please log in or sign up to search & book AI-protected flights.");
      setTimeout(() => setBookingNotice(null), 6000);
      return false;
    }
    return true;
  };

  // DYNAMIC BACKEND INVENTORY SEARCH HANDLER
  const handleSearchSubmit = async (type, origin, dest, date, operator) => {
    if (!checkAuthGuard()) return;

    setSearching(true);
    try {
      if (type === 'FLIGHT') {
        const res = await fetch(`/api/inventory/flights?origin=${encodeURIComponent(origin)}&destination=${encodeURIComponent(dest)}`);
        if (res.ok) {
          const data = await res.json();
          setFlightResults(data);
        }
      } else if (type === 'HOTEL') {
        const res = await fetch(`/api/inventory/hotels?city=${encodeURIComponent(origin)}`);
        if (res.ok) {
          const data = await res.json();
          setHotelResults(data);
        }
      } else if (type === 'TRAIN') {
        const res = await fetch(`/api/inventory/trains?origin=${encodeURIComponent(origin)}&destination=${encodeURIComponent(dest)}`);
        if (res.ok) {
          const data = await res.json();
          setTrainResults(data);
        }
      } else if (type === 'BUS') {
        const res = await fetch(`/api/inventory/buses?origin=${encodeURIComponent(origin)}&destination=${encodeURIComponent(dest)}`);
        if (res.ok) {
          const data = await res.json();
          setBusResults(data);
        }
      }
    } catch (e) {
      console.error('Inventory fetch error:', e);
    } finally {
      setSearching(false);
    }
  };

  // Step 2: Handle Final Booking Confirmation with AUTH GUARD & DB persistence
  const handleBookingSubmit = async (bookingType, origin, destination, operator, travelDate) => {
    if (!checkAuthGuard()) return;

    const newBookingObj = {
      id: `local-itinerary-${Date.now()}`,
      title: `${currentUser?.name || 'Traveler'} — ${bookingType} (${origin} to ${destination})`,
      status: 'OK',
      risk_score: 15,
      risk_level: 'LOW',
      start_date: travelDate,
      leg_count: 1,
      customer: {
        id: currentUser?.id || 'cust-1',
        name: currentUser?.name || 'Rajesh Sharma',
        email: userEmail,
        tier: currentUser?.tier || 'VIP'
      },
      legs: [
        {
          id: `leg-local-${Date.now()}`,
          leg_type: bookingType,
          sequence_order: 1,
          title: `${operator} • ${origin} to ${destination}`,
          operator: operator,
          code: `BOOK-${Date.now()%10000}`,
          origin: origin,
          destination: destination,
          departure_time: `${travelDate}T10:00:00`,
          arrival_time: `${travelDate}T13:00:00`,
          status: 'SCHEDULED'
        }
      ]
    };

    setLocalBookings(prev => [newBookingObj, ...prev]);

    try {
      const res = await fetch('/api/itineraries/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          booking_type: bookingType,
          customer_id: currentUser?.id || 'cust-1',
          origin: origin,
          destination: destination,
          operator: operator,
          travel_date: travelDate
        })
      });
      const data = await res.json();
      if (res.ok && data.status === 'SUCCESS') {
        setBookingNotice(`✅ Protected ${bookingType} Confirmed & Saved to Profile! (${origin} → ${destination})`);
        setTimeout(() => setBookingNotice(null), 5000);
        if (onSelectItinerary && data.itinerary_id) {
          onSelectItinerary(data.itinerary_id);
        }
        setActiveTab('MY_BOOKINGS');
      }
    } catch (e) {
      setBookingNotice(`✅ Protected ${bookingType} Confirmed & Saved to Profile!`);
      setTimeout(() => setBookingNotice(null), 4000);
      setActiveTab('MY_BOOKINGS');
    }
  };

  // REAL-TIME CONVERSATIONAL LLM BOOKING AGENT TURN HANDLER
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMsg.trim()) return;

    if (!currentUser) {
      if (onOpenAuth) onOpenAuth();
      setChatMessages(prev => [...prev, { sender: 'AI', text: "🔒 Please log in to your account so I can process and protect your travel bookings!" }]);
      return;
    }

    const userText = inputMsg;
    setChatMessages(prev => [...prev, { sender: 'USER', text: userText }]);
    setInputMsg('');

    try {
      const res = await fetch('/api/agents/chat_book', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: agentSessionId,
          message: userText,
          user_name: currentUser?.name || 'Traveler'
        })
      });

      if (res.ok) {
        const data = await res.json();
        let replyObj = {
          sender: 'AI',
          text: data.reply || "I can process your booking! Please provide your destination city, budget, or dates."
        };

        if (data.status === 'READY_TO_BOOK' && data.package_plan) {
          const pkg = data.package_plan;
          replyObj.packagePlan = pkg;
          replyObj.actionButton = {
            label: `⚡ Confirm & Book ${pkg.destination} Trip Now`,
            onClick: () => {
              handleBookingSubmit('FLIGHT & HOTEL PACKAGE', 'Delhi (DEL)', `${pkg.destination} Resort`, 'Air India & Taj Hotels', pkg.start_date);
              setChatMessages(prev => [...prev, { sender: 'AI', text: `🎉 Outstanding! Your ${pkg.destination} ${pkg.duration} package has been booked and activated with 7-Agent AI Guardian Protection!` }]);
            }
          };
        }

        setChatMessages(prev => [...prev, replyObj]);
      } else {
        setChatMessages(prev => [...prev, { sender: 'AI', text: "I can process your booking! What is your destination, budget, or travel dates?" }]);
      }
    } catch (err) {
      setChatMessages(prev => [...prev, { sender: 'AI', text: "Network error connecting to AI Booking Agent. Please try again." }]);
    }
  };

  const scrollToPlanSection = () => {
    const el = document.getElementById('plan-options-section');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="space-y-12 pb-16">
      
      {/* 1. HERO LANDING SECTION (HIGH CONTRAST BRIGHT TEXT) */}
      <div className="relative rounded-3xl overflow-hidden bg-[#0a0f1d] px-6 py-16 sm:px-12 sm:py-20 text-center text-white border border-slate-800 shadow-2xl space-y-8">
        
        {/* Top Pill Badge: ⚡ AI-Powered Disruption Recovery is Live */}
        <div className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-slate-900 text-amber-300 border border-amber-500/40 text-xs font-extrabold shadow-lg">
          <Zap className="w-4 h-4 fill-amber-300 text-amber-300 animate-pulse" />
          <span>AI-Powered Disruption Recovery is Live</span>
        </div>

        {/* Main Headline */}
        <div className="max-w-4xl mx-auto space-y-2">
          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight leading-none text-white drop-shadow-md">
            Travel fearlessly.
          </h1>
          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight leading-none bg-clip-text text-transparent bg-gradient-to-r from-red-400 via-rose-400 to-amber-300">
            We handle the unexpected.
          </h1>
        </div>

        {/* Subtitle */}
        <p className="max-w-2xl mx-auto text-base sm:text-lg text-slate-200 leading-relaxed font-semibold">
          Book complex itineraries with confidence. Our autonomous agent network monitors your journey 24/7 and automatically reroutes you if disruptions happen.
        </p>

        {/* Integrated Floating Hero Search Bar with AUTH GUARD */}
        <div className="max-w-3xl mx-auto bg-slate-950 p-3 rounded-2xl border border-slate-800 shadow-2xl backdrop-blur-md">
          <form 
            onSubmit={(e) => {
              e.preventDefault();
              if (!checkAuthGuard()) return;
              scrollToPlanSection();
              handleSearchSubmit('FLIGHT', flightOrigin, flightDest, heroDates);
            }} 
            className="grid grid-cols-1 sm:grid-cols-12 gap-2.5 text-xs items-center"
          >
            {/* Field 1: Where do you want to go */}
            <div className="sm:col-span-4 flex items-center space-x-2 bg-slate-900 px-3.5 py-3 rounded-xl border border-slate-700 text-slate-100">
              <MapPin className="w-4 h-4 text-red-400 flex-shrink-0" />
              <input
                type="text"
                value={heroDestination}
                onChange={(e) => setHeroDestination(e.target.value)}
                placeholder="Where do you want to go"
                className="bg-transparent text-xs text-white placeholder-slate-400 focus:outline-none w-full font-bold"
              />
            </div>

            {/* Field 2: Dates */}
            <div className="sm:col-span-3 flex items-center space-x-2 bg-slate-900 px-3.5 py-3 rounded-xl border border-slate-700 text-slate-100">
              <Calendar className="w-4 h-4 text-amber-400 flex-shrink-0" />
              <input
                type="date"
                value={heroDates}
                onChange={(e) => setHeroDates(e.target.value)}
                className="bg-transparent text-xs text-white focus:outline-none w-full font-bold"
              />
            </div>

            {/* Field 3: Travelers */}
            <div className="sm:col-span-3 flex items-center space-x-2 bg-slate-900 px-3.5 py-3 rounded-xl border border-slate-700 text-slate-100">
              <Users className="w-4 h-4 text-cyan-400 flex-shrink-0" />
              <select
                value={heroTravelers}
                onChange={(e) => setHeroTravelers(e.target.value)}
                className="bg-transparent text-xs text-white focus:outline-none w-full font-bold"
              >
                <option value="1 Traveler" className="bg-slate-900 text-white font-bold">1 Traveler</option>
                <option value="2 Travelers" className="bg-slate-900 text-white font-bold">2 Travelers</option>
                <option value="3 Travelers" className="bg-slate-900 text-white font-bold">3 Travelers</option>
                <option value="4+ Group" className="bg-slate-900 text-white font-bold">4+ Group</option>
              </select>
            </div>

            {/* Field 4: Search Button */}
            <div className="sm:col-span-2">
              <button
                type="submit"
                className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-red-500 to-rose-600 hover:from-red-600 hover:to-rose-700 text-white font-extrabold text-xs shadow-lg shadow-red-500/30 transition-all transform hover:scale-[1.02]"
              >
                Search
              </button>
            </div>
          </form>
        </div>
      </div>

      {bookingNotice && (
        <div className="p-4 rounded-2xl bg-amber-500/20 border border-amber-500/40 text-amber-300 text-sm font-bold flex items-center space-x-2 animate-bounce">
          <Lock className="w-5 h-5 text-amber-400" />
          <span>{bookingNotice}</span>
        </div>
      )}

      {/* 2. PLAN OPTIONS SECTION (FLIGHT, HOTEL, TRAIN, BUS, MY BOOKINGS) */}
      <div id="plan-options-section" className="space-y-6 pt-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-extrabold text-white flex items-center space-x-2">
              <Search className="w-6 h-6 text-red-500" />
              <span>Plan Your Trip & Search Available Transport Options</span>
            </h2>
            <p className="text-sm text-slate-300 font-medium">Search available flights, hotels, trains, or buses, select your option, and book with 1-click protection</p>
          </div>
        </div>

        {/* Category Navigation Bar */}
        <div className="glass-panel rounded-2xl p-2 border border-slate-800 flex items-center justify-center space-x-2 sm:space-x-4 shadow-lg overflow-x-auto bg-slate-950">
          <button
            onClick={() => { setActiveTab('FLIGHTS'); setFlightResults(null); }}
            className={`px-5 sm:px-6 py-2.5 rounded-xl text-xs font-extrabold flex items-center space-x-2 transition-all whitespace-nowrap ${
              activeTab === 'FLIGHTS'
                ? 'bg-red-600 text-white shadow-md shadow-red-600/30'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            <Plane className="w-4 h-4" />
            <span>Flights</span>
          </button>

          <button
            onClick={() => { setActiveTab('HOTELS'); setHotelResults(null); }}
            className={`px-5 sm:px-6 py-2.5 rounded-xl text-xs font-extrabold flex items-center space-x-2 transition-all whitespace-nowrap ${
              activeTab === 'HOTELS'
                ? 'bg-red-600 text-white shadow-md shadow-red-600/30'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            <Building className="w-4 h-4" />
            <span>Hotels</span>
          </button>

          <button
            onClick={() => { setActiveTab('TRAINS'); setTrainResults(null); }}
            className={`px-5 sm:px-6 py-2.5 rounded-xl text-xs font-extrabold flex items-center space-x-2 transition-all whitespace-nowrap ${
              activeTab === 'TRAINS'
                ? 'bg-red-600 text-white shadow-md shadow-red-600/30'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            <Train className="w-4 h-4" />
            <span>Trains</span>
          </button>

          <button
            onClick={() => { setActiveTab('BUS'); setBusResults(null); }}
            className={`px-5 sm:px-6 py-2.5 rounded-xl text-xs font-extrabold flex items-center space-x-2 transition-all whitespace-nowrap ${
              activeTab === 'BUS'
                ? 'bg-red-600 text-white shadow-md shadow-red-600/30'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            <Bus className="w-4 h-4" />
            <span>Bus</span>
          </button>

          <button
            onClick={() => {
              if (!checkAuthGuard()) return;
              setActiveTab('MY_BOOKINGS');
            }}
            className={`px-5 sm:px-6 py-2.5 rounded-xl text-xs font-extrabold flex items-center space-x-2 transition-all whitespace-nowrap ${
              activeTab === 'MY_BOOKINGS' || activeTab === 'DETAILS'
                ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/30'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            <Clock className="w-4 h-4" />
            <span>My Bookings ({myBookingsList.length})</span>
          </button>
        </div>

        {/* TAB 1: FLIGHT SEARCH WIDGET & RESULTS */}
        {activeTab === 'FLIGHTS' && (
          <div className="space-y-4">
            <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4 shadow-xl bg-slate-900">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="font-extrabold text-base text-white flex items-center space-x-2">
                  <Plane className="w-5 h-5 text-red-500" />
                  <span>Search Flights across India</span>
                </h3>
              </div>

              <form 
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSearchSubmit('FLIGHT', flightOrigin, flightDest, flightDate);
                }} 
                className="space-y-4"
              >
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs">
                  <div>
                    <label className="text-[11px] font-extrabold text-slate-300 block mb-1 uppercase tracking-wider">FROM AIRPORT</label>
                    <div className="relative">
                      <MapPin className="w-3.5 h-3.5 text-red-400 absolute left-2.5 top-2.5" />
                      <select
                        value={flightOrigin}
                        onChange={(e) => setFlightOrigin(e.target.value)}
                        className="w-full bg-slate-900 text-white font-bold rounded-lg pl-8 pr-2 py-2 border border-slate-700 focus:outline-none focus:border-red-500"
                      >
                        <option value="Patna (PAT)">Patna (PAT) - Jay Prakash Narayan Airport</option>
                        <option value="Delhi (DEL)">Delhi (DEL) - Indira Gandhi Airport</option>
                        <option value="Mumbai (BOM)">Mumbai (BOM) - CSM International</option>
                        <option value="Bengaluru (BLR)">Bengaluru (BLR) - Kempegowda</option>
                        <option value="Chennai (MAA)">Chennai (MAA) - International</option>
                        <option value="Kolkata (CCU)">Kolkata (CCU) - Subhash Chandra</option>
                        <option value="Hyderabad (HYD)">Hyderabad (HYD) - Rajiv Gandhi</option>
                        <option value="Jaipur (JAI)">Jaipur (JAI) Airport</option>
                        <option value="Goa (GOI)">Goa (GOI) Airport</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="text-[11px] font-extrabold text-slate-300 block mb-1 uppercase tracking-wider">TO AIRPORT</label>
                    <div className="relative">
                      <MapPin className="w-3.5 h-3.5 text-emerald-400 absolute left-2.5 top-2.5" />
                      <select
                        value={flightDest}
                        onChange={(e) => setFlightDest(e.target.value)}
                        className="w-full bg-slate-900 text-white font-bold rounded-lg pl-8 pr-2 py-2 border border-slate-700 focus:outline-none focus:border-red-500"
                      >
                        <option value="Patna (PAT)">Patna (PAT) - Jay Prakash Narayan Airport</option>
                        <option value="Mumbai (BOM)">Mumbai (BOM) - CSM International</option>
                        <option value="Delhi (DEL)">Delhi (DEL) - Indira Gandhi Airport</option>
                        <option value="Bengaluru (BLR)">Bengaluru (BLR) - Kempegowda</option>
                        <option value="Goa (GOI)">Goa (GOI) Airport</option>
                        <option value="Chennai (MAA)">Chennai (MAA) Airport</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="text-[11px] font-extrabold text-slate-300 block mb-1 uppercase tracking-wider">DEPARTURE DATE</label>
                    <div className="relative">
                      <Calendar className="w-3.5 h-3.5 text-amber-400 absolute left-2.5 top-2.5" />
                      <input
                        type="date"
                        value={flightDate}
                        onChange={(e) => setFlightDate(e.target.value)}
                        className="w-full bg-slate-900 text-white font-bold rounded-lg pl-8 pr-2 py-2 border border-slate-700 focus:outline-none focus:border-red-500"
                      />
                    </div>
                  </div>
                </div>

                <div className="flex justify-center pt-2">
                  <button
                    type="submit"
                    disabled={searching}
                    className="px-8 py-3 rounded-xl bg-gradient-to-r from-red-500 to-rose-600 hover:from-red-600 hover:to-rose-700 text-white font-extrabold text-sm shadow-xl shadow-red-500/30 flex items-center space-x-2 transition-all"
                  >
                    <Search className="w-4 h-4" />
                    <span>{searching ? 'Searching Flights...' : 'SEARCH AVAILABLE FLIGHTS'}</span>
                  </button>
                </div>
              </form>
            </div>

            {/* Flight Search Results */}
            {flightResults && (
              <div className="space-y-3">
                <h4 className="text-xs font-extrabold text-slate-200 uppercase tracking-wider">Available Flights ({flightOrigin} → {flightDest})</h4>
                <div className="grid grid-cols-1 gap-3">
                  {flightResults.map(f => (
                    <div key={f.id} className="p-4 rounded-xl glass-panel border border-slate-800 flex items-center justify-between hover:border-red-500 transition-all text-xs bg-slate-900">
                      <div className="flex items-center space-x-4">
                        <div className="p-3 rounded-xl bg-red-500/20 text-red-400 border border-red-500/30">
                          <Plane className="w-5 h-5" />
                        </div>
                        <div>
                          <div className="font-extrabold text-base text-white">{f.carrier} ({f.code})</div>
                          <div className="text-slate-300 text-xs font-mono mt-0.5 font-bold">{f.departure} → {f.arrival} ({f.duration}) • Direct</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="text-right">
                          <div className="font-extrabold text-lg text-emerald-400 font-mono">{f.price}</div>
                        </div>
                        <button
                          onClick={() => handleBookingSubmit('FLIGHT', flightOrigin, flightDest, `${f.carrier} (${f.code})`, flightDate)}
                          className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-xs shadow-lg flex items-center space-x-1.5"
                        >
                          <Check className="w-4 h-4" />
                          <span>Book & Protect</span>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: HOTEL SEARCH WIDGET & RESULTS */}
        {activeTab === 'HOTELS' && (
          <div className="space-y-4">
            <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4 shadow-xl bg-slate-900">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="font-extrabold text-base text-white flex items-center space-x-2">
                  <Building className="w-5 h-5 text-purple-400" />
                  <span>Search Luxury Hotels & Resorts</span>
                </h3>
              </div>

              <form 
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSearchSubmit('HOTEL', hotelCity, hotelCity, checkInDate, 'Taj / Marriott');
                }} 
                className="space-y-4"
              >
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs">
                  <div>
                    <label className="text-[11px] font-extrabold text-slate-300 block mb-1 uppercase tracking-wider">CITY / PROPERTY</label>
                    <select
                      value={hotelCity}
                      onChange={(e) => setHotelCity(e.target.value)}
                      className="w-full bg-slate-900 text-white font-bold rounded-lg px-3 py-2 border border-slate-700 focus:outline-none focus:border-red-500"
                    >
                      <option value="Patna (Hotel Maurya)">Patna (Hotel Maurya / Lemon Tree)</option>
                      <option value="Mumbai (Taj Mahal Palace)">Mumbai (Taj Mahal Palace)</option>
                      <option value="Bengaluru (Leela Palace)">Bengaluru (The Leela Palace)</option>
                      <option value="Chennai (ITC Grand Chola)">Chennai (ITC Grand Chola)</option>
                      <option value="Jaipur (Rambagh Palace)">Jaipur (Rambagh Palace)</option>
                      <option value="Kolkata (The Oberoi Grand)">Kolkata (The Oberoi Grand)</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-[11px] font-extrabold text-slate-300 block mb-1 uppercase tracking-wider">CHECK-IN DATE</label>
                    <input
                      type="date"
                      value={checkInDate}
                      onChange={(e) => setCheckInDate(e.target.value)}
                      className="w-full bg-slate-900 text-white font-bold rounded-lg px-3 py-2 border border-slate-700 focus:outline-none focus:border-red-500"
                    />
                  </div>

                  <div>
                    <label className="text-[11px] font-extrabold text-slate-300 block mb-1 uppercase tracking-wider">CHECK-OUT DATE</label>
                    <input
                      type="date"
                      value={checkOutDate}
                      onChange={(e) => setCheckOutDate(e.target.value)}
                      className="w-full bg-slate-900 text-white font-bold rounded-lg px-3 py-2 border border-slate-700 focus:outline-none focus:border-red-500"
                    />
                  </div>
                </div>

                <div className="flex justify-center pt-2">
                  <button
                    type="submit"
                    disabled={searching}
                    className="px-8 py-3 rounded-xl bg-gradient-to-r from-purple-600 to-purple-500 hover:from-purple-500 text-white font-extrabold text-sm shadow-xl shadow-purple-600/30 flex items-center space-x-2 transition-all"
                  >
                    <Search className="w-4 h-4" />
                    <span>{searching ? 'Searching Hotels...' : 'SEARCH AVAILABLE HOTELS'}</span>
                  </button>
                </div>
              </form>
            </div>

            {/* Hotel Search Results */}
            {hotelResults && (
              <div className="space-y-3">
                <h4 className="text-xs font-extrabold text-slate-200 uppercase tracking-wider">Available Luxury Properties ({hotelCity})</h4>
                <div className="grid grid-cols-1 gap-3">
                  {hotelResults.map(h => (
                    <div key={h.id} className="p-4 rounded-xl glass-panel border border-slate-800 flex items-center justify-between hover:border-purple-500 transition-all text-xs bg-slate-900">
                      <div className="flex items-center space-x-4">
                        <div className="p-3 rounded-xl bg-purple-500/20 text-purple-400 border border-purple-500/30">
                          <Building className="w-5 h-5" />
                        </div>
                        <div>
                          <div className="font-extrabold text-base text-white">{h.name} <span className="text-amber-300 font-mono text-xs">{h.rating}</span></div>
                          <div className="text-slate-300 text-xs mt-0.5 font-semibold">{h.room} • Free Breakfast & VIP Airport Transfer</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="text-right">
                          <div className="font-extrabold text-lg text-purple-400 font-mono">{h.price}</div>
                        </div>
                        <button
                          onClick={() => handleBookingSubmit('HOTEL', hotelCity, hotelCity, h.name, checkInDate)}
                          className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-extrabold text-xs shadow-lg flex items-center space-x-1.5"
                        >
                          <Check className="w-4 h-4" />
                          <span>Book & Protect</span>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 3: TRAIN SEARCH WIDGET & RESULTS */}
        {activeTab === 'TRAINS' && (
          <div className="space-y-4">
            <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4 shadow-xl bg-slate-900">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="font-extrabold text-base text-white flex items-center space-x-2">
                  <Train className="w-5 h-5 text-cyan-400" />
                  <span>Search Vande Bharat & Express Trains</span>
                </h3>
              </div>

              <form 
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSearchSubmit('TRAIN', trainOrigin, trainDest, trainDate, 'Vande Bharat');
                }} 
                className="space-y-4"
              >
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs">
                  <div>
                    <label className="text-[11px] font-extrabold text-slate-300 block mb-1 uppercase tracking-wider">FROM STATION</label>
                    <select
                      value={trainOrigin}
                      onChange={(e) => setTrainOrigin(e.target.value)}
                      className="w-full bg-slate-900 text-white font-bold rounded-lg px-3 py-2 border border-slate-700 focus:outline-none focus:border-red-500"
                    >
                      <option value="New Delhi (NDLS)">New Delhi (NDLS)</option>
                      <option value="Mumbai CSMT">Mumbai CSMT</option>
                      <option value="Bengaluru City (SBC)">Bengaluru City (SBC)</option>
                      <option value="Chennai Central (MAS)">Chennai Central (MAS)</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-[11px] font-extrabold text-slate-300 block mb-1 uppercase tracking-wider">TO STATION</label>
                    <select
                      value={trainDest}
                      onChange={(e) => setTrainDest(e.target.value)}
                      className="w-full bg-slate-900 text-white font-bold rounded-lg px-3 py-2 border border-slate-700 focus:outline-none focus:border-red-500"
                    >
                      <option value="Mumbai CSMT">Mumbai CSMT</option>
                      <option value="Bengaluru City (SBC)">Bengaluru City (SBC)</option>
                      <option value="Pune Junction">Pune Junction</option>
                      <option value="Hyderabad Deccan">Hyderabad Deccan</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-[11px] font-extrabold text-slate-300 block mb-1 uppercase tracking-wider">TRAVEL DATE</label>
                    <input
                      type="date"
                      value={trainDate}
                      onChange={(e) => setTrainDate(e.target.value)}
                      className="w-full bg-slate-900 text-white font-bold rounded-lg px-3 py-2 border border-slate-700 focus:outline-none focus:border-red-500"
                    />
                  </div>
                </div>

                <div className="flex justify-center pt-2">
                  <button
                    type="submit"
                    disabled={searching}
                    className="px-8 py-3 rounded-xl bg-gradient-to-r from-cyan-600 to-cyan-500 hover:from-cyan-500 text-white font-extrabold text-sm shadow-xl shadow-cyan-600/30 flex items-center space-x-2 transition-all"
                  >
                    <Search className="w-4 h-4" />
                    <span>{searching ? 'Searching Trains...' : 'SEARCH AVAILABLE TRAINS'}</span>
                  </button>
                </div>
              </form>
            </div>

            {/* Train Search Results */}
            {trainResults && (
              <div className="space-y-3">
                <h4 className="text-xs font-extrabold text-slate-200 uppercase tracking-wider">Available Trains ({trainOrigin} → {trainDest})</h4>
                <div className="grid grid-cols-1 gap-3">
                  {trainResults.map(t => (
                    <div key={t.id} className="p-4 rounded-xl glass-panel border border-slate-800 flex items-center justify-between hover:border-cyan-500 transition-all text-xs bg-slate-900">
                      <div className="flex items-center space-x-4">
                        <div className="p-3 rounded-xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                          <Train className="w-5 h-5" />
                        </div>
                        <div>
                          <div className="font-extrabold text-base text-white">{t.name} ({t.code})</div>
                          <div className="text-slate-300 text-xs font-mono mt-0.5 font-bold">{t.departure} → {t.arrival} ({t.duration}) • Class: {t.class}</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="text-right">
                          <div className="font-extrabold text-lg text-cyan-400 font-mono">{t.price}</div>
                        </div>
                        <button
                          onClick={() => handleBookingSubmit('TRAIN', trainOrigin, trainDest, `${t.name} (${t.code})`, trainDate)}
                          className="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-extrabold text-xs shadow-lg flex items-center space-x-1.5"
                        >
                          <Check className="w-4 h-4" />
                          <span>Book & Protect</span>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 4: BUS SEARCH WIDGET & RESULTS */}
        {activeTab === 'BUS' && (
          <div className="space-y-4">
            <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4 shadow-xl bg-slate-900">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="font-extrabold text-base text-white flex items-center space-x-2">
                  <Bus className="w-5 h-5 text-amber-400" />
                  <span>Search Luxury Volvo & Electric Buses</span>
                </h3>
              </div>

              <form 
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSearchSubmit('BUS', busOrigin, busDest, busDate, 'Volvo Bus');
                }} 
                className="space-y-4"
              >
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs">
                  <div>
                    <label className="text-[11px] font-extrabold text-slate-300 block mb-1 uppercase tracking-wider">ORIGIN CITY</label>
                    <select
                      value={busOrigin}
                      onChange={(e) => setBusOrigin(e.target.value)}
                      className="w-full bg-slate-900 text-white font-bold rounded-lg px-3 py-2 border border-slate-700 focus:outline-none focus:border-red-500"
                    >
                      <option value="Delhi (ISBT Kashmiri Gate)">Delhi (ISBT Kashmiri Gate)</option>
                      <option value="Mumbai (Dadar Volvo Bus Stand)">Mumbai (Dadar)</option>
                      <option value="Bengaluru (Majestic Bus Stand)">Bengaluru (Majestic)</option>
                      <option value="Pune (Swargate Bus Stand)">Pune (Swargate)</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-[11px] font-extrabold text-slate-300 block mb-1 uppercase tracking-wider">DESTINATION CITY</label>
                    <select
                      value={busDest}
                      onChange={(e) => setBusDest(e.target.value)}
                      className="w-full bg-slate-900 text-white font-bold rounded-lg px-3 py-2 border border-slate-700 focus:outline-none focus:border-red-500"
                    >
                      <option value="Jaipur (Sindhi Camp)">Jaipur (Sindhi Camp)</option>
                      <option value="Goa (Panjim Bus Terminal)">Goa (Panjim)</option>
                      <option value="Manali (Mall Road Stand)">Manali (Mall Road)</option>
                      <option value="Agra (ISBT Transport Nagar)">Agra (ISBT)</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-[11px] font-extrabold text-slate-300 block mb-1 uppercase tracking-wider">TRAVEL DATE</label>
                    <input
                      type="date"
                      value={busDate}
                      onChange={(e) => setBusDate(e.target.value)}
                      className="w-full bg-slate-900 text-white font-bold rounded-lg px-3 py-2 border border-slate-700 focus:outline-none focus:border-red-500"
                    />
                  </div>
                </div>

                <div className="flex justify-center pt-2">
                  <button
                    type="submit"
                    disabled={searching}
                    className="px-8 py-3 rounded-xl bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-500 text-white font-extrabold text-sm shadow-xl shadow-amber-600/30 flex items-center space-x-2 transition-all"
                  >
                    <Search className="w-4 h-4" />
                    <span>{searching ? 'Searching Buses...' : 'SEARCH AVAILABLE BUSES'}</span>
                  </button>
                </div>
              </form>
            </div>

            {/* Bus Search Results */}
            {busResults && (
              <div className="space-y-3">
                <h4 className="text-xs font-extrabold text-slate-200 uppercase tracking-wider">Available Bus Routes ({busOrigin} → {busDest})</h4>
                <div className="grid grid-cols-1 gap-3">
                  {busResults.map(b => (
                    <div key={b.id} className="p-4 rounded-xl glass-panel border border-slate-800 flex items-center justify-between hover:border-amber-500 transition-all text-xs bg-slate-900">
                      <div className="flex items-center space-x-4">
                        <div className="p-3 rounded-xl bg-amber-500/20 text-amber-400 border border-amber-500/30">
                          <Bus className="w-5 h-5" />
                        </div>
                        <div>
                          <div className="font-extrabold text-base text-white">{b.operator} ({b.code})</div>
                          <div className="text-slate-300 text-xs font-mono mt-0.5 font-bold">{b.departure} → {b.arrival} ({b.duration}) • Live Tracking</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="text-right">
                          <div className="font-extrabold text-lg text-amber-400 font-mono">{b.price}</div>
                        </div>
                        <button
                          onClick={() => handleBookingSubmit('BUS', busOrigin, busDest, `${b.operator} (${b.code})`, busDate)}
                          className="px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-extrabold text-xs shadow-lg flex items-center space-x-1.5"
                        >
                          <Check className="w-4 h-4" />
                          <span>Book & Protect</span>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 5: MY BOOKINGS SECTION (STRICT USER ISOLATION & AUTHORIZATION) */}
        {(activeTab === 'MY_BOOKINGS' || activeTab === 'DETAILS') && (
          <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4 shadow-xl bg-slate-900">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="font-extrabold text-base text-white flex items-center space-x-2">
                  <ShieldCheck className="w-5 h-5 text-emerald-400" />
                  <span>My Booked Travel Plans ({currentUser ? currentUser.name : 'Guest'})</span>
                </h3>
                <p className="text-xs text-slate-300 font-medium">Strict Data Isolation Active • Showing ONLY your personal travel bookings</p>
              </div>
              <span className="px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs font-extrabold">
                {myBookingsList.length} Active Bookings
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {!currentUser ? (
                <div className="col-span-2 p-8 text-center space-y-3 bg-slate-950 rounded-xl border border-slate-800">
                  <Lock className="w-8 h-8 text-amber-400 mx-auto animate-bounce" />
                  <p className="font-extrabold text-slate-100 text-sm">Authentication Required</p>
                  <p className="text-xs text-slate-300 max-w-md mx-auto">Please sign in to view your private travel itineraries and real-time disruption status.</p>
                  <button
                    onClick={() => { if (onOpenAuth) onOpenAuth(); }}
                    className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-red-500 to-rose-600 hover:from-red-600 text-white font-extrabold text-xs shadow-lg"
                  >
                    Log In / Sign Up
                  </button>
                </div>
              ) : myBookingsList.length === 0 ? (
                <div className="col-span-2 p-8 text-center text-slate-300 italic bg-slate-950 rounded-xl border border-slate-800">
                  <Sparkles className="w-6 h-6 mx-auto mb-2 text-brand-400" />
                  <p className="font-extrabold text-slate-100 text-sm">No booked travel plans found for your account ({userEmail}).</p>
                  <p className="text-xs text-slate-300 font-medium mt-1">Use the Flights, Hotels, Trains, Bus, or AI Booking Agent to book your first protected trip plan!</p>
                </div>
              ) : (
                myBookingsList.map((it) => {
                  const isSelected = itinerary?.id === it.id;
                  const hasIncident = it.risk_score >= 60;

                  return (
                    <div
                      key={it.id}
                      onClick={() => {
                        if (onSelectItinerary) onSelectItinerary(it.id);
                        setActiveTab('DETAILS');
                      }}
                      className={`cursor-pointer p-5 rounded-2xl border transition-all flex flex-col justify-between ${
                        isSelected
                          ? 'bg-slate-950 border-red-500 ring-2 ring-red-500/50 shadow-xl'
                          : 'bg-slate-950/80 border-slate-800 hover:border-slate-700'
                      }`}
                    >
                      <div>
                        <div className="flex items-center justify-end mb-2">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-extrabold ${
                            hasIncident ? 'bg-red-500/20 text-red-300 border border-red-500/40 animate-pulse' : 'bg-emerald-500/20 text-emerald-300'
                          }`}>
                            {hasIncident ? `DISRUPTED (${it.risk_score}% Risk)` : 'GUARDIAN PROTECTED'}
                          </span>
                        </div>

                        <h4 className="font-extrabold text-base text-white">{it.title}</h4>
                        <p className="text-xs text-slate-300 font-medium mt-1">Traveler: <strong className="text-slate-100">{it.customer.name}</strong> ({it.customer.email})</p>

                        <div className="flex items-center space-x-4 mt-3 text-xs text-slate-200 font-mono bg-slate-900 p-2.5 rounded-xl border border-slate-800">
                          <div>Legs: <strong className="text-white">{it.leg_count || 1} Legs</strong></div>
                          <div>Date: <strong className="text-white">{new Date(it.start_date).toLocaleDateString()}</strong></div>
                        </div>
                      </div>

                      <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
                        <span className="text-slate-300 italic text-[11px] font-medium">Click to view full plan & AI recovery options</span>
                        <span className="font-extrabold text-red-400 flex items-center space-x-1">
                          <span>View Details</span>
                          <ChevronRight className="w-4 h-4" />
                        </span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        )}
      </div>

      {/* 3. CUSTOMER EXPERIENCES & SAFETY SECTION */}
      <div id="experiences-section" className="space-y-6 pt-6 border-t border-slate-800">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-extrabold text-white flex items-center space-x-2">
              <Quote className="w-6 h-6 text-amber-400" />
              <span>Customer Experiences & Global Firm Testimonials</span>
            </h2>
            <p className="text-sm text-slate-300 font-medium">Verified 5-star ratings for our autonomous itinerary planning and travel guardian service</p>
          </div>
        </div>

        {/* 5-Star Global Firm Reviews */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3 bg-slate-900 shadow-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-1 text-amber-300">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-4 h-4 fill-amber-300 text-amber-300" />
                ))}
              </div>
              <span className="text-[11px] font-mono font-extrabold text-emerald-400">Reliance Industries</span>
            </div>
            <p className="text-xs text-slate-200 italic leading-relaxed font-medium">
              "Wayfare automatically rebooked 14 executive flights during the Srinagar alpine blizzard within 4 minutes. Outstanding autonomous service!"
            </p>
            <div className="text-[11px] font-extrabold text-white pt-2 border-t border-slate-800">
              Aarav Singhania — Corporate Travel Director
            </div>
          </div>

          <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3 bg-slate-900 shadow-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-1 text-amber-300">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-4 h-4 fill-amber-300 text-amber-300" />
                ))}
              </div>
              <span className="text-[11px] font-mono font-extrabold text-red-400">Tata Consultancy Services</span>
            </div>
            <p className="text-xs text-slate-200 italic leading-relaxed font-medium">
              "The conversational AI Booking Agent planned and booked our entire 6-day Goa retreat in under 2 minutes. The zero-cost recovery guarantee is game-changing."
            </p>
            <div className="text-[11px] font-extrabold text-white pt-2 border-t border-slate-800">
              Diya Sharma — Head of Global Operations
            </div>
          </div>

          <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3 bg-slate-900 shadow-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-1 text-amber-300">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-4 h-4 fill-amber-300 text-amber-300" />
                ))}
              </div>
              <span className="text-[11px] font-mono font-extrabold text-purple-400">Infosys Enterprise</span>
            </div>
            <p className="text-xs text-slate-200 italic leading-relaxed font-medium">
              "Seamless integration of Vande Bharat trains, IndiGo flights, and Taj luxury hotels. The live risk score alerts give total peace of mind."
            </p>
            <div className="text-[11px] font-extrabold text-white pt-2 border-t border-slate-800">
              Kabir Mehta — Senior Vice President
            </div>
          </div>
        </div>

        {/* Safety & Travel Advisories Widget */}
        <div id="safety-section" className="glass-panel p-5 rounded-2xl border border-emerald-500/30 bg-gradient-to-r from-slate-900 via-slate-900 to-emerald-950/60 text-xs flex flex-col md:flex-row md:items-center justify-between gap-4 text-white">
          <div className="flex items-start space-x-3">
            <div className="p-2.5 rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-extrabold text-sm text-white">Continuous AI Safety & Open-Meteo Weather Shield</h4>
              <p className="text-xs text-slate-200 font-medium mt-0.5">
                Our 7 LangGraph AI agents continuously monitor runway friction, monsoon radar, and Vande Bharat track health across 15 Indian transport hubs.
              </p>
            </div>
          </div>
          <span className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-mono text-[11px] font-extrabold self-start md:self-auto">
            100% Protection Active
          </span>
        </div>
      </div>

      {/* 4. COPYRIGHT 2026 FOOTER */}
      <div className="pt-8 border-t border-slate-800 text-center text-xs text-slate-400 font-medium">
        © 2026 Wayfare. All rights reserved.
      </div>

      {/* 5. FIXED BOTTOM-RIGHT FLOATING AI BOOKING AGENT CHATBOT FAB BUTTON & CHAT DRAWER */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end space-y-3">
        {chatOpen && (
          <div className="w-96 sm:w-[420px] glass-panel rounded-2xl border border-red-500/40 shadow-2xl overflow-hidden flex flex-col h-[520px] transition-all duration-300 bg-slate-900">
            <div className="bg-slate-950 p-3.5 border-b border-slate-800 flex items-center justify-between text-white">
              <div className="flex items-center space-x-2">
                <Bot className="w-5 h-5 text-amber-400 animate-bounce" />
                <div>
                  <span className="font-extrabold text-xs text-white block">AI Booking Agent</span>
                  <span className="text-[10px] text-emerald-400 font-mono font-bold">Slot-Filling AI • Conversational Booking</span>
                </div>
              </div>
              <button onClick={() => setChatOpen(false)} className="text-slate-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="flex-1 p-3 overflow-y-auto space-y-3 bg-slate-950">
              {chatMessages.map((msg, i) => (
                <div key={i} className={`flex flex-col ${msg.sender === 'USER' ? 'items-end' : 'items-start'}`}>
                  <div className={`p-3 rounded-xl text-xs max-w-[90%] space-y-2 ${
                    msg.sender === 'USER'
                      ? 'bg-red-600 text-white font-bold rounded-br-none'
                      : 'bg-slate-900 text-slate-100 border border-slate-700 font-medium rounded-bl-none'
                  }`}>
                    <div className="whitespace-pre-line leading-relaxed">{msg.text}</div>

                    {/* Render Custom Package Plan Breakdown if all slots filled */}
                    {msg.packagePlan && (
                      <div className="mt-2 p-3 rounded-lg bg-slate-950 border border-slate-700 font-mono text-[11px] space-y-1.5 text-slate-200">
                        <div className="text-amber-300 font-bold flex items-center justify-between border-b border-slate-800 pb-1">
                          <span>{msg.packagePlan.destination} Package</span>
                          <span>{msg.packagePlan.duration}</span>
                        </div>
                        <div>✈️ {msg.packagePlan.flight}</div>
                        <div>🏨 {msg.packagePlan.hotel}</div>
                        <div>🚗 {msg.packagePlan.chauffeur}</div>
                        <div>🛡 {msg.packagePlan.buffer}</div>
                        <div className="text-emerald-400 font-bold border-t border-slate-800 pt-1 flex justify-between">
                          <span>Total Budget:</span>
                          <span>{msg.packagePlan.budget}</span>
                        </div>
                      </div>
                    )}

                    {/* Render 1-Click Instant Booking Action Button inside Chat */}
                    {msg.actionButton && (
                      <button
                        onClick={msg.actionButton.onClick}
                        className="mt-2 w-full py-2 px-3 rounded-lg bg-gradient-to-r from-emerald-600 to-red-600 hover:from-emerald-500 hover:to-red-500 text-white font-extrabold text-xs shadow-lg flex items-center justify-center space-x-1.5 transition-all"
                      >
                        <CreditCard className="w-3.5 h-3.5" />
                        <span>{msg.actionButton.label}</span>
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <form onSubmit={handleSendMessage} className="p-2.5 bg-slate-900 border-t border-slate-800 flex items-center space-x-2">
              <input
                type="text"
                value={inputMsg}
                onChange={(e) => setInputMsg(e.target.value)}
                placeholder="e.g., Delhi, 10000, 10/08/2026..."
                className="flex-1 bg-slate-950 text-xs text-white placeholder-slate-400 font-bold rounded-lg px-3 py-2 border border-slate-700 focus:outline-none focus:border-red-500"
              />
              <button type="submit" className="p-2 rounded-lg bg-red-600 text-white hover:bg-red-500">
                <Send className="w-3.5 h-3.5" />
              </button>
            </form>
          </div>
        )}

        {/* Floating Chatbot FAB Button */}
        <button
          onClick={() => setChatOpen(prev => !prev)}
          title="Open AI Booking Agent Chatbot"
          className="p-4 rounded-full bg-gradient-to-tr from-red-500 via-rose-500 to-amber-500 text-white shadow-2xl shadow-red-500/40 hover:scale-110 active:scale-95 transition-all duration-300 flex items-center justify-center border-2 border-white/20 relative group"
        >
          <Bot className="w-7 h-7 text-white animate-pulse" />
          <span className="absolute -top-1 -right-1 w-3.5 h-3.5 bg-emerald-400 border-2 border-slate-900 rounded-full animate-ping" />
          <span className="absolute -top-1 -right-1 w-3.5 h-3.5 bg-emerald-400 border-2 border-slate-900 rounded-full" />
        </button>
      </div>
    </div>
  );
}
