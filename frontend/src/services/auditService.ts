import { apiClient } from './api';
import { LogAuditoria, ListPaginada } from '@/types/api';

/**
 * Audit Service - Endpoints for audit logs and traceability
 */

export const auditService = {
  /**
   * Get paginated list of audit logs
   */
  async getLogs(
    skip: number = 0,
    limit: number = 10,
    tipoAccion?: string,
    usuarioId?: string,
    fechaDesde?: string,
    fechaHasta?: string,
    search?: string
  ): Promise<ListPaginada<LogAuditoria>> {
    const params: Record<string, unknown> = { skip, limit };
    if (tipoAccion) params.tipo_accion = tipoAccion;
    if (usuarioId) params.usuario_id = usuarioId;
    if (fechaDesde) params.fecha_desde = fechaDesde;
    if (fechaHasta) params.fecha_hasta = fechaHasta;
    if (search) params.search = search;
    const response = await apiClient.get('/audit/logs', { params });
    return response.data;
  },

  /**
   * Get audit log details
   */
  async getLogDetalle(logId: string): Promise<LogAuditoria> {
    const response = await apiClient.get(`/audit/logs/${logId}`);
    return response.data;
  },

  /**
   * Export audit logs as CSV
   */
  async exportarLogs(
    tipoAccion?: string,
    usuarioId?: string,
    fechaDesde?: string,
    fechaHasta?: string,
    search?: string
  ): Promise<Blob> {
    const params: Record<string, unknown> = {};
    if (tipoAccion) params.tipo_accion = tipoAccion;
    if (usuarioId) params.usuario_id = usuarioId;
    if (fechaDesde) params.fecha_desde = fechaDesde;
    if (fechaHasta) params.fecha_hasta = fechaHasta;
    if (search) params.search = search;
    const response = await apiClient.get('/audit/logs/export', {
      params,
      responseType: 'blob',
    });
    return response.data;
  },
};

export default auditService;
