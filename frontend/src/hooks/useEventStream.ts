import { useState, useEffect, useRef } from 'react';

export interface TelemetryData {
  event_title: string;
  status: string;
  playback_error_rate_pct: number;
  transcoder_latency_ms: number;
  gpu_allocation_failure_pct: number;
  concurrent_viewers: number;
  affected_viewers: number;
  affected_regions: string[];
  active_cluster: string;
  routing_weights: Record<string, number>;
  recent_deployment?: string;
}

export interface LiveLogEntry {
  id: string;
  timestamp: string;
  level: 'INFO' | 'WARN' | 'ERROR' | 'CRITICAL';
  service: string;
  message: string;
}

export interface StateTransitionEvent {
  incident_id: string;
  from_state: string;
  to_state: string;
  timestamp: number;
}

export const useEventStream = (streamUrl: string = 'http://localhost:8000/api/v1/stream/events') => {
  const [telemetry, setTelemetry] = useState<TelemetryData>({
    event_title: 'India vs Australia Final',
    status: 'HEALTHY',
    playback_error_rate_pct: 0.41,
    transcoder_latency_ms: 18.2,
    gpu_allocation_failure_pct: 0.0,
    concurrent_viewers: 12400000,
    affected_viewers: 0,
    affected_regions: [],
    active_cluster: 'transcoder-syd-01',
    routing_weights: { 'transcoder-syd-01': 0.5, 'transcoder-sin-01': 0.5, 'transcoder-us-01': 0.0 }
  });

  const [activeWorkflowState, setActiveWorkflowState] = useState<string>('HEALTHY');
  const [timelineEvents, setTimelineEvents] = useState<any[]>([]);
  const [predictiveStatus, setPredictiveStatus] = useState<any | null>(null);
  const [liveLogs, setLiveLogs] = useState<LiveLogEntry[]>([]);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    let es: EventSource;

    const connect = () => {
      es = new EventSource(streamUrl);
      eventSourceRef.current = es;

      es.onopen = () => {
        setIsConnected(true);
      };

      es.onmessage = (e) => {
        try {
          const parsed = JSON.parse(e.data);
          if (parsed.type === 'TELEMETRY_HEARTBEAT') {
            setTelemetry(parsed.data);
            if (parsed.data.status) {
              setActiveWorkflowState((prev) => (prev === 'HEALTHY' || prev === 'DEGRADED' || prev === 'RESOLVED') ? parsed.data.status : prev);
            }
          } else if (parsed.type === 'STATE_TRANSITION') {
            setActiveWorkflowState(parsed.data.to_state);
            setTimelineEvents((prev) => [
              {
                id: Date.now().toString(),
                from: parsed.data.from_state,
                to: parsed.data.to_state,
                timestamp: parsed.data.timestamp || Date.now() / 1000
              },
              ...prev.slice(0, 19)
            ]);
          } else if (parsed.type === 'PREDICTIVE_SNAPSHOT') {
            setPredictiveStatus(parsed.data);
          } else if (parsed.type === 'REACTIVE_FALLBACK_TRIGGERED') {
            setActiveWorkflowState('INVESTIGATING');
            setTimelineEvents((prev) => [
              {
                id: Date.now().toString(),
                from: 'PREDICTIVE_WATCH',
                to: 'REACTIVE_INVESTIGATION',
                timestamp: parsed.data.timestamp || Date.now() / 1000,
                reason: parsed.data.reason,
              },
              ...prev.slice(0, 19)
            ]);
          } else if (parsed.type === 'LOKI_LOG_BATCH') {
            const incoming: LiveLogEntry[] = (parsed.data || []).map((l: any, i: number) => ({
              id: `${Date.now()}-${i}-${Math.random().toString(36).substr(2, 5)}`,
              timestamp: l.timestamp || new Date().toISOString(),
              level: l.level || 'INFO',
              service: l.service || 'media-pipeline',
              message: l.message || '',
            }));
            setLiveLogs((prev) => {
              const combined = [...incoming, ...prev];
              return combined.slice(0, 200); // Keep latest 200 log entries
            });
          } else if (parsed.type === 'LOKI_LOG_LINE') {
            const entry: LiveLogEntry = {
              id: `${Date.now()}-${Math.random().toString(36).substr(2, 5)}`,
              timestamp: parsed.data.timestamp || new Date().toISOString(),
              level: parsed.data.level || 'INFO',
              service: parsed.data.service || 'media-pipeline',
              message: parsed.data.message || '',
            };
            setLiveLogs((prev) => [entry, ...prev].slice(0, 200));
          }
        } catch (err) {
          console.error('Failed to parse SSE event payload:', err);
        }
      };


      es.onerror = () => {
        setIsConnected(false);
        es.close();
        setTimeout(connect, 3000); // Auto-reconnect after 3 seconds
      };
    };

    connect();

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, [streamUrl]);

  const clearLogs = () => setLiveLogs([]);

  return {
    telemetry,
    activeWorkflowState,
    timelineEvents,
    isConnected,
    predictiveStatus,
    setPredictiveStatus,
    liveLogs,
    clearLogs,
  };
};

