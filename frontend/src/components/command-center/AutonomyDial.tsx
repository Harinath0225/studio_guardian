import React, { useState } from 'react';
import { GlassCard } from '../common/GlassCard';
import { ShieldCheck, UserCheck, Lock } from 'lucide-react';

export const AutonomyDial: React.FC = () => {
  const [mode, setMode] = useState<'AUTO' | 'ASSISTED' | 'MANUAL'>('AUTO');

  return (
    <GlassCard title="Safety Director • Autonomy Policy Engine">
      <div className="grid grid-cols-3 gap-2">
        <button
          onClick={() => setMode('AUTO')}
          className={`p-2.5 rounded-lg border text-left transition-all ${
            mode === 'AUTO'
              ? 'bg-blue-600/20 border-blue-500/50 text-white shadow-lg shadow-blue-500/10'
              : 'bg-white/5 border-white/5 text-gray-400 hover:text-gray-200'
          }`}
        >
          <div className="flex items-center gap-1.5 mb-1">
            <ShieldCheck className="h-4 w-4 text-blue-400" />
            <span className="text-xs font-mono font-bold">FULL AUTONOMY</span>
          </div>
          <p className="text-[10px] text-gray-400 leading-tight">
            Auto-executes safe allowlisted actions if blast radius &le; 25% & confidence &ge; 85%.
          </p>
        </button>

        <button
          onClick={() => setMode('ASSISTED')}
          className={`p-2.5 rounded-lg border text-left transition-all ${
            mode === 'ASSISTED'
              ? 'bg-amber-600/20 border-amber-500/50 text-white shadow-lg shadow-amber-500/10'
              : 'bg-white/5 border-white/5 text-gray-400 hover:text-gray-200'
          }`}
        >
          <div className="flex items-center gap-1.5 mb-1">
            <UserCheck className="h-4 w-4 text-amber-400" />
            <span className="text-xs font-mono font-bold">ASSISTED</span>
          </div>
          <p className="text-[10px] text-gray-400 leading-tight">
            Requires human operator confirmation before dispatching remediation.
          </p>
        </button>

        <button
          onClick={() => setMode('MANUAL')}
          className={`p-2.5 rounded-lg border text-left transition-all ${
            mode === 'MANUAL'
              ? 'bg-red-600/20 border-red-500/50 text-white shadow-lg shadow-red-500/10'
              : 'bg-white/5 border-white/5 text-gray-400 hover:text-gray-200'
          }`}
        >
          <div className="flex items-center gap-1.5 mb-1">
            <Lock className="h-4 w-4 text-red-400" />
            <span className="text-xs font-mono font-bold">MANUAL LOCK</span>
          </div>
          <p className="text-[10px] text-gray-400 leading-tight">
            Freezes all agent mutations. Operator takes full manual control.
          </p>
        </button>
      </div>
    </GlassCard>
  );
};
