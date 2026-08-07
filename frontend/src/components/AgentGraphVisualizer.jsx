import React, { useState } from 'react';
import { Cpu, ShieldCheck, Activity, Search, AlertTriangle, Compass, CalendarCheck, MessageSquare, BarChart3, CheckCircle2, ChevronRight } from 'lucide-react';

export default function AgentGraphVisualizer({ logs = [] }) {
  const [selectedAgent, setSelectedAgent] = useState(null);

  const agents = [
    { id: 'SUPERVISOR', name: 'Supervisor Agent', icon: Cpu, role: 'Orchestration & Verification', color: 'from-blue-600 to-indigo-600' },
    { id: 'JOURNEY_MONITORING', name: 'Journey Monitoring', icon: Search, role: 'Live Open-Meteo, OSRM, NASA APIs', color: 'from-cyan-600 to-teal-600' },
    { id: 'DISRUPTION_DETECTION', name: 'Disruption Detection', icon: AlertTriangle, role: 'Anomaly & Weather Detection', color: 'from-amber-600 to-orange-600' },
    { id: 'IMPACT_ANALYSIS', name: 'Impact Analysis', icon: Compass, role: 'Cascading Layover Calculations', color: 'from-purple-600 to-pink-600' },
    { id: 'RECOVERY_PLANNING', name: 'Recovery Planning', icon: Activity, role: 'Multi-Option & RAG Vector Synthesis', color: 'from-emerald-600 to-green-600' },
    { id: 'CUSTOMER_COMMUNICATION', name: 'Customer Communication', icon: MessageSquare, role: 'SMS, Push & Assistant Drafts', color: 'from-sky-600 to-blue-600' },
    { id: 'BOOKING_COORDINATION', name: 'Booking & Coordination', icon: CalendarCheck, role: 'Carrier GDS Holds & Rebooking', color: 'from-indigo-600 to-purple-600' },
    { id: 'OPERATIONS_DASHBOARD', name: 'Operations Dashboard', icon: BarChart3, role: 'Fleet Risk & MTTR Telemetry', color: 'from-rose-600 to-red-600' }
  ];

  return (
    <div className="glass-panel rounded-xl p-5 border border-slate-800">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <div className="p-2 rounded-lg bg-brand-500/10 text-brand-400">
            <Cpu className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h3 className="font-bold text-slate-100 text-sm">LangGraph 7-Agent Orchestration Flow</h3>
            <p className="text-xs text-slate-400">Active multi-agent execution pipeline & state machine</p>
          </div>
        </div>
        <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold flex items-center space-x-1">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          <span>Autonomous Protection Active</span>
        </span>
      </div>

      {/* Visual Workflow Graph */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 my-4">
        {agents.map((agent, index) => {
          const Icon = agent.icon;
          const agentLogs = logs.filter(l => l.agent_name.toLowerCase().includes(agent.name.toLowerCase().split(' ')[0]));
          const hasActivity = agentLogs.length > 0;
          const isSelected = selectedAgent === agent.id;

          return (
            <div
              key={agent.id}
              onClick={() => setSelectedAgent(isSelected ? null : agent.id)}
              className={`cursor-pointer p-3 rounded-xl border text-left transition-all ${
                isSelected 
                  ? 'bg-slate-800 border-brand-500 shadow-lg ring-1 ring-brand-500' 
                  : hasActivity 
                    ? 'bg-slate-800/60 border-slate-700 hover:border-slate-600' 
                    : 'bg-slate-900/40 border-slate-800/80 opacity-80 hover:opacity-100'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className={`p-2 rounded-lg bg-gradient-to-br ${agent.color} text-white shadow-md`}>
                  <Icon className="w-4 h-4" />
                </div>
                {hasActivity ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                ) : (
                  <span className="text-[10px] text-slate-500 font-mono">#{index + 1}</span>
                )}
              </div>
              <h4 className="font-semibold text-xs text-slate-200 truncate">{agent.name}</h4>
              <p className="text-[10px] text-slate-400 mt-0.5 line-clamp-1">{agent.role}</p>

              {hasActivity && (
                <div className="mt-2 text-[10px] font-mono text-emerald-400 flex items-center space-x-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                  <span>Executed ({agentLogs.length})</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Log Feed for Selected / Recent Execution */}
      <div className="mt-4 bg-slate-950/80 rounded-xl p-3 border border-slate-800">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold text-slate-300 flex items-center space-x-1">
            <Activity className="w-3.5 h-3.5 text-brand-400" />
            <span>Agent Execution Log Stream ({logs.length} events)</span>
          </span>
          <span className="text-[10px] text-slate-500 font-mono">Real-time LangGraph Output</span>
        </div>

        <div className="space-y-1.5 max-h-40 overflow-y-auto pr-1">
          {logs.length === 0 ? (
            <p className="text-xs text-slate-500 italic py-2 text-center">No agent logs yet. Trigger a disruption simulation above to watch agents execute!</p>
          ) : (
            logs.map((log, idx) => (
              <div key={idx} className="text-xs font-mono p-2 rounded bg-slate-900/80 border border-slate-800/80 flex items-start space-x-2">
                <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                  log.status === 'WARNING' ? 'bg-amber-500/20 text-amber-400' :
                  log.status === 'SUCCESS' ? 'bg-emerald-500/20 text-emerald-400' :
                  'bg-brand-500/20 text-brand-400'
                }`}>
                  {log.agent_name}
                </span>
                <span className="text-slate-400 flex-1">{log.details}</span>
                <span className="text-[10px] text-slate-500 whitespace-nowrap">{new Date(log.timestamp).toLocaleTimeString()}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
