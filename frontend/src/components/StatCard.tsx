import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  color?: 'amber' | 'emerald' | 'blue' | 'purple' | 'red';
  trend?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  color = 'amber',
  trend
}) => {
  const colorMap = {
    amber: {
      bg: 'bg-honey-500/10',
      border: 'border-honey-500/20',
      text: 'text-honey-400',
      glow: 'shadow-honey-500/5',
    },
    emerald: {
      bg: 'bg-emerald-500/10',
      border: 'border-emerald-500/20',
      text: 'text-emerald-400',
      glow: 'shadow-emerald-500/5',
    },
    blue: {
      bg: 'bg-blue-500/10',
      border: 'border-blue-500/20',
      text: 'text-blue-400',
      glow: 'shadow-blue-500/5',
    },
    purple: {
      bg: 'bg-purple-500/10',
      border: 'border-purple-500/20',
      text: 'text-purple-400',
      glow: 'shadow-purple-500/5',
    },
    red: {
      bg: 'bg-rose-500/10',
      border: 'border-rose-500/20',
      text: 'text-rose-400',
      glow: 'shadow-rose-500/5',
    },
  };

  const scheme = colorMap[color];

  return (
    <div className={`p-5 rounded-2xl bg-charcoal-900/80 border ${scheme.border} shadow-lg ${scheme.glow} backdrop-blur-sm transition-all hover:border-opacity-40`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-charcoal-400">
          {title}
        </span>
        <div className={`w-9 h-9 rounded-xl ${scheme.bg} flex items-center justify-center`}>
          <Icon className={`w-5 h-5 ${scheme.text}`} />
        </div>
      </div>
      <div className="mt-3 flex items-baseline space-x-2">
        <span className="text-3xl font-extrabold text-white font-mono tracking-tight">
          {value}
        </span>
        {trend && (
          <span className="text-xs font-medium text-emerald-400">
            {trend}
          </span>
        )}
      </div>
      {subtitle && (
        <p className="mt-1 text-xs text-charcoal-400">
          {subtitle}
        </p>
      )}
    </div>
  );
};
