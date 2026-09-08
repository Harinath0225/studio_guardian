import React from 'react';
import { GlassCard } from '../common/GlassCard';
import { Info } from 'lucide-react';
import { SignalContributor } from '../../types/prediction';

interface ContributingFactorsCardProps {
  contributors: SignalContributor[];
}

export const ContributingFactorsCard: React.FC<ContributingFactorsCardProps> = ({
  contributors = [],
}) => {
  // Sort descending by points impact
  const sorted = [...contributors].sort((a, b) => b.points - a.points);

  const getBarColor = (points: number) => {
    if (points >= 18) return 'bg-red-500';
    if (points >= 10) return 'bg-amber-500';
    if (points >= 5) return 'bg-yellow-500';
    return 'bg-emerald-500';
  };

  return (
    <GlassCard title="Leading Telemetry Contributor Breakdown">
      <div className="space-y-3">
        <div className="flex items-center justify-between text-[11px] text-gray-400 font-mono pb-1 border-b border-white/5">
          <span>Signal Name</span>
          <div className="flex gap-6">
            <span>Raw Value</span>
            <span className="w-16 text-right">Risk Points</span>
          </div>
        </div>

        {sorted.length === 0 ? (
          <div className="text-xs text-gray-400 font-mono py-4 text-center">
            No telemetry signals recorded yet.
          </div>
        ) : (
          <div className="space-y-2.5">
            {sorted.map((item) => (
              <div key={item.name} className="space-y-1">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="text-gray-200 font-medium truncate max-w-[200px]" title={item.label}>
                    {item.label}
                  </span>
                  <div className="flex items-center gap-6">
                    <span className="text-gray-400 text-[11px]">
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
                <div className="h-1.5 w-full bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${getBarColor(item.points)}`}
                    style={{ width: `${Math.min(100, Math.max(2, item.points * 4))}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="flex items-center gap-1.5 text-[10px] text-gray-500 font-mono pt-2 border-t border-white/5">
          <Info className="h-3 w-3 shrink-0" />
          <span>Calculated via deterministic linear SLO normalization and 60-second velocity regression.</span>
        </div>
      </div>
    </GlassCard>
  );
};
