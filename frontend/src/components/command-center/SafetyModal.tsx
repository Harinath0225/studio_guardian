import React, { useState } from 'react';
import { GlassCard } from '../common/GlassCard';
import { ShieldAlert, CheckCircle, XCircle } from 'lucide-react';

interface SafetyModalProps {
  isOpen: boolean;
  incidentId: string;
  actionType: string;
  targetComponent: string;
  blastRadiusPct: number;
  confidenceScore: number;
  policyReason: string;
  onApprove: (incidentId: string, notes?: string) => Promise<void>;
  onReject: (incidentId: string, notes?: string) => Promise<void>;
  onClose: () => void;
}

export const SafetyModal: React.FC<SafetyModalProps> = ({
  isOpen,
  incidentId,
  actionType,
  targetComponent,
  blastRadiusPct,
  confidenceScore,
  policyReason,
  onApprove,
  onReject,
  onClose
}) => {
  const [operatorNotes, setOperatorNotes] = useState<string>('');
  const [submitting, setSubmitting] = useState<boolean>(false);

  if (!isOpen) return null;

  const handleDecision = async (approved: boolean) => {
    setSubmitting(true);
    try {
      if (approved) {
        await onApprove(incidentId, operatorNotes);
      } else {
        await onReject(incidentId, operatorNotes);
      }
      onClose();
    } catch (err) {
      console.error('Failed to submit approval decision:', err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-md p-4 animate-fade-in">
      <div className="w-full max-w-lg">
        <GlassCard variant="danger" className="border border-amber-500/40 shadow-2xl shadow-amber-500/10">
          <div className="flex items-center gap-3 pb-3 border-b border-white/10">
            <div className="h-10 w-10 rounded-lg bg-amber-500/20 flex items-center justify-center text-amber-400">
              <ShieldAlert className="h-6 w-6" />
            </div>
            <div>
              <h3 className="text-base font-bold font-mono text-white">Operator Authorization Required</h3>
              <p className="text-xs text-amber-300/90 font-mono">Safety Director Gating Triggered</p>
            </div>
          </div>

          <div className="mt-4 space-y-3 font-mono text-xs">
            <div className="p-3 rounded-lg bg-black/40 border border-white/5 space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-400">Incident ID:</span>
                <span className="text-white font-semibold">{incidentId}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Proposed Action:</span>
                <span className="text-cyan-300 font-bold">{actionType}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Target Subsystem:</span>
                <span className="text-gray-200">{targetComponent}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Estimated Blast Radius:</span>
                <span className={`font-bold ${blastRadiusPct > 25 ? 'text-red-400' : 'text-emerald-400'}`}>
                  {blastRadiusPct.toFixed(1)}% {blastRadiusPct > 25 ? '(Exceeds 25% Threshold)' : ''}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Diagnostic Confidence:</span>
                <span className={`font-bold ${confidenceScore < 0.85 ? 'text-amber-400' : 'text-emerald-400'}`}>
                  {(confidenceScore * 100).toFixed(0)}% {confidenceScore < 0.85 ? '(< 85% Confidence)' : ''}
                </span>
              </div>
            </div>

            <p className="text-gray-300 text-[11px] leading-relaxed bg-amber-500/10 p-2.5 rounded border border-amber-500/20">
              <span className="font-bold text-amber-300">Policy Rationale: </span>
              {policyReason}
            </p>

            <div>
              <label className="block text-gray-400 text-[11px] mb-1">Operator Notes / Rationale (Optional):</label>
              <textarea
                value={operatorNotes}
                onChange={(e) => setOperatorNotes(e.target.value)}
                placeholder="e.g. Authorized emergency traffic shift to warm standby per SRE playbook."
                className="w-full h-16 bg-black/50 border border-white/10 rounded p-2 text-white placeholder-gray-600 focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          <div className="mt-5 pt-3 border-t border-white/10 flex justify-end gap-2">
            <button
              onClick={() => handleDecision(false)}
              disabled={submitting}
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-red-600/20 hover:bg-red-600/30 text-red-300 border border-red-500/30 text-xs font-mono font-semibold transition-all disabled:opacity-50"
            >
              <XCircle className="h-4 w-4" /> Reject Action
            </button>
            <button
              onClick={() => handleDecision(true)}
              disabled={submitting}
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-mono font-bold shadow-lg shadow-emerald-600/30 transition-all disabled:opacity-50"
            >
              <CheckCircle className="h-4 w-4" /> Authorize &amp; Execute
            </button>
          </div>
        </GlassCard>
      </div>
    </div>
  );
};
