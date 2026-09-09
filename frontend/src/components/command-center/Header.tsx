import React from 'react';
import { StatusBadge } from '../common/StatusBadge';
import { ManualOverrideButton } from './ManualOverrideButton';
import { Shield, RotateCcw, AlertTriangle } from 'lucide-react';

interface HeaderProps {
  eventTitle: string;
  status: string;
  concurrentViewers: number;
  onTriggerIncident: () => void;
  onReset: () => void;
  onForceFailure: () => void;
  onEmergencyTakeover?: () => Promise<void>;
  isDegraded: boolean;
  actionLoading?: boolean;
  mode?: 'PREDICTIVE' | 'REACTIVE';
  onModeChange?: (mode: 'PREDICTIVE' | 'REACTIVE') => void;
}

export const Header: React.FC<HeaderProps> = ({
  eventTitle,
  status,
  concurrentViewers,
  onTriggerIncident,
  onReset,
  onForceFailure,
  onEmergencyTakeover,
  isDegraded,
  actionLoading = false,
  mode = 'PREDICTIVE',
  onModeChange,
}) => {
  return (
    <header className="glass-panel sticky top-0 z-50 border-b border-white/10 px-6 py-4">
      <div className="flex flex-wrap items-center justify-between gap-4 max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-cyan-600/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shadow-lg shadow-cyan-500/20">
            <Shield className="h-6 w-6 text-cyan-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-extrabold tracking-tight text-white font-display">STUDIO GUARDIAN</h1>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/15 text-cyan-300 font-mono font-bold border border-cyan-500/30 tracking-wider">
                AUTONOMOUS MEDIA SRE
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              Event: <span className="text-slate-200 font-semibold">{eventTitle}</span> • Viewers: <span className="text-cyan-300 font-semibold font-mono">{concurrentViewers.toLocaleString()}</span>
            </p>
          </div>
        </div>

        {/* Predictive vs Reactive Mode Switcher */}
        {onModeChange && (
          <div className="flex items-center bg-black/60 p-1 rounded-xl border border-white/10 font-mono text-xs">
            <button
              onClick={() => onModeChange('PREDICTIVE')}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-all flex items-center gap-2 ${
                mode === 'PREDICTIVE'
                  ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-md shadow-cyan-500/20'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <span className={`h-2 w-2 rounded-full ${mode === 'PREDICTIVE' ? 'bg-cyan-300 animate-pulse' : 'bg-slate-500'}`} />
              Predictive Ops
            </button>
            <button
              onClick={() => onModeChange('REACTIVE')}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-all flex items-center gap-2 ${
                mode === 'REACTIVE'
                  ? 'bg-gradient-to-r from-amber-600 to-red-600 text-white shadow-md shadow-red-500/20'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <span className={`h-2 w-2 rounded-full ${mode === 'REACTIVE' ? 'bg-red-400 animate-pulse' : 'bg-slate-500'}`} />
              Incident Director
            </button>
          </div>
        )}

        <div className="flex items-center gap-3.5">
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400 uppercase tracking-wider font-mono">Stream Status:</span>
            <StatusBadge status={status} size="lg" />
          </div>

          <div className="h-6 w-px bg-white/10" />

          {/* Emergency Operator Override */}
          <ManualOverrideButton
            onAbort={onEmergencyTakeover || (async () => {
              await fetch('/api/v1/incidents/emergency-takeover', { method: 'POST' });
            })}
            isOverridden={status === 'ESCALATED_HUMAN_TAKEOVER'}
          />

          <div className="h-6 w-px bg-white/10" />

          {/* Hackathon Demo Control Bar */}
          <div className="flex items-center gap-2 bg-black/40 p-1.5 rounded-xl border border-white/10 shadow-inner">
            <button
              onClick={onTriggerIncident}
              className={`flex items-center gap-1.5 text-xs font-mono font-bold px-3 py-1.5 rounded-lg transition-all active:scale-[0.98] ${
                isDegraded || actionLoading
                  ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-white/5'
                  : 'bg-red-600 hover:bg-red-500 text-white shadow-lg shadow-red-600/30'
              }`}
              disabled={isDegraded || actionLoading}
            >
              <AlertTriangle className="h-3.5 w-3.5" />
              {actionLoading ? 'Triggering...' : 'Trigger Incident'}
            </button>
            <button
              onClick={onReset}
              disabled={actionLoading}
              className="flex items-center gap-1.5 text-xs font-mono font-semibold px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 transition-all border border-white/5 active:scale-[0.98] disabled:opacity-50"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              Reset
            </button>
            <button
              onClick={onForceFailure}
              disabled={actionLoading}
              className="flex items-center gap-1.5 text-xs font-mono font-semibold px-2.5 py-1.5 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 transition-all active:scale-[0.98] disabled:opacity-50"
              title="Forces warm standby to fail, triggering human escalation loop"
            >
              Force Escalate
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
