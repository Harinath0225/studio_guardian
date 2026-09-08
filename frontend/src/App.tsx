import { useState, useEffect } from 'react';
import { Header } from './components/command-center/Header';
import { SystemTopology3D } from './components/canvas3d/SystemTopology3D';
import { TelemetryGrid } from './components/command-center/TelemetryGrid';
import { AutonomyDial } from './components/command-center/AutonomyDial';
import { SimulatorBar } from './components/simulator/SimulatorBar';
import { ReportDrawer } from './components/command-center/ReportDrawer';
import { SafetyModal } from './components/command-center/SafetyModal';
import { DegradedBanner } from './components/common/DegradedBanner';
import { PredictView } from './components/command-center/PredictView';
import { ProtectView } from './components/command-center/ProtectView';
import { RespondView } from './components/command-center/RespondView';
import { GameDayView } from './components/command-center/GameDayView';
import { DataProvenanceDrawer } from './components/command-center/DataProvenanceDrawer';
import { LiveObservabilityConsole } from './components/observability/LiveObservabilityConsole';
import { Flame } from 'lucide-react';
import { useEventStream } from './hooks/useEventStream';
import {
  fetchPredictiveStatus,
  evaluateOperationalRisk,
  authorizeProposal,
  rejectProposal,
} from './services/predictionApi';
import { DashboardMode, PredictiveStatus } from './types/prediction';

export type OperationalView = 'PREDICT' | 'PROTECT' | 'RESPOND' | 'GAME_DAY' | 'GRAFANA_STREAM';

const DEFAULT_PREDICTIVE_STATUS: PredictiveStatus = {
  state: 'HEALTHY',
  risk_score: 0.18,
  risk_level: 'LOW',
  confidence_score: 0.94,
  predicted_failure_mode: 'Nominal Operational State',
  estimated_window_minutes: { min: 10, max: 15 },
  contributors: [
    { name: 'gpu_pressure', label: 'GPU Utilization Saturation', raw_value: 65.0, normalized: 0.33, points: 8.25 },
    { name: 'queue_growth', label: 'Transcoder Queue Buildup', raw_value: 6.0, normalized: 0.02, points: 0.4 },
    { name: 'latency_pressure', label: 'Segment Fetch Latency', raw_value: 220.0, normalized: 0.20, points: 4.0 },
    { name: 'error_growth', label: 'Playback Buffer Degradation', raw_value: 0.41, normalized: 0.09, points: 1.35 },
    { name: 'viewer_growth', label: 'Audience Concurrency Surge', raw_value: 10800000, normalized: 0.58, points: 5.8 },
  ],
  failure_hypothesis: 'All leading operational signals across transcoders, queues, and regional proxies remain well within designated SLO bounds.',
  reasoning_summary: 'Continuous Grafana MCP sweep detects stable streaming pipelines.',
  runtime_metadata: {
    agent_engine: 'Vertex AI (gemini-2.5-flash)',
    active_agent: 'Predictive Risk Agent',
    session_id: 'session-pred-init',
    telemetry_source: 'LIVE_GRAFANA_MCP',
  },
  updated_at: new Date().toISOString(),
};

