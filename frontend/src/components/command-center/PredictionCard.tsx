import React from 'react';
import { GlassCard } from '../common/GlassCard';
import { Clock, Cpu, Sparkles, AlertTriangle, CheckCircle } from 'lucide-react';
import { PredictiveStatus } from '../../types/prediction';

interface PredictionCardProps {
  status: PredictiveStatus;
  onAuthorizeProposal?: (proposalId: string) => void;
  onRejectProposal?: (proposalId: string) => void;
  isActionLoading?: boolean;
}

export const PredictionCard: React.FC<PredictionCardProps> = ({
  status,
  onAuthorizeProposal,
  onRejectProposal,
  isActionLoading = false,
}) => {
  const isElevated = (status.risk_score || 0) >= 0.60;
  const proposal = status.active_proposal;

  return (
    <GlassCard
      title="Predictive Causal Hypothesis • Vertex AI Agent Engine"
      variant={isElevated ? 'danger' : 'default'}
    >
      <div className="space-y-4">
        {/* Failure mode & Horizon header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-white/5 pb-3">
          <div className="flex items-start gap-2.5">
            {isElevated ? (
              <AlertTriangle className="h-5 w-5 text-amber-400 shrink-0 mt-0.5" />
            ) : (
              <CheckCircle className="h-5 w-5 text-emerald-400 shrink-0 mt-0.5" />
            )}
            <div>
              <h4 className="text-sm font-bold font-mono text-gray-100">
                {status.predicted_failure_mode || 'Nominal Broadcast Health'}
              </h4>
              <p className="text-xs text-gray-400 mt-0.5">
                Session: <span className="text-cyan-300 font-mono">{status.runtime_metadata?.session_id}</span> • Source: <span className="text-gray-300 font-mono">{status.runtime_metadata?.telemetry_source}</span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-black/40 border border-white/10 text-xs font-mono text-amber-300 self-start sm:self-auto">
            <Clock className="h-3.5 w-3.5 text-amber-400" />
            <span>Horizon: {status.estimated_window_minutes?.min ?? 5}–{status.estimated_window_minutes?.max ?? 15}m</span>
          </div>
        </div>

        {/* Causal hypothesis narrative */}
        <div className="space-y-2">
          <div className="flex items-center gap-1.5 text-xs text-gray-400 font-mono uppercase tracking-wider">
            <Sparkles className="h-3.5 w-3.5 text-cyan-400" />
            <span>Causal Failure Narrative</span>
          </div>
          <p className="text-xs text-gray-300 leading-relaxed bg-black/30 p-3 rounded-lg border border-white/5 font-sans">
            {status.failure_hypothesis || 'Observability signals across all regional transcoding clusters show healthy operational buffers. No emerging degradation signatures detected.'}
          </p>
        </div>

        {/* Reasoning summary */}
        {status.reasoning_summary && (
          <div className="bg-cyan-950/20 border border-cyan-500/20 p-2.5 rounded-lg text-xs text-cyan-200">
            <strong className="font-mono text-cyan-400 block mb-1">Operational SRE Assessment:</strong>
            {status.reasoning_summary}
          </div>
        )}

        {/* Active Prevention Proposal Briefing */}
        {proposal && (
          <div className="bg-black/50 p-3.5 rounded-lg border border-amber-500/30 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold text-amber-300 flex items-center gap-1.5">
                <Cpu className="h-4 w-4 text-amber-400" />
                Recommended Preventive Action: {proposal.action_type}
              </span>
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
                proposal.policy_verdict === 'AUTO_APPROVED'
                  ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
                  : 'bg-amber-500/20 text-amber-300 border-amber-500/30'
              }`}>
                {proposal.policy_verdict}
              </span>
            </div>

            <div className="grid grid-cols-3 gap-2 text-xs font-mono">
              <div className="bg-white/5 p-2 rounded">
                <span className="text-gray-400 block text-[10px]">Blast Radius</span>
                <span className="text-gray-200 font-bold">{proposal.blast_radius_pct}%</span>
              </div>
              <div className="bg-white/5 p-2 rounded">
                <span className="text-gray-400 block text-[10px]">Exp. Exposure</span>
                <span className="text-red-400 font-bold">${proposal.expected_loss_without_action?.toLocaleString()}</span>
              </div>
              <div className="bg-white/5 p-2 rounded">
                <span className="text-gray-400 block text-[10px]">Cost to Scale</span>
                <span className="text-emerald-400 font-bold">${proposal.cost_of_prevention?.toLocaleString()}</span>
              </div>
            </div>

            {proposal.requires_approval && (
              <div className="flex items-center gap-2 pt-1">
                <button
                  onClick={() => onAuthorizeProposal && onAuthorizeProposal(proposal.id)}
                  disabled={isActionLoading}
                  className="flex-1 py-1.5 px-3 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-mono text-xs font-bold transition-colors disabled:opacity-50"
                >
                  Authorize 2x Scaling
                </button>
                <button
                  onClick={() => onRejectProposal && onRejectProposal(proposal.id)}
                  disabled={isActionLoading}
                  className="py-1.5 px-3 rounded bg-white/5 hover:bg-white/10 text-gray-300 font-mono text-xs transition-colors disabled:opacity-50"
                >
                  Hold Action
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </GlassCard>
  );
};
