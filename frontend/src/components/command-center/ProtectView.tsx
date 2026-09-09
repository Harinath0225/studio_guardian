import React from 'react';
import { Shield, Zap } from 'lucide-react';
import { PreventionEconomicsCard } from './PreventionEconomicsCard';
import { VerificationResultCard } from './VerificationResultCard';

interface ProtectViewProps {
  status: any;
  onAuthorizeProposal?: (proposalId: string) => void;
  onRejectProposal?: (proposalId: string) => void;
  actionLoading?: boolean;
}

export const ProtectView: React.FC<ProtectViewProps> = ({
  status,
  onAuthorizeProposal,
  actionLoading,
}) => {
  const proposal = status?.active_proposal;
  const isAutoApproved = proposal?.policy_verdict === 'AUTO_APPROVED' || (status?.risk_score ?? 0) >= 0.80;

  return (
    <div className="space-y-6">
      <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white tracking-wide">
            Automated Protection &amp; Policy Governance
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Safety Director policy evaluation for controlled capacity scaling and preventive remediation.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 ${
            isAutoApproved 
              ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-700' 
              : 'bg-amber-950/80 text-amber-300 border border-amber-700'
          }`}>
            <Shield className="w-3.5 h-3.5" />
            {isAutoApproved ? 'Policy: Auto-Execute Approved' : 'Policy: Operator Approval Required'}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Candidate Remediation Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-semibold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
                <Zap className="w-4 h-4" /> Active Candidate Action
              </span>
              <span className="text-xs font-mono bg-slate-800 text-slate-300 px-2 py-0.5 rounded">
                Allowlisted
              </span>
            </div>

            <h3 className="text-lg font-bold text-white mb-2 font-display">
              Transcoder Capacity Scaling (scale_transcoder_pool)
            </h3>
            <p className="text-sm text-slate-300 font-sans leading-relaxed mb-4 max-w-[70ch]">
              Proactively doubles transcoding worker slots (from 8 to 16 nodes) to shed impending queue buildup before packet drop begins.
            </p>

            <div className="grid grid-cols-2 gap-3 mb-4 text-xs font-mono">
              <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                <div className="text-slate-400">Target Subsystem</div>
                <div className="text-slate-200 font-semibold mt-0.5">transcoder-worker-pool</div>
              </div>
              <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                <div className="text-slate-400">Blast Radius Risk</div>
                <div className="text-emerald-400 font-semibold mt-0.5">0.0% (Isolated Scale)</div>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800 flex gap-3">
            <button
              onClick={() => onAuthorizeProposal && onAuthorizeProposal(proposal?.id || 'prop-scale')}
              disabled={actionLoading}
              className="flex-1 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs rounded-lg transition tracking-wide disabled:opacity-50"
            >
              {actionLoading ? 'Scaling Pool...' : 'Execute Capacity Scaling'}
            </button>
          </div>
        </div>

        {/* Counterfactual ROI Economics */}
        <PreventionEconomicsCard proposal={proposal} />
      </div>

      {/* Verification Results Panel */}
      <VerificationResultCard result={status?.last_verification} />
    </div>
  );
};