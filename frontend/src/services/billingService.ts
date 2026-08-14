import { apiClient } from './api';
import { Factura, FacturaDetalle, ListPaginada } from '@/types/api';

/**
 * Billing Service - Endpoints for invoicing operations
 */

export const billingService = {
  /**
   * Get paginated list of invoices
   */
  async getFacturas(
    skip: number = 0,
    limit: number = 10,
    estado?: 'Pendiente' | 'Pagado' | 'Vencido'
  ): Promise<ListPaginada<Factura>> {
    const params: Record<string, unknown> = { skip, limit };
    if (estado) params.estado = estado;
    const response = await apiClient.get('/billing/facturas', { params });
    return response.data;
  },

  /**
   * Get invoice details
   */
  async getFacturaDetalle(facturaId: string): Promise<FacturaDetalle> {
    const response = await apiClient.get(`/billing/facturas/${facturaId}`);
    return response.data;
  },

  /**
   * Execute billing cycle
   */
  async ejecutarCiclo(
    cicloId: string,
    forceReview: boolean = false
  ): Promise<{ status: string; ciclo_id: string; mensaje: string }> {
    const params = { ciclo_id: cicloId, force_review: forceReview };
    const response = await apiClient.post('/billing/ciclos/ejecutar', {}, { params });
    return response.data;
  },
};

export default billingService;
