import React from 'react';
import { GlassCard } from '../common/GlassCard';
import { History, ShieldCheck } from 'lucide-react';

export const IncidentMemoryCard: React.FC = () => {
  return (
    <GlassCard title="Historical Incident Memory • Vertex Vector Recall">
      <div className="space-y-2">
        <div className="flex items-start gap-2.5 p-2.5 rounded-lg bg-black/30 border border-white/5">
          <History className="h-4 w-4 text-cyan-400 mt-0.5 shrink-0" />
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs font-bold font-mono text-cyan-300 truncate">
                MATCH: ICC Cricket Semifinal (2024)
              </span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                85% Match
              </span>
            </div>
            <p className="text-[11px] text-gray-400 mt-1 leading-snug">
              Symptoms: Elevated buffer ratio in AU zone after patch deployment. Resolved by regional warm-standby traffic shift.
            </p>
            <div className="mt-2 flex items-center gap-1 text-[11px] font-mono text-emerald-400">
              <ShieldCheck className="h-3.5 w-3.5" />
              <span>Prior Successful Fix: TRAFFIC_SHIFT to transcoder-us-01</span>
            </div>
          </div>
        </div>
      </div>
    </GlassCard>
  );
};
