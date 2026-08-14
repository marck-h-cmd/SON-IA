'use client';

import React, { useEffect, useState } from 'react';
import Card from '@/components/ui/Card';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import Table from '@/components/ui/Table';
import Modal from '@/components/ui/Modal';
import Breadcrumbs from '@/components/layout/Breadcrumbs';
import Skeleton from '@/components/ui/Skeleton';
import { auditService } from '@/services/auditService';
import { formatDateTime } from '@/utils/formatting';
import type { LogAuditoria, ListPaginada } from '@/types/api';

export default function AuditPage() {
  const [logs, setLogs] = useState<LogAuditoria[]>([]);
  const [selectedLog, setSelectedLog] = useState<LogAuditoria | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  const [filters, setFilters] = useState({
    skip: 0,
    limit: 10,
    tipoAccion: '',
    fechaDesde: '',
    fechaHasta: '',
  });

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const result = await auditService.getLogs(
        filters.skip,
        filters.limit,
        filters.tipoAccion || undefined,
        undefined,
        filters.fechaDesde || undefined,
        filters.fechaHasta || undefined
      );
      setLogs(result.items);
      setTotal(result.total);
    } catch (err) {
      console.error('Error fetching audit logs:', err);
      setError('Error cargando registros de auditoría');
    } finally {
      setLoading(false);
    }
  };

  const handleExportLogs = async () => {
    try {
      const blob = await auditService.exportarLogs(
        filters.tipoAccion || undefined,
        undefined,
        filters.fechaDesde || undefined,
        filters.fechaHasta || undefined
      );
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `auditoria_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Error exporting logs:', err);
      setError('Error exportando registros');
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [filters.skip, filters.limit]);

  const handleFilterChange = (newFilters: Partial<typeof filters>) => {
    setFilters({ ...filters, ...newFilters, skip: 0 });
  };

  const handlePrevPage = () => {
    if (filters.skip > 0) {
      setFilters({ ...filters, skip: filters.skip - filters.limit });
    }
  };

  const handleNextPage = () => {
    if (filters.skip + filters.limit < total) {
      setFilters({ ...filters, skip: filters.skip + filters.limit });
    }
  };

  const getResultVariant = (resultado: string) => {
    return resultado === 'exitoso' ? 'success' : 'danger';
  };

  const commonActionTypes = ['crear', 'actualizar', 'eliminar', 'ver', 'descargar', 'registrar_pago', 'aceptar_oferta'];

  return (
    <div className="space-y-8">
      <Breadcrumbs
        items={[
          { label: 'Dashboard', href: '/dashboard-interno' },
          { label: 'Auditoría' },
        ]}
      />

      <div>
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">Auditoría</h1>
        <p className="text-gray-600 dark:text-gray-400">Registro de acciones y rastrabilidad del sistema</p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total de Registros</p>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{total}</p>
        </Card>
        <Card>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Período</p>
          <p className="text-sm font-semibold">Últimos 90 días</p>
        </Card>
        <Card>
          <Button variant="primary" size="sm" onClick={handleExportLogs} className="w-full">
            📥 Descargar CSV
          </Button>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Filtros</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Tipo de Acción</label>
              <select
                value={filters.tipoAccion}
                onChange={(e) => handleFilterChange({ tipoAccion: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">Todas</option>
                {commonActionTypes.map((type) => (
                  <option key={type} value={type}>
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </option>
                ))}
              </select>
            </div>
            <Input
              type="date"
              label="Desde"
              value={filters.fechaDesde}
              onChange={(e) => handleFilterChange({ fechaDesde: e.target.value })}
            />
            <Input
              type="date"
              label="Hasta"
              value={filters.fechaHasta}
              onChange={(e) => handleFilterChange({ fechaHasta: e.target.value })}
            />
            <div className="flex items-end">
              <Button variant="secondary" className="w-full" onClick={() => handleFilterChange({ tipoAccion: '', fechaDesde: '', fechaHasta: '' })}>
                Limpiar
              </Button>
            </div>
          </div>
        </div>
      </Card>

      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* Logs Table */}
      <Card>
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Registros de Auditoría ({total} total)</h2>
        </div>

        <Table
          columns={[
            { header: 'Fecha', key: 'fecha_accion', render: (val) => formatDateTime(val as string) },
            { header: 'Usuario', key: 'usuario_nombre' },
            { header: 'Acción', key: 'tipo_accion' },
            { header: 'Entidad', key: 'entidad_tipo' },
            { header: 'Entidad ID', key: 'entidad_id', render: (val) => `#${val}` },
            {
              header: 'Resultado',
              key: 'resultado',
              render: (val) => <Badge variant={getResultVariant(val as string)}>{String(val)}</Badge>,
            },
            { header: 'IP Origen', key: 'ip_origen', render: (val) => <code className="text-xs bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">{String(val)}</code> },
            {
              header: 'Detalles',
              key: 'id',
              render: (val) => (
                <button
                  onClick={() => {
                    const log = logs.find((l) => l.id === val);
                    if (log) {
                      setSelectedLog(log);
                      setShowDetails(true);
                    }
                  }}
                  className="px-3 py-1 text-sm bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded hover:bg-blue-200 dark:hover:bg-blue-800"
                >
                  Ver
                </button>
              ),
            },
          ]}
          data={logs}
          loading={loading}
          keyExtractor={(row) => row.id}
        />

        {/* Pagination */}
        <div className="mt-6 flex justify-between items-center">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Mostrando {filters.skip + 1} a {Math.min(filters.skip + filters.limit, total)} de {total}
          </p>
          <div className="flex gap-2">
            <Button onClick={handlePrevPage} disabled={filters.skip === 0} variant="secondary" size="sm">
              ← Anterior
            </Button>
            <Button
              onClick={handleNextPage}
              disabled={filters.skip + filters.limit >= total}
              variant="secondary"
              size="sm"
            >
              Siguiente →
            </Button>
          </div>
        </div>
      </Card>

      {/* Log Detail Modal */}
      <Modal isOpen={showDetails} title="Detalle de Registro de Auditoría" onClose={() => setShowDetails(false)} size="lg">
        {selectedLog ? (
          <div className="space-y-4">
            {/* Basic Info */}
            <div className="grid grid-cols-2 gap-4 pb-4 border-b">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">ID Registro</p>
                <p className="font-mono text-sm font-bold">{selectedLog.id}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Fecha</p>
                <p className="font-semibold">{formatDateTime(selectedLog.fecha_accion)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Usuario</p>
                <p className="font-semibold">{selectedLog.usuario_nombre}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Resultado</p>
                <Badge variant={getResultVariant(selectedLog.resultado)}>{selectedLog.resultado}</Badge>
              </div>
            </div>

            {/* Action Info */}
            <div>
              <h3 className="font-semibold mb-3">Información de la Acción</h3>
              <div className="space-y-2">
                <div className="flex justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded">
                  <span className="text-gray-700 dark:text-gray-300">Tipo</span>
                  <span className="font-semibold">{selectedLog.tipo_accion}</span>
                </div>
                <div className="flex justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded">
                  <span className="text-gray-700 dark:text-gray-300">Descripción</span>
                  <span className="font-semibold text-right">{selectedLog.descripcion}</span>
                </div>
                <div className="flex justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded">
                  <span className="text-gray-700 dark:text-gray-300">Entidad</span>
                  <span className="font-semibold">
                    {selectedLog.entidad_tipo} #{selectedLog.entidad_id}
                  </span>
                </div>
                <div className="flex justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded">
                  <span className="text-gray-700 dark:text-gray-300">IP Origen</span>
                  <span className="font-mono text-sm">{selectedLog.ip_origen}</span>
                </div>
              </div>
            </div>

            {/* Changes */}
            {(selectedLog.cambios_anteriores || selectedLog.cambios_nuevos) && (
              <div>
                <h3 className="font-semibold mb-3">Cambios Registrados</h3>
                <div className="space-y-3">
                  {selectedLog.cambios_anteriores && (
                    <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded">
                      <p className="text-sm font-semibold text-red-700 dark:text-red-300 mb-2">Valores Anteriores</p>
                      <pre className="text-xs overflow-auto bg-white dark:bg-gray-800 p-2 rounded border border-red-200 dark:border-red-800">
                        {JSON.stringify(selectedLog.cambios_anteriores, null, 2)}
                      </pre>
                    </div>
                  )}
                  {selectedLog.cambios_nuevos && (
                    <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded">
                      <p className="text-sm font-semibold text-green-700 dark:text-green-300 mb-2">Valores Nuevos</p>
                      <pre className="text-xs overflow-auto bg-white dark:bg-gray-800 p-2 rounded border border-green-200 dark:border-green-800">
                        {JSON.stringify(selectedLog.cambios_nuevos, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        ) : (
          <Skeleton count={5} className="h-8 mb-4" />
        )}
      </Modal>
    </div>
  );
}
