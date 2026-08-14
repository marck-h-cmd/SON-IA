import { apiClient } from './api';
import { Cliente, ClientePerfil, Factura, ListPaginada } from '@/types/api';

/**
 * Clients Service - Endpoints for client management and information
 */

export const clientsService = {
  /**
   * Get paginated list of clients
   */
  async getClientes(
    skip: number = 0,
    limit: number = 10,
    segmento?: 'B2B' | 'B2C' | 'Gobierno'
  ): Promise<ListPaginada<Cliente>> {
    const params: Record<string, unknown> = { skip, limit };
    if (segmento) params.segmento = segmento;
    const response = await apiClient.get('/clients', { params });
    return response.data;
  },

  /**
   * Get client profile with detailed information
   */
  async getClientePerfil(clienteId: string): Promise<ClientePerfil> {
    const response = await apiClient.get(`/clients/${clienteId}`);
    return response.data;
  },

  /**
   * Get client invoice history
   */
  async getHistorialFacturas(
    clienteId: string,
    skip: number = 0,
    limit: number = 10
  ): Promise<ListPaginada<Factura>> {
    const params = { skip, limit };
    const response = await apiClient.get(`/clients/${clienteId}/historial-facturas`, { params });
    return response.data;
  },

  /**
   * Get client confidence score
   */
  async getClienteScore(clienteId: string): Promise<{ score: number; clasificacion: string }> {
    const response = await apiClient.get(`/clients/${clienteId}/score`);
    return response.data;
  },
};

export default clientsService;
