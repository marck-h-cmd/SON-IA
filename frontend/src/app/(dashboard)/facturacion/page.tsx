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
import MovistarInvoiceModal from '@/components/billing/MovistarInvoiceModal';
import { billingService } from '@/services/billingService';
import { formatCurrency, formatDate } from '@/utils/formatting';
import { exportToCsv } from '@/utils/exportToExcel';
import { getStatusTextClass, getStatusBgClass } from '@/utils/colors';
import type { Factura, FacturaDetalle, ListPaginada } from '@/types/api';

export default function BillingPage() {
  const router = useRouter();
  const [facturas, setFacturas] = useState<Factura[]>([]);
  const [selectedFactura, setSelectedFactura] = useState<FacturaDetalle | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [showMovistarModal, setShowMovistarModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  // Estados para Ejecutar Ciclo de Facturación
  const [showCicloModal, setShowCicloModal] = useState(false);
  const [selectedCicloId, setSelectedCicloId] = useState('31');
  const [forceHumanReview, setForceHumanReview] = useState(false);
  const [cicloExecuting, setCicloExecuting] = useState(false);
  const [cicloResult, setCicloResult] = useState<{
    status: string;
    ciclo_id?: string | number;
    message?: string;
    action?: string;
    agents_involved?: string[];
  } | null>(null);

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

  const handleEjecutarCiclo = async () => {
    try {
      setCicloExecuting(true);
      setError(null);
      const res = await billingService.ejecutarCiclo(selectedCicloId, forceHumanReview);
      setCicloResult(res);
      setShowCicloModal(false);
      fetchFacturas();
    } catch (err: any) {
      console.error('Error ejecutando ciclo de facturación:', err);
      alert('Error ejecutando ciclo de facturación: ' + (err?.response?.data?.detail || err.message));
    } finally {
      setCicloExecuting(false);
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
        <p className="text-gray-600 dark:text-gray-400">Gestión de facturas y ciclos de facturación B2B</p>
      </div>

      {/* Notificación de Ciclo Ejecutado */}
      {cicloResult && (
        <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg space-y-2">
          <div className="flex justify-between items-center">
            <h3 className="font-bold text-blue-900 dark:text-blue-200 flex items-center gap-2">
              🤖 Ciclo {cicloResult.ciclo_id || selectedCicloId} Procesado por Enjambre IA
            </h3>
            <Badge variant={cicloResult.status === 'auto_approved' ? 'success' : 'warning'}>
              {cicloResult.status.toUpperCase()}
            </Badge>
          </div>
          <p className="text-sm text-blue-800 dark:text-blue-300">
            {cicloResult.message || 'El Supervisor Agent coordinó la validación y cálculo de facturas.'}
          </p>
          {cicloResult.agents_involved && (
            <p className="text-xs text-blue-600 dark:text-blue-400 font-mono">
              Agentes activos: {cicloResult.agents_involved.join(' • ')}
            </p>
          )}
          {cicloResult.action === 'send_to_hitl_dashboard' && (
            <div className="pt-2">
              <Button size="sm" variant="primary" onClick={() => router.push('/aprobaciones')}>
                🛡️ Ir al Centro de Aprobaciones HITL
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Filters and Actions */}
      <Card>
        <div className="space-y-4">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">Filtros</h2>
            <div className="flex gap-2">
              <Button
                variant="secondary"
                onClick={() =>
                  exportToCsv('Facturas_B2B_Integratel', facturas, [
                    { header: 'Número Factura', key: 'numero_factura' },
                    { header: 'Cliente', key: 'cliente_nombre' },
                    { header: 'RUC', key: 'cliente_id' },
                    { header: 'Monto Total', key: 'monto' },
                    { header: 'Fecha Emisión', key: 'fecha_emision' },
                    { header: 'Fecha Vencimiento', key: 'fecha_vencimiento' },
                    { header: 'Estado', key: 'estado' },
                  ])
                }
              >
                📊 Exportar a Excel
              </Button>
              <Button variant="primary" onClick={() => setShowCicloModal(true)}>
                🔄 Ejecutar Ciclo
              </Button>
            </div>
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
                  {String(val)}
                </Badge>
              ),
            },
            {
              header: 'Acciones',
              key: 'id',
              render: (val, row: Factura) => (
                <div className="flex gap-2">
                  <button
                    onClick={() => fetchFacturaDetalle(val as string)}
                    className="px-2.5 py-1 text-xs bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded hover:bg-blue-200 dark:hover:bg-blue-800 font-medium"
                  >
                    Detalle
                  </button>
                  <button
                    onClick={async () => {
                      await fetchFacturaDetalle(val as string);
                      setShowDetails(false);
                      setShowMovistarModal(true);
                    }}
                    className="px-2.5 py-1 text-xs bg-[#00A9E0] text-white rounded hover:bg-[#008cc0] font-medium"
                    title="Ver Recibo Oficial Movistar"
                  >
                    📄 Recibo Movistar
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
                {(selectedFactura.lineas || []).map((linea) => (
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
            {(selectedFactura.pagos_parciales || (selectedFactura as any).pagos || []).length > 0 && (
              <div>
                <h3 className="font-semibold mb-3">Pagos Registrados</h3>
                <div className="space-y-2">
                  {(selectedFactura.pagos_parciales || (selectedFactura as any).pagos || []).map((pago: any) => (
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

            {/* SUNAT UBL 2.1 Info & Actions */}
            <div className="p-4 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm font-bold text-gray-800 dark:text-gray-200">
                  📑 Comprobante Electrónico SUNAT (UBL 2.1)
                </span>
                <Badge variant="success">ACEPTADO OSE</Badge>
              </div>
              <p className="text-xs text-gray-500 font-mono">
                Hash SHA-256: AmvYDsBIul9VvRvzZ5o+GLlYMMgPCvIzelpMWcXUbsA=
              </p>
              <div className="flex gap-3 pt-2">
                <Button
                  size="sm"
                  variant="primary"
                  onClick={async () => {
                    try {
                      const blob = await billingService.descargarXml(selectedFactura.id);
                      const url = window.URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = `20601234567-14-${selectedFactura.numero_factura}.xml`;
                      document.body.appendChild(a);
                      a.click();
                      window.URL.revokeObjectURL(url);
                    } catch (e) {
                      alert('Error descargando XML SUNAT');
                    }
                  }}
                >
                  📥 Descargar XML UBL 2.1
                </Button>
                <button
                  onClick={() => {
                    setShowDetails(false);
                    setShowMovistarModal(true);
                  }}
                  className="px-3 py-1 text-xs bg-[#00A9E0] text-white rounded hover:bg-[#008cc0] font-semibold transition-colors"
                >
                  📄 Ver Recibo Movistar (PDF)
                </button>
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={async () => {
                    const email = prompt(
                      'Ingresa el correo electrónico destino para enviar el Recibo Movistar:',
                      selectedFactura.cliente?.email || `pagos@${selectedFactura.cliente?.ruc || 'cliente'}.com`
                    );
                    if (email) {
                      try {
                        const res = await billingService.enviarEmailFactura(selectedFactura.id, email);
                        alert(`✅ ${res.mensaje}`);
                      } catch (e) {
                        alert('Error al enviar el recibo por correo');
                      }
                    }
                  }}
                >
                  ✉️ Enviar por Correo
                </Button>
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => alert(`Cadena QR SUNAT:\n20601234567|14|${selectedFactura.numero_factura}|${selectedFactura.igv}|${selectedFactura.monto_total}`)}
                >
                  🔍 Ver Código QR
                </Button>
              </div>
            </div>
          </div>
        ) : (
          <Skeleton count={5} className="h-8 mb-4" />
        )}
      </Modal>

      {/* Modal: Visor Oficial de Recibo Movistar (Printable PDF) */}
      <MovistarInvoiceModal
        isOpen={showMovistarModal}
        onClose={() => setShowMovistarModal(false)}
        factura={selectedFactura}
        onSendEmail={async (emailDestino) => {
          if (!selectedFactura) return;
          try {
            const res = await billingService.enviarEmailFactura(selectedFactura.id, emailDestino);
            alert(`✅ ${res.mensaje}`);
          } catch (e) {
            alert('Error enviando recibo por correo electrónico');
          }
        }}
        onDownloadPdf={async () => {
          if (!selectedFactura) return;
          try {
            const blob = await billingService.descargarPdf(selectedFactura.id);
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Recibo_Movistar_${selectedFactura.numero_factura}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
          } catch (e) {
            alert('Error descargando PDF Oficial de Movistar');
          }
        }}
        onDownloadXml={async () => {
          if (!selectedFactura) return;
          try {
            const blob = await billingService.descargarXml(selectedFactura.id);
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `20601234567-14-${selectedFactura.numero_factura}.xml`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
          } catch (e) {
            alert('Error descargando XML SUNAT');
          }
        }}
      />

      {/* Modal: Ejecutar Ciclo de Facturación con Enjambre IA */}
      <Modal
        isOpen={showCicloModal}
        title="Ejecutar Ciclo de Facturación B2B"
        onClose={() => setShowCicloModal(false)}
        footer={
          <>
            <Button variant="secondary" onClick={() => setShowCicloModal(false)} disabled={cicloExecuting}>
              Cancelar
            </Button>
            <Button variant="primary" onClick={handleEjecutarCiclo} loading={cicloExecuting}>
              🚀 Iniciar Enjambre IA
            </Button>
          </>
        }
      >
        <div className="space-y-5">
          <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 border border-blue-200 dark:border-blue-800 rounded-lg">
            <h4 className="font-bold text-blue-900 dark:text-blue-200 mb-1 flex items-center gap-2">
              🤖 Orquestación Multi-Agente Autónoma
            </h4>
            <p className="text-xs text-blue-800 dark:text-blue-300">
              El <strong>SupervisorAgent</strong> coordinará al <strong>BillingAgent</strong> (cálculo simbólico PxQ e IGV 18%) y al <strong>ClassifierAgent</strong> para verificar consistencia histórica y retener anomalías en el Centro HITL.
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
              Seleccionar Ciclo de Facturación
            </label>
            <select
              value={selectedCicloId}
              onChange={(e) => setSelectedCicloId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="31">Ciclo 31 - Cierre de Mes (Clientes Corporativos)</option>
              <option value="01">Ciclo 01 - Primer Día del Mes</option>
              <option value="15">Ciclo 15 - Quincena (Pymes y Móviles)</option>
              <option value="28">Ciclo 28 - Fin de Ciclo Fijo</option>
            </select>
          </div>

          <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={forceHumanReview}
                onChange={(e) => setForceHumanReview(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
              />
              <div>
                <span className="text-sm font-medium text-gray-900 dark:text-white block">
                  Forzar Revisión Humana (Human-in-the-Loop)
                </span>
                <span className="text-xs text-gray-500 block">
                  Envía todas las facturas del ciclo a la bandeja de Aprobaciones HITL antes de la emisión final.
                </span>
              </div>
            </label>
          </div>

          <div className="text-xs text-gray-500 space-y-1">
            <p>• <strong>Cálculos exactos:</strong> Zero-Hallucination mediante motor matemático determinista.</p>
            <p>• <strong>Regla HITL activa:</strong> Facturas con score &lt; 0.80 o monto &gt; S/ 100,000 se retienen automáticamente.</p>
          </div>
        </div>
      </Modal>
    </div>
  );
}

