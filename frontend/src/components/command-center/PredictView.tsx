import React from 'react';
import { PredictionCard } from './PredictionCard';
import { RiskTrajectoryCard } from './RiskTrajectoryCard';
import { ContributingFactorsCard } from './ContributingFactorsCard';
import { PredictiveMemoryCard } from './PredictiveMemoryCard';
import { MemoryCalloutCard } from './MemoryCalloutCard';
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
      {/* Sub-header Bar with Context & Key Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white tracking-wide font-display">
            Predictive Horizon &amp; Risk Intelligence
          </h2>
          <p className="text-xs text-slate-400 mt-0.5 font-sans">
            Continuous Grafana MCP leading signal detection across transcoders, queues, and regional manifests.
          </p>
        </div>
        <div className="flex items-center gap-2 self-start sm:self-auto">
          {onEvaluate && (
            <button
              onClick={onEvaluate}
              className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-slate-200 text-xs font-mono font-semibold tracking-wider transition-all"
            >
              Re-evaluate Risk
            </button>
          )}
          <button
            onClick={onOpenProvenance}
            className="flex items-center gap-2 px-3 py-1.5 bg-cyan-950/80 border border-cyan-700/80 hover:border-cyan-500 rounded-lg text-cyan-300 text-xs font-mono font-semibold tracking-wider transition-all shadow-sm"
          >
            <Calculator className="w-4 h-4" />
            Data Provenance
          </button>
        </div>
      </div>

      {/* Hero Element: Large Central Risk Gauge */}
      <RiskTrajectoryCard
        status={status}
        onForceEvaluate={onEvaluate}
        heroMode={true}
      />

      {/* Operational Deep Dive Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column (2 cols): Causal Hypothesis & Signal Breakdown */}
        <div className="lg:col-span-2 space-y-6">
          <PredictionCard status={status} />
          <ContributingFactorsCard contributors={status?.contributors || []} />
        </div>

        {/* Right Column (1 col): Storytelling differentiator + Technical Evidence */}
        <div className="space-y-6">
          {/* Differentiator: Vertex AI Top Match Callout */}
          <MemoryCalloutCard />
          <TechnicalEvidencePanel />
          <PredictiveMemoryCard />
        </div>
      </div>
    </div>
  );
};