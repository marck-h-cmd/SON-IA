'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Card from '@/components/ui/Card';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import Table from '@/components/ui/Table';
import Modal from '@/components/ui/Modal';
import Breadcrumbs from '@/components/layout/Breadcrumbs';
import Skeleton from '@/components/ui/Skeleton';
import { billingService } from '@/services/billingService';
import { formatCurrency, formatDate } from '@/utils/formatting';
import { getStatusTextClass, getStatusBgClass } from '@/utils/colors';
import type { Factura, FacturaDetalle, ListPaginada } from '@/types/api';

export default function BillingPage() {
  const router = useRouter();
  const [facturas, setFacturas] = useState<Factura[]>([]);
  const [selectedFactura, setSelectedFactura] = useState<FacturaDetalle | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  const [filters, setFilters] = useState({
    skip: 0,
    limit: 10,
    estado: '' as '' | 'Pendiente' | 'Pagado' | 'Vencido',
  });

  const fetchFacturas = async () => {
    try {
      setLoading(true);
      const result = await billingService.getFacturas(
        filters.skip,
        filters.limit,
        filters.estado || undefined
      );
      setFacturas(result.items);
      setTotal(result.total);
    } catch (err) {
      console.error('Error fetching facturas:', err);
      setError('Error cargando facturas');
    } finally {
      setLoading(false);
    }
  };

  const fetchFacturaDetalle = async (facturaId: string) => {
    try {
      const detail = await billingService.getFacturaDetalle(facturaId);
      setSelectedFactura(detail);
      setShowDetails(true);
    } catch (err) {
      console.error('Error fetching factura details:', err);
      setError('Error cargando detalles de factura');
    }
  };

  useEffect(() => {
    fetchFacturas();
  }, [filters.skip, filters.limit, filters.estado]);

  const handleStatusChange = (estado: '' | 'Pendiente' | 'Pagado' | 'Vencido') => {
    setFilters({ ...filters, estado, skip: 0 });
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

  return (
    <div className="space-y-8">
      <Breadcrumbs
        items={[
          { label: 'Dashboard', href: '/dashboard-interno' },
          { label: 'Facturación' },
        ]}
      />

      <div>
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">Facturación</h1>
        <p className="text-gray-600 dark:text-gray-400">Gestión de facturas y ciclos de facturación</p>
      </div>

      {/* Filters and Actions */}
      <Card>
        <div className="space-y-4">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">Filtros</h2>
            <Button variant="primary" onClick={() => alert('Ejecutar ciclo - A implementar')}>
              🔄 Ejecutar Ciclo
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Estado</label>
              <select
                value={filters.estado}
                onChange={(e) => handleStatusChange(e.target.value as any)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">Todos</option>
                <option value="Pendiente">Pendiente</option>
                <option value="Pagado">Pagado</option>
                <option value="Vencido">Vencido</option>
              </select>
            </div>
            <Input type="date" placeholder="Desde" label="Fecha Desde" />
            <Input type="date" placeholder="Hasta" label="Fecha Hasta" />
          </div>
        </div>
      </Card>

      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* Facturas Table */}
      <Card>
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Listado de Facturas ({total} total)
          </h2>
        </div>

        <Table
          columns={[
            { header: 'Factura', key: 'numero_factura' },
            { header: 'Cliente', key: 'cliente_nombre' },
            { header: 'Monto', key: 'monto', render: (val) => formatCurrency(val as number), align: 'right' },
            { header: 'Emisión', key: 'fecha_emision', render: (val) => formatDate(val as string) },
            { header: 'Vencimiento', key: 'fecha_vencimiento', render: (val) => formatDate(val as string) },
            {
              header: 'Estado',
              key: 'estado',
              render: (val) => (
                <Badge variant={val === 'Pagado' ? 'success' : val === 'Vencido' ? 'danger' : 'warning'}>
                  {val}
                </Badge>
              ),
            },
            {
              header: 'Acciones',
              key: 'id',
              render: (val) => (
                <div className="flex gap-2">
                  <button
                    onClick={() => fetchFacturaDetalle(val as string)}
                    className="px-3 py-1 text-sm bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded hover:bg-blue-200 dark:hover:bg-blue-800"
                  >
                    Ver
                  </button>
                </div>
              ),
            },
          ]}
          data={facturas}
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

      {/* Factura Detail Modal */}
      <Modal isOpen={showDetails} title="Detalle de Factura" onClose={() => setShowDetails(false)} size="lg">
        {selectedFactura ? (
          <div className="space-y-6">
            {/* Header */}
            <div className="grid grid-cols-2 gap-4 pb-4 border-b">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Factura</p>
                <p className="text-lg font-bold">{selectedFactura.numero_factura}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Estado</p>
                <Badge variant={selectedFactura.estado === 'Pagado' ? 'success' : 'warning'}>
                  {selectedFactura.estado}
                </Badge>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Cliente</p>
                <p className="font-semibold">{selectedFactura.cliente.razon_social}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">RUC</p>
                <p className="font-semibold">{selectedFactura.cliente.ruc}</p>
              </div>
            </div>

            {/* Dates */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Fecha Emisión</p>
                <p className="font-semibold">{formatDate(selectedFactura.fecha_emision)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Fecha Vencimiento</p>
                <p className="font-semibold">{formatDate(selectedFactura.fecha_vencimiento)}</p>
              </div>
            </div>

            {/* Line Items */}
            <div>
              <h3 className="font-semibold mb-3">Líneas de Factura</h3>
              <div className="space-y-2">
                {selectedFactura.lineas.map((linea) => (
                  <div key={linea.id} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded">
                    <div className="flex-1">
                      <p className="font-medium text-gray-900 dark:text-white">{linea.descripcion}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {linea.cantidad} x {formatCurrency(linea.precio_unitario)}
                      </p>
                    </div>
                    <p className="font-bold">{formatCurrency(linea.subtotal)}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Totals */}
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-700 dark:text-gray-300">Subtotal:</span>
                <span className="font-bold">{formatCurrency(selectedFactura.subtotal)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-700 dark:text-gray-300">IGV:</span>
                <span className="font-bold">{formatCurrency(selectedFactura.igv)}</span>
              </div>
              <div className="border-t border-blue-200 dark:border-blue-800 pt-2 flex justify-between">
                <span className="font-bold text-gray-900 dark:text-white">Total:</span>
                <span className="font-bold text-lg text-blue-600 dark:text-blue-400">
                  {formatCurrency(selectedFactura.monto_total)}
                </span>
              </div>
            </div>

            {/* Pagos Parciales */}
            {selectedFactura.pagos_parciales.length > 0 && (
              <div>
                <h3 className="font-semibold mb-3">Pagos Registrados</h3>
                <div className="space-y-2">
                  {selectedFactura.pagos_parciales.map((pago) => (
                    <div key={pago.id} className="flex justify-between items-center p-2 text-sm">
                      <div>
                        <p className="text-gray-900 dark:text-white">{formatDate(pago.fecha)}</p>
                        <p className="text-gray-600 dark:text-gray-400">{pago.referencia}</p>
                      </div>
                      <p className="font-semibold">{formatCurrency(pago.monto)}</p>
                    </div>
                  ))}
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
