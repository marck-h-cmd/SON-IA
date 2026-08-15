'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export const Sidebar: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();

  const menuItems = [
    {
      label: 'Dashboard',
      icon: '📊',
      href: '/dashboard-interno',
      matches: ['/dashboard-interno'],
    },
    {
      label: 'Facturación',
      icon: '📄',
      href: '/facturacion',
      matches: ['/facturacion'],
    },
    {
      label: 'Clientes',
      icon: '👥',
      href: '/clientes',
      matches: ['/clientes'],
    },
    {
      label: 'Cobranzas',
      icon: '💰',
      href: '/cobranzas',
      matches: ['/cobranzas'],
    },
    {
      label: 'Negociación',
      icon: '🤝',
      href: '/negociacion',
      matches: ['/negociacion'],
    },
    {
      label: 'Aprobaciones HITL',
      icon: '🛡️',
      href: '/aprobaciones',
      matches: ['/aprobaciones'],
    },
    {
      label: 'Auditoría',
      icon: '📋',
      href: '/auditoria',
      matches: ['/auditoria'],
    },
  ];

  const isActive = (href: string) => pathname.startsWith(href);

  return (
    <aside
      className={`
        bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800
        transition-all duration-300 flex flex-col h-screen
        ${collapsed ? 'w-20' : 'w-64'}
      `}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-800">
        {!collapsed && <h1 className="text-xl font-bold text-blue-600">SON-IA</h1>}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
          title={collapsed ? 'Expandir' : 'Contraer'}
        >
          {collapsed ? '→' : '←'}
        </button>
      </div>

      {/* Menu Items */}
      <nav className="flex-1 overflow-y-auto p-4 space-y-2">
        {menuItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`
              flex items-center gap-3 px-4 py-3 rounded-lg transition-colors
              ${
                isActive(item.href)
                  ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 font-semibold'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
              }
            `}
            title={collapsed ? item.label : ''}
          >
            <span className="text-xl">{item.icon}</span>
            {!collapsed && <span>{item.label}</span>}
          </Link>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-800">
        {!collapsed && (
          <p className="text-xs text-gray-500 dark:text-gray-400">
            SON-IA Dashboard v1.0
          </p>
        )}
      </div>
    </aside>
  );
};

export default Sidebar;
