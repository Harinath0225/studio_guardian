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
  actionLoading = false
}) => {
  return (
    <header className="glass-panel sticky top-0 z-50 border-b border-white/10 px-6 py-4">
      <div className="flex flex-wrap items-center justify-between gap-4 max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 shadow-lg shadow-blue-500/20">
            <Shield className="h-6 w-6 text-blue-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight text-white font-sans">STUDIO GUARDIAN</h1>
              <span className="text-xs px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 font-mono font-medium border border-blue-500/30">
                AUTONOMOUS MEDIA SRE
              </span>
            </div>
            <p className="text-xs text-gray-400 font-mono mt-0.5">
              Event: <span className="text-gray-200 font-semibold">{eventTitle}</span> • Viewers: <span className="text-blue-300 font-semibold">{concurrentViewers.toLocaleString()}</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-400 uppercase tracking-wider font-mono">Stream Status:</span>
            <StatusBadge status={status} size="lg" />
          </div>

          <div className="h-6 w-px bg-white/10" />

          {/* Emergency Operator Override */}
          <ManualOverrideButton
            onAbort={onEmergencyTakeover || (async () => {
              await fetch('http://localhost:8000/api/v1/incidents/emergency-takeover', { method: 'POST' });
            })}
            isOverridden={status === 'ESCALATED_HUMAN_TAKEOVER'}
          />

          <div className="h-6 w-px bg-white/10" />

          {/* Hackathon Demo Control Bar */}
          <div className="flex items-center gap-2 bg-black/40 p-1.5 rounded-lg border border-white/10">
            <button
              onClick={onTriggerIncident}
              className={`flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-md transition-all ${
                isDegraded || actionLoading
                  ? 'bg-gray-800 text-gray-500 cursor-not-allowed'
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
              className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-md bg-gray-800 hover:bg-gray-700 text-gray-200 transition-all border border-white/5 disabled:opacity-50"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              Reset
            </button>
            <button
              onClick={onForceFailure}
              disabled={actionLoading}
              className="flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1.5 rounded-md bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 transition-all disabled:opacity-50"
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
