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

  /**
   * Obtiene metadatos de facturación electrónica SUNAT UBL 2.1
   */
  async getSunatInfo(facturaId: string): Promise<{
    factura_id: string;
    tipo_comprobante: string;
    tipo_nombre: string;
    serie: string;
    correlativo: string;
    hash_sha256: string;
    qr_cadena: string;
    estado_sunat: string;
    xml_filename: string;
  }> {
    const response = await apiClient.get(`/billing/facturas/${facturaId}/sunat-info`);
    return response.data;
  },

  /**
   * Descarga archivo XML SUNAT UBL 2.1
   */
  async descargarXml(facturaId: string): Promise<Blob> {
    const response = await apiClient.get(`/billing/facturas/${facturaId}/xml`, {
      responseType: 'blob',
    });
    return response.data;
  },

  /**
   * Descarga archivo PDF Oficial Movistar con diseño corporativo
   */
  async descargarPdf(facturaId: string): Promise<Blob> {
    const response = await apiClient.get(`/billing/facturas/${facturaId}/pdf`, {
      responseType: 'blob',
    });
    return response.data;
  },

  /**
   * Envía el recibo PDF oficial por correo electrónico
   */
  async enviarEmailFactura(
    facturaId: string,
    emailDestino?: string
  ): Promise<{ status: string; mensaje: string; destinatario: string }> {
    const params = emailDestino ? { email_destino: emailDestino } : {};
    const response = await apiClient.post(
      `/billing/facturas/${facturaId}/enviar-email`,
      {},
      { params }
    );
    return response.data;
  },
};


export default billingService;
