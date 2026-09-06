import { useState } from 'react';
import { Header } from './components/command-center/Header';
import { SceneCanvas } from './components/canvas3d/SceneCanvas';
import { TelemetryGrid } from './components/command-center/TelemetryGrid';
import { AgentTimeline } from './components/command-center/AgentTimeline';
import { RootCauseCard } from './components/command-center/RootCauseCard';
import { BusinessCard } from './components/command-center/BusinessCard';
import { AutonomyDial } from './components/command-center/AutonomyDial';
import { IncidentMemoryCard } from './components/command-center/IncidentMemoryCard';
import { SimulatorBar } from './components/simulator/SimulatorBar';
import { ReportDrawer } from './components/command-center/ReportDrawer';
import { SafetyModal } from './components/command-center/SafetyModal';
import { DegradedBanner } from './components/common/DegradedBanner';
import { useEventStream } from './hooks/useEventStream';

export function App() {
  const { telemetry, activeWorkflowState, timelineEvents, isConnected } = useEventStream();
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [reportDrawerOpen, setReportDrawerOpen] = useState<boolean>(false);
  const [isSafetyModalOpen, setIsSafetyModalOpen] = useState<boolean>(false);
  const [activeIncidentId, setActiveIncidentId] = useState<string>('incident-live-01');

  const isDegraded = telemetry.status === 'DEGRADED' || activeWorkflowState === 'DEGRADED' || activeWorkflowState === 'ESCALATED_HUMAN_TAKEOVER';
  const showSafetyModal = isSafetyModalOpen || activeWorkflowState === 'WAITING_HUMAN_APPROVAL';

  const handleTriggerIncident = async () => {
    setActionLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/v1/demo/incident', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario: 'india_vs_australia_final' })
      });
      if (res.ok) {
        const data = await res.json();
        if (data.incident_id) {
          setActiveIncidentId(data.incident_id);
        }
      }
    } catch (e) {
      console.error('Trigger incident error:', e);
    } finally {
      setActionLoading(false);
    }
  };

  const handleReset = async () => {
    setActionLoading(true);
    try {
      await fetch('http://localhost:8000/api/v1/demo/reset', { method: 'POST' });
    } catch (e) {
      console.error('Reset error:', e);
    } finally {
      setActionLoading(false);
    }
  };

  const handleForceFailure = async () => {
    setActionLoading(true);
    try {
      await fetch('http://localhost:8000/api/v1/demo/force-failure?enable=true', { method: 'POST' });
    } catch (e) {
      console.error('Force failure error:', e);
    } finally {
      setActionLoading(false);
    }
  };

  const handleEmergencyTakeover = async () => {
    try {
      await fetch('http://localhost:8000/api/v1/incidents/emergency-takeover', { method: 'POST' });
    } catch (e) {
      console.error('Emergency takeover error:', e);
    }
  };

  const handleApprove = async (id: string, notes?: string) => {
    try {
      await fetch(`http://localhost:8000/api/v1/incidents/${id}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approved: true, operator_notes: notes || 'Operator approved in Command Center' })
      });
    } catch (e) {
      console.error('Approval submission error:', e);
    } finally {
      setIsSafetyModalOpen(false);
    }
  };

  const handleReject = async (id: string, notes?: string) => {
    try {
      await fetch(`http://localhost:8000/api/v1/incidents/${id}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approved: false, operator_notes: notes || 'Operator rejected in Command Center' })
      });
    } catch (e) {
      console.error('Rejection submission error:', e);
    } finally {
      setIsSafetyModalOpen(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#060913] text-gray-100 flex flex-col font-sans selection:bg-blue-600 selection:text-white">
      {/* Degraded Stream / Offline Fallback Notice Banner */}
      <DegradedBanner
        grafanaConnected={true}
        geminiConnected={true}
        isOfflineMode={!isConnected}
      />

      {/* Global Command Center Header */}
      <Header
        eventTitle={telemetry.event_title}
        status={activeWorkflowState || telemetry.status}
        concurrentViewers={telemetry.concurrent_viewers}
        onTriggerIncident={handleTriggerIncident}
        onReset={handleReset}
        onForceFailure={handleForceFailure}
        onEmergencyTakeover={handleEmergencyTakeover}
        isDegraded={isDegraded}
        actionLoading={actionLoading}
      />

      {/* Main Dashboard Layout */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 space-y-6">
        {/* Top Section: 3D Spatial Mesh Core & Real-Time Telemetry Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <SceneCanvas status={activeWorkflowState} activeWeights={telemetry.routing_weights || {}} />
          </div>
          <div className="lg:col-span-2 flex flex-col justify-between">
            <TelemetryGrid
              playbackErrorRate={telemetry.playback_error_rate_pct}
              transcoderLatency={telemetry.transcoder_latency_ms}
              gpuAllocationFailure={telemetry.gpu_allocation_failure_pct}
            />
            <div className="mt-4">
              <AutonomyDial />
            </div>
          </div>
        </div>

        {/* Middle Section: Root Cause Correlation & Commercial Impact */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <RootCauseCard
            isDegraded={isDegraded}
            activeCluster={telemetry.active_cluster}
            recentDeployment={telemetry.recent_deployment}
          />
          <BusinessCard
            isDegraded={isDegraded}
            affectedViewers={telemetry.affected_viewers}
            totalViewers={telemetry.concurrent_viewers}
          />
        </div>

        {/* Bottom Section: Multi-Agent Hierarchy Timeline & Incident Memory */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <AgentTimeline
              currentState={activeWorkflowState}
              timelineEvents={timelineEvents}
            />
          </div>
          <div className="lg:col-span-1">
            <IncidentMemoryCard />
          </div>
        </div>
      </main>

      {/* Footer connection status & Post-Incident Report Center Trigger */}
      <footer className="border-t border-white/5 px-6 py-4 text-xs font-mono text-gray-500 flex flex-wrap justify-between items-center max-w-7xl mx-auto w-full gap-4 pb-20">
        <div className="flex items-center gap-4">
          <span>Google Cloud &amp; Grafana Labs Hackathon • Studio Guardian v1.0.0</span>
          <button
            onClick={() => setReportDrawerOpen(true)}
            className="px-2.5 py-1 rounded bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 border border-blue-500/30 transition-all font-semibold"
          >
            Open Post-Incident RCA Drawer
          </button>
        </div>
        <span className="flex items-center gap-1.5">
          <span className={`h-2 w-2 rounded-full ${isConnected ? 'bg-emerald-400' : 'bg-red-400'}`} />
          {isConnected ? 'SSE Live Stream Active (1 Hz)' : 'Reconnecting to SSE Stream...'}
        </span>
      </footer>

      {/* Sticky Floating Demo Simulator Bar */}
      <SimulatorBar
        onTriggerIncident={handleTriggerIncident}
        onReset={handleReset}
        onForceFailure={handleForceFailure}
        isDegraded={isDegraded}
        actionLoading={actionLoading}
      />

      {/* Post-Incident Report Drawer */}
      <ReportDrawer
        isOpen={reportDrawerOpen}
        onClose={() => setReportDrawerOpen(false)}
        incidentId={activeIncidentId}
      />

      {/* Human Operator Safety Approval Modal */}
      <SafetyModal
        isOpen={showSafetyModal}
        incidentId={activeIncidentId}
        actionType="TRAFFIC_SHIFT"
        targetComponent="transcoder-syd-01"
        blastRadiusPct={14.7}
        confidenceScore={0.92}
        policyReason="Automated execution paused: Operator authorization required for traffic rerouting during live broadcast final."
        onApprove={handleApprove}
        onReject={handleReject}
        onClose={() => setIsSafetyModalOpen(false)}
      />
    </div>
  );
}

export default App;
