import React from 'react';
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
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-4 overflow-hidden flex flex-col h-full text-slate-300">
      <div className="flex items-center gap-2 mb-4 text-cyan-400">
        <Terminal className="w-5 h-5" />
        <h3 className="font-semibold text-sm tracking-wider uppercase">Grafana MCP Telemetry Evidence</h3>
      </div>
      
      <div className="flex-1 overflow-y-auto space-y-3">
        {invocations.length === 0 ? (
          <div className="text-sm text-slate-500 italic">No recent MCP tool invocations.</div>
        ) : (
          invocations.map((inv, idx) => (
            <div key={idx} className="bg-slate-800 p-3 rounded text-xs border border-slate-700 font-mono">
              <div className="flex justify-between text-slate-400 mb-1">
                <span className="text-cyan-300 font-bold">{inv.tool_name}</span>
                <span>{inv.query_duration_ms.toFixed(1)}ms</span>
              </div>
              <div className="flex items-center gap-2 text-slate-500 mt-2 mb-2">
                <Server className="w-3 h-3" />
                <span>Agent</span>
                <ArrowRight className="w-3 h-3" />
                <Database className="w-3 h-3 text-orange-400" />
                <span className="text-orange-400">{inv.datasource}</span>
              </div>
              <div className="bg-slate-950 p-2 rounded text-slate-300 overflow-x-auto whitespace-pre">
                {inv.query_expression}
              </div>
              <div className="text-right text-slate-600 mt-1 text-[10px]">
                {new Date(inv.timestamp).toLocaleTimeString()}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
