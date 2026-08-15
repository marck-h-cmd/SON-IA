"""
Modelos SQLAlchemy para SON-IA (Adaptados al Dataset Real B2B)
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass

# ============================================
# CLIENTES
# ============================================

class BSSCliente(Base):
    __tablename__ = "bss_clientes"
    
    numero_identificacion_fiscal: Mapped[str] = mapped_column(String(20), primary_key=True)
    tipo_documento: Mapped[Optional[str]] = mapped_column(String(10))
    razon_social: Mapped[Optional[str]] = mapped_column(String(255))
    segmento_pais: Mapped[Optional[str]] = mapped_column(String(50))
    sunat_estado_ruc: Mapped[Optional[str]] = mapped_column(String(50))
    sunat_estado_contribuyente: Mapped[Optional[str]] = mapped_column(String(50))
    sunat_departamento: Mapped[Optional[str]] = mapped_column(String(100))
    sunat_provincia: Mapped[Optional[str]] = mapped_column(String(100))
    sunat_distrito: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Virtual fields for agents compatibility
    score_confianza: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0.80)

    # Teléfono de contacto (WhatsApp) - usado por la integración con OpenWA
    numero_celular: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Relationships
    planta_fija: Mapped[List["OSSPlantaFija"]] = relationship(back_populates="cliente")
    planta_movil: Mapped[List["OSSPlantaMovil"]] = relationship(back_populates="cliente")
    facturas: Mapped[List["BSSFactura"]] = relationship(back_populates="cliente")
    pagos: Mapped[List["BSSPago"]] = relationship(back_populates="cliente")
    notas_credito: Mapped[List["BSSNotaCredito"]] = relationship(back_populates="cliente")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

# ============================================
# PLANTA (SERVICIOS)
# ============================================

class OSSPlantaFija(Base):
    __tablename__ = "oss_planta_fija"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    numero_identificacion_fiscal: Mapped[str] = mapped_column(ForeignKey("bss_clientes.numero_identificacion_fiscal"))
    cod_cliente: Mapped[Optional[str]] = mapped_column(String(50))
    cod_cuenta: Mapped[Optional[str]] = mapped_column(String(50))
    ciclo: Mapped[Optional[str]] = mapped_column(String(20))
    fecha_alta: Mapped[Optional[date]] = mapped_column(Date)
    status_desc: Mapped[Optional[str]] = mapped_column(String(50))
    ln_plan_desc: Mapped[Optional[str]] = mapped_column(String(255))
    ln_subscriber_status_desc: Mapped[Optional[str]] = mapped_column(String(50))
    int_plan_desc: Mapped[Optional[str]] = mapped_column(String(255))
    int_original_activation_date: Mapped[Optional[date]] = mapped_column(Date)
    tv_plan_desc: Mapped[Optional[str]] = mapped_column(String(255))
    tv_original_activation_date: Mapped[Optional[date]] = mapped_column(Date)
    tv_tecnologia: Mapped[Optional[str]] = mapped_column(String(50))
    tv_service_technology: Mapped[Optional[str]] = mapped_column(String(50))
    tv_subscriber_status_desc: Mapped[Optional[str]] = mapped_column(String(50))
    sub_main_offer_desc: Mapped[Optional[str]] = mapped_column(String(255))
    int_subscriber_status_desc: Mapped[Optional[str]] = mapped_column(String(50))
    sub_main_offer_trioduo: Mapped[Optional[str]] = mapped_column(String(100))
    es_movistartotal: Mapped[Optional[str]] = mapped_column(String(10))
    descuento_promocion_producto_desc: Mapped[Optional[str]] = mapped_column(String(255))
    decos_cantidad: Mapped[Optional[str]] = mapped_column(String(20))
    
    cliente: Mapped["BSSCliente"] = relationship(back_populates="planta_fija")

class OSSPlantaMovil(Base):
    __tablename__ = "oss_planta_movil"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    numero_identificacion_fiscal: Mapped[str] = mapped_column(ForeignKey("bss_clientes.numero_identificacion_fiscal"))
    cod_cliente: Mapped[Optional[str]] = mapped_column(String(50))
    cod_cuenta: Mapped[Optional[str]] = mapped_column(String(50))
    flag_staff: Mapped[Optional[str]] = mapped_column(String(10))
    producto: Mapped[Optional[str]] = mapped_column(String(100))
    fecha_alta: Mapped[Optional[date]] = mapped_column(Date)
    estado_linea: Mapped[Optional[str]] = mapped_column(String(50))
    estado_telefono_razon: Mapped[Optional[str]] = mapped_column(String(100))
    tipo_linea: Mapped[Optional[str]] = mapped_column(String(50))
    product_desc: Mapped[Optional[str]] = mapped_column(String(255))
    plan_principal: Mapped[Optional[str]] = mapped_column(String(255))
    cant_promociones: Mapped[Optional[str]] = mapped_column(String(50))
    prom_dscto: Mapped[Optional[str]] = mapped_column(String(255))
    plan_roaming_datos: Mapped[Optional[str]] = mapped_column(String(255))
    fecha_inicio_permanencia: Mapped[Optional[date]] = mapped_column(Date)
    fecha_fin_permanencia: Mapped[Optional[date]] = mapped_column(Date)
    meses_permanencia: Mapped[Optional[str]] = mapped_column(String(20))
    
    cliente: Mapped["BSSCliente"] = relationship(back_populates="planta_movil")

# ============================================
# FACTURACIÓN Y PAGOS
# ============================================

class BSSFactura(Base):
    __tablename__ = "bss_facturas"
    
    nro_doc_fiscal: Mapped[str] = mapped_column(String(50), primary_key=True)
    numero_identificacion_fiscal: Mapped[str] = mapped_column(ForeignKey("bss_clientes.numero_identificacion_fiscal"))
    cod_cliente: Mapped[Optional[str]] = mapped_column(String(50))
    cod_cuenta: Mapped[Optional[str]] = mapped_column(String(50))
    fuente: Mapped[Optional[str]] = mapped_column(String(100))
    sistema: Mapped[Optional[str]] = mapped_column(String(50))
    fecha_emision: Mapped[Optional[date]] = mapped_column(Date)
    fecha_vto: Mapped[Optional[date]] = mapped_column(Date)
    moneda: Mapped[Optional[str]] = mapped_column(String(10))
    charge_net_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    charge_igv_invoice: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    charge_total_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    
    cliente: Mapped["BSSCliente"] = relationship(back_populates="facturas")

class BSSPago(Base):
    __tablename__ = "bss_pagos"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    factura_afectada: Mapped[str] = mapped_column(String(50), index=True)
    numero_identificacion_fiscal: Mapped[str] = mapped_column(ForeignKey("bss_clientes.numero_identificacion_fiscal"))
    tipo_documento: Mapped[Optional[str]] = mapped_column(String(50))
    cod_cliente: Mapped[Optional[str]] = mapped_column(String(50))
    cod_cuenta: Mapped[Optional[str]] = mapped_column(String(50))
    sistema: Mapped[Optional[str]] = mapped_column(String(50))
    fecha_pago: Mapped[Optional[date]] = mapped_column(Date)
    moneda_factura: Mapped[Optional[str]] = mapped_column(String(10))
    subtotal: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    igv: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    monto_pagado: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    
    cliente: Mapped["BSSCliente"] = relationship(back_populates="pagos")

class BSSNotaCredito(Base):
    __tablename__ = "bss_notas_credito"
    
    nro_doc_fiscal: Mapped[str] = mapped_column(String(50), primary_key=True)
    numero_identificacion_fiscal: Mapped[str] = mapped_column(ForeignKey("bss_clientes.numero_identificacion_fiscal"))
    factura_afectada: Mapped[str] = mapped_column(String(50), index=True)
    cod_cliente: Mapped[Optional[str]] = mapped_column(String(50))
    cod_cuenta: Mapped[Optional[str]] = mapped_column(String(50))
    fuente: Mapped[Optional[str]] = mapped_column(String(100))
    sistema: Mapped[Optional[str]] = mapped_column(String(50))
    fecha_emision: Mapped[Optional[date]] = mapped_column(Date)
    moneda: Mapped[Optional[str]] = mapped_column(String(10))
    monto_sin_igv: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    subtotal: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    monto: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    
    cliente: Mapped["BSSCliente"] = relationship(back_populates="notas_credito")


# ============================================
# NEGOCIACIÓN
# ============================================

class BSSOfertaNegociacion(Base):
    __tablename__ = "bss_ofertas_negociacion"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    factura_id: Mapped[str] = mapped_column(String(50), index=True)
    numero_identificacion_fiscal: Mapped[str] = mapped_column(String(20), index=True)
    tipo_oferta: Mapped[Optional[str]] = mapped_column(String(50), default="descuento_pronto_pago")
    descuento_porcentaje: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0.0)
    monto_original: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0.0)
    monto_con_descuento: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0.0)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    fecha_expiracion: Mapped[Optional[date]] = mapped_column(Date)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")
    notas: Mapped[Optional[str]] = mapped_column(String(255))


# ============================================
# HUMAN-IN-THE-LOOP (HITL)
# ============================================

class BSSRevisionHITL(Base):
    __tablename__ = "bss_revisiones_hitl"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    solicitud_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    tipo_operacion: Mapped[str] = mapped_column(String(50), default="emision_factura")
    factura_id: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    numero_identificacion_fiscal: Mapped[str] = mapped_column(String(20), index=True)
    cliente_nombre: Mapped[Optional[str]] = mapped_column(String(255))
    monto: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0.0)
    score_confianza: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0.80)
    agente_origen: Mapped[str] = mapped_column(String(50), default="Supervisor Agent")
    motivo_retencion: Mapped[str] = mapped_column(String(255))
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")  # pendiente, aprobada, rechazada
    notas_supervisor: Mapped[Optional[str]] = mapped_column(Text)
    supervisor_responsable: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
