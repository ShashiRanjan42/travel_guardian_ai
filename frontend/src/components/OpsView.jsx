import React, { useState } from 'react';
import NotificationBell from './NotificationBell';
import { 
  LayoutDashboard, Calendar, AlertTriangle, Sparkles, MapPin, Bell, Truck, BarChart3, 
  FlaskConical, Settings, Search, Filter, ShieldCheck, ChevronRight, ChevronLeft, CheckCircle2, XCircle, 
  Clock, ArrowRight, Zap, RefreshCw, Send, X, Layers, Users, Hotel, Plane, Train, Car, MessageSquare, 
  TrendingUp, DollarSign, Activity, AlertCircle, ArrowUpRight, Check, Eye, HelpCircle, AlertOctagon,
  ChevronDown, Moon, User, Globe, LogOut 
} from 'lucide-react';

export default function OpsView({ 
  itineraries = [], 
  incidents = [], 
  analytics = {}, 
  agentLogs = [], 
  onApprovePlan, 
  loading,
  currentUser,
  onLogout,
  onSwitchRole,
  onOpenProfile 
}) {
  const [activeSection, setActiveSection] = useState('DASHBOARD'); // DASHBOARD, BOOKINGS, REQUESTS, DISRUPTIONS, RECOMMENDATIONS, TRACKING, NOTIFICATIONS, ANALYTICS, SETTINGS
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  
  // Auto-Approve AI Plans Toggle Switch State
  const [autoApprove, setAutoApprove] = useState(true);
  const [regionFilter, setRegionFilter] = useState('All Regions');
  const [riskFilter, setRiskFilter] = useState('Risk: All');

  // Swarm Status Bar collapse state
  const [swarmExpanded, setSwarmExpanded] = useState(false);

  // Copilot Floating Agent Chat State
  const [copilotOpen, setCopilotOpen] = useState(false);
  const [copilotMessages, setCopilotMessages] = useState([
    { sender: 'AI', text: "Namaste Operations Lead! 3 critical disruptions detected across Indian transit corridors. All 10 LangGraph Swarm Agents are active." }
  ]);
  const [copilotInput, setCopilotInput] = useState('');

  const activeIncidents = incidents.filter(i => i.status !== 'RECOVERED');

  const handleCopilotSend = async (e) => {
    e.preventDefault();
    if (!copilotInput.trim()) return;

    const userMsg = copilotInput;
    setCopilotMessages(prev => [...prev, { sender: 'USER', text: userMsg }]);
    setCopilotInput('');

    try {
      const res = await fetch('/api/v1/agents/chat_ops', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg })
      });
      if (res.ok) {
        const data = await res.json();
        setCopilotMessages(prev => [...prev, { sender: 'AI', text: data.reply }]);
      } else {
        setCopilotMessages(prev => [...prev, { sender: 'AI', text: "Error connecting to AI Copilot." }]);
      }
    } catch (e) {
      setCopilotMessages(prev => [...prev, { sender: 'AI', text: "Network Error: Unable to reach AI Copilot." }]);
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-[#070b14] text-slate-100 font-sans select-none">
      
      {/* 1. LEFT SIDEBAR NAVIGATION MATCHING LANDING PAGE WAYFARE THEME */}
      <aside className={`${sidebarCollapsed ? 'w-16' : 'w-60'} transition-all duration-300 bg-[#070b14] border-r border-slate-800/80 flex flex-col justify-between p-3.5 z-20`}>
        <div className="space-y-5">
          
          {/* Brand Logo & Arrow Toggle: 🌐 Wayfare */}
          <div 
            onClick={() => setSidebarCollapsed(prev => !prev)}
            className="flex items-center justify-between px-2 py-1 cursor-pointer group hover:bg-slate-900 rounded-xl transition-all"
            title={sidebarCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
          >
            {!sidebarCollapsed && (
              <div className="flex items-center space-x-2 text-white font-extrabold text-sm tracking-tight">
                <div className="p-1.5 rounded-xl bg-gradient-to-tr from-red-500 via-rose-500 to-orange-500 text-white shadow-lg shadow-rose-500/20">
                  <Globe className="w-4 h-4" />
                </div>
                <span className="font-extrabold text-lg tracking-tight text-white">Wayfare</span>
              </div>
            )}
            <button className="p-1.5 rounded-lg text-slate-400 group-hover:text-white transition-all">
              {sidebarCollapsed ? (
                <div className="p-1.5 rounded-xl bg-gradient-to-tr from-red-500 via-rose-500 to-orange-500 text-white shadow-md">
                  <Globe className="w-4 h-4" />
                </div>
              ) : (
                <ChevronLeft className="w-4 h-4 text-slate-400 group-hover:text-white" />
              )}
            </button>
          </div>

          {/* Section: OPERATIONS */}
          <div className="space-y-1">
            {!sidebarCollapsed && (
              <div className="px-3 text-[10px] font-extrabold text-slate-400 uppercase tracking-wider mb-2">
                OPERATIONS
              </div>
            )}

            <nav className="space-y-1">
              {[
                { id: 'DASHBOARD', label: 'Dashboard', icon: LayoutDashboard },
                { id: 'BOOKINGS', label: 'Bookings', icon: Calendar },
                { id: 'REQUESTS', label: 'Requests', icon: Users },
                { id: 'DISRUPTIONS', label: 'Disruptions', icon: AlertTriangle, badge: '3', badgeColor: 'bg-red-500/20 text-red-400 border border-red-500/40' },
                { id: 'RECOMMENDATIONS', label: 'Recommendations', icon: Sparkles },
                { id: 'TRACKING', label: 'Live Tracking', icon: MapPin },
                { id: 'NOTIFICATIONS', label: 'Notifications', icon: Bell },
                { id: 'ANALYTICS', label: 'Analytics', icon: BarChart3 }
              ].map((item) => {
                const Icon = item.icon;
                const isActive = activeSection === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveSection(item.id)}
                    title={item.label}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-bold transition-all ${
                      isActive
                        ? 'bg-red-600 text-white shadow-lg shadow-red-600/30 font-extrabold'
                        : 'text-slate-300 hover:bg-slate-900 hover:text-white'
                    }`}
                  >
                    <div className="flex items-center space-x-2.5">
                      <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                      {!sidebarCollapsed && <span>{item.label}</span>}
                    </div>
                    {!sidebarCollapsed && item.badge && (
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${item.badgeColor || 'bg-slate-800 text-slate-300'}`}>
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Section: SYSTEM */}
          <div className="space-y-1 pt-2">
            {!sidebarCollapsed && (
              <div className="px-3 text-[10px] font-extrabold text-slate-400 uppercase tracking-wider mb-2">
                SYSTEM
              </div>
            )}
            <button
              onClick={() => setActiveSection('SETTINGS')}
              className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-xl text-xs font-extrabold transition-all ${
                activeSection === 'SETTINGS' ? 'bg-red-600 text-white shadow-lg shadow-red-600/30' : 'text-slate-300 hover:bg-slate-900 hover:text-white'
              }`}
            >
              <Settings className="w-4 h-4 text-slate-400" />
              {!sidebarCollapsed && <span>Settings</span>}
            </button>
          </div>
        </div>
      </aside>

      {/* 2. MAIN CONTENT AREA */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden bg-[#070b14]">
        
        {/* UNIFIED SINGLE PROFESSIONAL TOP HEADER (High Z-Index z-[100] for maximum visibility) */}
        <header className="px-8 py-3.5 bg-[#070b14]/95 backdrop-blur border-b border-slate-800/80 flex items-center justify-end gap-4 sticky top-0 z-[100] shadow-xl">
          {/* Right Header Actions */}
          <div className="flex items-center space-x-4">
            <NotificationBell
              incidents={incidents}
              currentUser={currentUser}
              role="OPS"
              onSelectIncident={() => setActiveSection('DISRUPTIONS')}
            />

            {/* Interactive Profile Avatar & Logout Dropdown */}
            <div className="relative">
              <button
                onClick={() => setProfileDropdownOpen(prev => !prev)}
                title="Ops Profile & Logout Menu"
                className="flex items-center space-x-2 p-1 rounded-xl hover:bg-slate-900 transition-all focus:outline-none border border-transparent hover:border-slate-800"
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-red-500 via-rose-500 to-amber-500 text-white font-extrabold text-xs flex items-center justify-center border border-slate-700 shadow-md">
                  {currentUser?.name ? currentUser.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() : 'MI'}
                </div>
                <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
              </button>

              {profileDropdownOpen && (
                <div className="absolute right-0 mt-2 w-56 glass-panel bg-slate-900 rounded-2xl border border-slate-800 shadow-2xl py-2 z-[110] text-xs">
                  <div className="px-4 py-3 border-b border-slate-800">
                    <div className="font-extrabold text-white">{currentUser?.name || 'Priya Sharma'}</div>
                    <div className="text-[10px] text-slate-400 truncate">{currentUser?.email || 'ops.lead@wayfare.ai'}</div>
                    <span className="mt-1.5 inline-block px-2 py-0.5 rounded-md bg-red-500/20 text-red-300 border border-red-500/40 text-[10px] font-extrabold">
                      OPERATIONS LEAD
                    </span>
                  </div>

                  {onOpenProfile && (
                    <button
                      onClick={() => {
                        onOpenProfile();
                        setProfileDropdownOpen(false);
                      }}
                      className="w-full text-left px-4 py-2.5 hover:bg-slate-800 flex items-center space-x-2 text-slate-200 font-bold"
                    >
                      <User className="w-4 h-4 text-red-400" />
                      <span>My Profile</span>
                    </button>
                  )}

                  {onSwitchRole && (
                    <button
                      onClick={() => {
                        onSwitchRole();
                        setProfileDropdownOpen(false);
                      }}
                      className="w-full text-left px-4 py-2.5 hover:bg-slate-800 flex items-center space-x-2 text-slate-200 font-bold"
                    >
                      <Calendar className="w-4 h-4 text-emerald-400" />
                      <span>Switch to Customer View</span>
                    </button>
                  )}

                  <div className="border-t border-slate-800 my-1" />

                  <button
                    onClick={() => {
                      setProfileDropdownOpen(false);
                      if (onLogout) onLogout();
                    }}
                    className="w-full text-left px-4 py-2.5 hover:bg-slate-800 flex items-center space-x-2 text-rose-400 font-bold"
                  >
                    <LogOut className="w-4 h-4 text-rose-400" />
                    <span>Logout</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* DASHBOARD BODY AREA */}
        <div className="flex-1 overflow-y-auto p-8 space-y-8 bg-[#070b14]">
          
          {/* DASHBOARD TAB CONTENT */}
          {activeSection === 'DASHBOARD' && (
            <div className="space-y-8">
              
              {/* Breadcrumb & Title Bar with Auto-Approve AI Switch */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <div className="text-xs text-slate-400 font-semibold">Operations &gt; Command Center</div>
                  <h1 className="text-3xl font-extrabold text-white tracking-tight mt-0.5">Dashboard</h1>
                </div>

                {/* Auto-Approve AI Plans Control Switch */}
                <div className="glass-panel bg-slate-900 border border-slate-800 p-2.5 px-4 rounded-2xl shadow-xl flex items-center space-x-3 text-xs">
                  <span className="font-extrabold text-slate-200">Auto-Approve AI Plans</span>
                  <span className="text-slate-400 font-bold">Off</span>
                  <button 
                    onClick={() => setAutoApprove(prev => !prev)}
                    className={`w-12 h-6 rounded-full p-0.5 transition-all flex items-center ${
                      autoApprove ? 'bg-red-600 justify-end' : 'bg-slate-800 justify-start'
                    }`}
                  >
                    <div className="w-5 h-5 rounded-full bg-white shadow-md" />
                  </button>
                  <span className="text-red-400 font-extrabold text-[11px]">&gt;95% Conf</span>
                </div>
              </div>

              {/* 10 KPI CARDS GRID IN WAYFARE DARK PALETTE */}
              <div className="space-y-3">
                {/* ROW 1 (5 Cards) */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
                  <div className="glass-panel bg-slate-900 p-5 rounded-2xl border border-slate-800 shadow-xl flex flex-col justify-between space-y-3">
                    <span className="text-xs font-extrabold text-slate-300">Active Bookings</span>
                    <div className="text-3xl font-extrabold text-white">47</div>
                  </div>

                  <div className="glass-panel bg-slate-900 p-5 rounded-2xl border border-slate-800 shadow-xl flex flex-col justify-between space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-extrabold text-slate-300">Open Alerts</span>
                      <AlertTriangle className="w-4 h-4 text-amber-400" />
                    </div>
                    <div className="text-3xl font-extrabold text-white">1</div>
                  </div>

                  <div className="glass-panel bg-slate-900 p-5 rounded-2xl border border-slate-800 shadow-xl flex flex-col justify-between space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-extrabold text-slate-300">Critical Alerts</span>
                      <AlertOctagon className="w-4 h-4 text-red-500" />
                    </div>
                    <div className="text-3xl font-extrabold text-white">3</div>
                  </div>

                  <div className="glass-panel bg-slate-900 p-5 rounded-2xl border border-slate-800 shadow-xl flex flex-col justify-between space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-extrabold text-slate-300">Pending Approvals</span>
                      <div className="p-1 rounded-full bg-blue-500/20 text-blue-400">
                        <Clock className="w-3.5 h-3.5" />
                      </div>
                    </div>
                    <div className="text-3xl font-extrabold text-white">8</div>
                  </div>

                  <div className="glass-panel bg-slate-900 p-5 rounded-2xl border border-slate-800 shadow-xl flex flex-col justify-between space-y-3">
                    <span className="text-xs font-extrabold text-slate-300">High Risk Trips</span>
                    <div className="text-3xl font-extrabold text-white">15</div>
                  </div>
                </div>

                {/* ROW 2 (5 Cards) */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
                  <div className="glass-panel bg-slate-900 p-5 rounded-2xl border border-slate-800 shadow-xl flex flex-col justify-between space-y-3">
                    <span className="text-xs font-extrabold text-slate-300">Active Incidents</span>
                    <div className="text-3xl font-extrabold text-white">4</div>
                  </div>

                  <div className="glass-panel bg-slate-900 p-5 rounded-2xl border border-slate-800 shadow-xl flex flex-col justify-between space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-extrabold text-slate-300">Avg Resolution</span>
                      <div className="p-1 rounded-full bg-emerald-500/20 text-emerald-400">
                        <Zap className="w-3.5 h-3.5" />
                      </div>
                    </div>
                    <div className="text-3xl font-extrabold text-white">14s</div>
                    <div className="text-[10px] text-emerald-400 font-extrabold flex items-center space-x-1">
                      <span>⚡ vs 45m manual</span>
                    </div>
                  </div>

                  <div className="glass-panel bg-slate-900 p-5 rounded-2xl border border-slate-800 shadow-xl flex flex-col justify-between space-y-3">
                    <span className="text-xs font-extrabold text-slate-300">SLA Compliance</span>
                    <div className="text-3xl font-extrabold text-white">99.8%</div>
                  </div>

                  <div className="glass-panel bg-slate-900 p-5 rounded-2xl border border-slate-800 shadow-xl flex flex-col justify-between space-y-3">
                    <span className="text-xs font-extrabold text-slate-300">CSAT Score</span>
                    <div className="text-3xl font-extrabold text-white">4.9/5</div>
                  </div>

                  <div className="glass-panel bg-slate-900 p-5 rounded-2xl border border-slate-800 shadow-xl flex flex-col justify-between space-y-3">
                    <span className="text-xs font-extrabold text-slate-300">AI Automations</span>
                    <div className="text-3xl font-extrabold text-white">1,204</div>
                  </div>
                </div>
              </div>

              {/* SECTION 1: ENTERPRISE TRIAGE QUEUE */}
              <div className="glass-panel bg-slate-900 rounded-2xl border border-slate-800 p-6 space-y-5 shadow-xl">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div>
                    <h3 className="font-extrabold text-base text-white">Enterprise Triage Queue</h3>
                    <p className="text-xs text-slate-300 font-medium">Live Disruption Warnings &amp; Pending Approvals</p>
                  </div>

                  {/* Region & Risk Dropdown Filters */}
                  <div className="flex items-center space-x-3 text-xs">
                    <div className="relative">
                      <select
                        value={regionFilter}
                        onChange={(e) => setRegionFilter(e.target.value)}
                        className="bg-slate-950 border border-slate-800 text-slate-200 font-bold rounded-xl px-3 py-2 focus:outline-none"
                      >
                        <option value="All Regions">All Regions</option>
                        <option value="North India">North India</option>
                        <option value="West India">West India</option>
                        <option value="South India">South India</option>
                      </select>
                    </div>

                    <div className="relative">
                      <select
                        value={riskFilter}
                        onChange={(e) => setRiskFilter(e.target.value)}
                        className="bg-slate-950 border border-slate-800 text-slate-200 font-bold rounded-xl px-3 py-2 focus:outline-none"
                      >
                        <option value="Risk: All">Risk: All</option>
                        <option value="High Risk">High Risk</option>
                        <option value="Medium Risk">Medium Risk</option>
                        <option value="Low Risk">Low Risk</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Triage Queue Table */}
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-950 text-slate-300 font-bold uppercase text-[11px] border-b border-slate-800">
                      <tr>
                        <th className="py-3 px-4">Severity</th>
                        <th className="py-3 px-4">Traveller / PNR</th>
                        <th className="py-3 px-4">Issue</th>
                        <th className="py-3 px-4">Impact</th>
                        <th className="py-3 px-4">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800 text-slate-200">
                      <tr className="hover:bg-slate-800/60 transition-all">
                        <td className="py-4 px-4">
                          <div className="inline-flex items-center space-x-2">
                            <span className="px-2.5 py-1 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/40 text-[10px] font-extrabold">
                              HIGH
                            </span>
                            <span className="font-extrabold text-white text-xs">64.0</span>
                          </div>
                        </td>
                        <td className="py-4 px-4">
                          <div className="font-extrabold text-white">Rohan Desai</div>
                          <div className="text-[11px] text-slate-400 font-mono mt-0.5">WP7K2M9Q • Kasol</div>
                        </td>
                        <td className="py-4 px-4">
                          <div className="font-extrabold text-white">Landslide blocks NH-3 near Bhuntar</div>
                          <div className="text-[11px] text-slate-400 font-mono mt-0.5">T-14.2h • LANDSLIDE</div>
                        </td>
                        <td className="py-4 px-4 font-semibold text-slate-300">
                          1 direct, 3 cascade
                        </td>
                        <td className="py-4 px-4">
                          <span className="inline-flex items-center space-x-1.5 text-amber-300 font-extrabold text-[11px]">
                            <span className="w-2 h-2 rounded-full bg-amber-400" />
                            <span>PENDING OPS REVIEW</span>
                          </span>
                        </td>
                      </tr>

                      <tr className="hover:bg-slate-800/60 transition-all">
                        <td className="py-4 px-4">
                          <div className="inline-flex items-center space-x-2">
                            <span className="px-2.5 py-1 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/40 text-[10px] font-extrabold">
                              CRITICAL
                            </span>
                            <span className="font-extrabold text-white text-xs">92.5</span>
                          </div>
                        </td>
                        <td className="py-4 px-4">
                          <div className="font-extrabold text-white">Aarav Singhania</div>
                          <div className="text-[11px] text-slate-400 font-mono mt-0.5">SRN9901 • Srinagar</div>
                        </td>
                        <td className="py-4 px-4">
                          <div className="font-extrabold text-white">Alpine Blizzard closes Sheikh ul-Alam Airport</div>
                          <div className="text-[11px] text-slate-400 font-mono mt-0.5">T-2.1h • BLIZZARD</div>
                        </td>
                        <td className="py-4 px-4 font-semibold text-slate-300">
                          2 direct, 5 cascade
                        </td>
                        <td className="py-4 px-4">
                          <span className="inline-flex items-center space-x-1.5 text-emerald-400 font-extrabold text-[11px]">
                            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                            <span>AI REROUTING ACTIVE</span>
                          </span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              {/* SECTION 2: RECENT BOOKINGS */}
              <div className="glass-panel bg-slate-900 rounded-2xl border border-slate-800 p-6 space-y-5 shadow-xl">
                <h3 className="font-extrabold text-base text-white">Recent Bookings</h3>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-950 text-slate-300 font-bold uppercase text-[11px] border-b border-slate-800">
                      <tr>
                        <th className="py-3 px-4">PNR</th>
                        <th className="py-3 px-4">Traveller</th>
                        <th className="py-3 px-4">Route</th>
                        <th className="py-3 px-4">Dates</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800 text-slate-200 font-mono text-[11px]">
                      <tr className="hover:bg-slate-800/60 transition-all">
                        <td className="py-3.5 px-4 font-bold text-white">NDISE008</td>
                        <td className="py-3.5 px-4 font-sans font-extrabold text-slate-100">Rohan Desai</td>
                        <td className="py-3.5 px-4">Origin 0 → Dest 0</td>
                        <td className="py-3.5 px-4 text-slate-400">2026-08-08T00:00:00 to 2026-08-12T00:00:00</td>
                      </tr>
                      <tr className="hover:bg-slate-800/60 transition-all">
                        <td className="py-3.5 px-4 font-bold text-white">NDISE001</td>
                        <td className="py-3.5 px-4 font-sans font-extrabold text-slate-100">Rohan Desai</td>
                        <td className="py-3.5 px-4">Origin 1 → Dest 1</td>
                        <td className="py-3.5 px-4 text-slate-400">2026-08-08T00:00:00 to 2026-08-12T00:00:00</td>
                      </tr>
                      <tr className="hover:bg-slate-800/60 transition-all">
                        <td className="py-3.5 px-4 font-bold text-white">NDISE002</td>
                        <td className="py-3.5 px-4 font-sans font-extrabold text-slate-100">Rohan Desai</td>
                        <td className="py-3.5 px-4">Origin 2 → Dest 2</td>
                        <td className="py-3.5 px-4 text-slate-400">2026-08-08T00:00:00 to 2026-08-12T00:00:00</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* OTHER NAVIGATION SECTIONS */}
          {activeSection === 'BOOKINGS' && (
            <div className="glass-panel bg-slate-900 rounded-2xl border border-slate-800 p-6 space-y-4 shadow-xl">
              <h3 className="text-lg font-extrabold text-white">All Fleet Bookings ({itineraries.length})</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950 text-slate-300 uppercase text-[10px] font-bold border-b border-slate-800">
                    <tr>
                      <th className="p-3">PNR / ID</th>
                      <th className="p-3">Traveller</th>
                      <th className="p-3">Route</th>
                      <th className="p-3">Status</th>
                      <th className="p-3">Risk Level</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {itineraries.map((it) => (
                      <tr key={it.id} className="hover:bg-slate-800/60">
                        <td className="p-3 font-mono font-bold text-red-400">{it.id}</td>
                        <td className="p-3 font-extrabold text-white">{it.customer.name}</td>
                        <td className="p-3 text-slate-200">{it.title}</td>
                        <td className="p-3 font-extrabold text-emerald-400">{it.status}</td>
                        <td className="p-3 font-mono text-slate-300">{it.risk_score}% ({it.risk_level})</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeSection === 'DISRUPTIONS' && (
            <div className="glass-panel bg-slate-900 rounded-2xl border border-slate-800 p-6 space-y-4 shadow-xl">
              <h3 className="text-lg font-extrabold text-white">Active Disruption Incidents ({activeIncidents.length})</h3>
              <div className="space-y-3">
                {activeIncidents.map((inc) => (
                  <div key={inc.id} className="p-4 rounded-xl border border-rose-500/30 bg-rose-500/10 flex items-center justify-between text-xs">
                    <div>
                      <div className="font-extrabold text-rose-300 text-sm">{inc.title}</div>
                      <div className="text-slate-300 mt-1">{inc.description}</div>
                    </div>
                    <span className="px-3 py-1 rounded-full bg-rose-600 text-white font-extrabold text-xs">
                      {inc.severity}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* 3. FLOATING BOTTOM DOCKS */}
        
        {/* Bottom Left: ⚡ 10-Agent Swarm Status Collapsable Bar */}
        <div className="fixed bottom-4 left-4 z-40">
          <div className="bg-slate-950 text-white rounded-xl shadow-2xl border border-slate-800 overflow-hidden transition-all duration-300">
            <button
              onClick={() => setSwarmExpanded(prev => !prev)}
              className="px-4 py-2.5 text-xs font-extrabold flex items-center space-x-3 hover:bg-slate-900 transition-all"
            >
              <Zap className="w-4 h-4 text-amber-400 fill-amber-400 animate-pulse" />
              <span>10-Agent Swarm Status</span>
              <ChevronDown className={`w-3.5 h-3.5 transform transition-transform ${swarmExpanded ? 'rotate-180' : ''}`} />
            </button>

            {swarmExpanded && (
              <div className="p-4 border-t border-slate-800 text-xs space-y-2 max-w-sm bg-slate-950 font-mono text-slate-300">
                <div className="flex justify-between text-emerald-400 font-bold">
                  <span>Active LangGraph Swarm</span>
                  <span>10/10 Online</span>
                </div>
                <div>• Disruption Detection Agent</div>
                <div>• Flight & Rail Rerouting Agent</div>
                <div>• Hotel & Ground Logistics Agent</div>
                <div>• Recovery Planning & Risk Agent</div>
                <div>• Customer LLM Booking Agent</div>
              </div>
            )}
          </div>
        </div>

        {/* Bottom Right: Floating Red/Rose Chatbot Button */}
        <div className="fixed bottom-4 right-6 z-40 flex flex-col items-end space-y-3">
          {copilotOpen && (
            <div className="w-80 sm:w-[380px] glass-panel bg-slate-900 rounded-2xl border border-red-500/40 shadow-2xl overflow-hidden flex flex-col h-[460px] text-xs">
              <div className="bg-slate-950 p-3.5 text-white flex items-center justify-between border-b border-slate-800">
                <div className="flex items-center space-x-2 font-bold">
                  <Sparkles className="w-4 h-4 text-amber-300 animate-bounce" />
                  <span>Operations AI Copilot</span>
                </div>
                <button onClick={() => setCopilotOpen(false)} className="text-slate-400 hover:text-white">
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="flex-1 p-3 overflow-y-auto space-y-3 bg-slate-950">
                {copilotMessages.map((msg, idx) => (
                  <div key={idx} className={`flex flex-col ${msg.sender === 'USER' ? 'items-end' : 'items-start'}`}>
                    <div className={`p-3 rounded-xl max-w-[85%] ${
                      msg.sender === 'USER' ? 'bg-red-600 text-white font-bold' : 'bg-slate-900 border border-slate-700 text-slate-100 font-medium'
                    }`}>
                      {msg.text}
                    </div>
                  </div>
                ))}
              </div>

              <form onSubmit={handleCopilotSend} className="p-2.5 bg-slate-900 border-t border-slate-800 flex items-center space-x-2">
                <input
                  type="text"
                  value={copilotInput}
                  onChange={(e) => setCopilotInput(e.target.value)}
                  placeholder="Ask Ops AI Copilot..."
                  className="flex-1 bg-slate-950 text-white text-xs font-bold rounded-lg px-3 py-2 border border-slate-700 focus:outline-none focus:border-red-500"
                />
                <button type="submit" className="p-2 rounded-lg bg-red-600 text-white hover:bg-red-500">
                  <Send className="w-3.5 h-3.5" />
                </button>
              </form>
            </div>
          )}

          <button
            onClick={() => setCopilotOpen(prev => !prev)}
            className="p-3.5 rounded-full bg-gradient-to-tr from-red-500 via-rose-500 to-amber-500 text-white shadow-2xl hover:scale-110 active:scale-95 transition-all duration-300 border-2 border-white/20"
          >
            <MessageSquare className="w-6 h-6" />
          </button>
        </div>

      </div>
    </div>
  );
}
