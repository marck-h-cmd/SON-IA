'use client';

import React, { useEffect, useState } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import Table from '@/components/ui/Table';
import Modal from '@/components/ui/Modal';
import Breadcrumbs from '@/components/layout/Breadcrumbs';
import Skeleton from '@/components/ui/Skeleton';
import { hitlService } from '@/services/hitlService';
import { formatCurrency, formatDateTime } from '@/utils/formatting';
import type { SolicitudHITL, MetricasHITL } from '@/types/api';

export default function AprobacionesPage() {
  const [solicitudes, setSolicitudes] = useState<SolicitudHITL[]>([]);
  const [metricas, setMetricas] = useState<MetricasHITL | null>(null);
  const [selectedSolicitud, setSelectedSolicitud] = useState<SolicitudHITL | null>(null);
  const [showDecisionModal, setShowDecisionModal] = useState(false);
  const [decisionType, setDecisionType] = useState<'aprobar' | 'rechazar'>('aprobar');
  const [decisionNotes, setDecisionNotes] = useState('');
  const [supervisorNombre, setSupervisorNombre] = useState('Supervisor HITL');
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  const [filters, setFilters] = useState<{
    skip: number;
    limit: number;
    estado: 'pendiente' | 'aprobada' | 'rechazada' | '';
  }>({
    skip: 0,
    limit: 10,
    estado: 'pendiente',
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [solicitudesRes, metricasRes] = await Promise.all([
        hitlService.getSolicitudes(
          filters.skip,
          filters.limit,
          filters.estado || undefined
        ),
        hitlService.getMetricas(),
      ]);
      setSolicitudes(solicitudesRes.items);
      setTotal(solicitudesRes.total);
      setMetricas(metricasRes);
    } catch (err) {
      console.error('Error fetching HITL data:', err);
      setError('Error al cargar las solicitudes del Centro de Aprobaciones HITL');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [filters.skip, filters.limit, filters.estado]);

  const handleOpenDecision = (solicitud: SolicitudHITL, type: 'aprobar' | 'rechazar') => {
    setSelectedSolicitud(solicitud);
    setDecisionType(type);
    setDecisionNotes(
      type === 'aprobar'
        ? 'Aprobación autorizada tras verificación de solvencia y consistencia.'
        : 'Rechazado por riesgo financiero elevado.'
    );
    setShowDecisionModal(true);
  };

  const handleConfirmDecision = async () => {
    if (!selectedSolicitud) return;

    try {
      setActionLoading(true);
      if (decisionType === 'aprobar') {
        await hitlService.aprobarSolicitud(
          selectedSolicitud.solicitud_id,
          decisionNotes,
          supervisorNombre
        );
        setSuccessMessage(`Solicitud ${selectedSolicitud.solicitud_id} aprobada con éxito.`);
      } else {
        await hitlService.rechazarSolicitud(
          selectedSolicitud.solicitud_id,
          decisionNotes,
          supervisorNombre
        );
        setSuccessMessage(`Solicitud ${selectedSolicitud.solicitud_id} rechazada.`);
      }

      setShowDecisionModal(false);
      setSelectedSolicitud(null);
      fetchData();

      setTimeout(() => setSuccessMessage(null), 5000);
    } catch (err) {
      console.error('Error executing decision:', err);
      alert('Hubo un error al registrar la decisión. Intenta nuevamente.');
    } finally {
      setActionLoading(false);
    }
  };

  const getScoreBadge = (score: number) => {
    if (score >= 0.8) return <Badge variant="success">{(score * 100).toFixed(0)}% (Alto)</Badge>;
    if (score >= 0.6) return <Badge variant="warning">{(score * 100).toFixed(0)}% (Medio)</Badge>;
    return <Badge variant="danger">{(score * 100).toFixed(0)}% (Crítico)</Badge>;
  };

  const getEstadoBadge = (estado: string) => {
    switch (estado) {
      case 'aprobada':
        return <Badge variant="success">Aprobada</Badge>;
      case 'rechazada':
        return <Badge variant="danger">Rechazada</Badge>;
      default:
        return <Badge variant="warning">Pendiente</Badge>;
    }
  };

  return (
    <div className="space-y-8">
      {/* Breadcrumbs */}
      <Breadcrumbs
        items={[
          { label: 'Dashboard', href: '/dashboard-interno' },
          { label: 'Centro de Aprobaciones HITL' },
        ]}
      />

      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
          Centro de Aprobaciones HITL
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Supervisión humana (Human-in-the-Loop) para facturas y acuerdos retenidos por umbrales de riesgo
        </p>
      </div>

      {/* Notifications */}
      {successMessage && (
        <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg text-green-700 dark:text-green-300 font-medium">
          ✅ {successMessage}
        </div>
      )}

      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-600 dark:text-red-400">
          {error}
        </div>
      )}

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Pendientes de Revisión</p>
          <p className="text-3xl font-bold text-amber-600 mb-2">
            {metricas ? metricas.total_pendientes : <Skeleton className="h-8 w-16" />}
          </p>
          <p className="text-sm text-gray-500">Requieren autorización humana</p>
        </Card>

        <Card>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Monto Retenido</p>
          <p className="text-3xl font-bold text-blue-600 mb-2">
            {metricas ? formatCurrency(metricas.monto_total_retenido) : <Skeleton className="h-8 w-24" />}
          </p>
          <p className="text-sm text-gray-500">En solicitudes pendientes</p>
        </Card>

        <Card>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Aprobadas</p>
          <p className="text-3xl font-bold text-green-600 mb-2">
            {metricas ? metricas.total_aprobadas : <Skeleton className="h-8 w-16" />}
          </p>
          <p className="text-sm text-gray-500">Desbloqueadas por supervisor</p>
        </Card>

        <Card>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Rechazadas</p>
          <p className="text-3xl font-bold text-red-600 mb-2">
            {metricas ? metricas.total_rechazadas : <Skeleton className="h-8 w-16" />}
          </p>
          <p className="text-sm text-gray-500">Bloqueadas por riesgo</p>
        </Card>
      </div>

      {/* Filter Tabs */}
      <Card>
        <div className="flex flex-wrap gap-3 items-center justify-between">
          <div className="flex gap-2">
            <Button
              size="sm"
              variant={filters.estado === 'pendiente' ? 'primary' : 'secondary'}
              onClick={() => setFilters({ ...filters, estado: 'pendiente', skip: 0 })}
            >
              ⏳ Pendientes ({metricas?.total_pendientes || 0})
            </Button>
            <Button
              size="sm"
              variant={filters.estado === 'aprobada' ? 'primary' : 'secondary'}
              onClick={() => setFilters({ ...filters, estado: 'aprobada', skip: 0 })}
            >
              ✅ Aprobadas ({metricas?.total_aprobadas || 0})
            </Button>
            <Button
              size="sm"
              variant={filters.estado === 'rechazada' ? 'primary' : 'secondary'}
              onClick={() => setFilters({ ...filters, estado: 'rechazada', skip: 0 })}
            >
              🚫 Rechazadas ({metricas?.total_rechazadas || 0})
            </Button>
            <Button
              size="sm"
              variant={filters.estado === '' ? 'primary' : 'secondary'}
              onClick={() => setFilters({ ...filters, estado: '', skip: 0 })}
            >
              Todas
            </Button>
          </div>

          <Button size="sm" variant="secondary" onClick={() => fetchData()}>
            🔄 Actualizar
          </Button>
        </div>
      </Card>

      {/* Main Table */}
      <Card>
        <div className="mb-4 flex justify-between items-center">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Bandeja de Decisiones HITL ({total} registros)
          </h2>
        </div>

        <Table
          columns={[
            { header: 'Solicitud ID', key: 'solicitud_id' },
            {
              header: 'Cliente / RUC',
              key: 'cliente_nombre',
              render: (val, row: SolicitudHITL) => (
                <div>
                  <p className="font-semibold text-gray-900 dark:text-white">{String(val || 'N/A')}</p>
                  <p className="text-xs text-gray-500 font-mono">RUC: {row.numero_identificacion_fiscal}</p>
                </div>
              ),
            },
            {
              header: 'Monto',
              key: 'monto',
              render: (val) => formatCurrency(val as number),
              align: 'right',
            },
            {
              header: 'Score Confianza',
              key: 'score_confianza',
              render: (val) => getScoreBadge(val as number),
              align: 'center',
            },
            {
              header: 'Motivo de Retención',
              key: 'motivo_retencion',
              render: (val) => (
                <span className="text-sm text-gray-700 dark:text-gray-300 line-clamp-2" title={String(val)}>
                  {String(val)}
                </span>
              ),
            },
            {
              header: 'Estado',
              key: 'estado',
              render: (val) => getEstadoBadge(val as string),
              align: 'center',
            },
            {
              header: 'Acciones',
              key: 'id',
              align: 'center',
              render: (val, row: SolicitudHITL) => (
                <div className="flex gap-2 justify-center">
                  {row.estado === 'pendiente' ? (
                    <>
                      <button
                        onClick={() => handleOpenDecision(row, 'aprobar')}
                        className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white rounded text-xs font-semibold transition-colors"
                        title="Aprobar emisión"
                      >
                        Aprobar
                      </button>
                      <button
                        onClick={() => handleOpenDecision(row, 'rechazar')}
                        className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-xs font-semibold transition-colors"
                        title="Rechazar emisión"
                      >
                        Rechazar
                      </button>
                    </>
                  ) : (
                    <span className="text-xs text-gray-500">
                      Resuelto por {row.supervisor_responsable || 'Supervisor'}
                    </span>
                  )}
                </div>
              ),
            },
          ]}
          data={solicitudes}
          loading={loading}
          keyExtractor={(row) => row.solicitud_id}
        />

        {/* Pagination */}
        <div className="mt-6 flex justify-between items-center">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Mostrando {total === 0 ? 0 : filters.skip + 1} a {Math.min(filters.skip + filters.limit, total)} de {total}
          </p>
          <div className="flex gap-2">
            <Button
              onClick={() => setFilters({ ...filters, skip: Math.max(0, filters.skip - filters.limit) })}
              disabled={filters.skip === 0}
              variant="secondary"
              size="sm"
            >
              ← Anterior
            </Button>
            <Button
              onClick={() => setFilters({ ...filters, skip: filters.skip + filters.limit })}
              disabled={filters.skip + filters.limit >= total}
              variant="secondary"
              size="sm"
            >
              Siguiente →
            </Button>
          </div>
        </div>
      </Card>

      {/* Decision Modal */}
      <Modal
        isOpen={showDecisionModal}
        title={decisionType === 'aprobar' ? 'Aprobar Solicitud HITL' : 'Rechazar Solicitud HITL'}
        onClose={() => setShowDecisionModal(false)}
        footer={
          <>
            <Button variant="secondary" onClick={() => setShowDecisionModal(false)}>
              Cancelar
            </Button>
            <Button
              variant={decisionType === 'aprobar' ? 'success' : 'danger'}
              onClick={handleConfirmDecision}
              loading={actionLoading}
            >
              {decisionType === 'aprobar' ? 'Confirmar Aprobación' : 'Confirmar Rechazo'}
            </Button>
          </>
        }
      >
        {selectedSolicitud && (
          <div className="space-y-4">
            <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Solicitud:</span>
                <span className="font-bold text-gray-900 dark:text-white">{selectedSolicitud.solicitud_id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Factura Asociada:</span>
                <span className="font-mono text-gray-900 dark:text-white">{selectedSolicitud.factura_id || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Cliente:</span>
                <span className="font-medium text-gray-900 dark:text-white">{selectedSolicitud.cliente_nombre}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Monto:</span>
                <span className="font-bold text-lg text-blue-600">{formatCurrency(selectedSolicitud.monto)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600 dark:text-gray-400">Score de Confianza IA:</span>
                <span>{getScoreBadge(selectedSolicitud.score_confianza)}</span>
              </div>
            </div>

            <div className="p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
              <p className="text-xs text-amber-700 dark:text-amber-300 font-semibold mb-1">
                🔍 Motivo de retención del Supervisor Agent:
              </p>
              <p className="text-sm text-amber-800 dark:text-amber-200">{selectedSolicitud.motivo_retencion}</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
                Supervisor Responsable
              </label>
              <input
                type="text"
                value={supervisorNombre}
                onChange={(e) => setSupervisorNombre(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
                Comentarios / Justificación de la decisión
              </label>
              <textarea
                rows={3}
                value={decisionNotes}
                onChange={(e) => setDecisionNotes(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                placeholder="Escribe la justificación..."
              />
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
