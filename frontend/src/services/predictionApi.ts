import { PredictiveStatus, VerificationResult } from '../types/prediction';

const BASE_URL = 'http://localhost:8000/api/v1/prediction';

export async function fetchPredictiveStatus(): Promise<PredictiveStatus> {
  const res = await fetch(`${BASE_URL}/status`);
  if (!res.ok) {
    throw new Error(`Failed to fetch predictive status: ${res.statusText}`);
  }
  return res.json();
}

export async function evaluateOperationalRisk(forceRefresh = true): Promise<PredictiveStatus> {
  const res = await fetch(`${BASE_URL}/evaluate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ force_telemetry_refresh: forceRefresh }),
  });
  if (!res.ok) {
    throw new Error(`Failed to evaluate operational risk: ${res.statusText}`);
  }
  return res.json();
}

export async function authorizeProposal(
  proposalId: string,
  operatorId = 'sre-director-alpha',
  notes?: string
): Promise<{ action_id: string; status: string; message: string }> {
  const res = await fetch(`${BASE_URL}/proposals/${proposalId}/authorize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ operator_id: operatorId, notes }),
  });
  if (!res.ok) {
    throw new Error(`Failed to authorize proposal: ${res.statusText}`);
  }
  return res.json();
}

export async function rejectProposal(
  proposalId: string,
  operatorId = 'sre-operator',
  notes?: string
): Promise<{ proposal_id: string; status: string; message: string }> {
  const res = await fetch(`${BASE_URL}/proposals/${proposalId}/reject`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ operator_id: operatorId, notes }),
  });
  if (!res.ok) {
    throw new Error(`Failed to reject proposal: ${res.statusText}`);
  }
  return res.json();
}

export async function triggerDemoScenario(
  step: number,
  scenario = 'transcoder_saturation_surge'
): Promise<PredictiveStatus> {
  const res = await fetch(`${BASE_URL}/demo/scenario`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scenario, step }),
  });
  if (!res.ok) {
    throw new Error(`Failed to trigger demo scenario: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchPredictionHistory(limit = 15): Promise<any[]> {
  const res = await fetch(`${BASE_URL}/history?limit=${limit}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch history: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchVerificationDetails(actionId: string): Promise<VerificationResult> {
  const res = await fetch(`${BASE_URL}/verifications/${actionId}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch verification: ${res.statusText}`);
  }
  return res.json();
}
