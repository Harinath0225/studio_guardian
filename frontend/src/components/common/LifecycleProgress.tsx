import React from 'react';
import { Radio, Brain, ShieldCheck, Zap, CheckCircle2 } from 'lucide-react';

interface LifecycleProgressProps {
  activeWorkflowState?: string;
  className?: string;
}

interface StepDef {
  id: number;
  key: string;
  name: string;
  shortLabel: string;
  icon: React.ComponentType<{ className?: string }>;
}

const STEPS: StepDef[] = [
  { id: 1, key: 'DETECT', name: 'Detect', shortLabel: 'Telemetry Sweep', icon: Radio },
  { id: 2, key: 'PREDICT', name: 'Predict', shortLabel: 'Causal Risk Horizon', icon: Brain },
  { id: 3, key: 'DECIDE', name: 'Decide', shortLabel: 'Safety Director', icon: ShieldCheck },
  { id: 4, key: 'ACT', name: 'Act', shortLabel: 'Preemptive Mitigation', icon: Zap },
  { id: 5, key: 'VERIFY', name: 'Verify', shortLabel: 'SLO Confirmation', icon: CheckCircle2 },
];

export const LifecycleProgress: React.FC<LifecycleProgressProps> = ({
  activeWorkflowState = 'HEALTHY',
  className = '',
}) => {
  const normalized = (activeWorkflowState || 'HEALTHY').toUpperCase();

  // Determine current active step index (1-based)
  const getActiveStep = (): { current: number; isDegraded: boolean; isResolved: boolean } => {
    if (normalized === 'RESOLVED') {
      return { current: 5, isDegraded: false, isResolved: true };
    }
    if (normalized === 'VERIFYING') {
      return { current: 5, isDegraded: false, isResolved: false };
    }
    if (normalized === 'REMEDIATING' || normalized === 'DEGRADED') {
      return { current: 4, isDegraded: normalized === 'DEGRADED', isResolved: false };
    }
    if (normalized === 'WAITING_HUMAN_APPROVAL' || normalized === 'AWAITING_APPROVAL' || normalized === 'ESCALATED_HUMAN_TAKEOVER') {
      return { current: 3, isDegraded: normalized === 'ESCALATED_HUMAN_TAKEOVER', isResolved: false };
    }
    if (normalized === 'INVESTIGATING') {
      return { current: 2, isDegraded: false, isResolved: false };
    }
    // Default nominal state: Detect is actively monitoring
    return { current: 1, isDegraded: false, isResolved: false };
  };

  const { current, isDegraded, isResolved } = getActiveStep();

  return (
    <nav
      aria-label="Autonomous Incident Response Lifecycle"
      className={`glass-panel border border-white/10 rounded-xl px-4 py-2.5 shadow-lg ${className}`}
    >
      <div className="flex items-center justify-between gap-2 sm:gap-4 max-w-5xl mx-auto">
        {STEPS.map((step, idx) => {
          const Icon = step.icon;
          const isPassed = isResolved ? true : step.id < current;
          const isCurrent = !isResolved && step.id === current;

          let badgeColor = 'bg-slate-800 text-slate-400 border-white/5';
          let textColor = 'text-slate-400';
          let iconColor = 'text-slate-400';

          if (isPassed) {
            badgeColor = 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
            textColor = 'text-slate-200';
            iconColor = 'text-emerald-400';
          } else if (isCurrent) {
            if (isDegraded) {
              badgeColor = 'bg-red-500/20 text-red-300 border-red-500/40 animate-pulse';
              textColor = 'text-red-300 font-bold';
              iconColor = 'text-red-400';
            } else {
              badgeColor = 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40 shadow-md shadow-cyan-500/20 ring-1 ring-cyan-400/40';
              textColor = 'text-cyan-200 font-bold';
              iconColor = 'text-cyan-300';
            }
          }

          return (
            <React.Fragment key={step.id}>
              <div className="flex items-center gap-2 min-w-0">
                <div
                  className={`h-7 w-7 rounded-lg border flex items-center justify-center shrink-0 font-mono text-xs font-bold transition-all duration-300 ${badgeColor}`}
                >
                  <Icon className={`h-3.5 w-3.5 ${iconColor}`} />
                </div>
                <div className="hidden sm:flex flex-col min-w-0">
                  <div className="flex items-center gap-1.5 leading-none">
                    <span className="text-[10px] font-mono text-slate-400">0{step.id}</span>
                    <span className={`text-xs uppercase font-mono tracking-wider truncate ${textColor}`}>
                      {step.name}
                    </span>
                  </div>
                  <span className="text-[10px] font-sans text-slate-400 truncate mt-0.5">
                    {step.shortLabel}
                  </span>
                </div>
              </div>

              {/* Connecting line between steps */}
              {idx < STEPS.length - 1 && (
                <div className="flex-1 h-px bg-slate-800 relative hidden md:block">
                  <div
                    className={`h-full transition-all duration-500 ${
                      step.id < current || isResolved ? 'bg-emerald-500/50' : 'bg-transparent'
                    }`}
                  />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </nav>
  );
};
