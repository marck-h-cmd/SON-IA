"""
Schemas Pydantic para validación de datos
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


# ============================================
# Cliente
# ============================================
class ClienteBase(BaseModel):
    tipo_doc: str = Field(..., pattern="^(1|6)$", description="1=DNI, 6=RUC")
    num_doc: str = Field(..., min_length=8, max_length=20)
    nombre_razon_social: str = Field(..., min_length=1, max_length=255)
    segmento: Optional[str] = Field(None, max_length=50)
    email_contacto: Optional[EmailStr] = None
    telefono_contacto: Optional[str] = Field(None, max_length=20)


class ClienteCreate(ClienteBase):
    id_cliente: int


class ClienteResponse(ClienteBase):
    id_cliente: int
    score_confianza: Decimal = Field(default=Decimal("0.80"))
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# Factura
# ============================================
class FacturaDetalleCreate(BaseModel):
    id_servicio: int
    concepto: Optional[str] = None
    periodo_inicio: date
    periodo_fin: date
    monto_linea: Decimal


class FacturaCreate(BaseModel):
    id_factura: int
    id_cuenta: int
    serie: str = Field(..., max_length=4)
    correlativo: int
    f_emision: date
    f_vencimiento: date
    detalles: List[FacturaDetalleCreate]


class FacturaResponse(BaseModel):
    id_factura: int
    id_cuenta: int
    serie: str
    correlativo: int
    f_emision: date
    f_vencimiento: date
    subtotal_gravado: Optional[Decimal] = None
    igv_total: Optional[Decimal] = None
    importe_total: Optional[Decimal] = None
    estado_pago: Optional[str] = None
    validacion_automatica: bool = False
    
    class Config:
        from_attributes = True


# ============================================
# Oferta de Negociación
# ============================================
class OfertaCreate(BaseModel):
    id_factura: int
    descuento_ofrecido: Decimal = Field(..., ge=0, le=100)
    nuevo_plazo_dias: int = Field(..., gt=0)
    fecha_limite_aceptacion: date


class OfertaResponse(BaseModel):
    id_oferta: int
    id_factura: int
    descuento_ofrecido: Decimal
    estado: str
    
    class Config:
        from_attributes = True


# ============================================
# Métricas Dashboard
# ============================================
class DashboardMetrics(BaseModel):
    facturas_procesadas_hoy: int
    monto_total_recaudado: Decimal
    indice_morosidad: float
    ofertas_activas: int
    facturas_pendientes_revision: int


# ============================================
# Health Check
# ============================================
class HealthResponse(BaseModel):
    status: str
    app: str
    version: str