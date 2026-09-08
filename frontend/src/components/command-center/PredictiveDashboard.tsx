import React from 'react';
import { RiskTrajectoryCard } from './RiskTrajectoryCard';
import { PredictionCard } from './PredictionCard';
import { ContributingFactorsCard } from './ContributingFactorsCard';
import { PreventionEconomicsCard } from './PreventionEconomicsCard';
import { VerificationResultCard } from './VerificationResultCard';
import { PredictiveMemoryCard } from './PredictiveMemoryCard';
import { UnifiedRuntimeLedger } from './UnifiedRuntimeLedger';
import { PredictiveStatus } from '../../types/prediction';
import { Zap, AlertTriangle, ShieldCheck } from 'lucide-react';

interface PredictiveDashboardProps {
  predictiveStatus: PredictiveStatus;
  onEvaluate: () => void;
  onStepChange: (step: number) => void;
  onAuthorizeProposal: (proposalId: string) => void;
  onRejectProposal: (proposalId: string) => void;
  isLoading?: boolean;
}

export const PredictiveDashboard: React.FC<PredictiveDashboardProps> = ({
  predictiveStatus,
  onEvaluate,
  onStepChange,
  onAuthorizeProposal,
  onRejectProposal,
  isLoading = false,
}) => {
  const isPrevented = predictiveStatus.state === 'PREVENTED';

  return (
    <div className="space-y-6">
      {/* Top Demo Scenario Driver Bar */}
      <div className="glass-panel p-4 rounded-xl flex flex-wrap items-center justify-between gap-4 border border-cyan-500/20 bg-gradient-to-r from-cyan-950/20 via-black/40 to-blue-950/20">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
            <Zap className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold font-mono text-gray-100 uppercase tracking-wider flex items-center gap-2">
              Predictive Prevention Simulator
              <span className="text-[10px] font-normal px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                PREDICT → PREVENT → PROVE
              </span>
            </h3>
            <p className="text-xs text-gray-400 mt-0.5">
              Simulate progressive transcoder load surge and verify autonomous capacity scaling.
            </p>
          </div>
        </div>

        {/* 4-Step progression buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => onStepChange(1)}
            disabled={isLoading}
            className="px-3 py-1.5 rounded text-xs font-mono bg-white/5 hover:bg-white/10 text-gray-300 border border-white/10 transition-colors disabled:opacity-50"
            title="Step 1: Baseline Nominal"
          >
            Step 1: Nominal
          </button>
          <button
            onClick={() => onStepChange(2)}
            disabled={isLoading}
            className="px-3 py-1.5 rounded text-xs font-mono bg-yellow-500/10 hover:bg-yellow-500/20 text-yellow-300 border border-yellow-500/30 transition-colors disabled:opacity-50"
            title="Step 2: Queue Saturation"
          >
            Step 2: Watch
          </button>
          <button
            onClick={() => onStepChange(3)}
            disabled={isLoading}
            className="px-3 py-1.5 rounded text-xs font-mono bg-red-500/10 hover:bg-red-500/20 text-red-300 border border-red-500/30 transition-colors disabled:opacity-50 flex items-center gap-1.5"
            title="Step 3: Imminent Risk Saturation"
          >
            <AlertTriangle className="h-3 w-3" />
            Step 3: Surge
          </button>
          <button
            onClick={() => onStepChange(4)}
            disabled={isLoading}
            className="px-3 py-1.5 rounded text-xs font-mono bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 transition-colors disabled:opacity-50 flex items-center gap-1.5"
            title="Step 4: Autonomous Prevention Executed"
          >
            <ShieldCheck className="h-3 w-3" />
            Step 4: Prevented
          </button>
        </div>
      </div>

      {/* Primary 3-Card Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <RiskTrajectoryCard
          status={predictiveStatus}
          onForceEvaluate={onEvaluate}
          isLoading={isLoading}
        />
        <PredictionCard
          status={predictiveStatus}
          onAuthorizeProposal={onAuthorizeProposal}
          onRejectProposal={onRejectProposal}
          isActionLoading={isLoading}
        />
        <ContributingFactorsCard
          contributors={predictiveStatus.contributors}
        />
      </div>

      {/* Post-Prevention Verification Delta (Highlighted when Prevented) */}
      {isPrevented && (
        <VerificationResultCard />
      )}

      {/* Prevention Economics & Loss Trade-Off + Vertex AI Memory Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <PreventionEconomicsCard
          proposal={predictiveStatus.active_proposal}
        />
        <PredictiveMemoryCard />
      </div>

      {/* Unified Runtime Execution Ledger • Multi-Origin Audit Trail */}
      <UnifiedRuntimeLedger />
    </div>
  );
};


