import { apiClient } from './api';
import { FacturaVencida, CarteraMetricas, TAMNCalculo, PagoRegistro, ListPaginada } from '@/types/api';

/**
 * Collections Service - Endpoints for collections and overdue management
 */

export const collectionsService = {
  /**
   * Get paginated list of overdue invoices
   */
  async getFacturasVencidas(
    skip: number = 0,
    limit: number = 10,
    etapa?: 'temprana' | 'media' | 'tardia' | 'critica'
  ): Promise<ListPaginada<FacturaVencida>> {
    const params: Record<string, unknown> = { skip, limit };
    if (etapa) params.etapa = etapa;
    const response = await apiClient.get('/collections/facturas-vencidas', { params });
    return response.data;
  },

  /**
   * Get collections metrics (cartera summary)
   */
  async getCarteraMetricas(): Promise<CarteraMetricas> {
    const response = await apiClient.get('/collections/cartera-metricas');
    return response.data;
  },

  /**
   * Calculate TAMN (Tasa de Interés Moratorio) for an invoice
   */
  async calcularTAMN(facturaId: string): Promise<TAMNCalculo> {
    const response = await apiClient.post(`/collections/calcular-tamn/${facturaId}`);
    return response.data;
  },

  /**
   * Register a payment
   */
  async procesarPago(
    facturaId: string,
    montoPagado: number,
    fechaPago: string,
    referencia?: string,
    metodo: string = 'transferencia'
  ): Promise<{ status: string; mensaje: string; saldo_pendiente: number }> {
    const params = {
      factura_id: facturaId,
      monto_pagado: montoPagado,
      fecha_pago: fechaPago,
      ...(referencia && { referencia }),
      metodo,
    };
    const response = await apiClient.post('/collections/procesar-pago', {}, { params });
    return response.data;
  },
};

export default collectionsService;
