from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

# ============================================
# CLIENTES
# ============================================
class ClienteBase(BaseModel):
    numero_identificacion_fiscal: str = Field(..., max_length=20)
    tipo_documento: Optional[str] = None
    razon_social: Optional[str] = None
    segmento_pais: Optional[str] = None
    sunat_estado_ruc: Optional[str] = None
    sunat_estado_contribuyente: Optional[str] = None
    sunat_departamento: Optional[str] = None
    sunat_provincia: Optional[str] = None
    sunat_distrito: Optional[str] = None

class ClienteCreate(ClienteBase):
    pass

class ClienteResponse(ClienteBase):
    score_confianza: Decimal = Field(default=Decimal("0.80"))
    
    class Config:
        from_attributes = True

# ============================================
# PLANTA (SERVICIOS)
# ============================================
class PlantaFijaBase(BaseModel):
    numero_identificacion_fiscal: str
    cod_cliente: Optional[str] = None
    cod_cuenta: Optional[str] = None
    ciclo: Optional[str] = None
    fecha_alta: Optional[date] = None
    status_desc: Optional[str] = None
    ln_plan_desc: Optional[str] = None
    ln_subscriber_status_desc: Optional[str] = None
    int_plan_desc: Optional[str] = None
    tv_plan_desc: Optional[str] = None
    tv_tecnologia: Optional[str] = None
    sub_main_offer_desc: Optional[str] = None
    decos_cantidad: Optional[str] = None

class PlantaFijaResponse(PlantaFijaBase):
    id: int
    class Config:
        from_attributes = True

class PlantaMovilBase(BaseModel):
    numero_identificacion_fiscal: str
    cod_cliente: Optional[str] = None
    cod_cuenta: Optional[str] = None
    producto: Optional[str] = None
    fecha_alta: Optional[date] = None
    estado_linea: Optional[str] = None
    tipo_linea: Optional[str] = None
    plan_principal: Optional[str] = None
    cant_promociones: Optional[str] = None
    prom_dscto: Optional[str] = None
    fecha_inicio_permanencia: Optional[date] = None
    fecha_fin_permanencia: Optional[date] = None
    meses_permanencia: Optional[str] = None

class PlantaMovilResponse(PlantaMovilBase):
    id: int
    class Config:
        from_attributes = True

# ============================================
# FACTURAS Y PAGOS
# ============================================
class FacturaBase(BaseModel):
    nro_doc_fiscal: str
    numero_identificacion_fiscal: str
    cod_cuenta: Optional[str] = None
    fecha_emision: Optional[date] = None
    fecha_vto: Optional[date] = None
    charge_total_amount: Optional[Decimal] = None
    moneda: Optional[str] = None

class FacturaResponse(FacturaBase):
    class Config:
        from_attributes = True

class PagoBase(BaseModel):
    factura_afectada: str
    numero_identificacion_fiscal: str
    fecha_pago: Optional[date] = None
    monto_pagado: Optional[Decimal] = None
    moneda_factura: Optional[str] = None

class PagoResponse(PagoBase):
    id: int
    class Config:
        from_attributes = True