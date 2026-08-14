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
import { collectionsService } from '@/services/collectionsService';
import { formatCurrency, formatDate, formatNumber } from '@/utils/formatting';
import { getMoraStatusColor } from '@/utils/colors';
import type { FacturaVencida, CarteraMetricas, TAMNCalculo, ListPaginada } from '@/types/api';

export default function CollectionsPage() {
  const [facturas, setFacturas] = useState<FacturaVencida[]>([]);
  const [metricas, setMetricas] = useState<CarteraMetricas | null>(null);
  const [selectedFactura, setSelectedFactura] = useState<FacturaVencida | null>(null);
  const [tamnResult, setTamnResult] = useState<TAMNCalculo | null>(null);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [showTamnModal, setShowTamnModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  const [paymentForm, setPaymentForm] = useState({
    monto: '',
    fecha: new Date().toISOString().split('T')[0],
    referencia: '',
    metodo: 'transferencia',
  });

  const [filters, setFilters] = useState({
    skip: 0,
    limit: 10,
    etapa: '' as '' | 'temprana' | 'media' | 'tardia' | 'critica',
  });

  const fetchFacturas = async () => {
    try {
      setLoading(true);
      const [facturasRes, metricasRes] = await Promise.all([
        collectionsService.getFacturasVencidas(
          filters.skip,
          filters.limit,
          filters.etapa || undefined
        ),
        collectionsService.getCarteraMetricas(),
      ]);
      setFacturas(facturasRes.items);
      setTotal(facturasRes.total);
      setMetricas(metricasRes);
    } catch (err) {
      console.error('Error fetching collections data:', err);
      setError('Error cargando datos de cobranzas');
    } finally {
      setLoading(false);
    }
  };

  const handleCalcularTAMN = async (facturaId: string) => {
    try {
      const result = await collectionsService.calcularTAMN(facturaId);
      setTamnResult(result);
      setShowTamnModal(true);
    } catch (err) {
      console.error('Error calculating TAMN:', err);
      setError('Error calculando TAMN');
    }
  };

  const handleRegistrarPago = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!selectedFactura) return;

    try {
      const result = await collectionsService.procesarPago(
        selectedFactura.id,
        parseFloat(paymentForm.monto),
        paymentForm.fecha,
        paymentForm.referencia,
        paymentForm.metodo
      );
      alert('Pago registrado exitosamente');
      setShowPaymentModal(false);
      setPaymentForm({ monto: '', fecha: new Date().toISOString().split('T')[0], referencia: '', metodo: 'transferencia' });
      fetchFacturas();
    } catch (err) {
      console.error('Error registering payment:', err);
      setError('Error registrando pago');
    }
  };

  useEffect(() => {
    fetchFacturas();
  }, [filters.skip, filters.limit, filters.etapa]);

  const handleEtapaChange = (etapa: '' | 'temprana' | 'media' | 'tardia' | 'critica') => {
    setFilters({ ...filters, etapa, skip: 0 });
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

  const getMoraVariant = (etapa: string) => {
    switch (etapa) {
      case 'temprana':
        return 'warning';
      case 'media':
        return 'warning';
      case 'tardia':
        return 'danger';
      case 'critica':
        return 'danger';
      default:
        return 'default';
    }
  };

  return (
    <div className="space-y-8">
      <Breadcrumbs
        items={[
          { label: 'Dashboard', href: '/dashboard-interno' },
          { label: 'Cobranzas' },
        ]}
      />

      <div>
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">Cobranzas</h1>
        <p className="text-gray-600 dark:text-gray-400">Gestión de facturas vencidas y cálculo de intereses moratorios</p>
      </div>

      {/* Metrics Cards */}
      {metricas && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Cartera Vencida Total</p>
            <p className="text-3xl font-bold text-red-600 mb-2">{formatCurrency(metricas.total_cartera_vencida)}</p>
            <p className="text-sm text-gray-500">Monto pendiente</p>
          </Card>
          <Card>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Facturas Vencidas</p>
            <p className="text-3xl font-bold text-gray-900 dark:text-white mb-2">{metricas.cantidad_facturas_vencidas}</p>
            <p className="text-sm text-gray-500">Cantidad total</p>
          </Card>
          <Card>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">TAMN Acumulado</p>
            <p className="text-3xl font-bold text-amber-600 mb-2">{formatCurrency(metricas.tamn_acumulado)}</p>
            <p className="text-sm text-gray-500">Intereses moratorios</p>
          </Card>
          <Card>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Tendencia vs Mes</p>
            <p className={`text-3xl font-bold mb-2 ${metricas.tendencia_vs_mes_anterior > 0 ? 'text-red-600' : 'text-green-600'}`}>
              {metricas.tendencia_vs_mes_anterior > 0 ? '↑' : '↓'} {Math.abs(metricas.tendencia_vs_mes_anterior).toFixed(1)}%
            </p>
            <p className="text-sm text-gray-500">Cambio porcentual</p>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card>
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Filtros</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Etapa de Mora</label>
              <select
                value={filters.etapa}
                onChange={(e) => handleEtapaChange(e.target.value as any)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">Todas</option>
                <option value="temprana">Temprana (1-7 días)</option>
                <option value="media">Media (8-14 días)</option>
                <option value="tardia">Tardía (15-30 días)</option>
                <option value="critica">Crítica (&gt;30 días)</option>
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

      {/* Facturas Vencidas Table */}
      <Card>
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Facturas Vencidas ({total} total)
          </h2>
        </div>

        <Table
          columns={[
            { header: 'Factura', key: 'numero_factura' },
            { header: 'Cliente', key: 'cliente_nombre' },
            { header: 'Monto Original', key: 'monto_original', render: (val) => formatCurrency(val as number), align: 'right' },
            { header: 'Días Vencido', key: 'dias_vencido', align: 'right' },
            {
              header: 'Etapa Mora',
              key: 'etapa_mora',
              render: (val) => <Badge variant={getMoraVariant(val as string)}>{String(val)}</Badge>,
            },
            { header: 'TAMN Calculado', key: 'tamn_calculado', render: (val) => formatCurrency(val as number), align: 'right' },
            {
              header: 'Acciones',
              key: 'id',
              render: (val, row: FacturaVencida) => (
                <div className="flex gap-2 flex-wrap">
                  <button
                    onClick={() => handleCalcularTAMN(val as string)}
                    className="px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded hover:bg-blue-200 dark:hover:bg-blue-800"
                    title="Calcular TAMN"
                  >
                    Calcular
                  </button>
                  <button
                    onClick={() => {
                      setSelectedFactura(row);
                      setShowPaymentModal(true);
                    }}
                    className="px-2 py-1 text-xs bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded hover:bg-green-200 dark:hover:bg-green-800"
                    title="Registrar pago"
                  >
                    Pago
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

      {/* TAMN Calculation Modal */}
      <Modal isOpen={showTamnModal} title="Cálculo de TAMN" onClose={() => setShowTamnModal(false)}>
        {tamnResult ? (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4 pb-4 border-b">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Factura</p>
                <p className="font-bold">{tamnResult.factura_id}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Monto Original</p>
                <p className="font-bold">{formatCurrency(tamnResult.monto_original)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Tasa Moratoria</p>
                <p className="font-bold">{tamnResult.tasa_moratoria.toFixed(2)}%</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Días Vencido</p>
                <p className="font-bold">{tamnResult.dias_vencido} días</p>
              </div>
            </div>

            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <div className="flex justify-between mb-2">
                <span className="text-gray-700 dark:text-gray-300">Monto de Interés (TAMN):</span>
                <span className="font-bold text-lg text-blue-600">{formatCurrency(tamnResult.monto_interes)}</span>
              </div>
              <div className="flex justify-between border-t border-blue-200 dark:border-blue-800 pt-2">
                <span className="font-bold text-gray-900 dark:text-white">Total a Cobrar:</span>
                <span className="font-bold text-xl text-blue-600">{formatCurrency(tamnResult.monto_original + tamnResult.monto_interes)}</span>
              </div>
            </div>

            <Button
              variant="primary"
              className="w-full"
              onClick={() => {
                setShowTamnModal(false);
                setSelectedFactura(null);
              }}
            >
              Cerrar
            </Button>
          </div>
        ) : (
          <Skeleton count={5} className="h-8 mb-4" />
        )}
      </Modal>

      {/* Payment Registration Modal */}
      <Modal
        isOpen={showPaymentModal}
        title="Registrar Pago"
        onClose={() => setShowPaymentModal(false)}
        footer={
          <>
            <Button variant="secondary" onClick={() => setShowPaymentModal(false)}>
              Cancelar
            </Button>
            <Button variant="success" onClick={() => handleRegistrarPago()}>
              Registrar Pago
            </Button>
          </>
        }
      >
        {selectedFactura && (
          <form onSubmit={handleRegistrarPago} className="space-y-4">
            <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg mb-4">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Factura</p>
              <p className="font-bold text-lg">{selectedFactura.numero_factura}</p>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">Cliente: {selectedFactura.cliente_nombre}</p>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Monto Pendiente: {formatCurrency(selectedFactura.monto_pendiente)}
              </p>
            </div>

            <Input
              type="number"
              label="Monto Pagado"
              placeholder="0.00"
              required
              value={paymentForm.monto}
              onChange={(e) => setPaymentForm({ ...paymentForm, monto: e.target.value })}
            />

            <Input
              type="date"
              label="Fecha de Pago"
              required
              value={paymentForm.fecha}
              onChange={(e) => setPaymentForm({ ...paymentForm, fecha: e.target.value })}
            />

            <div>
              <label className="block text-sm font-medium mb-2">Método de Pago</label>
              <select
                value={paymentForm.metodo}
                onChange={(e) => setPaymentForm({ ...paymentForm, metodo: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="transferencia">Transferencia Bancaria</option>
                <option value="deposito">Depósito en Banco</option>
                <option value="efectivo">Efectivo</option>
                <option value="cheque">Cheque</option>
              </select>
            </div>

            <Input
              type="text"
              label="Referencia de Pago"
              placeholder="Ej: transf-202308120001"
              value={paymentForm.referencia}
              onChange={(e) => setPaymentForm({ ...paymentForm, referencia: e.target.value })}
            />
          </form>
        )}
      </Modal>
    </div>
  );
}
