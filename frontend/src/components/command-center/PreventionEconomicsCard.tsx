import React from 'react';
import { GlassCard } from '../common/GlassCard';
import { TrendingDown, CheckCircle2 } from 'lucide-react';
import { PreventionProposal } from '../../types/prediction';

interface PreventionEconomicsCardProps {
  proposal?: PreventionProposal;
}

export const PreventionEconomicsCard: React.FC<PreventionEconomicsCardProps> = ({
  proposal,
}) => {
  const expectedLoss = proposal?.expected_loss_without_action ?? 46000;
  const costToPrevent = proposal?.cost_of_prevention ?? 340;
  const netAvoided = proposal?.expected_avoided_exposure ?? (expectedLoss - costToPrevent);
  const roi = Math.round(netAvoided / Math.max(1, costToPrevent));

  return (
    <GlassCard title="Prevention Economics & Cost Trade-Off">
      <div className="space-y-4">
        {/* Metric Triad */}
        <div className="grid grid-cols-3 gap-3 text-center">
          <div className="bg-red-950/20 border border-red-500/20 p-3 rounded-xl">
            <span className="text-[11px] font-mono text-gray-400 block uppercase">Exp. Unmitigated Loss</span>
            <span className="text-lg sm:text-xl font-bold font-mono text-red-400">
              ${expectedLoss.toLocaleString()}
            </span>
          </div>

          <div className="bg-blue-950/20 border border-blue-500/20 p-3 rounded-xl">
            <span className="text-[11px] font-mono text-gray-400 block uppercase">Prevention Compute</span>
            <span className="text-lg sm:text-xl font-bold font-mono text-blue-300">
              ${costToPrevent.toLocaleString()}
            </span>
          </div>

          <div className="bg-emerald-950/20 border border-emerald-500/20 p-3 rounded-xl">
            <span className="text-[11px] font-mono text-gray-400 block uppercase">Net Avoided Exposure</span>
            <span className="text-lg sm:text-xl font-bold font-mono text-emerald-400">
              ${netAvoided.toLocaleString()}
            </span>
          </div>
        </div>

        {/* Visual cost-loss trade-off comparison bar */}
        <div className="bg-black/40 p-3 rounded-lg border border-white/5 space-y-2">
          <div className="flex justify-between text-xs font-mono">
            <span className="text-gray-400 flex items-center gap-1">
              <TrendingDown className="h-3.5 w-3.5 text-emerald-400" />
              Economic Return on Prevention:
            </span>
            <span className="text-emerald-400 font-bold">{roi}x ROI</span>
          </div>

          {/* Bar comparison */}
          <div className="space-y-1">
            <div className="flex justify-between text-[10px] font-mono text-gray-500">
              <span>Risk: 100% Potential Exposure</span>
              <span>Cost: &lt; 1% Compute Scaling</span>
            </div>
            <div className="h-2 w-full bg-red-900/40 rounded-full overflow-hidden flex">
              <div className="h-full bg-emerald-500 rounded-l-full w-[98%]" title="Avoided Loss" />
              <div className="h-full bg-blue-400 rounded-r-full w-[2%]" title="Scaling Compute Cost" />
            </div>
          </div>
        </div>

        {/* Protection assurance */}
        <div className="flex items-center gap-2 text-xs font-mono text-gray-300 bg-white/5 p-2.5 rounded-lg border border-white/5">
          <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
          <span>
            Proactive 2x worker scale prevents player re-buffering for approx 1.8M concurrent live viewers.
          </span>
        </div>
      </div>
    </GlassCard>
  );
};
