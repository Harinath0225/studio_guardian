import React from 'react';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'glow' | 'danger';
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
    default: 'glass-panel',
    glow: 'glass-panel-glow',
    danger: 'glass-panel-danger'
  }[variant];

  return (
    <div className={`rounded-xl p-5 transition-all duration-300 ${variantClass} ${className}`}>
      {title && (
        <div className="flex items-center justify-between pb-3 mb-4 border-b border-white/5">
          <h3 className="text-sm font-semibold tracking-wider text-gray-300 uppercase font-mono">
            {title}
          </h3>
          {headerAction && <div>{headerAction}</div>}
        </div>
      )}
      {children}
    </div>
  );
};
