import React from 'react';
import { GlassCard } from '../common/GlassCard';
import { Users, DollarSign, Crown, AlertCircle } from 'lucide-react';

interface BusinessCardProps {
  isDegraded: boolean;
  affectedViewers: number;
  totalViewers: number;
}

export const BusinessCard: React.FC<BusinessCardProps> = ({
  isDegraded,
  affectedViewers,
  totalViewers
}) => {
  const vipViewers = Math.round(affectedViewers * 0.04);
  const adRevenueAtRisk = isDegraded ? 18750.0 : 0.0;
  const slaLiability = isDegraded ? 37500.0 : 0.0;

  return (
    <GlassCard title="Commercial & Audience Impact • Executive Brief">
      <div className="grid grid-cols-2 gap-3">
        {/* Disrupted Viewers */}
        <div className="bg-white/5 p-3 rounded-lg border border-white/5">
          <div className="flex items-center gap-1.5 text-gray-400 text-xs font-mono">
            <Users className="h-3.5 w-3.5 text-blue-400" />
            <span>Disrupted Viewers</span>
          </div>
          <div className="mt-1 flex items-baseline gap-1.5">
            <span className={`text-xl font-bold font-mono ${isDegraded ? 'text-red-400' : 'text-gray-200'}`}>
              {isDegraded ? affectedViewers.toLocaleString() : '0'}
            </span>
            <span className="text-[10px] text-gray-500 font-mono">of {(totalViewers / 1e6).toFixed(1)}M</span>
          </div>
        </div>

        {/* High-Value VIP Audience */}
        <div className="bg-white/5 p-3 rounded-lg border border-white/5">
          <div className="flex items-center gap-1.5 text-gray-400 text-xs font-mono">
            <Crown className="h-3.5 w-3.5 text-amber-400" />
            <span>VIP Subscribers (4K)</span>
          </div>
          <div className="mt-1">
            <span className={`text-xl font-bold font-mono ${isDegraded ? 'text-amber-400' : 'text-gray-200'}`}>
              {isDegraded ? vipViewers.toLocaleString() : '0'}
            </span>
          </div>
        </div>

        {/* Ad Revenue Exposure */}
        <div className="bg-white/5 p-3 rounded-lg border border-white/5">
          <div className="flex items-center gap-1.5 text-gray-400 text-xs font-mono">
            <DollarSign className="h-3.5 w-3.5 text-emerald-400" />
            <span>Ad Revenue at Risk</span>
          </div>
          <div className="mt-1">
            <span className={`text-xl font-bold font-mono ${isDegraded ? 'text-red-400' : 'text-gray-200'}`}>
              ${adRevenueAtRisk.toLocaleString()}
            </span>
          </div>
        </div>

        {/* SLA Exposure */}
        <div className="bg-white/5 p-3 rounded-lg border border-white/5">
          <div className="flex items-center gap-1.5 text-gray-400 text-xs font-mono">
            <AlertCircle className="h-3.5 w-3.5 text-purple-400" />
            <span>SLA Penalty Exposure</span>
          </div>
          <div className="mt-1">
            <span className={`text-xl font-bold font-mono ${isDegraded ? 'text-red-400' : 'text-gray-200'}`}>
              ${slaLiability.toLocaleString()}
            </span>
          </div>
        </div>
      </div>

      <div className="mt-3 p-2.5 rounded bg-black/30 border border-white/5 text-xs text-gray-300 font-mono">
        {isDegraded ? (
          <span className="text-amber-300">
            URGENCY: IMMEDIATE • P1 broadcast breach in Australia/Singapore region. Immediate traffic diversion to warm-standby cluster recommended.
          </span>
        ) : (
          <span className="text-gray-400">
            Audience experience optimal. Ad burn rates and broadcast contractual SLA metrics normal.
          </span>
        )}
      </div>
    </GlassCard>
  );
};
