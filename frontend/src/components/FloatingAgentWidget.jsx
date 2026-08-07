import React, { useState } from 'react';
import { Bot, ChevronUp, ChevronDown, Activity, Cpu, HardDrive, Clock, CheckCircle2, AlertCircle } from 'lucide-react';

export default function FloatingAgentWidget() {
  const [expanded, setExpanded] = useState(false);

  const agents = [
    { name: "Booking Agent", status: "ONLINE", task: "Slot Filling & Package Booking", queue: 0, latency: "42ms", success: "99.8%", cpu: "12%", memory: "128MB", health: 100 },
    { name: "Disruption Detection Agent", status: "ONLINE", task: "Polling Open-Meteo & Radar", queue: 2, latency: "85ms", success: "99.5%", cpu: "24%", memory: "256MB", health: 98 },
    { name: "Recovery Planning Agent", status: "ONLINE", task: "RAG Vector Store Optimization", queue: 1, latency: "140ms", success: "98.9%", cpu: "38%", memory: "512MB", health: 97 },
    { name: "Weather Agent", status: "ONLINE", task: "NASA EONET Satellite Stream", queue: 0, latency: "60ms", success: "100%", cpu: "8%", memory: "96MB", health: 100 },
    { name: "Pricing Agent", status: "ONLINE", task: "Dynamic Cost Delta Evaluation", queue: 0, latency: "35ms", success: "99.9%", cpu: "15%", memory: "112MB", health: 100 },
    { name: "Notification Agent", status: "ONLINE", task: "Multi-Channel Push & WhatsApp", queue: 0, latency: "50ms", success: "99.7%", cpu: "10%", memory: "88MB", health: 100 },
    { name: "Customer Support Agent", status: "ONLINE", task: "Conversational Help Queue", queue: 1, latency: "110ms", success: "98.2%", cpu: "28%", memory: "320MB", health: 96 },
    { name: "Ops Assistant Agent", status: "ONLINE", task: "Copilot Contextual Telemetry", queue: 0, latency: "75ms", success: "99.4%", cpu: "18%", memory: "210MB", health: 99 },
    { name: "Analytics Agent", status: "ONLINE", task: "Fleet CSAT & SLA Metrics", queue: 0, latency: "90ms", success: "100%", cpu: "14%", memory: "160MB", health: 100 },
    { name: "Vendor Coordination Agent", status: "ONLINE", task: "Taj & Airline SLA Auditing", queue: 0, latency: "65ms", success: "99.6%", cpu: "16%", memory: "140MB", health: 100 }
  ];

  return (
    <div className="fixed bottom-4 left-4 z-40">
      <div className="glass-panel rounded-2xl border dark:border-slate-800 border-slate-200 shadow-2xl overflow-hidden transition-all duration-300">
        
        {/* Toggle Header */}
        <button
          onClick={() => setExpanded(prev => !prev)}
          className="w-full px-3.5 py-2 bg-slate-900 text-slate-100 flex items-center justify-between space-x-3 text-xs font-bold hover:bg-slate-800 transition-all"
        >
          <div className="flex items-center space-x-2">
            <Bot className="w-4 h-4 text-emerald-400 animate-pulse" />
            <span>AI Agents System Monitor</span>
            <span className="px-2 py-0.5 rounded-full text-[10px] bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              10/10 Agents Online
            </span>
          </div>
          {expanded ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronUp className="w-4 h-4 text-slate-400" />}
        </button>

        {/* Expanded Agent Telemetry Panel */}
        {expanded && (
          <div className="p-3 max-h-80 overflow-y-auto space-y-2 text-xs w-80 sm:w-96 dark:bg-slate-950 bg-white">
            {agents.map((ag, idx) => (
              <div key={idx} className="p-2.5 rounded-xl dark:bg-slate-900 bg-slate-50 border dark:border-slate-800 border-slate-200 space-y-1">
                <div className="flex items-center justify-between font-semibold">
                  <span className="dark:text-slate-100 text-slate-800 font-bold flex items-center space-x-1.5">
                    <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping inline-block" />
                    <span>{ag.name}</span>
                  </span>
                  <span className="text-[10px] font-mono text-emerald-400">{ag.latency}</span>
                </div>

                <div className="text-[11px] text-slate-400 truncate">{ag.task}</div>

                <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1 font-mono border-t dark:border-slate-800/80 border-slate-200">
                  <span className="flex items-center space-x-1">
                    <Cpu className="w-3 h-3 text-brand-400" />
                    <span>CPU: {ag.cpu}</span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <HardDrive className="w-3 h-3 text-purple-400" />
                    <span>RAM: {ag.memory}</span>
                  </span>
                  <span className="flex items-center space-x-1 text-emerald-400">
                    <CheckCircle2 className="w-3 h-3" />
                    <span>{ag.success}</span>
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
