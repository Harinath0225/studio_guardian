import React from 'react';
import { RotateCcw, AlertTriangle } from 'lucide-react';

interface SimulatorBarProps {
  onTriggerIncident: () => void;
  onReset: () => void;
  onForceFailure: () => void;
  isDegraded: boolean;
  actionLoading?: boolean;
}

export const SimulatorBar: React.FC<SimulatorBarProps> = ({
  onTriggerIncident,
  onReset,
  onForceFailure,
  isDegraded,
  actionLoading = false
}) => {
  return (
    <aside aria-label="Demo Simulator Bar" className="fixed bottom-4 left-1/2 -translate-x-1/2 z-40 max-w-xl w-[92%] glass-panel-glow border border-blue-500/30 rounded-2xl p-2.5 shadow-2xl backdrop-blur-xl">
      <div className="flex items-center justify-between gap-3 px-2">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-blue-400 animate-pulse" />
          <span className="text-xs font-mono font-bold text-gray-200">DEMO RUNNER</span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onTriggerIncident}
            disabled={isDegraded || actionLoading}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all ${
              isDegraded || actionLoading
                ? 'bg-gray-800 text-gray-500 cursor-not-allowed'
                : 'bg-red-600 hover:bg-red-500 text-white shadow-lg shadow-red-600/30 animate-pulse'
            }`}
          >
            <AlertTriangle className="h-3.5 w-3.5" />
            {isDegraded ? 'Incident Fired' : '1. Trigger Degradation'}
          </button>

          <button
            onClick={onReset}
            disabled={actionLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-200 text-xs font-mono font-semibold transition-all border border-white/10"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            Reset
          </button>

          <button
            onClick={onForceFailure}
            disabled={actionLoading}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 text-xs font-mono font-medium"
            title="Simulates standby cluster node failure to force human takeover escalation"
          >
            Force Escalate
          </button>
        </div>
      </div>
    </aside>
  );
};
