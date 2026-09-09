import React from 'react';
import { GlassCard } from '../common/GlassCard';
import { AreaChart, Area, ResponsiveContainer } from 'recharts';

interface TelemetryGridProps {
  playbackErrorRate: number;
  transcoderLatency: number;
  gpuAllocationFailure: number;
}

export const TelemetryGrid: React.FC<TelemetryGridProps> = ({
  playbackErrorRate,
  transcoderLatency,
  gpuAllocationFailure
}) => {
  // Generate simple dynamic sparkline points based on live value
  const errorData = [
    { time: '-20s', val: 0.4 },
    { time: '-15s', val: 0.42 },
    { time: '-10s', val: playbackErrorRate > 2.0 ? 3.5 : 0.41 },
    { time: '-5s', val: playbackErrorRate > 2.0 ? 6.8 : 0.39 },
    { time: 'now', val: playbackErrorRate }
  ];

  // Status checks per metric
  const getPlaybackStatus = () => {
    if (playbackErrorRate >= 2.0) return { variant: 'danger' as const, textColor: 'text-red-400', dot: 'bg-red-400 animate-pulse', stroke: '#EF4444', label: 'Breaching SLA (>2.0%)' };
    if (playbackErrorRate >= 1.0) return { variant: 'warning' as const, textColor: 'text-amber-400', dot: 'bg-amber-400', stroke: '#F59E0B', label: 'Elevated Error Rate' };
    return { variant: 'default' as const, textColor: 'text-slate-100', dot: 'bg-emerald-400', stroke: '#38BDF8', label: 'SLA Threshold < 2.0%' };
  };

  const getLatencyStatus = () => {
    if (transcoderLatency > 100) return { variant: 'danger' as const, textColor: 'text-red-400', dot: 'bg-red-400 animate-pulse', label: 'Severe stall on segment muxing' };
    if (transcoderLatency > 50) return { variant: 'warning' as const, textColor: 'text-amber-400', dot: 'bg-amber-400', label: 'Latency drift approaching threshold' };
    return { variant: 'default' as const, textColor: 'text-slate-100', dot: 'bg-emerald-400', label: 'Live encode pipelines nominal (18ms)' };
  };

  const getGpuStatus = () => {
    if (gpuAllocationFailure > 1.0) return { variant: 'danger' as const, textColor: 'text-red-400', dot: 'bg-red-400 animate-pulse', label: 'SIGSEGV SEI payload insertion failure' };
    if (gpuAllocationFailure > 0) return { variant: 'warning' as const, textColor: 'text-amber-400', dot: 'bg-amber-400', label: 'Intermittent allocation retry observed' };
    return { variant: 'default' as const, textColor: 'text-slate-100', dot: 'bg-emerald-400', label: 'Zero memory leaks detected' };
  };

  const pbStatus = getPlaybackStatus();
  const latStatus = getLatencyStatus();
  const gpuStatus = getGpuStatus();

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      {/* Metric 1: Playback Error Rate */}
      <GlassCard variant={pbStatus.variant}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className={`h-2 w-2 rounded-full ${pbStatus.dot}`} />
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">Playback Buffer</span>
          </div>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white/5 text-slate-400 border border-white/5">Prometheus</span>
        </div>
        <div className="mt-2.5 flex items-baseline gap-2">
          <span className={`text-2xl font-bold font-mono ${pbStatus.textColor}`}>
            {playbackErrorRate.toFixed(2)}%
          </span>
          <span className="text-xs text-slate-400 font-mono">{pbStatus.label}</span>
        </div>
        <div className="h-10 w-full mt-2">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={errorData}>
              <Area
                type="monotone"
                dataKey="val"
                stroke={pbStatus.stroke}
                fill={pbStatus.stroke}
                fillOpacity={0.15}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </GlassCard>

      {/* Metric 2: Transcoder Latency */}
      <GlassCard variant={latStatus.variant}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className={`h-2 w-2 rounded-full ${latStatus.dot}`} />
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">Transcode Latency</span>
          </div>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white/5 text-slate-400 border border-white/5">Tempo</span>
        </div>
        <div className="mt-2.5 flex items-baseline gap-2">
          <span className={`text-2xl font-bold font-mono ${latStatus.textColor}`}>
            {transcoderLatency.toFixed(1)} ms
          </span>
          <span className="text-xs text-slate-400 font-mono">Target: &lt; 35ms</span>
        </div>
        <p className="text-[11px] text-slate-400 font-mono mt-3 leading-relaxed">
          {latStatus.label}
        </p>
      </GlassCard>

      {/* Metric 3: GPU Allocation Failures */}
      <GlassCard variant={gpuStatus.variant}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className={`h-2 w-2 rounded-full ${gpuStatus.dot}`} />
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">GPU Allocation</span>
          </div>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white/5 text-slate-400 border border-white/5">Loki</span>
        </div>
        <div className="mt-2.5 flex items-baseline gap-2">
          <span className={`text-2xl font-bold font-mono ${gpuStatus.textColor}`}>
            {gpuAllocationFailure.toFixed(1)}%
          </span>
          <span className="text-xs text-slate-400 font-mono">Cluster: ap-south-1</span>
        </div>
        <p className="text-[11px] text-slate-400 font-mono mt-3 leading-relaxed">
          {gpuStatus.label}
        </p>
      </GlassCard>
    </div>
  );
};
