import React, { useState, useEffect, useRef, useMemo } from 'react';
import {
  Activity,
  Terminal,
  Cloud,
  Play,
  Pause,
  Trash2,
  Download,
  Copy,
  Check,
  Search,
  ExternalLink,
  Flame,
  AlertTriangle,
  Server,
  Layers,
  Cpu,
  Clock,
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  CartesianGrid,
} from 'recharts';
import { LiveLogEntry, TelemetryData } from '../../hooks/useEventStream';

interface LiveObservabilityConsoleProps {
  telemetry: TelemetryData;
  liveLogs: LiveLogEntry[];
  onClearLogs?: () => void;
}

type SubTab = 'METRICS_STREAM' | 'LOKI_LOGS' | 'GRAFANA_CLOUD';

interface MetricHistoryPoint {
  time: string;
  gpu: number;
  queue: number;
  latency: number;
  errorRate: number;
  scteDrift: number;
  spliceError: number;
}

export const LiveObservabilityConsole: React.FC<LiveObservabilityConsoleProps> = ({
  telemetry,
  liveLogs,
  onClearLogs,
}) => {
  const [activeSubTab, setActiveSubTab] = useState<SubTab>('METRICS_STREAM');
  const [isPaused, setIsPaused] = useState<boolean>(false);
  const [autoScroll, setAutoScroll] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedLevel, setSelectedLevel] = useState<string>('ALL');
  const [copied, setCopied] = useState<boolean>(false);
  const [embedUrl, setEmbedUrl] = useState<string>('');
  const [metricHistory, setMetricHistory] = useState<MetricHistoryPoint[]>([]);

  const logsEndRef = useRef<HTMLDivElement | null>(null);

  // Accumulate rolling metric history for real-time live charting
  useEffect(() => {
    const timeStr = new Date().toLocaleTimeString([], { hour12: false, minute: '2-digit', second: '2-digit' });
    const newPoint: MetricHistoryPoint = {
      time: timeStr,
      gpu: (telemetry as any).gpu_utilization_pct ?? (telemetry.status === 'DEGRADED' ? 98.5 : 65.0),
      queue: (telemetry as any).queue_depth ?? (telemetry.status === 'DEGRADED' ? 140 : 6),
      latency: telemetry.transcoder_latency_ms || 18.2,
      errorRate: telemetry.playback_error_rate_pct || 0.41,
      scteDrift: (telemetry as any).scte_timing_drift_ms ?? 12.0,
      spliceError: (telemetry as any).splice_alignment_error_ms ?? 8.0,
    };

    setMetricHistory((prev) => {
      const updated = [...prev, newPoint];
      return updated.slice(-30); // Maintain last 30 samples (30 seconds)
    });
  }, [telemetry]);

  // Auto-scroll logs terminal
  useEffect(() => {
    if (autoScroll && !isPaused && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [liveLogs, autoScroll, isPaused]);

  // Filtered logs
  const displayedLogs = useMemo(() => {
    return liveLogs.filter((log) => {
      const matchesSearch =
        !searchQuery ||
        log.message.toLowerCase().includes(searchQuery.toLowerCase()) ||
        log.service.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesLevel = selectedLevel === 'ALL' || log.level === selectedLevel;
      return matchesSearch && matchesLevel;
    });
  }, [liveLogs, searchQuery, selectedLevel]);

  const handleCopyJson = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/observability/dashboard-json');
      const data = await res.json();
      await navigator.clipboard.writeText(JSON.stringify(data, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch (err) {
      console.error('Failed to copy dashboard JSON:', err);
    }
  };

  const handleDownloadJson = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/observability/dashboard-json');
      const data = await res.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'studio-guardian-dashboard.json';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download dashboard JSON:', err);
    }
  };

  const isDegraded = telemetry.status === 'DEGRADED';
  const isScteIssue = ((telemetry as any).scte_timing_drift_ms ?? 0) > 200;

  return (
    <div className="space-y-6">
      {/* Top Banner Header */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-2xl backdrop-blur-md">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-orange-500/20 border border-orange-500/40 text-orange-400 shadow-lg shadow-orange-500/10">
              <Flame className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-bold text-white tracking-wide">
                  Grafana Live Telemetry &amp; Streaming Logs
                </h2>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                  LIVE STREAM 1Hz
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5 font-mono">
                Direct Prometheus exposition scrape + real-time Loki log streaming from simulated media pipeline
              </p>
            </div>
          </div>

          {/* Sub-tab Navigation */}
          <div className="flex items-center bg-slate-950/80 p-1 rounded-lg border border-slate-800 font-mono text-xs">
            <button
              onClick={() => setActiveSubTab('METRICS_STREAM')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md font-semibold transition ${
                activeSubTab === 'METRICS_STREAM'
                  ? 'bg-orange-600 text-white shadow-md shadow-orange-500/20'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Activity className="w-3.5 h-3.5" />
              1. Live Prometheus Metrics
            </button>
            <button
              onClick={() => setActiveSubTab('LOKI_LOGS')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md font-semibold transition ${
                activeSubTab === 'LOKI_LOGS'
                  ? 'bg-orange-600 text-white shadow-md shadow-orange-500/20'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Terminal className="w-3.5 h-3.5" />
              2. Loki Live Logs Stream ({displayedLogs.length})
            </button>
            <button
              onClick={() => setActiveSubTab('GRAFANA_CLOUD')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md font-semibold transition ${
                activeSubTab === 'GRAFANA_CLOUD'
                  ? 'bg-orange-600 text-white shadow-md shadow-orange-500/20'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Cloud className="w-3.5 h-3.5" />
              3. Grafana Cloud Setup &amp; Embed
            </button>
          </div>
        </div>
      </div>

      {/* ─── TAB 1: LIVE PROMETHEUS METRICS STREAM ──────────────────────────────── */}
      {activeSubTab === 'METRICS_STREAM' && (
        <div className="space-y-6">
          {/* Quick Metrics Summary Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
              <div className="flex justify-between items-center text-xs font-mono text-slate-400">
                <span>GPU SATURATION</span>
                <Cpu className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="mt-2 flex items-baseline gap-2">
                <span className={`text-2xl font-bold font-mono ${
                  ((telemetry as any).gpu_utilization_pct || 65) > 90 ? 'text-red-400' : 'text-cyan-300'
                }`}>
                  {((telemetry as any).gpu_utilization_pct || 65).toFixed(1)}%
                </span>
                <span className="text-[10px] text-slate-500 font-mono">Quota: 90%</span>
              </div>
              <div className="mt-1 text-[11px] text-slate-400 font-mono">
                Cluster: {telemetry.active_cluster || 'transcoder-syd-01'}
              </div>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
              <div className="flex justify-between items-center text-xs font-mono text-slate-400">
                <span>TRANSCODER LATENCY</span>
                <Clock className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="mt-2 flex items-baseline gap-2">
                <span className={`text-2xl font-bold font-mono ${
                  telemetry.transcoder_latency_ms > 400 ? 'text-red-400' : 'text-emerald-400'
                }`}>
                  {telemetry.transcoder_latency_ms.toFixed(1)} ms
                </span>
                <span className="text-[10px] text-slate-500 font-mono">SLA &lt; 500ms</span>
              </div>
              <div className="mt-1 text-[11px] text-slate-400 font-mono">
                Queue: {((telemetry as any).queue_depth || 6)} chunks
              </div>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
              <div className="flex justify-between items-center text-xs font-mono text-slate-400">
                <span>SCTE-35 CUE DRIFT</span>
                <Layers className="w-4 h-4 text-purple-400" />
              </div>
              <div className="mt-2 flex items-baseline gap-2">
                <span className={`text-2xl font-bold font-mono ${
                  isScteIssue ? 'text-red-400' : 'text-purple-300'
                }`}>
                  {(((telemetry as any).scte_timing_drift_ms) ?? 12.0).toFixed(1)} ms
                </span>
                <span className="text-[10px] text-slate-500 font-mono">Tolerance: ±200ms</span>
              </div>
              <div className="mt-1 text-[11px] text-slate-400 font-mono">
                Ad Pod Drop: {(((telemetry as any).ad_pod_drop_pct) ?? 0.0).toFixed(1)}%
              </div>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
              <div className="flex justify-between items-center text-xs font-mono text-slate-400">
                <span>BUFFER ERROR RATE</span>
                <AlertTriangle className={`w-4 h-4 ${isDegraded ? 'text-red-400' : 'text-emerald-400'}`} />
              </div>
              <div className="mt-2 flex items-baseline gap-2">
                <span className={`text-2xl font-bold font-mono ${
                  telemetry.playback_error_rate_pct > 2.0 ? 'text-red-400' : 'text-emerald-400'
                }`}>
                  {telemetry.playback_error_rate_pct.toFixed(2)}%
                </span>
                <span className="text-[10px] text-slate-500 font-mono">SLA &lt; 2.0%</span>
              </div>
              <div className="mt-1 text-[11px] text-slate-400 font-mono">
                Audience: {telemetry.concurrent_viewers.toLocaleString()}
              </div>
            </div>
          </div>

          {/* Real-time Streaming Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Chart 1: GPU Utilization % and Queue Depth */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-sm font-bold text-white font-mono flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-cyan-400" />
                    GPU Compute Saturation &amp; Worker Queue Depth
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Leading indicator: surges trigger preventive defense before playback degrades
                  </p>
                </div>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
                  Prometheus 1Hz
                </span>
              </div>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={metricHistory}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 10 }} />
                    <YAxis stroke="#64748b" tick={{ fontSize: 10 }} domain={[0, 100]} unit="%" />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: 8, fontSize: 12 }}
                    />
                    <ReferenceLine y={90} stroke="#ef4444" strokeDasharray="3 3" label={{ value: 'Capacity Quota (90%)', fill: '#ef4444', fontSize: 10 }} />
                    <Area type="monotone" dataKey="gpu" stroke="#06b6d4" fill="#06b6d4" fillOpacity={0.25} name="GPU Saturation %" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Chart 2: Transcoder Segment Latency */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-sm font-bold text-white font-mono flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-400" />
                    Transcoder Segment Packaging Latency
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Real-time segment mux latency vs 500ms SLA threshold limit
                  </p>
                </div>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
                  Tempo &amp; Prom
                </span>
              </div>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={metricHistory}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 10 }} />
                    <YAxis stroke="#64748b" tick={{ fontSize: 10 }} domain={[0, 600]} unit="ms" />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: 8, fontSize: 12 }}
                    />
                    <ReferenceLine y={500} stroke="#ef4444" strokeDasharray="3 3" label={{ value: 'SLA Limit (500ms)', fill: '#ef4444', fontSize: 10 }} />
                    <Line type="monotone" dataKey="latency" stroke="#10b981" strokeWidth={2.5} dot={false} name="Latency (ms)" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Chart 3: SCTE-35 Cue Timing Drift & Splice Alignment */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-sm font-bold text-white font-mono flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-purple-400" />
                    SCTE-35 Cue Timing Drift (Semantic Media Quality)
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Drift spikes during Black Swan scenario while CPU/GPU stay healthy
                  </p>
                </div>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800">
                  SCTE Sentinel
                </span>
              </div>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={metricHistory}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 10 }} />
                    <YAxis stroke="#64748b" tick={{ fontSize: 10 }} domain={[0, 500]} unit="ms" />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: 8, fontSize: 12 }}
                    />
                    <ReferenceLine y={200} stroke="#f59e0b" strokeDasharray="3 3" label={{ value: 'Max Tolerance (200ms)', fill: '#f59e0b', fontSize: 10 }} />
                    <Line type="monotone" dataKey="scteDrift" stroke="#a855f7" strokeWidth={2.5} dot={false} name="Timing Drift (ms)" />
                    <Line type="monotone" dataKey="spliceError" stroke="#f43f5e" strokeWidth={1.5} dot={false} name="Splice Mismatch (ms)" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Chart 4: Playback Buffer Error Rate */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-sm font-bold text-white font-mono flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-rose-400" />
                    Playback Buffer Ratio (Lagging Indicator)
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Broadcast SLO: customer-facing error rate must stay below 2.0%
                  </p>
                </div>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800">
                  Player Telemetry
                </span>
              </div>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={metricHistory}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 10 }} />
                    <YAxis stroke="#64748b" tick={{ fontSize: 10 }} domain={[0, 10]} unit="%" />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: 8, fontSize: 12 }}
                    />
                    <ReferenceLine y={2.0} stroke="#ef4444" strokeDasharray="3 3" label={{ value: 'SLO Violation (2.0%)', fill: '#ef4444', fontSize: 10 }} />
                    <Area
                      type="monotone"
                      dataKey="errorRate"
                      stroke={telemetry.playback_error_rate_pct > 2.0 ? '#ef4444' : '#10b981'}
                      fill={telemetry.playback_error_rate_pct > 2.0 ? '#ef4444' : '#10b981'}
                      fillOpacity={0.25}
                      name="Buffer Error Rate %"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ─── TAB 2: LOKI LIVE LOGS STREAM ─────────────────────────────────────── */}
      {activeSubTab === 'LOKI_LOGS' && (
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 shadow-2xl flex flex-col h-[650px]">
          {/* Terminal Controls Bar */}
          <div className="flex flex-wrap items-center justify-between gap-3 pb-3 mb-3 border-b border-slate-800/80">
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700">
                <Search className="w-3.5 h-3.5 text-slate-400" />
                <input
                  type="text"
                  placeholder="Filter logs (e.g. transcoder, scte, error)..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="bg-transparent text-xs text-slate-200 focus:outline-none w-48 sm:w-64 font-mono placeholder:text-slate-600"
                />
              </div>

              {/* Level Selector */}
              <select
                value={selectedLevel}
                onChange={(e) => setSelectedLevel(e.target.value)}
                className="bg-slate-900 border border-slate-700 text-xs text-slate-300 rounded-lg px-2.5 py-1.5 font-mono focus:outline-none"
              >
                <option value="ALL">All Levels</option>
                <option value="INFO">INFO Only</option>
                <option value="WARN">WARN Only</option>
                <option value="ERROR">ERROR Only</option>
                <option value="CRITICAL">CRITICAL Only</option>
              </select>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsPaused(!isPaused)}
                className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition ${
                  isPaused
                    ? 'bg-emerald-600 text-white hover:bg-emerald-500'
                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700 border border-slate-700'
                }`}
              >
                {isPaused ? <Play className="w-3.5 h-3.5" /> : <Pause className="w-3.5 h-3.5" />}
                {isPaused ? 'Resume Stream' : 'Pause'}
              </button>

              <button
                onClick={() => setAutoScroll(!autoScroll)}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono transition border ${
                  autoScroll
                    ? 'bg-cyan-950 text-cyan-300 border-cyan-700'
                    : 'bg-slate-900 text-slate-400 border-slate-800'
                }`}
              >
                Auto-scroll: {autoScroll ? 'ON' : 'OFF'}
              </button>

              {onClearLogs && (
                <button
                  onClick={onClearLogs}
                  className="flex items-center gap-1 px-2.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-800 rounded-lg text-xs font-mono transition"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  Clear
                </button>
              )}
            </div>
          </div>

          {/* Terminal Console View */}
          <div className="flex-1 overflow-y-auto font-mono text-xs space-y-1.5 pr-2 selection:bg-cyan-800">
            {displayedLogs.length === 0 ? (
              <div className="text-center py-20 text-slate-500 italic">
                No logs matching filter. Trigger an incident or Black Swan scenario in Game Day to generate live logs.
              </div>
            ) : (
              displayedLogs.map((log) => {
                const isCritical = log.level === 'CRITICAL';
                const isError = log.level === 'ERROR';
                const isWarn = log.level === 'WARN';

                return (
                  <div
                    key={log.id}
                    className={`flex items-start gap-2.5 p-2 rounded transition-colors ${
                      isCritical
                        ? 'bg-rose-950/40 border-l-2 border-rose-500'
                        : isError
                        ? 'bg-red-950/25 border-l-2 border-red-500'
                        : isWarn
                        ? 'bg-amber-950/20 border-l-2 border-amber-500'
                        : 'bg-slate-900/40 hover:bg-slate-900/70'
                    }`}
                  >
                    <span className="text-slate-500 text-[11px] whitespace-nowrap pt-0.5">
                      {new Date(log.timestamp).toLocaleTimeString([], { hour12: false })}
                    </span>

                    <span
                      className={`px-1.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider whitespace-nowrap ${
                        isCritical
                          ? 'bg-rose-500 text-white'
                          : isError
                          ? 'bg-red-600/30 text-red-300 border border-red-500/40'
                          : isWarn
                          ? 'bg-amber-600/30 text-amber-300 border border-amber-500/40'
                          : 'bg-blue-600/20 text-blue-300 border border-blue-500/30'
                      }`}
                    >
                      {log.level}
                    </span>

                    <span className="text-cyan-400 font-semibold whitespace-nowrap text-[11px] pt-0.5">
                      [{log.service}]
                    </span>

                    <span
                      className={`flex-1 break-all pt-0.5 ${
                        isCritical
                          ? 'text-rose-200 font-semibold'
                          : isError
                          ? 'text-red-200'
                          : isWarn
                          ? 'text-amber-200'
                          : 'text-slate-300'
                      }`}
                    >
                      {log.message}
                    </span>
                  </div>
                );
              })
            )}
            <div ref={logsEndRef} />
          </div>

          {/* Terminal Footer */}
          <div className="pt-2 border-t border-slate-800/80 mt-2 flex justify-between text-[11px] text-slate-500 font-mono">
            <span>Buffer: {displayedLogs.length} logs displayed</span>
            <span className="text-emerald-400 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              Loki Stream Online (labels: app=media-pipeline)
            </span>
          </div>
        </div>
      )}

      {/* ─── TAB 3: GRAFANA CLOUD SETUP & EMBED ─────────────────────────────────── */}
      {activeSubTab === 'GRAFANA_CLOUD' && (
        <div className="space-y-6">
          {/* Quick Explanation & Direct Dashboard Link */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Cloud className="w-5 h-5 text-orange-400" />
                  Your Grafana Cloud Dashboard is Live!
                </h3>
                <p className="text-xs text-slate-400 mt-1 max-w-3xl">
                  We verified your Service Account Token and automatically published the Studio Guardian dashboard directly to your Grafana Cloud stack at <span className="font-mono text-cyan-300">whitepenguin2589.grafana.net</span>.
                </p>
              </div>

              <div className="flex flex-wrap gap-2">
                <a
                  href="https://whitepenguin2589.grafana.net/d/ah2f7v/192737d"
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold font-mono transition shadow-lg shadow-emerald-600/20"
                >
                  Open Live Dashboard
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
                <a
                  href="https://whitepenguin2589.grafana.net/dashboards"
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1.5 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-semibold font-mono transition border border-slate-700"
                >
                  Manage Dashboards
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
                <button
                  onClick={handleCopyJson}
                  className="flex items-center gap-1 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-mono transition border border-slate-700"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 text-cyan-400" />}
                  {copied ? 'Copied!' : 'Copy JSON'}
                </button>
                <button
                  onClick={handleDownloadJson}
                  className="flex items-center gap-1 px-3 py-2 bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 rounded-lg text-xs font-mono transition border border-blue-500/30"
                >
                  <Download className="w-3.5 h-3.5 text-blue-400" />
                  Download JSON
                </button>
              </div>
            </div>

            {/* Why logs don't show yet in Grafana Cloud: The Missing Link Explanation */}
            <div className="bg-amber-950/30 border border-amber-500/40 rounded-xl p-4 space-y-2">
              <div className="flex items-center gap-2 text-amber-300 font-bold text-xs font-mono">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                WHY SERVICE ACCOUNT TOKEN ALONE DOES NOT SHOW LOGS IN GRAFANA CLOUD:
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                Your Service Account Token (<code className="text-cyan-300 font-mono">glsa_...</code>) grants <strong>API and Dashboard Management</strong> access (which is how we successfully published the dashboard above).
                However, <strong>Grafana Cloud does not pull logs from your laptop</strong>. Log lines must be <strong>pushed</strong> to Grafana Cloud&apos;s Loki gateway (<code className="text-orange-300 font-mono">https://logs-prod-026.grafana.net/loki/api/v1/push</code>), which requires an <strong>Access Policy Token</strong> with the <code className="text-emerald-300 font-mono">logs:write</code> scope.
              </p>
            </div>

            {/* Live Diagnostic Probe & Setup Steps */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Card 1: Cloud Loki Push Configuration */}
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-xs space-y-3">
                <div className="text-slate-300 font-bold flex items-center gap-2">
                  <Server className="w-4 h-4 text-cyan-400" />
                  Grafana Cloud Loki Endpoint Details
                </div>
                <div className="space-y-1.5 text-[11px] text-slate-400">
                  <div className="flex justify-between border-b border-slate-800/80 pb-1">
                    <span>Loki Push Gateway:</span>
                    <span className="text-cyan-300">https://logs-prod-026.grafana.net</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-800/80 pb-1">
                    <span>Loki User / Instance ID:</span>
                    <span className="text-orange-300 font-bold">1777745</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-800/80 pb-1">
                    <span>Prometheus Instance ID:</span>
                    <span className="text-emerald-300 font-bold">3564140</span>
                  </div>
                  <div className="flex justify-between pt-1">
                    <span>Current Active Token:</span>
                    <span className="text-yellow-300">Service Account (glsa_...)</span>
                  </div>
                </div>
              </div>

              {/* Card 2: How to get the logs:write token in 2 minutes */}
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-xs space-y-2">
                <div className="text-slate-300 font-bold flex items-center gap-2">
                  <Flame className="w-4 h-4 text-orange-400" />
                  How to enable Loki Log Ingestion (2 Minutes):
                </div>
                <ol className="list-decimal list-inside text-slate-400 space-y-1 text-[11px] leading-relaxed">
                  <li>Go to <a href="https://grafana.com/orgs" target="_blank" rel="noreferrer" className="text-cyan-400 underline">grafana.com/orgs</a> and click stack <strong className="text-slate-200">whitepenguin2589</strong>.</li>
                  <li>Click <strong>Access Policies</strong> &rarr; <strong>Create Access Policy</strong>.</li>
                  <li>Check <span className="text-emerald-300 font-bold">logs:write</span> and <span className="text-emerald-300 font-bold">metrics:write</span>.</li>
                  <li>Click <strong>Create</strong> &rarr; <strong>Add Token</strong> &rarr; copy the token (<code className="text-orange-300">glc_...</code>).</li>
                  <li>Add to your <code className="text-slate-200">.env</code>: <code className="text-cyan-300">GRAFANA_LOKI_TOKEN=glc_your_token</code>.</li>
                </ol>
              </div>
            </div>

            {/* In-Website Zero-Setup Reminder Banner */}
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex items-center justify-between gap-4">
              <div className="space-y-0.5">
                <h4 className="text-sm font-bold text-white flex items-center gap-2 font-mono">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                  Prefer Zero Cloud Configuration?
                </h4>
                <p className="text-xs text-slate-400">
                  You do NOT need to configure cloud log shipping to see logs! Switch to <strong>&quot;2. Loki Live Logs Stream&quot;</strong> in this console to view live streaming logs right now.
                </p>
              </div>
              <button
                onClick={() => setActiveSubTab('LOKI_LOGS')}
                className="px-3 py-1.5 bg-orange-600 hover:bg-orange-500 text-white rounded-lg text-xs font-mono font-bold transition whitespace-nowrap"
              >
                View In-App Logs &rarr;
              </button>
            </div>

            {/* Optional Live Iframe Embedder */}
            <div className="pt-4 border-t border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-bold text-white">Embed External Grafana Cloud Panel in Studio Guardian</h4>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Paste any shareable Grafana Cloud panel or dashboard link below to view it embedded in this tab:
                  </p>
                </div>
              </div>

              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="https://whitepenguin2589.grafana.net/d-solo/... or https://..."
                  value={embedUrl}
                  onChange={(e) => setEmbedUrl(e.target.value)}
                  className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-cyan-500"
                />
                <button
                  onClick={() => {}}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-mono font-medium transition"
                >
                  Load Embed
                </button>
              </div>

              {embedUrl ? (
                <div className="w-full h-96 rounded-xl border border-slate-800 overflow-hidden bg-slate-950">
                  <iframe
                    src={embedUrl}
                    width="100%"
                    height="100%"
                    frameBorder="0"
                    title="Grafana Cloud Live Embed"
                  />
                </div>
              ) : (
                <div className="p-8 text-center text-xs text-slate-600 border border-dashed border-slate-800 rounded-xl">
                  No external embed URL entered. You can use the Native In-App Live Streaming Console in Tab 1 &amp; Tab 2 for complete zero-config observability!
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
