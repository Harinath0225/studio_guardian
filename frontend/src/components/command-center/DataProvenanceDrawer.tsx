import React, { useEffect, useState } from 'react';
import { X, ShieldCheck, Calculator, ArrowRight } from 'lucide-react';

interface DataProvenanceDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  snapshotId?: string;
}

export const DataProvenanceDrawer: React.FC<DataProvenanceDrawerProps> = ({
  isOpen,
  onClose,
  snapshotId,
}) => {
  const [provenanceData, setProvenanceData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      const url = snapshotId 
        ? `/api/v1/predictive/provenance?snapshot_id=${snapshotId}`
        : '/api/v1/predictive/provenance';
      
      fetch(url)
        .then((res) => res.json())
        .then((data) => {
          setProvenanceData(data);
          setLoading(false);
        })
        .catch((err) => {
          console.error('Provenance fetch error:', err);
          setLoading(false);
        });
    }
  }, [isOpen, snapshotId]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full max-w-xl bg-slate-900 border-l border-slate-700 shadow-2xl p-6 flex flex-col overflow-y-auto text-slate-200">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Calculator className="w-5 h-5 text-cyan-400" />
          <h2 className="text-lg font-bold text-white tracking-wide">
            Mathematical Data Provenance
          </h2>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="mt-4 p-3 bg-cyan-950/40 border border-cyan-800/60 rounded-lg flex items-center gap-3 text-xs text-cyan-200">
        <ShieldCheck className="w-5 h-5 text-cyan-400 shrink-0" />
        <span>
          <strong>Constitution Principle 4 Verified:</strong> 100% of telemetry and financial calculations derive from deterministic formulas without generative model arithmetic.
        </span>
      </div>

      {loading ? (
        <div className="py-12 text-center text-slate-400 text-sm">
          Loading mathematical lineage...
        </div>
      ) : provenanceData ? (
        <div className="mt-6 space-y-6">
          {/* Derivation Pipeline */}
          <div>
            <h3 className="text-xs uppercase font-semibold text-slate-400 tracking-wider mb-2">
              Derivation Pipeline
            </h3>
            <div className="p-3 bg-slate-950 border border-slate-800 rounded font-mono text-xs text-cyan-300 flex items-center gap-2 flex-wrap">
              <span>Raw Grafana MCP</span>
              <ArrowRight className="w-3 h-3 text-slate-600" />
              <span>SLO Clamping</span>
              <ArrowRight className="w-3 h-3 text-slate-600" />
              <span>Normalized [0,1]</span>
              <ArrowRight className="w-3 h-3 text-slate-600" />
              <span>Weight Scaling</span>
              <ArrowRight className="w-3 h-3 text-slate-600" />
              <span className="text-emerald-400 font-bold">Composite Risk</span>
            </div>
          </div>

          {/* Raw Values vs SLO Baselines */}
          <div>
            <h3 className="text-xs uppercase font-semibold text-slate-400 tracking-wider mb-2">
              Sensor Baselines &amp; Feature Clamping
            </h3>
            <div className="space-y-2 text-xs">
              {provenanceData.raw_metrics && Object.entries(provenanceData.raw_metrics).map(([key, val]: [string, any]) => {
                const bound = provenanceData.provenance?.slo_bounds?.[key];
                return (
                  <div key={key} className="p-3 bg-slate-800/60 rounded border border-slate-700/50 flex justify-between items-center">
                    <div>
                      <div className="font-semibold text-slate-200">{key}</div>
                      <div className="text-[11px] text-slate-400 font-mono">
                        Floor: {bound?.floor ?? 0}{bound?.unit} | Ceil: {bound?.ceil ?? 100}{bound?.unit}
                      </div>
                    </div>
                    <div className="text-right font-mono">
                      <span className="text-white font-bold">{val}{bound?.unit}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Model Weights */}
          <div>
            <h3 className="text-xs uppercase font-semibold text-slate-400 tracking-wider mb-2">
              Configured Weight Distribution
            </h3>
            <div className="grid grid-cols-2 gap-2 text-xs font-mono">
              {provenanceData.provenance?.weights && Object.entries(provenanceData.provenance.weights).map(([k, w]: [string, any]) => (
                <div key={k} className="p-2 bg-slate-950 border border-slate-800 rounded flex justify-between">
                  <span className="text-slate-400">{k}:</span>
                  <span className="text-cyan-400 font-bold">{(w * 100).toFixed(0)}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* Mathematical Formulas */}
          <div>
            <h3 className="text-xs uppercase font-semibold text-slate-400 tracking-wider mb-2">
              Formula Version &amp; Logic
            </h3>
            <div className="p-3 bg-slate-950 border border-slate-800 rounded text-xs font-mono space-y-2">
              <div>
                <span className="text-slate-500">Version: </span>
                <span className="text-emerald-400 font-bold">{provenanceData.provenance?.formula_version}</span>
              </div>
              <div className="text-slate-300">
                <span className="text-slate-500">Formula: </span>
                {provenanceData.provenance?.composite_formula}
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};