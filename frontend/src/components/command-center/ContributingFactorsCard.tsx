import React, { useState } from 'react';
import { GlassCard } from '../common/GlassCard';
import { Info, ChevronDown, ChevronUp } from 'lucide-react';
import { SignalContributor } from '../../types/prediction';

interface ContributingFactorsCardProps {
  contributors: SignalContributor[];
}

export const ContributingFactorsCard: React.FC<ContributingFactorsCardProps> = ({
  contributors = [],
}) => {
  const [isExpanded, setIsExpanded] = useState<boolean>(false);

  // Sort descending by points impact
  const sorted = [...contributors].sort((a, b) => b.points - a.points);
  const visibleItems = isExpanded ? sorted : sorted.slice(0, 3);

  const getBarColor = (points: number) => {
    if (points >= 18) return 'bg-red-500';
    if (points >= 10) return 'bg-amber-500';
    if (points >= 5) return 'bg-amber-400';
    return 'bg-emerald-500';
  };

  return (
    <GlassCard
      title="Leading Telemetry Contributor Breakdown"
      headerAction={
        sorted.length > 3 ? (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-[11px] font-mono text-cyan-400 hover:text-cyan-300 flex items-center gap-1 transition-colors px-2 py-0.5 rounded bg-cyan-950/40 border border-cyan-800/40 hover:border-cyan-600/60"
          >
            {isExpanded ? (
              <>
                <span>Top 3</span>
                <ChevronUp className="h-3 w-3" />
              </>
            ) : (
              <>
                <span>+{sorted.length - 3} More</span>
                <ChevronDown className="h-3 w-3" />
              </>
            )}
          </button>
        ) : undefined
      }
    >
      <div className="space-y-3">
        <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono pb-1 border-b border-white/5">
          <span>Signal Name</span>
          <div className="flex gap-6">
            <span>Raw Value</span>
            <span className="w-16 text-right">Risk Points</span>
          </div>
        </div>

        {sorted.length === 0 ? (
          <div className="text-xs text-slate-400 font-mono py-4 text-center">
            No telemetry signals recorded yet.
          </div>
        ) : (
          <div className="space-y-2.5">
            {visibleItems.map((item) => (
              <div key={item.name} className="space-y-1">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="text-slate-200 font-medium truncate max-w-[200px]" title={item.label}>
                    {item.label}
                  </span>
                  <div className="flex items-center gap-6">
                    <span className="text-slate-400 text-[11px]">
                      {typeof item.raw_value === 'number'
                        ? item.raw_value > 10000
                          ? `${(item.raw_value / 1000000).toFixed(1)}M`
                          : item.raw_value.toFixed(1)
                        : item.raw_value}
                    </span>
                    <span className="text-right font-bold w-16 text-cyan-300">
                      +{item.points.toFixed(1)} pts
                    </span>
                  </div>
                </div>

                {/* Contribution points bar */}
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${getBarColor(item.points)}`}
                    style={{ width: `${Math.min(100, Math.max(2, item.points * 4))}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}

        {sorted.length > 3 && (
          <div className="pt-1 text-center">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-xs font-mono text-cyan-400 hover:text-cyan-300 inline-flex items-center gap-1.5 py-1 px-3 rounded-md bg-white/5 hover:bg-white/10 transition-colors"
            >
              {isExpanded ? (
                <>
                  <ChevronUp className="h-3.5 w-3.5" />
                  <span>Collapse to Top 3 Signals</span>
                </>
              ) : (
                <>
                  <ChevronDown className="h-3.5 w-3.5" />
                  <span>Expand All {sorted.length} Signals</span>
                </>
              )}
            </button>
          </div>
        )}

        <div className="flex items-center gap-1.5 text-[10px] text-slate-400 font-sans pt-2 border-t border-white/5">
          <Info className="h-3 w-3 text-slate-400 shrink-0" />
          <span>Calculated via deterministic linear SLO normalization and 60-second velocity regression.</span>
        </div>
      </div>
    </GlassCard>
  );
};
