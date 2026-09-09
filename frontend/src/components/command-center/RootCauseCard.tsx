import React from 'react';
import { GlassCard } from '../common/GlassCard';
import { AlertOctagon, CheckCircle2, GitCommit, Layers } from 'lucide-react';

interface RootCauseCardProps {
  isDegraded: boolean;
  activeCluster: string;
  recentDeployment?: string;
}

export const RootCauseCard: React.FC<RootCauseCardProps> = ({
  isDegraded,
  activeCluster,
  recentDeployment
}) => {
  if (!isDegraded) {
    return (
      <GlassCard title="Root Cause Analysis • Gemini 2.5 Multi-Signal">
        <div className="flex items-center gap-3 py-4 text-emerald-400">
          <CheckCircle2 className="h-6 w-6" />
          <div>
            <h4 className="text-sm font-semibold font-mono text-slate-200">All Live Broadcast Signals Nominal</h4>
            <p className="text-sm text-slate-400 font-sans leading-relaxed mt-0.5 max-w-[70ch]">
              Observability Investigator continuously polling Grafana MCP datasources across {activeCluster}.
            </p>
          </div>
        </div>
      </GlassCard>
    );
  }

  return (
    <GlassCard variant="danger" title="Diagnosed Root Cause • Gemini 2.5 Multi-Signal">
      <div className="space-y-3">
        <div className="flex items-start gap-2.5">
          <AlertOctagon className="h-5 w-5 text-red-400 mt-0.5 shrink-0" />
          <div>
            <h4 className="text-sm font-bold font-mono text-red-300">
              Memory Corruption / SIGSEGV in transcoder-syd-01
            </h4>
            <p className="text-sm text-slate-300 font-sans leading-relaxed mt-1 max-w-[70ch]">
              Correlated Loki stacktraces with Tempo latency spikes following recent deployment <span className="font-mono text-cyan-300 font-semibold">{recentDeployment || 'v4.2.1-transcoder-patch'}</span>.
            </p>
          </div>
        </div>

        {/* Confidence score bar */}
        <div className="bg-black/30 p-2.5 rounded-lg border border-white/5 space-y-1.5">
          <div className="flex justify-between text-xs font-mono">
            <span className="text-gray-400">Diagnostic Confidence</span>
            <span className="text-emerald-400 font-bold">92%</span>
          </div>
          <div className="h-2 w-full rounded-full bg-gray-800 overflow-hidden">
            <div className="h-full bg-emerald-500 rounded-full w-[92%]" />
          </div>
        </div>

        {/* Evidence correlation tags */}
        <div className="flex flex-wrap gap-1.5 pt-1">
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-red-500/20 text-red-300 border border-red-500/30 flex items-center gap-1">
            <Layers className="h-3 w-3" /> Loki: libx265 SEI segfault
          </span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1">
            <GitCommit className="h-3 w-3" /> Deployed: 3m before incident
          </span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30">
            Tempo: 4850ms span stall
          </span>
        </div>
      </div>
    </GlassCard>
  );
};
