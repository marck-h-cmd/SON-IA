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
        {!collapsed && (
          <div className="flex items-center gap-2">
            <span className="w-7 h-7 rounded-lg bg-[#00A9E0] flex items-center justify-center text-white font-black text-sm shadow-sm">
              M
            </span>
            <div>
              <h1 className="text-lg font-extrabold text-[#00A9E0] tracking-tight">SON-IA</h1>
              <p className="text-[10px] uppercase tracking-wider font-semibold text-gray-400 -mt-1">Movistar B2B</p>
            </div>
          </div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
          title={collapsed ? 'Expandir' : 'Contraer'}
        >
          {collapsed ? '→' : '←'}
        </button>
      </div>

      {/* Menu Items */}
      <nav className="flex-1 overflow-y-auto p-4 space-y-1.5">
        {menuItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`
              flex items-center gap-3 px-3.5 py-2.5 rounded-lg transition-all
              ${
                isActive(item.href)
                  ? 'bg-sky-50 dark:bg-sky-950/60 text-[#00A9E0] dark:text-[#38bdf8] font-bold border-r-4 border-[#00A9E0] shadow-sm'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800/80 hover:text-[#00A9E0]'
              }
            `}
            title={collapsed ? item.label : ''}
          >
            <span className="text-lg">{item.icon}</span>
            {!collapsed && <span className="text-sm">{item.label}</span>}
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
