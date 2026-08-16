import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'default', className = '' }) => {
  const variantClasses = {
    default: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
    success: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800',
    warning: 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 border border-amber-200 dark:border-amber-800',
    danger: 'bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300 border border-red-200 dark:border-red-800',
    info: 'bg-[#ebf7fc] text-[#0077a8] dark:bg-sky-950/70 dark:text-sky-300 border border-[#bae6fd] dark:border-sky-800',
  };

  return (
    <span className={`inline-block px-3 py-1 text-sm font-medium rounded-full ${variantClasses[variant]} ${className}`}>
      {children}
    </span>
  );
};

export default Badge;
