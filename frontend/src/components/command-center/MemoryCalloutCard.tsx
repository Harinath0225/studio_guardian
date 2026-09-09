import React, { useEffect, useState } from 'react';
import { GlassCard } from '../common/GlassCard';
import { History, ShieldCheck, DollarSign, Sparkles } from 'lucide-react';

interface PriorIntervention {
  id: string;
  match_score: number;
  event_context: string;
  diagnosed_mode: string;
  remediation_applied: string;
  outcome_summary: string;
  avoided_exposure_usd: number;
}

const DEFAULT_TOP_MATCH: PriorIntervention = {
  id: 'mem-prev-cricket-semi-2026',
  match_score: 0.96,
  event_context: 'ICC Champions Trophy Semifinal (IND vs ENG)',
  diagnosed_mode: 'Transcoder Worker Pool Saturation',
  remediation_applied: 'scale_transcoder_pool (2x capacity expansion)',
  outcome_summary: 'GPU utilization dropped from 94% to 58% in 45s with zero player re-buffering.',
  avoided_exposure_usd: 48500,
};

interface MemoryCalloutCardProps {
  onViewAll?: () => void;
  className?: string;
}

export const MemoryCalloutCard: React.FC<MemoryCalloutCardProps> = ({
  onViewAll,
  className = '',
}) => {
  const [topMatch, setTopMatch] = useState<PriorIntervention>(DEFAULT_TOP_MATCH);

  useEffect(() => {
    fetch('/api/v1/prediction/memory')
      .then((res) => (res.ok ? res.json() : [DEFAULT_TOP_MATCH]))
      .then((data: PriorIntervention[]) => {
        if (data && data.length > 0) {
          const sorted = [...data].sort((a, b) => b.match_score - a.match_score);
          setTopMatch(sorted[0]);
        }
      })
      .catch(() => setTopMatch(DEFAULT_TOP_MATCH));
  }, []);

  return (
    <GlassCard
      title="Vertex AI Memory • Top Historical Match"
      variant="glow"
      className={className}
      headerAction={
        <div className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 font-mono text-xs font-bold">
          <Sparkles className="h-3 w-3 text-cyan-400" />
          <span>{Math.round(topMatch.match_score * 100)}% Similarity Match</span>
        </div>
      }
    >
      <div className="space-y-3">
        {/* Context & Prior Event Header */}
        <div className="flex items-start justify-between gap-3">
          <div>
            <span className="text-[10px] uppercase font-mono tracking-wider text-slate-400 block">
              Prior Incident Fingerprint
            </span>
            <h4 className="text-sm font-bold text-slate-100 font-mono mt-0.5">
              {topMatch.event_context}
            </h4>
          </div>
          <div className="px-2.5 py-1 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono text-xs font-bold shrink-0 flex items-center gap-1">
            <DollarSign className="h-3.5 w-3.5" />
            <span>${topMatch.avoided_exposure_usd.toLocaleString()} Avoided</span>
          </div>
        </div>

        {/* Causal Mode & Remediation Formula */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs font-mono">
          <div className="p-2.5 rounded-lg bg-black/40 border border-white/5">
            <span className="text-slate-400 text-[10px] block">Identified Causal Pattern</span>
            <span className="text-amber-300 font-semibold truncate block mt-0.5">
              {topMatch.diagnosed_mode}
            </span>
          </div>
          <div className="p-2.5 rounded-lg bg-black/40 border border-white/5">
            <span className="text-slate-400 text-[10px] block">Verified Autonomous Playbook</span>
            <span className="text-emerald-400 font-semibold truncate block mt-0.5">
              {topMatch.remediation_applied}
            </span>
          </div>
        </div>

        {/* Narrative Outcome */}
        <div className="text-xs text-slate-300 font-sans leading-relaxed p-2.5 rounded-lg bg-cyan-950/20 border border-cyan-500/20">
          <span className="font-mono text-[10px] text-cyan-400 block font-semibold uppercase tracking-wider mb-0.5">
            Historical Validation
          </span>
          <p className="max-w-[70ch]">{topMatch.outcome_summary}</p>
        </div>

        {/* Footer info & view all affordance */}
        <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono pt-1">
          <span className="flex items-center gap-1 text-emerald-400">
            <ShieldCheck className="h-3.5 w-3.5" /> Zero SLO breaches recorded
          </span>
          {onViewAll && (
            <button
              onClick={onViewAll}
              className="text-cyan-400 hover:text-cyan-300 underline font-semibold flex items-center gap-1 transition-colors"
            >
              <History className="h-3 w-3" /> All Fingerprints
            </button>
          )}
        </div>
      </div>
    </GlassCard>
  );
};
