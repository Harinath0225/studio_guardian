import React from 'react';
import { GlassCard } from '../common/GlassCard';
import { CheckCircle, ArrowDownRight } from 'lucide-react';
import { VerificationResult } from '../../types/prediction';

interface VerificationResultCardProps {
  result?: VerificationResult;
}

const DEFAULT_VERIFICATION: VerificationResult = {
  action_id: 'act-verified-01',
  verdict: 'PREVENTION_VERIFIED',
  comparison: {
    risk_score: { before: 0.87, after: 0.22, delta: -0.65 },
    gpu_utilization_pct: { before: 93.4, after: 61.2, delta: -32.2 },
    transcoder_latency_ms: { before: 470.0, after: 260.0, delta: -210.0 },
    playback_error_rate_pct: { before: 0.48, after: 0.38, delta: -0.10 },
  },
  counterfactual: {
    projected_risk_reduction: '-74.7%',
    estimated_exposure_avoided: 45660,
    estimated_viewers_protected: 1820000,
  },
  verified_at: new Date().toISOString(),
};

export const VerificationResultCard: React.FC<VerificationResultCardProps> = ({
  result = DEFAULT_VERIFICATION,
}) => {
  const comp = result.comparison;
  const count = result.counterfactual;

  const rows = [
    { label: 'GPU Utilization Saturation', before: `${comp.gpu_utilization_pct.before.toFixed(1)}%`, after: `${comp.gpu_utilization_pct.after.toFixed(1)}%`, delta: `${comp.gpu_utilization_pct.delta.toFixed(1)}%` },
    { label: 'Transcoder Fetch Latency', before: `${comp.transcoder_latency_ms.before.toFixed(0)} ms`, after: `${comp.transcoder_latency_ms.after.toFixed(0)} ms`, delta: `${comp.transcoder_latency_ms.delta.toFixed(0)} ms` },
    { label: 'Operational Risk Score', before: comp.risk_score.before.toFixed(2), after: comp.risk_score.after.toFixed(2), delta: comp.risk_score.delta.toFixed(2) },
    { label: 'Playback Buffer Error Rate', before: `${comp.playback_error_rate_pct.before.toFixed(2)}%`, after: `${comp.playback_error_rate_pct.after.toFixed(2)}%`, delta: `${comp.playback_error_rate_pct.delta.toFixed(2)}%` },
  ];

  return (
    <GlassCard title="Independent Post-Prevention Telemetry Verification" variant="glow">
      <div className="space-y-4">
        {/* Verification Status Header */}
        <div className="flex items-center justify-between p-3 rounded-lg bg-emerald-950/20 border border-emerald-500/30">
          <div className="flex items-center gap-2.5">
            <CheckCircle className="h-5 w-5 text-emerald-400 shrink-0" />
            <div>
              <span className="text-xs font-mono font-bold text-emerald-300 block">
                Verification Verdict: {result.verdict}
              </span>
              <span className="text-[11px] text-gray-400 font-mono">
                Independently validated against Grafana MCP 30s &amp; 60s post-action
              </span>
            </div>
          </div>
          <span className="text-xs font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-bold">
            CONFIRMED
          </span>
        </div>

        {/* Telemetry Comparison Table */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-[11px] text-gray-400 font-mono pb-1 border-b border-white/5">
            <span>Operational Metric</span>
            <div className="flex gap-6">
              <span className="w-16 text-right">Pre-Action</span>
              <span className="w-16 text-right">Post-Action</span>
              <span className="w-16 text-right text-cyan-300">Delta</span>
            </div>
          </div>

          <div className="space-y-1.5">
            {rows.map((r, i) => (
              <div key={i} className="flex items-center justify-between text-xs font-mono bg-black/20 p-2 rounded">
                <span className="text-gray-300">{r.label}</span>
                <div className="flex gap-6">
                  <span className="w-16 text-right text-gray-400">{r.before}</span>
                  <span className="w-16 text-right text-emerald-400 font-medium">{r.after}</span>
                  <span className="w-16 text-right text-cyan-300 font-bold flex items-center justify-end gap-0.5">
                    <ArrowDownRight className="h-3 w-3" />
                    {r.delta}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Counterfactual Avoided Loss & Audience Protected */}
        <div className="grid grid-cols-3 gap-3 pt-1">
          <div className="bg-white/5 p-2.5 rounded-lg border border-white/5 text-center">
            <span className="text-[10px] font-mono text-gray-400 block uppercase">Risk Reduction</span>
            <span className="text-sm font-bold font-mono text-cyan-300">{count.projected_risk_reduction}</span>
          </div>

          <div className="bg-white/5 p-2.5 rounded-lg border border-white/5 text-center">
            <span className="text-[10px] font-mono text-gray-400 block uppercase">Audience Protected</span>
            <span className="text-sm font-bold font-mono text-emerald-400">
              {(count.estimated_viewers_protected / 1000000).toFixed(1)}M Viewers
            </span>
          </div>

          <div className="bg-white/5 p-2.5 rounded-lg border border-white/5 text-center">
            <span className="text-[10px] font-mono text-gray-400 block uppercase">Avoided Exposure</span>
            <span className="text-sm font-bold font-mono text-emerald-400">
              ${count.estimated_exposure_avoided.toLocaleString()}
            </span>
          </div>
        </div>
      </div>
    </GlassCard>
  );
};
