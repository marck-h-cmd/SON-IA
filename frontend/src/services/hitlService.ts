import { apiClient } from './api';
import { SolicitudHITL, MetricasHITL, ListPaginada } from '@/types/api';

/**
 * HITL Service - Human-in-the-Loop Approval Center
 */

export const hitlService = {
  /**
   * Obtiene lista paginada de solicitudes HITL
   */
  async getSolicitudes(
    skip: number = 0,
    limit: number = 10,
    estado?: 'pendiente' | 'aprobada' | 'rechazada'
  ): Promise<ListPaginada<SolicitudHITL>> {
    const params: Record<string, unknown> = { skip, limit };
    if (estado) params.estado = estado;
    const response = await apiClient.get('/hitl/solicitudes', { params });
    return response.data;
  },

  /**
   * Obtiene el detalle de una solicitud HITL
   */
  async getSolicitudDetalle(solicitudId: string): Promise<SolicitudHITL> {
    const response = await apiClient.get(`/hitl/solicitudes/${solicitudId}`);
    return response.data;
  },

  /**
   * Aprueba una solicitud HITL
   */
  async aprobarSolicitud(
    solicitudId: string,
    notas?: string,
    supervisorNombre: string = 'Supervisor HITL'
  ): Promise<{ status: string; message: string; solicitud_id: string; estado: string }> {
    const response = await apiClient.post(`/hitl/solicitudes/${solicitudId}/aprobar`, {
      notas,
      supervisor_nombre: supervisorNombre,
    });
    return response.data;
  },

  /**
   * Rechaza una solicitud HITL
   */
  async rechazarSolicitud(
    solicitudId: string,
    notas?: string,
    supervisorNombre: string = 'Supervisor HITL'
  ): Promise<{ status: string; message: string; solicitud_id: string; estado: string }> {
    const response = await apiClient.post(`/hitl/solicitudes/${solicitudId}/rechazar`, {
      notas,
      supervisor_nombre: supervisorNombre,
    });
    return response.data;
  },

  /**
   * Obtiene métricas del centro de aprobaciones HITL
   */
  async getMetricas(): Promise<MetricasHITL> {
    const response = await apiClient.get('/hitl/metricas');
    return response.data;
  },
};
