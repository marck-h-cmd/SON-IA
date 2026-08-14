/**
 * API Types and Interfaces for SON-IA Dashboard
 */

// ============ DASHBOARD TYPES ============
export interface DashboardMetrics {
  facturas_procesadas_hoy: number;
  monto_total_recaudado: number;
  indice_morosidad: number;
  ofertas_activas: number;
  facturas_pendientes_revision: number;
  tasa_aceptacion_ofertas: number;
  tiempo_promedio_emision_seg: number;
  agentes_activos: number;
  timestamp: string; // ISO 8601
}

export interface AgentState {
  estado: "activo" | "idle" | "error";
  modelo: string;
  proveedor: "Groq" | "Google" | "OpenAI";
  última_ejecución: string; // ISO 8601
  tareas_procesadas: number;
  tasa_error: number;
}

export interface AgentesEstado {
  supervisor: AgentState;
  billing: AgentState;
  collections: AgentState;
  negotiation: AgentState;
  customer: AgentState;
  classifier: AgentState;
  learning: AgentState;
}

// ============ BILLING TYPES ============
export interface Factura {
  id: string;
  cliente_id: string;
  cliente_nombre: string;
  cliente_ruc: string;
  monto: number;
  fecha_emision: string; // YYYY-MM-DD
  fecha_vencimiento: string; // YYYY-MM-DD
  estado: "Pendiente" | "Pagado" | "Vencido";
  numero_factura: string;
  periodo: string;
}

export interface FacturaDetalle {
  id: string;
  numero_factura: string;
  cliente: ClienteInfo;
  monto_total: number;
  igv: number;
  subtotal: number;
  fecha_emision: string;
  fecha_vencimiento: string;
  estado: string;
  lineas: LineaFactura[];
  ofertas: OfertaNegociacion[];
  pagos_parciales: PagoParcial[];
}

export interface LineaFactura {
  id: string;
  descripcion: string;
  servicio: string;
  cantidad: number;
  precio_unitario: number;
  subtotal: number;
}

export interface PagoParcial {
  id: string;
  fecha: string;
  monto: number;
  referencia: string;
}

export interface ListPaginada<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

// ============ CLIENT TYPES ============
export interface Cliente {
  id: string;
  ruc: string;
  razon_social: string;
  segmento: "B2B" | "B2C" | "Gobierno";
  telefono: string;
  email: string;
  score_confianza: number; // 0-100
  estado: "activo" | "inactivo";
}

export interface ClienteInfo {
  id: string;
  ruc: string;
  razon_social: string;
  email: string;
  telefono: string;
  direccion: string;
}

export interface ClientePerfil {
  cliente: Cliente;
  score_confianza: number;
  explicacion_score: ScoreExplicacion;
  cuentas: CuentaServicio[];
  servicios_activos: ServicioActivo[];
  facturas_totales: number;
  facturas_vencidas: number;
  monto_vencido: number;
}

export interface ScoreExplicacion {
  factores: ScoringFactor[];
  puntuacion_final: number;
  clasificacion: string;
}

export interface ScoringFactor {
  nombre: string;
  valor: number;
  peso: number;
  impacto: "positivo" | "negativo";
}

export interface CuentaServicio {
  id: string;
  numero_cuenta: string;
  tipo_servicio: string;
  estado: string;
  fecha_activacion: string;
}

export interface ServicioActivo {
  id: string;
  nombre: string;
  estado: "activo" | "suspendido";
  fecha_contratacion: string;
}

// ============ COLLECTIONS TYPES ============
export interface FacturaVencida {
  id: string;
  numero_factura: string;
  cliente_nombre: string;
  cliente_id: string;
  monto_original: number;
  monto_pendiente: number;
  dias_vencido: number;
  etapa_mora: "temprana" | "media" | "tardia" | "critica";
  fecha_vencimiento: string;
  tamn_calculado: number;
}

export interface CarteraMetricas {
  total_cartera_vencida: number;
  cantidad_facturas_vencidas: number;
  tamn_acumulado: number;
  tendencia_vs_mes_anterior: number; // Porcentaje de cambio
}

export interface TAMNCalculo {
  factura_id: string;
  monto_original: number;
  tasa_moratoria: number;
  dias_vencido: number;
  tamn: number;
  monto_interes: number;
}

export interface PagoRegistro {
  factura_id: string;
  monto_pagado: number;
  fecha_pago: string;
  referencia: string;
  metodo: "transferencia" | "deposito" | "efectivo" | "cheque";
}

// ============ NEGOTIATION TYPES ============
export interface OfertaNegociacion {
  id: string;
  factura_id: string;
  cliente_id: string;
  cliente_nombre: string;
  monto_original: number;
  descuento_ofrecido: number; // Porcentaje
  nuevo_plazo_dias: number;
  estado: "pendiente" | "aceptada" | "rechazada" | "expirada";
  fecha_creacion: string;
  fecha_expiracion: string;
  fecha_respuesta?: string;
}

export interface OfertaDetalle extends OfertaNegociacion {
  monto_final: number;
  ahorro_cliente: number;
  justificacion: string;
}

export interface TasaAceptacion {
  total_ofertas: number;
  ofertas_aceptadas: number;
  ofertas_rechazadas: number;
  ofertas_expiradas: number;
  tasa_aceptacion: number; // Porcentaje
}

// ============ AUDIT TYPES ============
export interface LogAuditoria {
  id: string;
  usuario_id: string;
  usuario_nombre: string;
  tipo_accion: string;
  descripcion: string;
  entidad_tipo: string;
  entidad_id: string;
  cambios_anteriores?: Record<string, unknown>;
  cambios_nuevos?: Record<string, unknown>;
  fecha_accion: string; // ISO 8601
  ip_origen: string;
  resultado: "exitoso" | "fallido";
}

// ============ API RESPONSE TYPES ============
export interface ApiResponse<T> {
  data: T;
  timestamp: string;
  status: "success" | "error";
  message?: string;
}

export interface ApiError {
  status: number;
  message: string;
  detail?: string;
}

// ============ HEALTH CHECK ============
export interface HealthResponse {
  status: "healthy" | "degraded" | "unhealthy";
  timestamp: string;
}

export interface DetailedHealthResponse {
  status: "healthy" | "degraded" | "unhealthy";
  components: {
    database: ComponentStatus;
    redis: ComponentStatus;
    groq: ComponentStatus;
    gemini: ComponentStatus;
  };
  timestamp: string;
}

export interface ComponentStatus {
  status: "ok" | "error";
  response_time_ms: number;
  message?: string;
}
