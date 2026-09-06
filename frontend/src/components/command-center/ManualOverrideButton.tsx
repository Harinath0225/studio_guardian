import React, { useState } from 'react';
import { PowerOff, AlertTriangle } from 'lucide-react';

interface ManualOverrideButtonProps {
  onAbort: () => Promise<void>;
  isOverridden: boolean;
}

export const ManualOverrideButton: React.FC<ManualOverrideButtonProps> = ({ onAbort, isOverridden }) => {
  const [confirming, setConfirming] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);

  const handleTrigger = async () => {
    if (!confirming) {
      setConfirming(true);
      return;
    }

    setLoading(true);
    try {
      await onAbort();
      setConfirming(false);
    } catch (e) {
      console.error('Manual takeover error:', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center gap-2">
      {confirming ? (
        <div className="flex items-center gap-2 animate-pulse">
          <button
            onClick={handleTrigger}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-600 hover:bg-red-500 text-white text-xs font-mono font-bold shadow-lg shadow-red-600/30"
          >
            <AlertTriangle className="h-3.5 w-3.5" />
            CONFIRM TAKEOVER
          </button>
          <button
            onClick={() => setConfirming(false)}
            className="px-2.5 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-gray-300 text-xs font-mono"
          >
            Cancel
          </button>
        </div>
      ) : (
        <button
          onClick={() => setConfirming(true)}
          disabled={isOverridden}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-mono font-semibold transition-all ${
            isOverridden
              ? 'bg-red-600/10 border-red-500/30 text-red-400 cursor-not-allowed'
              : 'bg-white/5 hover:bg-red-600/20 border-white/10 text-gray-300 hover:text-red-300 hover:border-red-500/30'
          }`}
        >
          <PowerOff className="h-3.5 w-3.5 text-red-400" />
          {isOverridden ? 'MANUAL TAKEOVER ACTIVE' : 'EMERGENCY TAKEOVER'}
        </button>
      )}
    </div>
  );
};
