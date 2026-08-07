import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, User, Headset, Sparkles, Activity, LogOut, Lock, AlertCircle, CheckCircle2, ChevronDown, Calendar, Phone, Award, Search, FileText, Globe 
} from 'lucide-react';
import CustomerMMTView from './components/CustomerMMTView';
import OpsView from './components/OpsView';
import AuthModal from './components/AuthModal';
import ProfileModal from './components/ProfileModal';
import NotificationBell from './components/NotificationBell';
import FloatingAgentWidget from './components/FloatingAgentWidget';
import GlobalSearchModal from './components/GlobalSearchModal';

export default function App() {
  // PERSISTENT SESSION MANAGEMENT
  const [currentUser, setCurrentUser] = useState(() => {
    try {
      const savedUser = localStorage.getItem('guardian_current_user');
      return savedUser ? JSON.parse(savedUser) : null;
    } catch {
      return null;
    }
  });

  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState('login'); // 'login' or 'signup'
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [showSearchModal, setShowSearchModal] = useState(false);
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  
  const [role, setRole] = useState(() => {
    try {
      const savedUser = localStorage.getItem('guardian_current_user');
      return savedUser ? JSON.parse(savedUser).role || 'CUSTOMER' : 'CUSTOMER';
    } catch {
      return 'CUSTOMER';
    }
  });

  const [itineraries, setItineraries] = useState([]);
  const [activeItineraryId, setActiveItineraryId] = useState(null);
  const [activeItinerary, setActiveItinerary] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [analytics, setAnalytics] = useState({});
  const [agentLogs, setAgentLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);

  // Permanently enforce dark theme class on document element
  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  // Keyboard shortcut (Ctrl+K or Cmd+K) to trigger Global Search
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setShowSearchModal(true);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Save current user session
  useEffect(() => {
    if (currentUser) {
      localStorage.setItem('guardian_current_user', JSON.stringify(currentUser));
    }
  }, [currentUser]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 6000);
    return () => clearInterval(interval);
  }, [currentUser, activeItineraryId]);

  const fetchData = async () => {
    try {
      const itRes = await fetch('/api/itineraries');
      if (itRes.ok) {
        const itData = await itRes.json();
        setItineraries(itData);
        if (itData.length > 0) {
          const selectedId = activeItineraryId || currentUser?.active_itinerary_id || itData[0].id;
          const detailRes = await fetch(`/api/itineraries/${selectedId}`);
          if (detailRes.ok) {
            const detailData = await detailRes.json();
            setActiveItinerary(detailData);
          }
        }
      }

      const incRes = await fetch('/api/incidents');
      if (incRes.ok) {
        const incData = await incRes.json();
        setIncidents(incData);
      }

      const anaRes = await fetch('/api/analytics');
      if (anaRes.ok) {
        const anaData = await anaRes.json();
        setAnalytics(anaData);
      }

      const logsRes = await fetch('/api/agents/logs');
      if (logsRes.ok) {
        const logsData = await logsRes.json();
        setAgentLogs(logsData);
      }
    } catch (e) {
      console.error('Error fetching data:', e);
    }
  };

  const handleLoginSuccess = (user) => {
    setCurrentUser(user);
    setRole(user.role);
    setShowAuthModal(false);
    localStorage.setItem('guardian_current_user', JSON.stringify(user));
    if (user.active_itinerary_id) {
      setActiveItineraryId(user.active_itinerary_id);
    }
    showToast(`Welcome back, ${user.name}! (${user.role} Portal Active)`, 'SUCCESS');
    fetchData();
  };

  const handleLogout = () => {
    setCurrentUser(null);
    localStorage.removeItem('guardian_current_user');
    setProfileDropdownOpen(false);
    showToast('Logged out successfully.', 'INFO');
  };

  const handleSelectItinerary = (id) => {
    setActiveItineraryId(id);
  };

  const handleApprovePlan = async (incidentId, planId) => {
    setLoading(true);
    showToast('⚙️ Rebooking ticket & chauffeur via Booking & Coordination Agent...', 'INFO');
    try {
      const res = await fetch(`/api/incidents/${incidentId}/approve_plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan_id: planId })
      });
      if (res.ok) {
        const data = await res.json();
        showToast(`✅ ${data.message}`, 'SUCCESS');
        await fetchData();
      } else {
        showToast('Approval failed.', 'ERROR');
      }
    } catch (e) {
      showToast('Network error during plan approval.', 'ERROR');
    } finally {
      setLoading(false);
    }
  };

  const showToast = (message, type = 'INFO') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 5000);
  };

  const scrollToSection = (id) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100 flex flex-col font-sans relative">
      
      {/* 1. TOP NAVBAR (High Z-Index z-[100] for maximum visibility) */}
      {role !== 'OPS' && (
        <header className="bg-[#070b14]/95 backdrop-blur border-b border-slate-800/80 sticky top-0 z-[100] shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          
          {/* Logo: 🌐 Wayfare */}
          <div className="flex items-center space-x-2 cursor-pointer" onClick={() => setRole('CUSTOMER')}>
            <div className="p-2 rounded-xl bg-gradient-to-tr from-red-500 via-rose-500 to-orange-500 text-white shadow-lg shadow-rose-500/20">
              <Globe className="w-5 h-5" />
            </div>
            <span className="font-extrabold text-xl tracking-tight text-white">Wayfare</span>
          </div>

          {/* Center Links: Destinations | Experiences | Safety */}
          {role === 'CUSTOMER' && (
            <div className="hidden md:flex items-center space-x-8 text-xs font-semibold text-slate-300">
              <button onClick={() => scrollToSection('plan-options-section')} className="hover:text-white transition-all">
                Destinations
              </button>
              <button onClick={() => scrollToSection('experiences-section')} className="hover:text-white transition-all">
                Experiences
              </button>
              <button onClick={() => scrollToSection('safety-section')} className="hover:text-white transition-all">
                Safety
              </button>
            </div>
          )}

          {/* Right Controls: Inbox, Log In, Sign Up */}
          <div className="flex items-center space-x-4">
            
            {/* Notification Bell */}
            {currentUser && (
              <NotificationBell
                incidents={incidents}
                currentUser={currentUser}
                role={role}
                onSelectIncident={(itId) => {
                  setActiveItineraryId(itId);
                  setRole('CUSTOMER');
                }}
              />
            )}

            {/* User Profile or Log In / Sign Up */}
            {currentUser ? (
              <div className="relative">
                <button
                  onClick={() => setProfileDropdownOpen(prev => !prev)}
                  className="flex items-center space-x-2 bg-slate-900 border border-slate-800 rounded-xl px-3 py-1.5 hover:border-brand-500 transition-all text-slate-200"
                >
                  <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-red-500 to-amber-500 flex items-center justify-center text-white font-bold text-xs">
                    {currentUser.name ? currentUser.name.charAt(0).toUpperCase() : 'U'}
                  </div>
                  <span className="text-xs font-semibold text-slate-200 hidden md:inline">{currentUser.name}</span>
                  <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                </button>

                {profileDropdownOpen && (
                  <div className="absolute right-0 mt-2 w-52 glass-panel rounded-2xl border border-slate-700 shadow-2xl py-2 z-50 text-xs">
                    <div className="px-3 py-2 border-b border-slate-800">
                      <div className="font-bold text-slate-100">{currentUser.name}</div>
                      <div className="text-[10px] text-slate-400 truncate">{currentUser.email}</div>
                    </div>

                    <button
                      onClick={() => {
                        setShowProfileModal(true);
                        setProfileDropdownOpen(false);
                      }}
                      className="w-full text-left px-3 py-2 hover:bg-slate-800 flex items-center space-x-2 text-slate-200 font-medium"
                    >
                      <User className="w-4 h-4 text-brand-400" />
                      <span>My Profile</span>
                    </button>

                    <button
                      onClick={() => {
                        setRole('CUSTOMER');
                        setProfileDropdownOpen(false);
                      }}
                      className="w-full text-left px-3 py-2 hover:bg-slate-800 flex items-center space-x-2 text-slate-200 font-medium"
                    >
                      <Calendar className="w-4 h-4 text-emerald-400" />
                      <span>My Bookings</span>
                    </button>

                    <div className="border-t border-slate-800 my-1" />

                    <button
                      onClick={handleLogout}
                      className="w-full text-left px-3 py-2 hover:bg-slate-800 flex items-center space-x-2 text-red-400 font-medium"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Logout</span>
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center space-x-3 text-xs">
                <button
                  onClick={() => { setAuthMode('login'); setShowAuthModal(true); }}
                  className="font-bold text-slate-300 hover:text-white transition-all px-2 py-1"
                >
                  Log In
                </button>

                <button
                  onClick={() => { setAuthMode('signup'); setShowAuthModal(true); }}
                  className="px-4 py-2 rounded-xl bg-gradient-to-r from-red-500 to-rose-600 hover:from-red-600 hover:to-rose-700 text-white font-extrabold shadow-lg shadow-red-500/30 transition-all transform hover:-translate-y-0.5"
                >
                  Sign Up
                </button>
              </div>
            )}
          </div>
        </div>
      </header>
      )}

      {/* Floating 10-Agent Status Monitoring Widget (Bottom-Left) */}
      <FloatingAgentWidget />

      {/* Global Search Modal (Ctrl+K) */}
      {showSearchModal && (
        <GlobalSearchModal
          itineraries={itineraries}
          incidents={incidents}
          onClose={() => setShowSearchModal(false)}
          onSelectResult={(type, id) => {
            if (type === 'BOOKING') {
              setActiveItineraryId(id);
              setRole('CUSTOMER');
            }
          }}
        />
      )}

      {/* Toast Notification */}
      {toast && (
        <div className="fixed top-16 right-6 z-50 animate-bounce">
          <div className={`px-4 py-3 rounded-xl border shadow-2xl text-xs font-semibold flex items-center space-x-2 ${
            toast.type === 'SUCCESS' ? 'bg-emerald-950/90 border-emerald-500/50 text-emerald-300' :
            toast.type === 'ERROR' ? 'bg-red-950/90 border-red-500/50 text-red-300' :
            'bg-slate-900/90 border-brand-500/50 text-brand-300'
          }`}>
            {toast.type === 'SUCCESS' && <CheckCircle2 className="w-4 h-4 text-emerald-500" />}
            {toast.type === 'ERROR' && <AlertCircle className="w-4 h-4 text-red-500" />}
            {toast.type === 'INFO' && <Sparkles className="w-4 h-4 text-brand-500 animate-spin" />}
            <span>{toast.message}</span>
          </div>
        </div>
      )}

      {/* Auth Modal */}
      {showAuthModal && (
        <AuthModal
          mode={authMode}
          onLoginSuccess={handleLoginSuccess}
          onCancel={() => setShowAuthModal(false)}
          canClose={true}
        />
      )}

      {/* Profile Modal */}
      {showProfileModal && currentUser && (
        <ProfileModal
          user={currentUser}
          onClose={() => setShowProfileModal(false)}
        />
      )}

      {/* Main View Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6">
        {role === 'CUSTOMER' ? (
          <CustomerMMTView
            itinerary={activeItinerary}
            allItineraries={itineraries}
            onApprovePlan={handleApprovePlan}
            onSelectItinerary={handleSelectItinerary}
            currentUser={currentUser}
            onOpenAuth={() => setShowAuthModal(true)}
            loading={loading}
          />
        ) : (
          <OpsView
            itineraries={itineraries}
            incidents={incidents}
            analytics={analytics}
            agentLogs={agentLogs}
            onApprovePlan={handleApprovePlan}
            loading={loading}
            currentUser={currentUser}
            onLogout={handleLogout}
            onSwitchRole={() => setRole('CUSTOMER')}
            onOpenProfile={() => setShowProfileModal(true)}
          />
        )}
      </main>
    </div>
  );
}
