import React from 'react';
import { GlassCard } from '../common/GlassCard';
import { ShieldAlert, TrendingUp, Zap } from 'lucide-react';
import { PredictiveStatus } from '../../types/prediction';

interface RiskTrajectoryCardProps {
  status: PredictiveStatus;
  onForceEvaluate?: () => void;
  isLoading?: boolean;
}

export const RiskTrajectoryCard: React.FC<RiskTrajectoryCardProps> = ({
  status,
  onForceEvaluate,
  isLoading = false,
}) => {
  const riskScore = status.risk_score || 0;
  const riskPct = Math.round(riskScore * 100);
  const confidencePct = Math.round((status.confidence_score || 0) * 100);

  // Color mapping based on operational risk score
  const getRiskColor = (score: number) => {
    if (score >= 0.80) return { stroke: '#ef4444', text: 'text-red-400', badge: 'bg-red-500/20 text-red-300 border-red-500/30' };
    if (score >= 0.60) return { stroke: '#f59e0b', text: 'text-amber-400', badge: 'bg-amber-500/20 text-amber-300 border-amber-500/30' };
    if (score >= 0.30) return { stroke: '#eab308', text: 'text-yellow-400', badge: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30' };
    return { stroke: '#10b981', text: 'text-emerald-400', badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' };
  };

  const colors = getRiskColor(riskScore);
  const circumference = 2 * Math.PI * 46;
  const strokeDashoffset = circumference - (riskScore * circumference);

  return (
    <GlassCard
      title="Predictive Operational Risk Gauge"
      variant={riskScore >= 0.80 ? 'danger' : riskScore >= 0.60 ? 'glow' : 'default'}
      headerAction={
        onForceEvaluate && (
          <button
            onClick={onForceEvaluate}
            disabled={isLoading}
            className="text-[11px] font-mono px-2.5 py-1 rounded bg-white/5 hover:bg-white/10 text-cyan-300 border border-cyan-500/30 flex items-center gap-1.5 transition-colors disabled:opacity-50"
          >
            <Zap className={`h-3 w-3 ${isLoading ? 'animate-spin' : ''}`} />
            Sweep MCP
          </button>
        )
      }
    >
      <div className="flex flex-col sm:flex-row items-center justify-between gap-6 py-2">
        {/* SVG Circular Gauge */}
        <div className="relative flex items-center justify-center">
          <svg className="w-32 h-32 transform -rotate-90">
            {/* Background track */}
            <circle
              cx="64"
              cy="64"
              r="46"
              stroke="#1f2937"
              strokeWidth="9"
              fill="transparent"
            />
            {/* Animated risk ring */}
            <circle
              cx="64"
              cy="64"
              r="46"
              stroke={colors.stroke}
              strokeWidth="9"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              fill="transparent"
              style={{ transition: 'stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1)' }}
            />
          </svg>
          <div className="absolute flex flex-col items-center justify-center text-center">
            <span className={`text-3xl font-extrabold font-mono ${colors.text}`}>
              {riskPct}
            </span>
            <span className="text-[10px] uppercase font-mono tracking-wider text-gray-400">
              Risk Score
            </span>
          </div>
        </div>

        {/* Risk details & Confidence */}
        <div className="flex-1 space-y-3 w-full">
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-400 font-mono">Operating Condition:</span>
            <span className={`text-xs font-mono font-bold px-2.5 py-0.5 rounded border ${colors.badge}`}>
              {status.state}
            </span>
          </div>

          <div className="bg-black/40 p-3 rounded-lg border border-white/5 space-y-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-gray-400 flex items-center gap-1.5">
                <TrendingUp className="h-3.5 w-3.5 text-cyan-400" />
                Data Confidence:
              </span>
              <span className="text-cyan-400 font-bold">{confidencePct}%</span>
            </div>
            <div className="h-2 w-full rounded-full bg-gray-800 overflow-hidden">
              <div
                className="h-full bg-cyan-500 rounded-full transition-all duration-500"
                style={{ width: `${confidencePct}%` }}
              />
            </div>
            <div className="flex justify-between text-[11px] text-gray-400 font-mono pt-1">
              <span>Risk Tier: <strong className="text-gray-200">{status.risk_level}</strong></span>
              <span>Horizon: <strong className="text-gray-200">{status.estimated_window_minutes?.min ?? 5}–{status.estimated_window_minutes?.max ?? 15}m</strong></span>
            </div>
          </div>

          <div className="flex items-center gap-2 text-[11px] text-gray-400 font-mono">
            <ShieldAlert className={`h-3.5 w-3.5 ${riskScore >= 0.80 ? 'text-red-400 animate-pulse' : 'text-emerald-400'}`} />
            <span>
              {riskScore >= 0.80
                ? 'Approaching critical SLO saturation. Auto-prevention armed.'
                : riskScore >= 0.60
                ? 'Elevated leading velocity detected across transcoder pool.'
                : 'All multi-signal leading indicators within nominal limits.'}
            </span>
          </div>
        </div>
      </div>
    </GlassCard>
  );
};
