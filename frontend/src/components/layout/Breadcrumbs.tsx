import React from 'react';
import Link from 'next/link';

interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
}

export const Breadcrumbs: React.FC<BreadcrumbsProps> = ({ items }) => {
  return (
    <nav className="flex items-center gap-2 text-sm" aria-label="Breadcrumb">
      {items.map((item, index) => (
        <div key={index} className="flex items-center gap-2">
          {item.href ? (
            <Link href={item.href} className="text-blue-600 dark:text-blue-400 hover:underline">
              {item.label}
            </Link>
          ) : (
            <span className="text-gray-600 dark:text-gray-400">{item.label}</span>
          )}
          {index < items.length - 1 && <span className="text-gray-400 dark:text-gray-600">/</span>}
        </div>
      ))}
    </nav>
  );
};

export default Breadcrumbs;
