'use client';

import React, { useEffect, useState } from 'react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import Card from '@/components/ui/Card';
import MetricCard from '@/components/dashboard/MetricCard';
import Skeleton from '@/components/ui/Skeleton';
import Badge from '@/components/ui/Badge';
import Table from '@/components/ui/Table';
import Breadcrumbs from '@/components/layout/Breadcrumbs';
import { dashboardService } from '@/services/dashboardService';
import { formatCurrency, formatPercentage, formatNumber, formatTimeAgo } from '@/utils/formatting';
import { getAgentStatusColor, getMorosidadColor } from '@/utils/colors';
import type { DashboardMetrics, AgentState } from '@/types/api';

const COLORS = ['#10B981', '#FCD34D', '#EF4444', '#3B82F6', '#8B5CF6', '#F59E0B', '#06B6D4'];

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [agentes, setAgentes] = useState<Record<string, AgentState>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [metricsRes, agentesRes] = await Promise.all([
          dashboardService.getMetrics(),
          dashboardService.getAgentesEstado(),
        ]);
        setMetrics(metricsRes);
        setAgentes(agentesRes);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Error cargando datos del dashboard');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (error) {
    return (
      <div className="p-8 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
        <h2 className="text-lg font-bold text-red-700 dark:text-red-300">Error</h2>
        <p className="text-red-600 dark:text-red-400">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Reintentar
        </button>
      </div>
    );
  }

  // Mock data for charts
  const chartData7Days = [
    { date: 'Lun', recaudacion: 15000 },
    { date: 'Mar', recaudacion: 22000 },
    { date: 'Mié', recaudacion: 18500 },
    { date: 'Jue', recaudacion: 25000 },
    { date: 'Vie', recaudacion: 31000 },
    { date: 'Sáb', recaudacion: 12000 },
    { date: 'Dom', recaudacion: 8000 },
  ];

  const facturasEstado = [
    { estado: 'Pendiente', cantidad: metrics?.facturas_pendientes_revision || 0 },
    { estado: 'Vencido', cantidad: 45 },
    { estado: 'Pagado', cantidad: 156 },
  ];

  const ofertasEstado = [
    { estado: 'Pendiente', cantidad: 12 },
    { estado: 'Aceptada', cantidad: 28 },
    { estado: 'Rechazada', cantidad: 5 },
    { estado: 'Expirada', cantidad: 3 },
  ];

  const agentesData = Object.entries(agentes).map(([name, state]) => ({
    nombre: name.charAt(0).toUpperCase() + name.slice(1),
    estado: state.estado,
    modelo: state.modelo,
    proveedor: state.proveedor,
    última_ejecución: state.última_ejecución,
    tareas_procesadas: state.tareas_procesadas,
    tasa_error: state.tasa_error,
  }));

  return (
    <div className="space-y-8">
      {/* Breadcrumbs */}
      <Breadcrumbs items={[{ label: 'Dashboard', href: '/dashboard-interno' }]} />

      <div>
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">Dashboard Operativo</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Resumen de métricas principales y estado del sistema
        </p>
      </div>

      {/* Metrics Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {loading ? (
          <>
            {[1, 2, 3, 4].map((i) => (
              <Card key={i}>
                <Skeleton className="h-10 mb-2" />
                <Skeleton className="h-8 mb-4" />
                <Skeleton className="h-4" />
              </Card>
            ))}
          </>
        ) : (
          <>
            <MetricCard
              title="Facturas Procesadas Hoy"
              value={metrics?.facturas_procesadas_hoy || 0}
              icon="📄"
              variant="default"
            />
            <MetricCard
              title="Monto Recaudado"
              value={formatCurrency(metrics?.monto_total_recaudado || 0)}
              icon="💰"
              variant="success"
              trend={8}
              trendUp={true}
            />
            <MetricCard
              title="Índice de Morosidad"
              value={formatPercentage(metrics?.indice_morosidad || 0)}
              icon="⚠️"
              variant={metrics && metrics.indice_morosidad > 5 ? 'danger' : metrics && metrics.indice_morosidad > 2 ? 'warning' : 'success'}
            />
            <MetricCard
              title="Facturas Pendientes Revisión"
              value={metrics?.facturas_pendientes_revision || 0}
              icon="🔍"
              subtitle="Requieren HITL"
              variant="warning"
            />
          </>
        )}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Revenue Trend */}
        <Card className="lg:col-span-2">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recaudación - Últimos 7 Días</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData7Days}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="date" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="recaudacion"
                stroke="#2563eb"
                name="Monto Recaudado (S/)"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        {/* Morosidad Trend */}
        <Card>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Estado de Agentes</h2>
          <div className="space-y-3">
            {Object.entries(agentes).map(([name, state]) => (
              <div key={name} className="flex items-center justify-between">
                <span className="text-sm text-gray-700 dark:text-gray-300 capitalize">{name}</span>
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: getAgentStatusColor(state.estado) }}
                  />
                  <Badge
                    variant={state.estado === 'activo' ? 'success' : state.estado === 'error' ? 'danger' : 'default'}
                  >
                    {state.estado}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Facturas and Ofertas Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Facturas por Estado */}
        <Card>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Facturas por Estado</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={facturasEstado}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="estado" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip />
              <Bar dataKey="cantidad" fill="#3b82f6" name="Cantidad" />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        {/* Ofertas Distribución */}
        <Card>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Ofertas por Estado</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={ofertasEstado}
                dataKey="cantidad"
                nameKey="estado"
                cx="50%"
                cy="50%"
                outerRadius={80}
                label
              >
                {ofertasEstado.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Agents Table */}
      <Card>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Estado del Enjambre de Agentes IA</h2>
        <Table
          columns={[
            { header: 'Agente', key: 'nombre' },
            { header: 'Estado', key: 'estado', render: (val) => <Badge variant="success">{String(val)}</Badge> },
            { header: 'Modelo', key: 'modelo' },
            { header: 'Proveedor', key: 'proveedor' },
            { header: 'Última Ejecución', key: 'última_ejecución', render: (val) => formatTimeAgo(val as string) },
            { header: 'Tareas', key: 'tareas_procesadas', align: 'right' },
            { header: 'Tasa Error', key: 'tasa_error', render: (val) => `${val}%`, align: 'right' },
          ]}
          data={agentesData}
          loading={loading}
          keyExtractor={(row) => row.nombre}
        />
      </Card>

      {/* Additional Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Ofertas Activas</h3>
          <p className="text-3xl font-bold text-blue-600 mb-2">{metrics?.ofertas_activas || 0}</p>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Tasa de aceptación: {formatPercentage(metrics?.tasa_aceptacion_ofertas || 0)}
          </p>
        </Card>

        <Card>
          <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Tiempo Promedio Emisión</h3>
          <p className="text-3xl font-bold text-green-600 mb-2">
            {formatNumber(metrics?.tiempo_promedio_emision_seg || 0)}s
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-400">Tiempo promedio en segundos</p>
        </Card>

        <Card>
          <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Agentes Activos</h3>
          <p className="text-3xl font-bold text-purple-600 mb-2">{metrics?.agentes_activos || 0}</p>
          <p className="text-sm text-gray-600 dark:text-gray-400">Del enjambre total</p>
        </Card>
      </div>
    </div>
  );
}
