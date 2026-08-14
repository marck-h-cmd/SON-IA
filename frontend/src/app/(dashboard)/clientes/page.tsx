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
import { clientsService } from '@/services/clientsService';
import { formatCurrency, formatDate, formatNumber } from '@/utils/formatting';
import { getScoreBadgeClass } from '@/utils/colors';
import type { Cliente, ClientePerfil, ListPaginada } from '@/types/api';

export default function ClientsPage() {
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [selectedCliente, setSelectedCliente] = useState<ClientePerfil | null>(null);
  const [showProfile, setShowProfile] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  const [filters, setFilters] = useState({
    skip: 0,
    limit: 10,
    segmento: '' as '' | 'B2B' | 'B2C' | 'Gobierno',
    search: '',
  });

  const fetchClientes = async () => {
    try {
      setLoading(true);
      const result = await clientsService.getClientes(
        filters.skip,
        filters.limit,
        filters.segmento || undefined
      );
      setClientes(result.items);
      setTotal(result.total);
    } catch (err) {
      console.error('Error fetching clientes:', err);
      setError('Error cargando clientes');
    } finally {
      setLoading(false);
    }
  };

  const fetchClientePerfil = async (clienteId: string) => {
    try {
      const profile = await clientsService.getClientePerfil(clienteId);
      setSelectedCliente(profile);
      setShowProfile(true);
    } catch (err) {
      console.error('Error fetching cliente profile:', err);
      setError('Error cargando perfil del cliente');
    }
  };

  useEffect(() => {
    fetchClientes();
  }, [filters.skip, filters.limit, filters.segmento]);

  const handleSegmentChange = (segmento: '' | 'B2B' | 'B2C' | 'Gobierno') => {
    setFilters({ ...filters, segmento, skip: 0 });
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

  const segmentBadgeVariant = (segmento: string) => {
    switch (segmento) {
      case 'B2B':
        return 'info';
      case 'Gobierno':
        return 'warning';
      case 'B2C':
        return 'default';
      default:
        return 'default';
    }
  };

  return (
    <div className="space-y-8">
      <Breadcrumbs
        items={[
          { label: 'Dashboard', href: '/dashboard-interno' },
          { label: 'Clientes' },
        ]}
      />

      <div>
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">Clientes</h1>
        <p className="text-gray-600 dark:text-gray-400">Gestión de información de clientes y scores de confianza</p>
      </div>

      {/* Filters and Actions */}
      <Card>
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Filtros y Búsqueda</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input type="text" placeholder="Buscar por RUC o razón social" label="Búsqueda" />
            <div>
              <label className="block text-sm font-medium mb-2">Segmento</label>
              <select
                value={filters.segmento}
                onChange={(e) => handleSegmentChange(e.target.value as any)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">Todos</option>
                <option value="B2B">B2B</option>
                <option value="B2C">B2C</option>
                <option value="Gobierno">Gobierno</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Estado</label>
              <select className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                <option value="">Todos</option>
                <option value="activo">Activo</option>
                <option value="inactivo">Inactivo</option>
              </select>
            </div>
          </div>
        </div>
      </Card>

      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* Clientes Table */}
      <Card>
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Listado de Clientes ({total} total)</h2>
        </div>

        <Table
          columns={[
            { header: 'RUC', key: 'ruc' },
            { header: 'Razón Social', key: 'razon_social' },
            { header: 'Segmento', key: 'segmento', render: (val) => <Badge variant={segmentBadgeVariant(val as string)}>{String(val)}</Badge> },
            {
              header: 'Score Confianza',
              key: 'score_confianza',
              render: (val) => (
                <div className="flex items-center gap-2">
                  <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${val}%` }}
                    />
                  </div>
                  <span className="text-sm font-semibold">{String(val)}</span>
                </div>
              ),
            },
            { header: 'Teléfono', key: 'telefono' },
            { header: 'Estado', key: 'estado', render: (val) => <Badge variant={String(val) === 'activo' ? 'success' : 'danger'}>{String(val)}</Badge> },
            {
              header: 'Acciones',
              key: 'id',
              render: (val) => (
                <button
                  onClick={() => fetchClientePerfil(val as string)}
                  className="px-3 py-1 text-sm bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded hover:bg-blue-200 dark:hover:bg-blue-800"
                >
                  Ver Perfil
                </button>
              ),
            },
          ]}
          data={clientes}
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

      {/* Client Profile Modal */}
      <Modal isOpen={showProfile} title="Perfil de Cliente" onClose={() => setShowProfile(false)} size="lg">
        {selectedCliente ? (
          <div className="space-y-6">
            {/* General Info */}
            <div>
              <h3 className="font-semibold text-lg mb-4">Información General</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">RUC</p>
                  <p className="font-semibold text-lg">{selectedCliente.cliente.ruc}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Razón Social</p>
                  <p className="font-semibold">{selectedCliente.cliente.razon_social}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Segmento</p>
                  <Badge variant={selectedCliente.cliente.segmento === 'B2B' ? 'info' : 'warning'}>
                    {selectedCliente.cliente.segmento}
                  </Badge>
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Estado</p>
                  <Badge variant={selectedCliente.cliente.estado === 'activo' ? 'success' : 'danger'}>
                    {selectedCliente.cliente.estado}
                  </Badge>
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Teléfono</p>
                  <p className="font-semibold">{selectedCliente.cliente.telefono}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Email</p>
                  <p className="font-semibold text-blue-600 dark:text-blue-400">{selectedCliente.cliente.email}</p>
                </div>
              </div>
            </div>

            {/* Score */}
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <h3 className="font-semibold mb-3">Score de Confianza</h3>
              <div className="flex items-end gap-4 mb-4">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Puntuación Final</p>
                  <p className={`text-4xl font-bold ${selectedCliente.score_confianza >= 80 ? 'text-green-600' : selectedCliente.score_confianza >= 60 ? 'text-blue-600' : 'text-amber-600'}`}>
                    {selectedCliente.score_confianza}
                  </p>
                </div>
                <div className="w-32 bg-gray-300 dark:bg-gray-700 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full ${selectedCliente.score_confianza >= 80 ? 'bg-green-600' : selectedCliente.score_confianza >= 60 ? 'bg-blue-600' : 'bg-amber-600'}`}
                    style={{ width: `${selectedCliente.score_confianza}%` }}
                  />
                </div>
                <p className="text-sm font-semibold">{selectedCliente.explicacion_score.clasificacion}</p>
              </div>

              {/* Scoring Factors */}
              <div className="space-y-2">
                {selectedCliente.explicacion_score.factores.map((factor, idx) => (
                  <div key={idx} className="flex justify-between items-center p-2 bg-white dark:bg-gray-800 rounded">
                    <span className="text-sm text-gray-700 dark:text-gray-300">{factor.nombre}</span>
                    <div className="flex items-center gap-2">
                      <span className={`text-sm font-bold ${factor.impacto === 'positivo' ? 'text-green-600' : 'text-red-600'}`}>
                        {factor.impacto === 'positivo' ? '+' : '-'}{Math.abs(factor.valor).toFixed(1)}
                      </span>
                      <span className="text-xs text-gray-500">({(factor.peso * 100).toFixed(0)}%)</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Accounting Summary */}
            <div className="grid grid-cols-3 gap-4">
              <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Facturas</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{selectedCliente.facturas_totales}</p>
              </div>
              <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400">Facturas Vencidas</p>
                <p className="text-2xl font-bold text-red-600 dark:text-red-400">{selectedCliente.facturas_vencidas}</p>
              </div>
              <div className="p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400">Monto Vencido</p>
                <p className="text-lg font-bold text-amber-600 dark:text-amber-400">
                  {formatCurrency(selectedCliente.monto_vencido)}
                </p>
              </div>
            </div>

            {/* Services */}
            <div>
              <h3 className="font-semibold mb-3">Servicios Activos</h3>
              <div className="space-y-2">
                {selectedCliente.servicios_activos.map((servicio) => (
                  <div key={servicio.id} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-800 rounded">
                    <div>
                      <p className="font-semibold text-gray-900 dark:text-white">{servicio.nombre}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Desde {formatDate(servicio.fecha_contratacion)}
                      </p>
                    </div>
                    <Badge variant={servicio.estado === 'activo' ? 'success' : 'danger'}>
                      {servicio.estado}
                    </Badge>
                  </div>
                ))}
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
