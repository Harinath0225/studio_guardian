import React from 'react';
import { PredictionCard } from './PredictionCard';
import { RiskTrajectoryCard } from './RiskTrajectoryCard';
import { ContributingFactorsCard } from './ContributingFactorsCard';
import { PredictiveMemoryCard } from './PredictiveMemoryCard';
import { TechnicalEvidencePanel } from './TechnicalEvidencePanel';
import { Calculator } from 'lucide-react';

interface PredictViewProps {
  status: any;
  onOpenProvenance: () => void;
  onEvaluate?: () => void;
}

export const PredictView: React.FC<PredictViewProps> = ({
  status,
  onOpenProvenance,
  onEvaluate,
}) => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between bg-slate-900/60 p-4 rounded-xl border border-slate-800">
        <div>
          <h2 className="text-xl font-bold text-white tracking-wide">
            Predictive Horizon &amp; Risk Intelligence
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Continuous Grafana MCP leading signal detection across transcoders, queues, and regional manifests.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {onEvaluate && (
            <button
              onClick={onEvaluate}
              className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-slate-200 text-xs font-semibold tracking-wider transition"
            >
              Re-evaluate Risk
            </button>
          )}
          <button
            onClick={onOpenProvenance}
            className="flex items-center gap-2 px-3 py-1.5 bg-cyan-950/80 border border-cyan-700 hover:border-cyan-500 rounded-lg text-cyan-300 text-xs font-semibold tracking-wider transition"
          >
            <Calculator className="w-4 h-4" />
            Data Provenance
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <PredictionCard status={status} />
          <RiskTrajectoryCard status={status} />
          <ContributingFactorsCard contributors={status?.contributors || []} />
        </div>
        <div className="space-y-6">
          <TechnicalEvidencePanel />
          <PredictiveMemoryCard />
        </div>
      </div>
    </div>
  );
};