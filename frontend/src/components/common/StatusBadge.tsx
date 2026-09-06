import React from 'react';

export type StatusType = 'HEALTHY' | 'INVESTIGATING' | 'AWAITING_APPROVAL' | 'REMEDIATING' | 'VERIFYING' | 'RESOLVED' | 'ESCALATED' | 'DEGRADED';

interface StatusBadgeProps {
  status: StatusType | string;
  size?: 'sm' | 'md' | 'lg';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const normalized = status.toUpperCase();

  let colors = 'bg-blue-500/10 text-blue-400 border-blue-500/30';
  let pulse = false;

  if (normalized === 'HEALTHY' || normalized === 'RESOLVED') {
    colors = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
  } else if (normalized === 'DEGRADED' || normalized === 'ESCALATED' || normalized === 'CRITICAL') {
    colors = 'bg-red-500/10 text-red-400 border-red-500/30 animate-pulse';
    pulse = true;
  } else if (normalized === 'AWAITING_APPROVAL' || normalized === 'WAITING_HUMAN_APPROVAL') {
    colors = 'bg-amber-500/10 text-amber-400 border-amber-500/30 animate-pulse';
    pulse = true;
  } else if (normalized === 'INVESTIGATING' || normalized === 'REMEDIATING' || normalized === 'VERIFYING') {
    colors = 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30';
    pulse = true;
  }

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
    lg: 'text-sm px-3.5 py-1.5 font-semibold'
  }[size];

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border font-mono uppercase tracking-wider ${sizeClasses} ${colors}`}>
      {pulse && <span className="h-1.5 w-1.5 rounded-full bg-current animate-ping" />}
      {!pulse && <span className="h-1.5 w-1.5 rounded-full bg-current" />}
      {status.replace(/_/g, ' ')}
    </span>
  );
};
