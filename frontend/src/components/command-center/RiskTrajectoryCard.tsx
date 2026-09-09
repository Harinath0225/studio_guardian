import React from 'react';
import { GlassCard } from '../common/GlassCard';
import { ShieldAlert, TrendingUp, Zap } from 'lucide-react';
import { PredictiveStatus } from '../../types/prediction';

interface RiskTrajectoryCardProps {
  status: PredictiveStatus;
  onForceEvaluate?: () => void;
  isLoading?: boolean;
  heroMode?: boolean;
}

export const RiskTrajectoryCard: React.FC<RiskTrajectoryCardProps> = ({
  status,
  onForceEvaluate,
  isLoading = false,
  heroMode = true,
}) => {
  const riskScore = status.risk_score || 0;
  const riskPct = Math.round(riskScore * 100);
  const confidencePct = Math.round((status.confidence_score || 0) * 100);

  // Color mapping based on operational risk score
  const getRiskColor = (score: number) => {
    if (score >= 0.80) return { stroke: '#ef4444', text: 'text-red-400', badge: 'bg-red-500/10 text-red-300 border-red-500/30' };
    if (score >= 0.60) return { stroke: '#f59e0b', text: 'text-amber-400', badge: 'bg-amber-500/10 text-amber-300 border-amber-500/30' };
    if (score >= 0.30) return { stroke: '#eab308', text: 'text-amber-300', badge: 'bg-amber-500/10 text-amber-300 border-amber-500/30' };
    return { stroke: '#10b981', text: 'text-emerald-400', badge: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30' };
  };

  const colors = getRiskColor(riskScore);
  const radius = heroMode ? 62 : 46;
  const strokeWidth = heroMode ? 11 : 9;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (riskScore * circumference);
  const center = heroMode ? 78 : 64;
  const svgSize = heroMode ? 156 : 128;

  const cardVariant = heroMode
    ? 'hero'
    : riskScore >= 0.80
    ? 'danger'
    : riskScore >= 0.60
    ? 'warning'
    : 'default';

  return (
    <GlassCard
      title="Predictive Operational Risk Core"
      variant={cardVariant}
      headerAction={
        onForceEvaluate && (
          <button
            onClick={onForceEvaluate}
            disabled={isLoading}
            className="text-xs font-mono px-3 py-1.5 rounded-lg bg-cyan-950/40 hover:bg-cyan-900/60 text-cyan-300 border border-cyan-700/40 flex items-center gap-1.5 transition-all disabled:opacity-50"
          >
            <Zap className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            Sweep MCP Telemetry
          </button>
        )
      }
    >
      <div className="flex flex-col md:flex-row items-center justify-between gap-6 py-1">
        {/* Large Central Hero SVG Circular Gauge */}
        <div className="relative flex items-center justify-center shrink-0">
          <svg width={svgSize} height={svgSize} className="transform -rotate-90">
            {/* Background track */}
            <circle
              cx={center}
              cy={center}
              r={radius}
              stroke="#1e293b"
              strokeWidth={strokeWidth}
              fill="transparent"
            />
            {/* Animated risk ring */}
            <circle
              cx={center}
              cy={center}
              r={radius}
              stroke={colors.stroke}
              strokeWidth={strokeWidth}
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              fill="transparent"
              style={{ transition: 'stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1)' }}
            />
          </svg>
          <div className="absolute flex flex-col items-center justify-center text-center">
            <span className={`${heroMode ? 'text-4xl sm:text-5xl' : 'text-3xl'} font-extrabold font-mono tracking-tight ${colors.text}`}>
              {riskPct}
            </span>
            <span className="text-[10px] uppercase font-mono tracking-wider text-slate-400 font-semibold mt-0.5">
              Risk Score
            </span>
          </div>
        </div>

        {/* Risk details & Confidence */}
        <div className="flex-1 space-y-3 w-full">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-mono">Operating Condition:</span>
            <span className={`text-xs font-mono font-bold px-3 py-1 rounded-full border ${colors.badge}`}>
              {status.state}
            </span>
          </div>

          <div className="bg-black/30 p-3.5 rounded-xl border border-white/5 space-y-2.5">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-400 flex items-center gap-1.5">
                <TrendingUp className="h-3.5 w-3.5 text-cyan-400" />
                Data Confidence:
              </span>
              <span className="text-cyan-300 font-bold">{confidencePct}%</span>
            </div>
            <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
              <div
                className="h-full bg-cyan-400 rounded-full transition-all duration-500"
                style={{ width: `${confidencePct}%` }}
              />
            </div>
            <div className="flex justify-between text-xs text-slate-400 font-mono pt-1">
              <span>Risk Tier: <strong className="text-slate-200">{status.risk_level}</strong></span>
              <span>Horizon Window: <strong className="text-cyan-300">{status.estimated_window_minutes?.min ?? 5}–{status.estimated_window_minutes?.max ?? 15}m</strong></span>
            </div>
          </div>

          <div className="flex items-center gap-2 text-xs text-slate-400 font-sans leading-relaxed">
            <ShieldAlert className={`h-4 w-4 shrink-0 ${riskScore >= 0.80 ? 'text-red-400 animate-pulse' : 'text-emerald-400'}`} />
            <span>
              {riskScore >= 0.80
                ? 'Approaching critical SLO saturation. Automated mitigation armed.'
                : riskScore >= 0.60
                ? 'Elevated leading velocity detected across transcoder pool.'
                : 'All multi-signal leading indicators within nominal SLO limits.'}
            </span>
          </div>
        </div>
      </div>
    </GlassCard>
  );
};
