import React, { useState } from 'react';
import { GlassCard } from '../common/GlassCard';
import { ChevronDown, ChevronRight, Copy, Check } from 'lucide-react';
import { AgentRuntimeTrace } from '../../types/prediction';

interface UnifiedRuntimeLedgerProps {
  traces?: AgentRuntimeTrace[];
}

const DEFAULT_TRACES: AgentRuntimeTrace[] = [
  {
    trace_id: 'trc-mcp-prom-01',
    timestamp: Date.now() - 45000,
    runtime_origin: 'Grafana MCP',
    tool_name: 'query_prometheus_metrics',
    query: "avg(media_transcode_gpu_utilization_pct{region='ap-south-1'})",
    duration_ms: 38.4,
    status: 'SUCCESS',
    sanitized_payload: { status: 'success', resultType: 'vector', value: [1725700000, '93.4'] },
  },
  {
    trace_id: 'trc-mcp-loki-02',
    timestamp: Date.now() - 42000,
    runtime_origin: 'Grafana MCP',
    tool_name: 'search_loki_logs',
    query: '{service="transcoder"} |= "queue"',
    duration_ms: 64.1,
    status: 'SUCCESS',
    sanitized_payload: { status: 'success', values: [['1725700000', 'WARN: worker queue threshold exceeded (depth=48)']] },
  },
  {
    trace_id: 'trc-vertex-gemini-03',
    timestamp: Date.now() - 38000,
    runtime_origin: 'Vertex AI Agent Engine',
    tool_name: 'PredictiveRiskAgent.execute_structured',
    query: 'Operational Telemetry Risk Assessment (gemini-3.6-flash)',
    duration_ms: 340.2,
    status: 'SUCCESS',
    sanitized_payload: {
      failure_mode: 'Transcoder Worker Pool Capacity Saturation',
      hypothesis: 'GPU saturation at 93.4% with queue depth accumulating at 48 chunks indicates imminent buffer starvation.',
      confidence: 0.94,
    },
  },
  {
    trace_id: 'trc-policy-gate-04',
    timestamp: Date.now() - 32000,
    runtime_origin: 'Safety Policy',
    tool_name: 'SafetyDirector.evaluate_predictive_proposal',
    query: 'Action: scale_transcoder_pool (blast_radius=15.0%, risk=0.87, confidence=0.94)',
    duration_ms: 2.1,
    status: 'SUCCESS',
    sanitized_payload: { decision: 'AUTO_EXECUTE', allowed: true, reason: 'Conforms to autonomous criteria' },
  },
  {
    trace_id: 'trc-remediation-dispatch-05',
    timestamp: Date.now() - 28000,
    runtime_origin: 'FastAPI Core',
    tool_name: 'RemediationAgent.execute_preventive_action',
    query: 'scale_transcoder_pool (scale_factor=2.0)',
    duration_ms: 12.8,
    status: 'SUCCESS',
    sanitized_payload: { status: 'COMPLETED', target: 'transcoder-worker-pool', previous_size: 8, new_size: 16 },
  },
  {
    trace_id: 'trc-verification-delta-06',
    timestamp: Date.now() - 15000,
    runtime_origin: 'Grafana MCP',
    tool_name: 'VerificationAgent.verify_prevention',
    query: 'query_prometheus_metrics 30s post-action delta',
    duration_ms: 45.3,
    status: 'SUCCESS',
    sanitized_payload: { delta_gpu: -32.2, delta_risk: -0.65, verdict: 'VERIFIED_SUCCESSFUL' },
  },
];

