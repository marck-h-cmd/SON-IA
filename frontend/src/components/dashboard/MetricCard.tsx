import React from 'react';
import Card from '@/components/ui/Card';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: string;
  trend?: number; // Percentage change
  trendUp?: boolean;
  variant?: 'default' | 'success' | 'warning' | 'danger';
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  trend,
  trendUp = true,
  variant = 'default',
}) => {
  const variantClasses = {
    default: 'border-l-4 border-blue-500',
    success: 'border-l-4 border-green-500',
    warning: 'border-l-4 border-amber-500',
    danger: 'border-l-4 border-red-500',
  };

  return (
    <Card className={variantClasses[variant]}>
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">{title}</p>
          <h3 className="text-3xl font-bold text-gray-900 dark:text-white">{value}</h3>
          {subtitle && <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">{subtitle}</p>}
        </div>
        {icon && <span className="text-4xl">{icon}</span>}
      </div>

      {trend !== undefined && (
        <div className="mt-4 flex items-center gap-1">
          <span className={`text-sm font-semibold ${trendUp ? 'text-green-600' : 'text-red-600'}`}>
            {trendUp ? '↑' : '↓'} {Math.abs(trend)}%
          </span>
          <span className="text-xs text-gray-500 dark:text-gray-400">vs mes anterior</span>
        </div>
      )}
    </Card>
  );
};

export default MetricCard;
