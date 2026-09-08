import React from 'react';
import { RootCauseCard } from './RootCauseCard';
import { BusinessCard } from './BusinessCard';
import { AgentTimeline } from './AgentTimeline';
import { AlertTriangle, ArrowRight } from 'lucide-react';

interface RespondViewProps {
  telemetry: any;
  activeWorkflowState: string;
  timelineEvents: any[];
  activeIncidentId: string;
  onShiftRoute?: (cluster: string) => void;
}

export const RespondView: React.FC<RespondViewProps> = ({
  telemetry,
  activeWorkflowState,
  timelineEvents,
  activeIncidentId,
  onShiftRoute,
}) => {
  return (
    <div className="space-y-6">
      <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white tracking-wide flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            Reactive Incident Response &amp; Root Cause
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Detect &rarr; Investigate &rarr; Remediate &rarr; Verify closed loop for active playback degradation.
          </p>
        </div>
        <div className="text-xs font-mono text-slate-400 bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700">
          Incident: <span className="text-white font-bold">{activeIncidentId}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <RootCauseCard
            isDegraded={telemetry?.status === 'DEGRADED'}
            activeCluster={telemetry?.active_cluster || 'transcoder-syd-01'}
            recentDeployment={telemetry?.recent_deployment}
          />
          <BusinessCard
            isDegraded={telemetry?.status === 'DEGRADED'}
            affectedViewers={telemetry?.affected_viewers || 0}
            totalViewers={telemetry?.concurrent_viewers || 12400000}
          />
        </div>
        <div className="space-y-6">
          {/* Traffic Shifting Panel */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <h3 className="text-xs font-semibold text-cyan-400 uppercase tracking-wider mb-3">
              Regional Traffic Divert Control
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Shift degraded AU/SG playback clusters to warm standby us-east cluster.
            </p>
            <button
              onClick={() => onShiftRoute && onShiftRoute('transcoder-us-01')}
              className="w-full py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs rounded-lg transition tracking-wide flex items-center justify-center gap-2"
            >
              <span>Divert 100% Traffic to Standby (transcoder-us-01)</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          <AgentTimeline
            currentState={activeWorkflowState}
            timelineEvents={timelineEvents}
          />
        </div>
      </div>
    </div>
  );
};