export const UnifiedRuntimeLedger: React.FC<UnifiedRuntimeLedgerProps> = ({
  traces = DEFAULT_TRACES,
}) => {
  const [filter, setFilter] = useState<string>('ALL');
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const filtered = traces.filter((t) => {
    if (filter === 'ALL') return true;
    if (filter === 'VERTEX') return t.runtime_origin === 'Vertex AI Agent Engine';
    if (filter === 'GRAFANA') return t.runtime_origin === 'Grafana MCP';
    if (filter === 'POLICY') return t.runtime_origin === 'Safety Policy';
    return true;
  });

  const getOriginBadge = (origin: string) => {
    if (origin === 'Vertex AI Agent Engine') {
      return { label: 'Vertex AI Agent Engine', badge: 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30' };
    }
    if (origin === 'Grafana MCP') {
      return { label: 'Grafana MCP', badge: 'bg-orange-500/10 text-orange-300 border-orange-500/30' };
    }
    if (origin === 'Safety Policy') {
      return { label: 'Safety Policy', badge: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30' };
    }
    return { label: origin, badge: 'bg-blue-500/10 text-blue-300 border-blue-500/30' };
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <GlassCard title="Unified Runtime Execution Ledger • Multi-Origin Audit Trail">
      <div className="space-y-4">
        {/* Filter Toolbar */}
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/5 pb-3">
          <div className="flex items-center gap-1.5 font-mono text-xs">
            <button
              onClick={() => setFilter('ALL')}
              className={`px-2.5 py-1 rounded transition-colors ${
                filter === 'ALL' ? 'bg-white/20 text-white font-bold' : 'text-gray-400 hover:text-gray-200'
              }`}
            >
              All Traces ({traces.length})
            </button>
            <button
              onClick={() => setFilter('VERTEX')}
              className={`px-2.5 py-1 rounded transition-colors ${
                filter === 'VERTEX' ? 'bg-cyan-500/20 text-cyan-300 font-bold border border-cyan-500/30' : 'text-gray-400 hover:text-gray-200'
              }`}
            >
              Vertex AI
            </button>
            <button
              onClick={() => setFilter('GRAFANA')}
              className={`px-2.5 py-1 rounded transition-colors ${
                filter === 'GRAFANA' ? 'bg-orange-500/20 text-orange-300 font-bold border border-orange-500/30' : 'text-gray-400 hover:text-gray-200'
              }`}
            >
              Grafana MCP
            </button>
            <button
              onClick={() => setFilter('POLICY')}
              className={`px-2.5 py-1 rounded transition-colors ${
                filter === 'POLICY' ? 'bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30' : 'text-gray-400 hover:text-gray-200'
              }`}
            >
              Safety Policy
            </button>
          </div>

          <span className="text-[11px] text-gray-500 font-mono">
            Full PromQL &amp; Vertex AI audit record
          </span>
        </div>

        {/* Chronological Traces List */}
        <div className="space-y-2">
          {filtered.map((t) => {
            const originInfo = getOriginBadge(t.runtime_origin);
            const isExpanded = expandedId === t.trace_id;

            return (
              <div
                key={t.trace_id}
                className="bg-black/30 border border-white/5 rounded-lg overflow-hidden font-mono transition-colors"
              >
                {/* Header line */}
                <div
                  onClick={() => setExpandedId(isExpanded ? null : t.trace_id)}
                  className="p-3 flex items-center justify-between gap-3 cursor-pointer hover:bg-white/5 text-xs"
                >
                  <div className="flex items-center gap-2.5">
                    {isExpanded ? (
                      <ChevronDown className="h-4 w-4 text-gray-400 shrink-0" />
                    ) : (
                      <ChevronRight className="h-4 w-4 text-gray-400 shrink-0" />
                    )}
                    <span className={`text-[10px] px-2 py-0.5 rounded border ${originInfo.badge}`}>
                      {originInfo.label}
                    </span>
                    <span className="font-semibold text-gray-200">{t.tool_name}</span>
                  </div>

                  <div className="flex items-center gap-3 text-[11px]">
                    <span className="text-gray-500 truncate max-w-[240px] hidden sm:inline" title={t.query}>
                      {t.query}
                    </span>
                    <span className="text-cyan-400">{t.duration_ms.toFixed(1)}ms</span>
                    <span className="text-emerald-400">●</span>
                  </div>
                </div>

                {/* Expandable Inspect Drawer */}
                {isExpanded && (
                  <div className="p-3 bg-black/60 border-t border-white/5 space-y-2.5 text-xs">
                    <div>
                      <div className="flex justify-between items-center text-[10px] text-gray-400 mb-1">
                        <span>Invoked Expression / Query:</span>
                        <button
                          onClick={() => handleCopy(t.trace_id, t.query)}
                          className="flex items-center gap-1 text-cyan-300 hover:text-cyan-200"
                        >
                          {copiedId === t.trace_id ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                          Copy
                        </button>
                      </div>
                      <div className="bg-black/80 p-2 rounded text-cyan-200 font-mono text-[11px] break-all border border-white/5">
                        {t.query}
                      </div>
                    </div>

                    <div>
                      <div className="text-[10px] text-gray-400 mb-1">Sanitized Execution Payload:</div>
                      <pre className="bg-black/80 p-2 rounded text-gray-300 font-mono text-[11px] overflow-x-auto border border-white/5 max-h-40">
                        {JSON.stringify(t.sanitized_payload, null, 2)}
                      </pre>
                    </div>

                    <div className="flex justify-between text-[10px] text-gray-500 pt-1">
                      <span>Trace ID: {t.trace_id}</span>
                      <span>Recorded: {new Date(t.timestamp).toLocaleTimeString()}</span>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </GlassCard>
  );
};
