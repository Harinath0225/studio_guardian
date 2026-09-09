import React from 'react';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'glow' | 'warning' | 'danger' | 'hero';
  title?: string;
  headerAction?: React.ReactNode;
}

export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  className = '',
  variant = 'default',
  title,
  headerAction
}) => {
  const variantClass = {
    default: 'glass-panel hover:border-white/15',
    glow: 'glass-panel-glow hover:border-cyan-500/40',
    warning: 'glass-panel-warning hover:border-amber-500/40',
    danger: 'glass-panel-danger hover:border-red-500/40',
    hero: 'glass-panel-hero hover:border-cyan-400/40 shadow-xl'
  }[variant];

  const paddingClass = variant === 'hero' ? 'p-6 sm:p-7' : 'p-5 sm:p-6';

  return (
    <div className={`rounded-xl ${paddingClass} transition-all duration-200 ${variantClass} ${className}`}>
      {title && (
        <div className="flex items-center justify-between pb-3 mb-4 border-b border-white/5">
          <h3 className="text-xs font-semibold tracking-wider text-slate-300 uppercase font-mono flex items-center gap-2">
            {title}
          </h3>
          {headerAction && <div>{headerAction}</div>}
        </div>
      )}
      {children}
    </div>
  );
};
