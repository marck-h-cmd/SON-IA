'use client';

import React, { useState } from 'react';

interface TabItem {
  label: string;
  id: string;
  content: React.ReactNode;
  badge?: number;
}

interface TabsProps {
  tabs: TabItem[];
  defaultActiveId?: string;
  onChange?: (activeId: string) => void;
}

export const Tabs: React.FC<TabsProps> = ({ tabs, defaultActiveId, onChange }) => {
  const [activeId, setActiveId] = useState(defaultActiveId || tabs[0]?.id);

  const handleTabChange = (id: string) => {
    setActiveId(id);
    onChange?.(id);
  };

  return (
    <div className="w-full">
      {/* Tab Headers */}
      <div className="border-b border-gray-200 dark:border-gray-700 flex gap-0">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => handleTabChange(tab.id)}
            className={`
              px-4 py-3 font-medium text-sm border-b-2 transition-colors whitespace-nowrap
              ${
                activeId === tab.id
                  ? 'text-blue-600 dark:text-blue-400 border-blue-600 dark:border-blue-400'
                  : 'text-gray-600 dark:text-gray-400 border-transparent hover:text-gray-800 dark:hover:text-gray-200'
              }
            `}
          >
            {tab.label}
            {tab.badge !== undefined && (
              <span className="ml-2 inline-block px-2 py-0.5 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 text-xs rounded-full font-bold">
                {tab.badge}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="mt-4">
        {tabs.find((tab) => tab.id === activeId)?.content}
      </div>
    </div>
  );
};

export default Tabs;
