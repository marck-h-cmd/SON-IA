"""
Modelos SQLAlchemy para SON-IA
Representan las tablas definidas en la Sección 4 de la documentación
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
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Clase base para todos los modelos"""
    pass


# ============================================
# BSS - Business Support System
# ============================================

class BSSCliente(Base):
    """
    1. MAESTRA DE CLIENTES (BSS)
    Almacena información comercial y perfil de confianza
    """
    __tablename__ = "bss_clientes"
    
    id_cliente: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    tipo_doc: Mapped[str] = mapped_column(String(2), nullable=False, comment="1=DNI, 6=RUC")
    num_doc: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    nombre_razon_social: Mapped[str] = mapped_column(String(255), nullable=False)
    segmento: Mapped[Optional[str]] = mapped_column(String(50))
    email_contacto: Mapped[Optional[str]] = mapped_column(String(100))
    telefono_contacto: Mapped[Optional[str]] = mapped_column(String(20))
    score_confianza: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=0.80, comment="Perfil de confianza (0-1)"
    )
    
    # Relaciones
    cuentas: Mapped[List["BSSCuenta"]] = relationship(back_populates="cliente", lazy="selectin")
    historial_pagos: Mapped[List["BSSHistorialPago"]] = relationship(back_populates="cliente", lazy="selectin")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Cliente {self.id_cliente}: {self.nombre_razon_social}>"


class BSSCuenta(Base):
    """
    2. CUENTAS DE FACTURACIÓN (BSS)
    Configuración de facturación por cliente
    """
    __tablename__ = "bss_cuentas"
    
    id_cuenta: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    id_cliente: Mapped[int] = mapped_column(ForeignKey("bss_clientes.id_cliente"), nullable=False)
    ciclo_facturacion: Mapped[int] = mapped_column(Integer, nullable=False, comment="Día del mes")
    metodo_pago: Mapped[Optional[str]] = mapped_column(String(50))
    estado_cuenta: Mapped[Optional[str]] = mapped_column(String(20))
    limite_credito: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    dias_plazo_estandar: Mapped[int] = mapped_column(Integer, default=8)
    
    # Relaciones
    cliente: Mapped["BSSCliente"] = relationship(back_populates="cuentas")
    servicios: Mapped[List["OSSPlanta"]] = relationship(back_populates="cuenta", lazy="selectin")
    facturas: Mapped[List["BSSFacturaCabecera"]] = relationship(back_populates="cuenta", lazy="selectin")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


# ============================================
# OSS - Operations Support System (Planta)
# ============================================

class OSSPlanta(Base):
    """
    3. MAESTRA DE PLANTA - SERVICIOS (OSS)
    Servicios técnicos activos del cliente
    """
    __tablename__ = "oss_planta"
    
    id_servicio: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    id_cuenta: Mapped[int] = mapped_column(ForeignKey("bss_cuentas.id_cuenta"), nullable=False)
    tecnologia: Mapped[Optional[str]] = mapped_column(String(20))
    identificador_recurso: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    cargo_fijo_mensual: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    fecha_alta: Mapped[date] = mapped_column(Date, nullable=False)
    estado_servicio: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Relaciones
    cuenta: Mapped["BSSCuenta"] = relationship(back_populates="servicios")
    detalles_factura: Mapped[List["BSSFacturaDetalle"]] = relationship(back_populates="servicio")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


# ============================================
# Históricos y Transacciones
# ============================================

class BSSHistorialPago(Base):
    """
    4. HISTÓRICO DE COMPORTAMIENTO DE PAGO
    Registro de pagos para cálculo de score
    """
    __tablename__ = "bss_historial_pagos"
    
    id_historial: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_cliente: Mapped[int] = mapped_column(ForeignKey("bss_clientes.id_cliente"), nullable=False)
    fecha_vencimiento: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_pago: Mapped[Optional[date]] = mapped_column(Date)
    dias_mora: Mapped[Optional[int]] = mapped_column(Integer)
    monto_pagado: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    fue_disputado: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relaciones
    cliente: Mapped["BSSCliente"] = relationship(back_populates="historial_pagos")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class BSSFacturaCabecera(Base):
    """
    5. TRANSACCIONES DE FACTURACIÓN (CABECERA)
    """
    __tablename__ = "bss_factura_cabecera"
    
    id_factura: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    id_cuenta: Mapped[int] = mapped_column(ForeignKey("bss_cuentas.id_cuenta"), nullable=False)
    serie: Mapped[str] = mapped_column(String(4), nullable=False)
    correlativo: Mapped[int] = mapped_column(Integer, nullable=False)
    f_emision: Mapped[date] = mapped_column(Date, nullable=False)
    f_vencimiento: Mapped[date] = mapped_column(Date, nullable=False)
    subtotal_gravado: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    igv_total: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    importe_total: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    estado_pago: Mapped[Optional[str]] = mapped_column(String(20))
    validacion_automatica: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relaciones
    cuenta: Mapped["BSSCuenta"] = relationship(back_populates="facturas")
    detalles: Mapped[List["BSSFacturaDetalle"]] = relationship(back_populates="factura", lazy="selectin")
    ofertas: Mapped[List["BSSOfertaNegociacion"]] = relationship(back_populates="factura", lazy="selectin")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("serie", "correlativo", name="uq_serie_correlativo"),
    )
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class BSSFacturaDetalle(Base):
    """
    6. DETALLE DE SALDOS Y REGISTRO DE VENTA
    """
    __tablename__ = "bss_factura_detalle"
    
    id_detalle: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_factura: Mapped[int] = mapped_column(ForeignKey("bss_factura_cabecera.id_factura"), nullable=False)
    id_servicio: Mapped[int] = mapped_column(ForeignKey("oss_planta.id_servicio"), nullable=False)
    concepto: Mapped[Optional[str]] = mapped_column(String(100))
    periodo_inicio: Mapped[Optional[date]] = mapped_column(Date)
    periodo_fin: Mapped[Optional[date]] = mapped_column(Date)
    monto_linea: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    
    # Relaciones
    factura: Mapped["BSSFacturaCabecera"] = relationship(back_populates="detalles")
    servicio: Mapped["OSSPlanta"] = relationship(back_populates="detalles_factura")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class BSSOfertaNegociacion(Base):
    """
    7. OFERTAS DE NEGOCIACIÓN
    Registro de ofertas predictivas
    """
    __tablename__ = "bss_ofertas_negociacion"
    
    id_oferta: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_factura: Mapped[int] = mapped_column(ForeignKey("bss_factura_cabecera.id_factura"), nullable=False)
    fecha_oferta: Mapped[Optional[date]] = mapped_column(Date)
    descuento_ofrecido: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    nuevo_plazo_dias: Mapped[Optional[int]] = mapped_column(Integer)
    fecha_limite_aceptacion: Mapped[Optional[date]] = mapped_column(Date)
    estado: Mapped[Optional[str]] = mapped_column(String(20), comment="pendiente, aceptada, rechazada, expirada")
    
    # Relaciones
    factura: Mapped["BSSFacturaCabecera"] = relationship(back_populates="ofertas")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())