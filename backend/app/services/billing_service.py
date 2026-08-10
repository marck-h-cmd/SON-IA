"""
Servicio de Facturación
Lógica de negocio para facturación y clientes
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import structlog

from app.database.models import (
    BSSCliente,
    BSSCuenta,
    BSSFacturaCabecera,
    BSSFacturaDetalle,
    BSSOfertaNegociacion,
)

logger = structlog.get_logger(__name__)


class BillingService:
    """Servicio para operaciones de facturación"""
    
    async def get_facturas(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        estado: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Obtiene lista de facturas con filtros
        """
        query = select(BSSFacturaCabecera)
        
        if estado:
            query = query.where(BSSFacturaCabecera.estado_pago == estado)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        facturas = result.scalars().all()
        
        return [
            {
                "id_factura": f.id_factura,
                "id_cuenta": f.id_cuenta,
                "serie": f.serie,
                "correlativo": f.correlativo,
                "f_emision": f.f_emision.isoformat() if f.f_emision else None,
                "f_vencimiento": f.f_vencimiento.isoformat() if f.f_vencimiento else None,
                "importe_total": float(f.importe_total) if f.importe_total else 0,
                "estado_pago": f.estado_pago,
                "validacion_automatica": f.validacion_automatica,
            }
            for f in facturas
        ]
    
    async def get_factura(
        self,
        db: AsyncSession,
        factura_id: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene detalle completo de una factura
        """
        result = await db.execute(
            select(BSSFacturaCabecera).where(BSSFacturaCabecera.id_factura == factura_id)
        )
        factura = result.scalar_one_or_none()
        
        if not factura:
            return None
        
        # Obtener detalles
        detalles_result = await db.execute(
            select(BSSFacturaDetalle).where(
                BSSFacturaDetalle.id_factura == factura_id
            )
        )
        detalles = detalles_result.scalars().all()
        
        # Obtener ofertas
        ofertas_result = await db.execute(
            select(BSSOfertaNegociacion).where(
                BSSOfertaNegociacion.id_factura == factura_id
            )
        )
        ofertas = ofertas_result.scalars().all()
        
        return {
            "id_factura": factura.id_factura,
            "cuenta": factura.id_cuenta,
            "f_emision": factura.f_emision.isoformat() if factura.f_emision else None,
            "f_vencimiento": factura.f_vencimiento.isoformat() if factura.f_vencimiento else None,
            "subtotal": float(factura.subtotal_gravado) if factura.subtotal_gravado else 0,
            "igv": float(factura.igv_total) if factura.igv_total else 0,
            "total": float(factura.importe_total) if factura.importe_total else 0,
            "estado": factura.estado_pago,
            "validacion_automatica": factura.validacion_automatica,
            "detalles": [
                {
                    "id": d.id_detalle,
                    "concepto": d.concepto,
                    "monto": float(d.monto_linea) if d.monto_linea else 0,
                }
                for d in detalles
            ],
            "ofertas": [
                {
                    "id": o.id_oferta,
                    "descuento": float(o.descuento_ofrecido) if o.descuento_ofrecido else 0,
                    "estado": o.estado,
                }
                for o in ofertas
            ],
        }
    
    async def get_clientes(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        segmento: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Obtiene lista de clientes"""
        query = select(BSSCliente)
        if segmento:
            query = query.where(BSSCliente.segmento == segmento)
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        clientes = result.scalars().all()
        
        return [
            {
                "id_cliente": c.id_cliente,
                "nombre": c.nombre_razon_social,
                "segmento": c.segmento,
                "score_confianza": float(c.score_confianza) if c.score_confianza else 0,
            }
            for c in clientes
        ]
    
    async def get_cliente(
        self,
        db: AsyncSession,
        cliente_id: int,
    ) -> Optional[Dict[str, Any]]:
        """Obtiene detalle de un cliente"""
        result = await db.execute(
            select(BSSCliente).where(BSSCliente.id_cliente == cliente_id)
        )
        cliente = result.scalar_one_or_none()
        
        if not cliente:
            return None
        
        return {
            "id_cliente": cliente.id_cliente,
            "tipo_doc": cliente.tipo_doc,
            "num_doc": cliente.num_doc,
            "nombre": cliente.nombre_razon_social,
            "segmento": cliente.segmento,
            "email": cliente.email_contacto,
            "telefono": cliente.telefono_contacto,
            "score_confianza": float(cliente.score_confianza) if cliente.score_confianza else 0,
        }
    
    async def get_historial_facturas(
        self,
        db: AsyncSession,
        cliente_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Obtiene historial de facturas de un cliente"""
        # Join con cuentas para filtrar por cliente
        query = (
            select(BSSFacturaCabecera)
            .join(BSSCuenta)
            .where(BSSCuenta.id_cliente == cliente_id)
            .offset(skip)
            .limit(limit)
        )
        
        result = await db.execute(query)
        facturas = result.scalars().all()
        
        return [
            {
                "id_factura": f.id_factura,
                "f_emision": f.f_emision.isoformat() if f.f_emision else None,
                "total": float(f.importe_total) if f.importe_total else 0,
                "estado": f.estado_pago,
            }
            for f in facturas
        ]
    
    async def get_score_cliente(
        self,
        db: AsyncSession,
        cliente_id: int,
    ) -> Optional[Dict[str, Any]]:
        """Obtiene score de confianza del cliente"""
        result = await db.execute(
            select(BSSCliente).where(BSSCliente.id_cliente == cliente_id)
        )
        cliente = result.scalar_one_or_none()
        
        if not cliente:
            return None
        
        return {
            "cliente_id": cliente.id_cliente,
            "score": float(cliente.score_confianza) if cliente.score_confianza else 0,
            "es_confiable": float(cliente.score_confianza or 0) >= 0.80,
        }
    
    async def validar_factura_manual(
        self,
        db: AsyncSession,
        factura_id: int,
    ) -> bool:
        """Valida manualmente una factura"""
        result = await db.execute(
            select(BSSFacturaCabecera).where(BSSFacturaCabecera.id_factura == factura_id)
        )
        factura = result.scalar_one_or_none()
        
        if not factura:
            return False
        
        factura.validacion_automatica = True
        factura.estado_pago = "Pendiente"
        await db.commit()
        
        return True
    
    async def get_ofertas(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
        estado: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Obtiene ofertas de negociación"""
        query = select(BSSOfertaNegociacion)
        if estado:
            query = query.where(BSSOfertaNegociacion.estado == estado)
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        ofertas = result.scalars().all()
        
        return [
            {
                "id_oferta": o.id_oferta,
                "id_factura": o.id_factura,
                "descuento": float(o.descuento_ofrecido) if o.descuento_ofrecido else 0,
                "estado": o.estado,
            }
            for o in ofertas
        ]
    
    async def aceptar_oferta(self, db: AsyncSession, oferta_id: int) -> bool:
        """Acepta una oferta de negociación"""
        result = await db.execute(
            select(BSSOfertaNegociacion).where(BSSOfertaNegociacion.id_oferta == oferta_id)
        )
        oferta = result.scalar_one_or_none()
        
        if not oferta:
            return False
        
        oferta.estado = "aceptada"
        await db.commit()
        return True
    
    async def rechazar_oferta(self, db: AsyncSession, oferta_id: int) -> bool:
        """Rechaza una oferta de negociación"""
        result = await db.execute(
            select(BSSOfertaNegociacion).where(BSSOfertaNegociacion.id_oferta == oferta_id)
        )
        oferta = result.scalar_one_or_none()
        
        if not oferta:
            return False
        
        oferta.estado = "rechazada"
        await db.commit()
        return True