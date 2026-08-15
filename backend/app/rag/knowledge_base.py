"""
Base de Conocimiento Institucional para SON-IA (Integratel).

Contiene documentos canónicos indexables en la base vectorial (RAG):
1. Catálogo de Planes y Servicios B2B (Fibra, Dúo, Móvil Control/Abierto, Roaming).
2. Políticas de Cobranza y Facturación (Ciclos 15/31, moratorias TAMN, etapas de mora).
3. Normativas Fiscales SUNAT y Políticas de Reclamos (Recibo tipo 14, IGV 18%, plazos).
4. Procedimientos de Pago y Canales de Atención.
"""

from typing import List, Dict, Any

KNOWLEDGE_DOCUMENTS: List[Dict[str, Any]] = [
    # =========================================================================
    # CATÁLOGO DE PLANES Y SERVICIOS B2B
    # =========================================================================
    {
        "id": "plan_fibra_optica_b2b",
        "title": "Plan Fibra Óptica B2B Dedicada",
        "category": "planes_servicios",
        "content": (
            "Servicio de Internet por Fibra Óptica para Empresas (B2B). "
            "Ofrece ancho de banda simétrico garantizado al 100%, IP fija pública incluida, "
            "SLA de disponibilidad de 99.85% y soporte técnico prioritario 24/7. "
            "Tarifas estándar: Fibra 200 Mbps (S/ 1,200.00 + IGV), Fibra 500 Mbps (S/ 2,500.00 + IGV), "
            "Fibra 1 Gbps (S/ 4,200.00 + IGV). Permanencia mínima contractual: 12 meses."
        ),
        "metadata": {
            "producto": "Fibra Óptica B2B",
            "categoria": "Internet Fijo",
            "segmento": "B2B",
            "sla": "99.85%",
        }
    },
    {
        "id": "plan_voz_duo_ctrl",
        "title": "Movistar Voz Dúo Control Empresarial",
        "category": "planes_servicios",
        "content": (
            "Plan Dúo Plano que integra Telefonía Fija Digital con Internet Empresarial. "
            "Incluye minutos ilimitados a destinos fijos y móviles nacionales, central virtual básica, "
            "y conexión de banda ancha de respaldo. "
            "Cargo fijo mensual promedio: S/ 150.00 a S/ 350.00 + IGV según velocidad elegida. "
            "Ciclos de facturación habituales: Día 15 o Día 31 de cada mes."
        ),
        "metadata": {
            "producto": "Voz Dúo Control",
            "categoria": "Telefonia e Internet",
            "segmento": "B2B / Pyme",
        }
    },
    {
        "id": "plan_movil_b2b_elige_todo",
        "title": "Planes Móviles B2B - Elige Todo y Control",
        "category": "planes_servicios",
        "content": (
            "Planes móviles corporativos para líneas de staff y ejecutivos. "
            "1. Plan Elige Todo+ Empresarial (S/ 56.90 + IGV): Datos ilimitados en alta velocidad hasta 50GB, "
            "minutos y SMS ilimitados, roaming internacional para datos en América Latina incluido. "
            "2. Plan Control Ahorro (S/ 39.90 + IGV): 25GB de datos, minutos ilimitados, consumo controlado sin excedentes. "
            "3. Plan Móvil Abierto Corporativo (S/ 89.90 + IGV): Datos ilimitados sin degradación, minutos internacionales a USA/Canadá. "
            "Todos los planes permiten compartir gigas entre cuentas corporativas autorizadas."
        ),
        "metadata": {
            "producto": "Planta Movil B2B",
            "categoria": "Telefonia Movil",
            "segmento": "B2B",
        }
    },
    {
        "id": "plan_roaming_internacional",
        "title": "Servicio Roaming de Datos Internacional",
        "category": "planes_servicios",
        "content": (
            "Activación de paquetes de datos y voz en el extranjero para líneas corporativas. "
            "Zonas de cobertura: Zona 1 (América y Europa: S/ 30.00 por día o S/ 120.00 por paquete de 5GB semanal), "
            "Zona 2 (Asia y Oceanía: S/ 50.00 por día). "
            "Para evitar cobros involuntarios, las líneas con 'Plan Control' requieren confirmación previa antes de activar roaming."
        ),
        "metadata": {
            "producto": "Roaming Internacional",
            "categoria": "Servicios Adicionales",
            "segmento": "B2B",
        }
    },

    # =========================================================================
    # POLÍTICAS DE COBRANZA, MORA Y TAMN
    # =========================================================================
    {
        "id": "politica_cobranza_etapas_mora",
        "title": "Políticas de Cobranza y Etapas de Mora",
        "category": "politicas_cobranza",
        "content": (
            "Clasificación oficial de etapas de mora en Integratel / SON-IA: "
            "1. Mora Temprana (1 a 7 días de vencido): Recordatorio preventivo amable vía WhatsApp y correo electrónico. "
            "2. Mora Media (8 a 14 días de vencido): Segundo aviso, cálculo de interés compensatorio e inicio de ofertas de facilidades. "
            "3. Mora Tardía (15 a 30 días de vencido): Notificación formal de suspensión temporal de servicio saliente. "
            "4. Mora Crítica (> 30 días de vencido): Suspensión total del servicio, cálculo acumulado TAMN y derivación a gestión legal o cobranza especializada."
        ),
        "metadata": {
            "categoria": "Cobranzas",
            "aplicacion": "Cuentas con facturas vencidas",
        }
    },
    {
        "id": "politica_calculo_tamn",
        "title": "Cálculo de Tasa de Interés Moratorio (TAMN)",
        "category": "politicas_cobranza",
        "content": (
            "El cálculo de intereses moratorios se rige bajo la Tasa Activa en Moneda Nacional (TAMN) "
            "publicada por la Superintendencia de Banca, Seguros y AFP (SBS) del Perú. "
            "Fórmula aplicada por el Motor Simbólico Zero-Hallucination: "
            "Interés Moratorio = Monto Pendiente * ((1 + Tasa_Diaria)^Dias_Vencidos - 1). "
            "Tasa diaria referencial estándar: 0.042% diario (aproximado 15.3% anual según regulación SBS). "
            "Los intereses se calculan a partir del primer día posterior a la fecha de vencimiento consignada en el comprobante."
        ),
        "metadata": {
            "categoria": "TAMN e Intereses",
            "regulacion": "SBS / Banco Central de Reserva del Perú",
        }
    },
    {
        "id": "politica_negociacion_predictiva",
        "title": "Política de Negociación Predictiva y Descuentos",
        "category": "politicas_cobranza",
        "content": (
            "A los clientes en riesgo de impago o con facturas por vencer (T-5 días), el Agente de Negociación "
            "puede generar ofertas preventivas según su score de confianza: "
            "- Score Confianza >= 0.75 (Happy Path): Sin descuento financiero; recordatorio con métodos de pago digitales. "
            "- Score Confianza 0.40 - 0.74 (Warning Path): Descuento por pronto pago entre 5% y 15% condicionado a pago en 48 horas. "
            "- Score Confianza < 0.40 (Unhappy Path): Fraccionamiento en hasta 3 cuotas o condonación de hasta 20% de intereses TAMN. "
            "Cualquier descuento superior al 20% o en facturas > S/ 100,000 requiere autorización en el Centro HITL (Human-in-the-Loop)."
        ),
        "metadata": {
            "categoria": "Negociacion Predictiva",
            "limite_autonomo": "20% maximo descuento",
        }
    },

    # =========================================================================
    # FACTURACIÓN FISCAL, SUNAT Y RECLAMOS
    # =========================================================================
    {
        "id": "normativa_sunat_recibo_tipo_14",
        "title": "Normativa SUNAT: Recibos por Servicios Públicos (Tipo 14) y Facturas (Tipo 01)",
        "category": "facturacion_fiscal",
        "content": (
            "1. Recibo de Servicios Públicos (Tipo 14): Documento electrónico regulado por SUNAT para servicios "
            "de telecomunicaciones, internet y telefonía fija/móvil. Otorga derecho a crédito fiscal de IGV. "
            "2. Impuesto General a las Ventas (IGV): Tasa fija del 18.00% aplicada sobre la base imponible (subtotal). "
            "3. Moneda: Soles Peruanos (PEN - S/) con opción en dólares para contratos específicos. "
            "4. Ciclos de Facturación: Ciclo 15 (emisión día 15, vencimiento día 05 del mes siguiente) y "
            "Ciclo 31 (emisión último día del mes, vencimiento día 20 del mes siguiente)."
        ),
        "metadata": {
            "normativa": "SUNAT Resolucion de Superintendencia N° 123-2020",
            "tipo_comprobante": "Tipo 14 y 01",
            "igv": "18%",
        }
    },
    {
        "id": "politica_atencion_reclamos",
        "title": "Procedimiento de Reclamos y Disputas de Facturación",
        "category": "atencion_cliente",
        "content": (
            "Si un cliente detecta una discrepancia en su factura (ejemplo: prorrateo de días no disfrutados, "
            "cargos por servicios no contratados o falla técnica prolongada): "
            "1. El cliente puede solicitar una explicación automática vía WhatsApp las 24 horas. "
            "2. Si la inconsistencia se confirma (score de validación < 0.80), el sistema emite una Nota de Crédito Electrónica "
            "(Comprobante Tipo 07) para rectificar el monto facturado. "
            "3. Plazo máximo de resolución de disputas: 5 días hábiles conforme a directivas de OSIPTEL."
        ),
        "metadata": {
            "regulador": "OSIPTEL",
            "comprobante_rectificatorio": "Nota de Credito Tipo 07",
        }
    },
    {
        "id": "canales_y_medios_pago",
        "title": "Canales Oficiales y Métodos de Pago Habilitados",
        "category": "procedimientos_pago",
        "content": (
            "Medios de pago autorizados para saldar facturas y acuerdos de negociación: "
            "1. Transferencia Bancaria Interbancaria (BCP, BBVA, Scotiabank, Interbank) indicando RUC/Código de Cliente. "
            "2. Débito Automático en Cuenta o Tarjeta de Crédito Corporativa. "
            "3. Pago Directo por Pasarela Web o enlace seguro de WhatsApp. "
            "4. Agentes autorizados y ventanillas bancarias con Código de Pago de Recaudación Integratel (CP: 49821). "
            "La conciliación bancaria se ejecuta automáticamente en un plazo de 15 a 60 minutos mediante el servicio asíncrono."
        ),
        "metadata": {
            "categoria": "Pagos",
            "codigo_recaudacion": "49821",
            "tiempo_conciliacion": "15-60 min",
        }
    },
]
