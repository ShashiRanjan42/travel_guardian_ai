import React, { useState } from 'react';
import { Zap, AlertTriangle, CloudRain, Wind, Train, Flame, Loader2 } from 'lucide-react';

export default function SimulationBar({ onSimulate, loading }) {
  const [activePreset, setActivePreset] = useState(null);

  const presets = [
    {
      id: 'MONSOON_MUMBAI_BOM',
      label: 'Monsoon Rain at Mumbai BOM',
      icon: CloudRain,
      color: 'bg-red-500/20 text-red-400 border-red-500/30 hover:bg-red-500/30'
    },
    {
      id: 'SMOG_DELHI_IGI',
      label: 'Smog CAT III-B at Delhi DEL',
      icon: Wind,
      color: 'bg-amber-500/20 text-amber-400 border-amber-500/30 hover:bg-amber-500/30'
    },
    {
      id: 'VANDE_BHARAT_RAIL_BLOCK',
      label: 'Vande Bharat Rail Corridor Block',
      icon: Train,
      color: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30 hover:bg-cyan-500/30'
    },
    {
      id: 'CYCLONE_BAY_OF_BENGAL',
      label: 'Bay of Bengal Cyclone Alert',
      icon: Flame,
      color: 'bg-purple-500/20 text-purple-400 border-purple-500/30 hover:bg-purple-500/30'
    }
  ];

  const handleSimulate = (presetId) => {
    setActivePreset(presetId);
    onSimulate(presetId);
  };

  return (
    <div className="bg-slate-900/90 border-b border-slate-800 px-4 py-2 flex flex-wrap items-center justify-between gap-3 text-xs">
      <div className="flex items-center space-x-2">
        <div className="p-1 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
          <Zap className="w-3.5 h-3.5 animate-pulse" />
        </div>
      </div>

      <div className="flex items-center space-x-2 overflow-x-auto py-0.5">
        {presets.map((preset) => {
          const Icon = preset.icon;
          const isSelected = activePreset === preset.id;
          return (
            <button
              key={preset.id}
              disabled={loading}
              onClick={() => handleSimulate(preset.id)}
              className={`px-3 py-1.5 rounded-lg border text-xs font-medium flex items-center space-x-1.5 transition-all whitespace-nowrap ${preset.color} ${isSelected ? 'ring-2 ring-brand-500' : ''}`}
            >
              {loading && isSelected ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Icon className="w-3.5 h-3.5" />
              )}
              <span>{preset.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
