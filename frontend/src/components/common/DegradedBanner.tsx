import React from 'react';
import { AlertCircle, WifiOff } from 'lucide-react';

interface DegradedBannerProps {
  grafanaConnected?: boolean;
  geminiConnected?: boolean;
  isOfflineMode?: boolean;
}

export const DegradedBanner: React.FC<DegradedBannerProps> = ({
  grafanaConnected = true,
  geminiConnected = true,
  isOfflineMode = false
}) => {
  if (grafanaConnected && geminiConnected && !isOfflineMode) {
    return null;
  }

  return (
    <div className="w-full bg-amber-950/60 border-b border-amber-500/30 px-6 py-2.5 flex items-center justify-between text-xs font-mono text-amber-200">
      <div className="flex items-center gap-2">
        <AlertCircle className="h-4 w-4 text-amber-400 shrink-0" />
        <span>
          {isOfflineMode
            ? 'Running in High-Fidelity Deterministic Offline Mode (Mock MCP & Gemini local synthesizer enabled).'
            : 'External Partner Service Degraded: Autonomous fallback active for Grafana / Vertex AI.'}
        </span>
      </div>
      <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1">
        <WifiOff className="h-3 w-3" /> FALLBACK ACTIVE
      </span>
    </div>
  );
};
