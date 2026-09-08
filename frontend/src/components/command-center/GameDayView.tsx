import React, { useState } from 'react';
import { Flame, Radio, RotateCcw, AlertOctagon, CheckCircle2 } from 'lucide-react';

interface GameDayViewProps {
  onScenarioTriggered?: () => void;
}

export const GameDayView: React.FC<GameDayViewProps> = ({ onScenarioTriggered }) => {
  const [activeMessage, setActiveMessage] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  const triggerChaos = async (endpoint: string, label: string) => {
    setLoading(true);
    setActiveMessage(`Injecting scenario: ${label}...`);
    try {
      const res = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      const data = await res.json();
      setActiveMessage(data.message || `Scenario ${label} active.`);
      if (onScenarioTriggered) onScenarioTriggered();
    } catch (e) {
      console.error(e);
      setActiveMessage(`Error triggering ${label}.`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white tracking-wide flex items-center gap-2">
            <Flame className="w-5 h-5 text-red-500" />
            Deterministic Black Swan Game Day
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Inject controlled broadcast failure cascades to demonstrate autonomous predictive and reactive mitigation.
          </p>
        </div>
        <button
          onClick={() => triggerChaos('/api/v1/demo/black-swan/reset', 'Baseline Reset')}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-xs font-semibold tracking-wider transition"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Reset Baseline
        </button>
      </div>

      {activeMessage && (
        <div className="p-3 bg-cyan-950/40 border border-cyan-800 rounded-lg text-xs text-cyan-300 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0" />
          <span>{activeMessage}</span>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Scenario 1: Transcoder Surge */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col justify-between hover:border-red-900/50 transition">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="p-2 bg-red-950 text-red-400 rounded-lg">
                <Flame className="w-5 h-5" />
              </span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 bg-red-900/40 text-red-300 rounded border border-red-800/60">
                Predictive Path
              </span>
            </div>
            <h3 className="text-base font-bold text-white mb-1.5">
              Transcoder Capacity Surge
            </h3>
            <p className="text-xs text-slate-400 mb-4 leading-relaxed">
              Spikes 4K/HDR load escalating GPU to 93.4% and queue depth to 48 while error rate remains low. Triggers predictive capacity scaling.
            </p>
          </div>
          <button
            onClick={() => triggerChaos('/api/v1/demo/black-swan/transcoder-surge', 'Transcoder Surge')}
            disabled={loading}
            className="w-full py-2.5 bg-red-600 hover:bg-red-500 text-white font-bold text-xs rounded-lg transition tracking-wide shadow-lg shadow-red-950/50"
          >
            Inject Transcoder Surge
          </button>
        </div>

        {/* Scenario 2: SCTE-35 Splice Corruption */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col justify-between hover:border-amber-900/50 transition">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="p-2 bg-amber-950 text-amber-400 rounded-lg">
                <Radio className="w-5 h-5" />
              </span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 bg-amber-900/40 text-amber-300 rounded border border-amber-800/60">
                Ad Integrity Path
              </span>
            </div>
            <h3 className="text-base font-bold text-white mb-1.5">
              SCTE-35 Splice Corruption
            </h3>
            <p className="text-xs text-slate-400 mb-4 leading-relaxed">
              Drifts ad cue timing (+420ms) and corrupts splice inserts without impacting server CPU/GPU. Triggers Ad Integrity Sentinel and backup slate.
            </p>
          </div>
          <button
            onClick={() => triggerChaos('/api/v1/demo/black-swan/scte35-corruption', 'SCTE-35 Corruption')}
            disabled={loading}
            className="w-full py-2.5 bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs rounded-lg transition tracking-wide shadow-lg shadow-amber-950/50"
          >
            Inject SCTE-35 Corruption
          </button>
        </div>

        {/* Scenario 3: Acute Playback Failure */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col justify-between hover:border-purple-900/50 transition">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="p-2 bg-purple-950 text-purple-400 rounded-lg">
                <AlertOctagon className="w-5 h-5" />
              </span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 bg-purple-900/40 text-purple-300 rounded border border-purple-800/60">
                Reactive Path
              </span>
            </div>
            <h3 className="text-base font-bold text-white mb-1.5">
              Sudden Regional Cluster Failure
            </h3>
            <p className="text-xs text-slate-400 mb-4 leading-relaxed">
              Spikes playback error rate to 8.7% and latency to 485ms in AU/SG. Demonstrates immediate reactive fallback and regional traffic shifting.
            </p>
          </div>
          <button
            onClick={() => triggerChaos('/api/v1/demo/incident', 'Sudden Outage')}
            disabled={loading}
            className="w-full py-2.5 bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs rounded-lg transition tracking-wide shadow-lg shadow-purple-950/50"
          >
            Inject Sudden Outage
          </button>
        </div>
      </div>
    </div>
  );
};