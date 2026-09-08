export type PredictiveState =
  | 'HEALTHY'
  | 'WATCH'
  | 'ELEVATED_RISK'
  | 'HIGH_RISK'
  | 'IMMINENT_RISK'
  | 'PREVENTIVE_REMEDIATION'
  | 'VERIFYING'
  | 'PREVENTED'
  | 'ESCALATED';

export type DashboardMode = 'PREDICTIVE' | 'REACTIVE';

export interface SignalContributor {
  name: string;
  label: string;
  raw_value: number;
  normalized: number;
  points: number;
}

export interface FailureWindow {
  min: number;
  max: number;
}

export interface PreventionProposal {
  id: string;
  action_type: string;
  target_service: string;
  blast_radius_pct: number;
  expected_loss_without_action: number;
  cost_of_prevention: number;
  expected_avoided_exposure: number;
  policy_verdict: 'AUTO_EXECUTE' | 'AUTO_APPROVED' | 'REQUIRE_APPROVAL' | 'WAITING_HUMAN_APPROVAL' | 'REJECTED' | string;
  status: 'PENDING' | 'PENDING_APPROVAL' | 'DISPATCHED' | 'COMPLETED' | 'FAILED' | string;
  requires_approval: boolean;
}

export interface RuntimeMetadata {
  agent_engine: string;
  active_agent: string;
  session_id: string;
  telemetry_source: string;
}

export interface PredictiveStatus {
  state: PredictiveState;
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  confidence_score: number;
  predicted_failure_mode?: string;
  estimated_window_minutes?: FailureWindow;
  contributors: SignalContributor[];
  failure_hypothesis?: string;
  reasoning_summary?: string;
  active_proposal?: PreventionProposal;
  runtime_metadata: RuntimeMetadata;
  updated_at: string;
}

export interface MetricDelta {
  before: number;
  after: number;
  delta: number;
}

export interface TelemetryComparison {
  risk_score: MetricDelta;
  gpu_utilization_pct: MetricDelta;
  transcoder_latency_ms: MetricDelta;
  playback_error_rate_pct: MetricDelta;
}

export interface CounterfactualEstimate {
  projected_risk_reduction: string;
  estimated_exposure_avoided: number;
  estimated_viewers_protected: number;
}

export interface VerificationResult {
  action_id: string;
  verdict: 'PREVENTION_VERIFIED' | 'PREVENTION_FAILED';
  comparison: TelemetryComparison;
  counterfactual: CounterfactualEstimate;
  verified_at: string;
}

export interface AgentRuntimeTrace {
  trace_id: string;
  timestamp: number;
  runtime_origin: 'Vertex AI Agent Engine' | 'Grafana MCP' | 'Safety Policy' | 'FastAPI Core';
  tool_name: string;
  query: string;
  duration_ms: number;
  status: 'SUCCESS' | 'WARNING' | 'ERROR';
  sanitized_payload: Record<string, any>;
}