export function App() {
  const {
    telemetry,
    activeWorkflowState,
    timelineEvents,
    isConnected,
    predictiveStatus: ssePredStatus,
    liveLogs,
    clearLogs,
  } = useEventStream();
  const [dashboardMode, setDashboardMode] = useState<DashboardMode>('PREDICTIVE');
  const [predStatus, setPredStatus] = useState<PredictiveStatus>(DEFAULT_PREDICTIVE_STATUS);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [reportDrawerOpen, setReportDrawerOpen] = useState<boolean>(false);
  const [isSafetyModalOpen, setIsSafetyModalOpen] = useState<boolean>(false);
  const [activeIncidentId, setActiveIncidentId] = useState<string>('incident-live-01');
  const [currentView, setCurrentView] = useState<OperationalView>('PREDICT');
  const [provenanceDrawerOpen, setProvenanceDrawerOpen] = useState<boolean>(false);

  // Sync SSE predictive snapshot if received
  useEffect(() => {
    if (ssePredStatus) {
      setPredStatus(ssePredStatus);
    }
  }, [ssePredStatus]);

  // Initial fetch of predictive status
  useEffect(() => {
    fetchPredictiveStatus()
      .then((status) => setPredStatus(status))
      .catch((err) => console.log('Predictive status initial load:', err));
  }, []);

  // Seamless auto-switch to reactive mode if acute degradation occurs
  useEffect(() => {
    if (telemetry.status === 'DEGRADED' || activeWorkflowState === 'DEGRADED' || activeWorkflowState === 'INVESTIGATING') {
      setDashboardMode('REACTIVE');
      setCurrentView('RESPOND');
    }
  }, [telemetry.status, activeWorkflowState]);

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
        setDashboardMode('REACTIVE');
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
      const fresh = await evaluateOperationalRisk(true);
      setPredStatus(fresh);
      setDashboardMode('PREDICTIVE');
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

  const handleShiftRoute = async (cluster: string = 'transcoder-us-01') => {
    setActionLoading(true);
    try {
      await fetch('http://localhost:8000/api/v1/simulator/route', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_cluster: cluster, shift_pct: 100.0 })
      });
    } catch (e) {
      console.error('Route shift error:', e);
    } finally {
      setActionLoading(false);
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

  // Predictive handlers
  const handleEvaluate = async () => {
    setActionLoading(true);
    try {
      const updated = await evaluateOperationalRisk(true);
      setPredStatus(updated);
    } catch (err) {
      console.error('Failed to evaluate predictive risk:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleAuthorizeProposal = async (proposalId: string) => {
    setActionLoading(true);
    try {
      await authorizeProposal(proposalId);
      const fresh = await evaluateOperationalRisk(true);
      setPredStatus(fresh);
    } catch (err) {
      console.error('Failed to authorize proposal:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleRejectProposal = async (proposalId: string) => {
    setActionLoading(true);
    try {
      await rejectProposal(proposalId);
      const fresh = await evaluateOperationalRisk(true);
      setPredStatus(fresh);
    } catch (err) {
      console.error('Failed to reject proposal:', err);
    } finally {
      setActionLoading(false);
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

      {/* Global Command Center Header with Mode Switcher */}
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
        mode={dashboardMode}
        onModeChange={setDashboardMode}
      />

      {/* Main Dashboard Layout */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 space-y-6">
        {/* Top Section: 3D Spatial Mesh Core with Predictive Stress Visualization */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <SystemTopology3D
              status={activeWorkflowState}
              activeWeights={telemetry.routing_weights || {}}
              predictiveState={predStatus.state}
              riskScore={predStatus.risk_score}
            />
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

        {/* Four Operational Views Tab Navigation (Constitution 16, Plan §10) */}
        <div className="flex border-b border-slate-800 space-x-2 pt-2">
          <button
            onClick={() => setCurrentView('PREDICT')}
            className={`px-4 py-2 text-xs font-bold uppercase tracking-wider rounded-t-lg transition border-t border-x ${
              currentView === 'PREDICT'
                ? 'bg-slate-900 text-cyan-400 border-slate-700'
                : 'text-slate-400 border-transparent hover:text-slate-200'
            }`}
          >
            1. PREDICT (Risk &amp; Telemetry)
          </button>
          <button
            onClick={() => setCurrentView('PROTECT')}
            className={`px-4 py-2 text-xs font-bold uppercase tracking-wider rounded-t-lg transition border-t border-x ${
              currentView === 'PROTECT'
                ? 'bg-slate-900 text-emerald-400 border-slate-700'
                : 'text-slate-400 border-transparent hover:text-slate-200'
            }`}
          >
            2. PROTECT (Policy &amp; Scaling)
          </button>
          <button
            onClick={() => setCurrentView('RESPOND')}
            className={`px-4 py-2 text-xs font-bold uppercase tracking-wider rounded-t-lg transition border-t border-x ${
              currentView === 'RESPOND'
                ? 'bg-slate-900 text-amber-400 border-slate-700'
                : 'text-slate-400 border-transparent hover:text-slate-200'
            }`}
          >
            3. RESPOND (Incident Fallback)
          </button>
          <button
            onClick={() => setCurrentView('GAME_DAY')}
            className={`px-4 py-2 text-xs font-bold uppercase tracking-wider rounded-t-lg transition border-t border-x ${
              currentView === 'GAME_DAY'
                ? 'bg-slate-900 text-red-400 border-slate-700'
                : 'text-slate-400 border-transparent hover:text-slate-200'
            }`}
          >
            4. GAME DAY (Black Swan Chaos)
          </button>
          <button
            onClick={() => setCurrentView('GRAFANA_STREAM')}
            className={`px-4 py-2 text-xs font-bold uppercase tracking-wider rounded-t-lg transition border-t border-x flex items-center gap-1.5 ${
              currentView === 'GRAFANA_STREAM'
                ? 'bg-slate-900 text-orange-400 border-slate-700'
                : 'text-slate-400 border-transparent hover:text-slate-200'
            }`}
          >
            <Flame className="w-3.5 h-3.5 text-orange-400" />
            5. GRAFANA LIVE (Observability &amp; Logs)
          </button>
        </div>

        {/* Operational View Switcher */}
        {currentView === 'PREDICT' && (
          <PredictView
            status={predStatus}
            onOpenProvenance={() => setProvenanceDrawerOpen(true)}
            onEvaluate={handleEvaluate}
          />
        )}
        {currentView === 'PROTECT' && (
          <ProtectView
            status={predStatus}
            onAuthorizeProposal={handleAuthorizeProposal}
            onRejectProposal={handleRejectProposal}
            actionLoading={actionLoading}
          />
        )}
        {currentView === 'RESPOND' && (
          <RespondView
            telemetry={telemetry}
            activeWorkflowState={activeWorkflowState}
            timelineEvents={timelineEvents}
            activeIncidentId={activeIncidentId}
            onShiftRoute={handleShiftRoute}
          />
        )}
        {currentView === 'GAME_DAY' && (
          <GameDayView
            onScenarioTriggered={() => {
              fetchPredictiveStatus().then(setPredStatus);
            }}
          />
        )}
        {currentView === 'GRAFANA_STREAM' && (
          <LiveObservabilityConsole
            telemetry={telemetry}
            liveLogs={liveLogs}
            onClearLogs={clearLogs}
          />
        )}
      </main>

      {/* Footer connection status */}
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

      {/* Data Provenance Slide-over Drawer */}
      <DataProvenanceDrawer
        isOpen={provenanceDrawerOpen}
        onClose={() => setProvenanceDrawerOpen(false)}
        snapshotId={(predStatus as any)?.snapshot_id}
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
