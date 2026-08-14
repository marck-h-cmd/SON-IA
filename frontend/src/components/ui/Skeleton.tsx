import React from 'react';

interface SkeletonProps {
  className?: string;
  count?: number;
}

export const Skeleton: React.FC<SkeletonProps> = ({ className = '', count = 1 }) => {
  const items = Array.from({ length: count }, (_, i) => i);

  return (
    <>
      {items.map((i) => (
        <div key={i} className={`animate-pulse bg-gray-200 dark:bg-gray-700 rounded ${className}`} />
      ))}
    </>
  );
};

export default Skeleton;
