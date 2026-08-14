import { apiClient } from './api';
import { OfertaNegociacion, OfertaDetalle, TasaAceptacion, ListPaginada } from '@/types/api';

/**
 * Negotiations Service - Endpoints for negotiation and offers management
 */

export const negotiationsService = {
  /**
   * Get paginated list of negotiation offers
   */
  async getOfertas(
    skip: number = 0,
    limit: number = 10,
    estado?: 'pendiente' | 'aceptada' | 'rechazada' | 'expirada'
  ): Promise<ListPaginada<OfertaNegociacion>> {
    const params: Record<string, unknown> = { skip, limit };
    if (estado) params.estado = estado;
    const response = await apiClient.get('/negotiations/ofertas', { params });
    return response.data;
  },

  /**
   * Get offer details
   */
  async getOfertaDetalle(ofertaId: string): Promise<OfertaDetalle> {
    const response = await apiClient.get(`/negotiations/ofertas/${ofertaId}`);
    return response.data;
  },

  /**
   * Accept negotiation offer
   */
  async aceptarOferta(ofertaId: string): Promise<{ status: string; mensaje: string }> {
    const response = await apiClient.post(`/negotiations/ofertas/${ofertaId}/aceptar`);
    return response.data;
  },

  /**
   * Reject negotiation offer
   */
  async rechazarOferta(ofertaId: string, razon?: string): Promise<{ status: string; mensaje: string }> {
    const params = razon ? { razon } : {};
    const response = await apiClient.post(`/negotiations/ofertas/${ofertaId}/rechazar`, {}, { params });
    return response.data;
  },

  /**
   * Get offer acceptance rate
   */
  async getTasaAceptacion(): Promise<TasaAceptacion> {
    const response = await apiClient.get('/negotiations/tasa-aceptacion');
    return response.data;
  },
};

export default negotiationsService;
