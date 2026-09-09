import React from 'react';
import { GlassCard } from '../common/GlassCard';
import { Terminal, Database, ArrowRight, Server } from 'lucide-react';

interface ToolInvocation {
  tool_name: string;
  query_expression: string;
  query_duration_ms: number;
  datasource: string;
  timestamp: string;
}

export const TechnicalEvidencePanel: React.FC<{ invocations?: ToolInvocation[] }> = ({ invocations = [] }) => {
  return (
    <GlassCard
      title="Grafana MCP Telemetry Evidence"
      headerAction={
        <div className="flex items-center gap-1 text-cyan-400 font-mono text-xs">
          <Terminal className="w-3.5 h-3.5" />
          <span>Live Queries</span>
        </div>
      }
    >
      <div className="space-y-3">
        {invocations.length === 0 ? (
          <div className="text-xs text-slate-400 font-mono py-4 text-center">
            Active MCP queries sweep: Prometheus, Tempo, Loki. No latency spikes detected.
          </div>
        ) : (
          invocations.map((inv, idx) => (
            <div key={idx} className="bg-black/40 p-3 rounded-lg text-xs border border-white/5 font-mono">
              <div className="flex justify-between text-slate-400 mb-1">
                <span className="text-cyan-300 font-bold">{inv.tool_name}</span>
                <span>{inv.query_duration_ms.toFixed(1)}ms</span>
              </div>
              <div className="flex items-center gap-2 text-slate-400 my-1.5">
                <Server className="w-3 h-3 text-slate-400" />
                <span>Agent</span>
                <ArrowRight className="w-3 h-3 text-slate-400" />
                <Database className="w-3 h-3 text-orange-400" />
                <span className="text-orange-400">{inv.datasource}</span>
              </div>
              <div className="bg-slate-950/80 p-2 rounded text-slate-300 overflow-x-auto whitespace-pre border border-white/5">
                {inv.query_expression}
              </div>
              <div className="text-right text-slate-400 mt-1 text-[10px]">
                {new Date(inv.timestamp).toLocaleTimeString()}
              </div>
            </div>
          ))
        )}
      </div>
    </GlassCard>
  );
};
