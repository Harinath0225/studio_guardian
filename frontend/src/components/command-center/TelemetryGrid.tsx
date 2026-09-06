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

  const isCritical = playbackErrorRate >= 2.0;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      {/* Metric 1: Playback Error Rate */}
      <GlassCard variant={isCritical ? 'danger' : 'default'} className="p-4">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono text-gray-400 uppercase tracking-wider">Playback Buffer Error</span>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white/5 text-gray-400">Prometheus</span>
        </div>
        <div className="mt-2 flex items-baseline gap-2">
          <span className={`text-2xl font-bold font-mono ${isCritical ? 'text-red-400' : 'text-emerald-400'}`}>
            {playbackErrorRate.toFixed(2)}%
          </span>
          <span className="text-xs text-gray-500 font-mono">SLA Threshold &lt; 2.0%</span>
        </div>
        <div className="h-12 w-full mt-2">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={errorData}>
              <Area
                type="monotone"
                dataKey="val"
                stroke={isCritical ? '#EF4444' : '#10B981'}
                fill={isCritical ? '#EF4444' : '#10B981'}
                fillOpacity={0.2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </GlassCard>

      {/* Metric 2: Transcoder Latency */}
      <GlassCard variant={transcoderLatency > 100 ? 'danger' : 'default'} className="p-4">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono text-gray-400 uppercase tracking-wider">Transcode Latency</span>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white/5 text-gray-400">Tempo</span>
        </div>
        <div className="mt-2 flex items-baseline gap-2">
          <span className={`text-2xl font-bold font-mono ${transcoderLatency > 100 ? 'text-red-400' : 'text-emerald-400'}`}>
            {transcoderLatency.toFixed(1)} ms
          </span>
          <span className="text-xs text-gray-500 font-mono">Nominal: 18ms</span>
        </div>
        <p className="text-[11px] text-gray-400 font-mono mt-3">
          {transcoderLatency > 100 ? 'Severe stall detected on segment muxing' : 'Live encode pipelines nominal'}
        </p>
      </GlassCard>

      {/* Metric 3: GPU Allocation Failures */}
      <GlassCard variant={gpuAllocationFailure > 0 ? 'danger' : 'default'} className="p-4">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono text-gray-400 uppercase tracking-wider">GPU OOM / Segfault</span>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white/5 text-gray-400">Loki</span>
        </div>
        <div className="mt-2 flex items-baseline gap-2">
          <span className={`text-2xl font-bold font-mono ${gpuAllocationFailure > 0 ? 'text-red-400' : 'text-emerald-400'}`}>
            {gpuAllocationFailure.toFixed(1)}%
          </span>
          <span className="text-xs text-gray-500 font-mono">Cluster: ap-south-1</span>
        </div>
        <p className="text-[11px] text-gray-400 font-mono mt-3">
          {gpuAllocationFailure > 0 ? 'SIGSEGV SEI payload insertion failure' : 'Zero memory leaks detected'}
        </p>
      </GlassCard>
    </div>
  );
};
