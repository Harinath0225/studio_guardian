import React from 'react';
import { Server, Activity, ShieldCheck, Database, Cpu } from 'lucide-react';

interface Fallback2DTopologyProps {
  status?: string;
  activeWeights?: Record<string, number>;
  riskScore?: number;
}

export const Fallback2DTopology: React.FC<Fallback2DTopologyProps> = ({
  status = 'HEALTHY',
  activeWeights = { 'transcoder-syd-01': 0.5, 'transcoder-sin-01': 0.5, 'transcoder-us-01': 0.0 },
  riskScore = 0.18,
}) => {
  const isHighRisk = (riskScore ?? 0) >= 0.80 || status === 'DEGRADED';
  const isWarning = (riskScore ?? 0) >= 0.60;

  return (
    <div className="w-full h-full min-h-[220px] bg-slate-950 border border-slate-800 rounded-xl p-4 flex flex-col justify-between text-slate-300">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-bold uppercase tracking-wider text-slate-200">
            System Topology (2D Operational View)
          </span>
        </div>
        <span className="text-[10px] font-mono text-slate-500">SVG Canvas Fallback</span>
      </div>

      <div className="grid grid-cols-3 gap-3 my-3 text-xs">
        {/* Node 1: Sydney Transcoder */}
        <div className={`p-3 rounded-lg border flex flex-col justify-between ${
          isHighRisk 
            ? 'bg-red-950/40 border-red-700/60 text-red-200' 
            : isWarning 
              ? 'bg-amber-950/40 border-amber-700/60 text-amber-200' 
              : 'bg-slate-900 border-slate-800 text-slate-200'
        }`}>
          <div className="flex items-center justify-between mb-1">
            <Server className="w-4 h-4 text-cyan-400" />
            <span className="text-[10px] font-mono font-bold">{(activeWeights['transcoder-syd-01'] ?? 0.5) * 100}%</span>
          </div>
          <div className="font-bold">transcoder-syd-01</div>
          <div className="text-[10px] text-slate-400 mt-1">Active Worker Pool</div>
        </div>

        {/* Node 2: Singapore Transcoder */}
        <div className="p-3 rounded-lg border bg-slate-900 border-slate-800 text-slate-200 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-1">
            <Server className="w-4 h-4 text-cyan-400" />
            <span className="text-[10px] font-mono font-bold">{(activeWeights['transcoder-sin-01'] ?? 0.5) * 100}%</span>
          </div>
          <div className="font-bold">transcoder-sin-01</div>
          <div className="text-[10px] text-slate-400 mt-1">Active Worker Pool</div>
        </div>

        {/* Node 3: US East Standby */}
        <div className={`p-3 rounded-lg border flex flex-col justify-between ${
          (activeWeights['transcoder-us-01'] ?? 0) > 0.1 
            ? 'bg-emerald-950/40 border-emerald-700/60 text-emerald-200' 
            : 'bg-slate-900/60 border-slate-800 text-slate-400'
        }`}>
          <div className="flex items-center justify-between mb-1">
            <Server className="w-4 h-4 text-emerald-400" />
            <span className="text-[10px] font-mono font-bold">{(activeWeights['transcoder-us-01'] ?? 0) * 100}%</span>
          </div>
          <div className="font-bold">transcoder-us-01</div>
          <div className="text-[10px] text-slate-400 mt-1">Standby Failover</div>
        </div>
      </div>

      <div className="flex items-center justify-between pt-2 border-t border-slate-800/80 text-[11px] font-mono text-slate-400">
        <div className="flex items-center gap-1.5">
          <Database className="w-3.5 h-3.5 text-orange-400" />
          <span>Grafana MCP (Live)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <Cpu className="w-3.5 h-3.5 text-blue-400" />
          <span>Vertex AI Agent Engine</span>
        </div>
        <div className="flex items-center gap-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>Safety Director</span>
        </div>
      </div>
    </div>
  );
};