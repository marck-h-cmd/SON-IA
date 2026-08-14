'use client';

import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import Card from '@/components/ui/Card';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import Table from '@/components/ui/Table';
import Modal from '@/components/ui/Modal';
import Breadcrumbs from '@/components/layout/Breadcrumbs';
import Skeleton from '@/components/ui/Skeleton';
import { negotiationsService } from '@/services/negotiationService';
import { formatCurrency, formatDate, formatPercentage } from '@/utils/formatting';
import type { OfertaNegociacion, OfertaDetalle, TasaAceptacion, ListPaginada } from '@/types/api';

export default function NegotiationsPage() {
  const [ofertas, setOfertas] = useState<OfertaNegociacion[]>([]);
  const [selectedOferta, setSelectedOferta] = useState<OfertaDetalle | null>(null);
  const [tasaAceptacion, setTasaAceptacion] = useState<TasaAceptacion | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [actionLoading, setActionLoading] = useState(false);

  const [filters, setFilters] = useState({
    skip: 0,
    limit: 10,
    estado: '' as '' | 'pendiente' | 'aceptada' | 'rechazada' | 'expirada',
  });

  const fetchOfertas = async () => {
    try {
      setLoading(true);
      const [ofertasRes, tasaRes] = await Promise.all([
        negotiationsService.getOfertas(
          filters.skip,
          filters.limit,
          filters.estado || undefined
        ),
        negotiationsService.getTasaAceptacion(),
      ]);
      setOfertas(ofertasRes.items);
      setTotal(ofertasRes.total);
      setTasaAceptacion(tasaRes);
    } catch (err) {
      console.error('Error fetching ofertas:', err);
      setError('Error cargando ofertas');
    } finally {
      setLoading(false);
    }
  };

  const fetchOfertaDetalle = async (ofertaId: string) => {
    try {
      const detail = await negotiationsService.getOfertaDetalle(ofertaId);
      setSelectedOferta(detail);
      setShowDetails(true);
    } catch (err) {
      console.error('Error fetching oferta details:', err);
      setError('Error cargando detalles de oferta');
    }
  };

  const handleAceptarOferta = async (ofertaId: string) => {
    if (!confirm('¿Está seguro que desea aceptar esta oferta?')) return;

    try {
      setActionLoading(true);
      await negotiationsService.aceptarOferta(ofertaId);
      alert('Oferta aceptada exitosamente');
      setShowDetails(false);
      fetchOfertas();
    } catch (err) {
      console.error('Error accepting oferta:', err);
      setError('Error aceptando oferta');
    } finally {
      setActionLoading(false);
    }
  };

  const handleRechazarOferta = async (ofertaId: string) => {
    const razon = prompt('¿Razón del rechazo (opcional)?');
    if (razon === null) return;

    try {
      setActionLoading(true);
      await negotiationsService.rechazarOferta(ofertaId, razon || undefined);
      alert('Oferta rechazada');
      setShowDetails(false);
      fetchOfertas();
    } catch (err) {
      console.error('Error rejecting oferta:', err);
      setError('Error rechazando oferta');
    } finally {
      setActionLoading(false);
    }
  };

  useEffect(() => {
    fetchOfertas();
  }, [filters.skip, filters.limit, filters.estado]);

  const handleStatusChange = (estado: '' | 'pendiente' | 'aceptada' | 'rechazada' | 'expirada') => {
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

  const getEstadoVariant = (estado: string) => {
    switch (estado) {
      case 'pendiente':
        return 'info';
      case 'aceptada':
        return 'success';
      case 'rechazada':
        return 'danger';
      case 'expirada':
        return 'default';
      default:
        return 'default';
    }
  };

  // Chart data for acceptance rate
  const chartData = tasaAceptacion
    ? [
        { estado: 'Aceptadas', cantidad: tasaAceptacion.ofertas_aceptadas },
        { estado: 'Rechazadas', cantidad: tasaAceptacion.ofertas_rechazadas },
        { estado: 'Expiradas', cantidad: tasaAceptacion.ofertas_expiradas },
        { estado: 'Pendientes', cantidad: tasaAceptacion.total_ofertas - tasaAceptacion.ofertas_aceptadas - tasaAceptacion.ofertas_rechazadas - tasaAceptacion.ofertas_expiradas },
      ]
    : [];

  return (
    <div className="space-y-8">
      <Breadcrumbs
        items={[
          { label: 'Dashboard', href: '/dashboard-interno' },
          { label: 'Negociación' },
        ]}
      />

      <div>
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">Negociación</h1>
        <p className="text-gray-600 dark:text-gray-400">Gestión de ofertas de negociación y descuentos</p>
      </div>

      {/* Metrics */}
      {tasaAceptacion && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
          <Card>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Ofertas</p>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">{tasaAceptacion.total_ofertas}</p>
          </Card>
          <Card>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Aceptadas</p>
            <p className="text-3xl font-bold text-green-600">{tasaAceptacion.ofertas_aceptadas}</p>
          </Card>
          <Card>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Rechazadas</p>
            <p className="text-3xl font-bold text-red-600">{tasaAceptacion.ofertas_rechazadas}</p>
          </Card>
          <Card>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Expiradas</p>
            <p className="text-3xl font-bold text-gray-600">{tasaAceptacion.ofertas_expiradas}</p>
          </Card>
          <Card className="bg-blue-50 dark:bg-blue-900/20">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Tasa Aceptación</p>
            <p className="text-3xl font-bold text-blue-600">{tasaAceptacion.tasa_aceptacion.toFixed(1)}%</p>
          </Card>
        </div>
      )}

      {/* Acceptance Rate Chart */}
      {chartData.length > 0 && (
        <Card>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Distribución de Ofertas</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="estado" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip />
              <Bar dataKey="cantidad" fill="#3b82f6" name="Cantidad" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      )}

      {/* Filters */}
      <Card>
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Filtros</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Estado</label>
              <select
                value={filters.estado}
                onChange={(e) => handleStatusChange(e.target.value as any)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">Todos</option>
                <option value="pendiente">Pendiente</option>
                <option value="aceptada">Aceptada</option>
                <option value="rechazada">Rechazada</option>
                <option value="expirada">Expirada</option>
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

      {/* Ofertas Table */}
      <Card>
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Listado de Ofertas ({total} total)</h2>
        </div>

        <Table
          columns={[
            { header: 'Oferta ID', key: 'id', render: (val) => `#${val}` },
            { header: 'Cliente', key: 'cliente_nombre' },
            { header: 'Factura', key: 'factura_id', render: (val) => `#${val}` },
            { header: 'Monto Original', key: 'monto_original', render: (val) => formatCurrency(val as number), align: 'right' },
            { header: 'Descuento', key: 'descuento_ofrecido', render: (val) => `${val}%`, align: 'right' },
            { header: 'Nuevo Plazo', key: 'nuevo_plazo_dias', render: (val) => `${val} días`, align: 'right' },
            {
              header: 'Estado',
              key: 'estado',
              render: (val) => <Badge variant={getEstadoVariant(val as string)}>{String(val)}</Badge>,
            },
            {
              header: 'Vencimiento',
              key: 'fecha_expiracion',
              render: (val) => formatDate(val as string),
            },
            {
              header: 'Acciones',
              key: 'id',
              render: (val) => (
                <button
                  onClick={() => fetchOfertaDetalle(val as string)}
                  className="px-3 py-1 text-sm bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded hover:bg-blue-200 dark:hover:bg-blue-800"
                >
                  Ver
                </button>
              ),
            },
          ]}
          data={ofertas}
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

      {/* Oferta Detail Modal */}
      <Modal
        isOpen={showDetails}
        title="Detalle de Oferta de Negociación"
        onClose={() => setShowDetails(false)}
        size="lg"
        footer={
          selectedOferta && selectedOferta.estado === 'pendiente' ? (
            <>
              <Button
                variant="danger"
                onClick={() => handleRechazarOferta(selectedOferta.id)}
                disabled={actionLoading}
              >
                Rechazar
              </Button>
              <Button
                variant="success"
                onClick={() => handleAceptarOferta(selectedOferta.id)}
                loading={actionLoading}
              >
                Aceptar
              </Button>
            </>
          ) : undefined
        }
      >
        {selectedOferta ? (
          <div className="space-y-6">
            {/* Header */}
            <div className="grid grid-cols-2 gap-4 pb-4 border-b">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Oferta ID</p>
                <p className="text-lg font-bold">#{selectedOferta.id}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Estado</p>
                <Badge variant={getEstadoVariant(selectedOferta.estado)}>{selectedOferta.estado}</Badge>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Cliente</p>
                <p className="font-semibold">{selectedOferta.cliente_nombre}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Factura</p>
                <p className="font-semibold">#{selectedOferta.factura_id}</p>
              </div>
            </div>

            {/* Offer Details */}
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded">
                <p className="text-sm text-gray-600 dark:text-gray-400">Monto Original</p>
                <p className="text-xl font-bold">{formatCurrency(selectedOferta.monto_original)}</p>
              </div>
              <div className="p-3 bg-amber-50 dark:bg-amber-900/20 rounded">
                <p className="text-sm text-gray-600 dark:text-gray-400">Descuento Ofrecido</p>
                <p className="text-xl font-bold text-amber-600">{selectedOferta.descuento_ofrecido}%</p>
              </div>
              <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded">
                <p className="text-sm text-gray-600 dark:text-gray-400">Monto Final</p>
                <p className="text-xl font-bold text-green-600">{formatCurrency(selectedOferta.monto_final)}</p>
              </div>
              <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded">
                <p className="text-sm text-gray-600 dark:text-gray-400">Ahorro Cliente</p>
                <p className="text-xl font-bold text-blue-600">{formatCurrency(selectedOferta.ahorro_cliente)}</p>
              </div>
            </div>

            {/* Payment Terms */}
            <div className="grid grid-cols-2 gap-4 pb-4 border-b">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Nuevo Plazo</p>
                <p className="font-semibold text-lg">{selectedOferta.nuevo_plazo_dias} días</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Nueva Fecha Vencimiento</p>
                <p className="font-semibold">{formatDate(selectedOferta.fecha_expiracion)}</p>
              </div>
            </div>

            {/* Justification */}
            <div>
              <h3 className="font-semibold mb-2">Justificación de Oferta</h3>
              <p className="text-gray-700 dark:text-gray-300 p-3 bg-gray-50 dark:bg-gray-700 rounded">
                {selectedOferta.justificacion}
              </p>
            </div>

            {/* Dates */}
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-600 dark:text-gray-400">Creada</p>
                <p className="font-semibold">{formatDate(selectedOferta.fecha_creacion)}</p>
              </div>
              <div>
                <p className="text-gray-600 dark:text-gray-400">Expira</p>
                <p className="font-semibold">{formatDate(selectedOferta.fecha_expiracion)}</p>
              </div>
            </div>
          </div>
        ) : (
          <Skeleton count={5} className="h-8 mb-4" />
        )}
      </Modal>
    </div>
  );
}
