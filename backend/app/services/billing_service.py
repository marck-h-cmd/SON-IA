"""
Servicio de Facturación
Lógica de negocio para facturación y clientes
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date
import structlog

from app.database.models import (
    BSSCliente,
    BSSFactura,
    BSSPago,
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
        query = select(BSSFactura)
        
        # Simple fake state logic based on vto
        if estado == "Vencido":
            query = query.where(BSSFactura.fecha_vto < date.today())
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        facturas = result.scalars().all()
        
        return [
            {
                "id_factura": f.nro_doc_fiscal, # Map for legacy frontend
                "id_cuenta": f.cod_cuenta,
                "f_emision": f.fecha_emision.isoformat() if f.fecha_emision else None,
                "f_vencimiento": f.fecha_vto.isoformat() if f.fecha_vto else None,
                "importe_total": float(f.charge_total_amount) if f.charge_total_amount else 0,
                "estado_pago": "Vencido" if f.fecha_vto and f.fecha_vto < date.today() else "Pendiente",
                "validacion_automatica": True,
            }
            for f in facturas
        ]
    
    async def get_factura(
        self,
        db: AsyncSession,
        factura_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene detalle completo de una factura
        """
        result = await db.execute(
            select(BSSFactura).where(BSSFactura.nro_doc_fiscal == factura_id)
        )
        factura = result.scalar_one_or_none()
        
        if not factura:
            return None
        
        return {
            "id_factura": factura.nro_doc_fiscal,
            "cuenta": factura.cod_cuenta,
            "f_emision": factura.fecha_emision.isoformat() if factura.fecha_emision else None,
            "f_vencimiento": factura.fecha_vto.isoformat() if factura.fecha_vto else None,
            "subtotal": float(factura.charge_net_amount) if factura.charge_net_amount else 0,
            "igv": float(factura.charge_igv_invoice) if factura.charge_igv_invoice else 0,
            "total": float(factura.charge_total_amount) if factura.charge_total_amount else 0,
            "estado": "Vencido" if factura.fecha_vto and factura.fecha_vto < date.today() else "Pendiente",
            "validacion_automatica": True,
            "detalles": [],
            "ofertas": [],
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
            query = query.where(BSSCliente.segmento_pais == segmento)
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        clientes = result.scalars().all()
        
        return [
            {
                "id_cliente": c.numero_identificacion_fiscal,
                "nombre": c.razon_social,
                "segmento": c.segmento_pais,
                "score_confianza": float(c.score_confianza) if c.score_confianza else 0,
            }
            for c in clientes
        ]
    
    async def get_cliente(
        self,
        db: AsyncSession,
        cliente_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Obtiene detalle de un cliente"""
        result = await db.execute(
            select(BSSCliente).where(BSSCliente.numero_identificacion_fiscal == cliente_id)
        )
        cliente = result.scalar_one_or_none()
        
        if not cliente:
            return None
        
        return {
            "id_cliente": cliente.numero_identificacion_fiscal,
            "tipo_doc": cliente.tipo_documento,
            "num_doc": cliente.numero_identificacion_fiscal,
            "nombre": cliente.razon_social,
            "segmento": cliente.segmento_pais,
            "score_confianza": float(cliente.score_confianza) if cliente.score_confianza else 0,
        }
    
    async def get_historial_facturas(
        self,
        db: AsyncSession,
        cliente_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Obtiene historial de facturas de un cliente"""
        query = (
            select(BSSFactura)
            .where(BSSFactura.numero_identificacion_fiscal == cliente_id)
            .offset(skip)
            .limit(limit)
        )
        
        result = await db.execute(query)
        facturas = result.scalars().all()
        
        return [
            {
                "id_factura": f.nro_doc_fiscal,
                "f_emision": f.fecha_emision.isoformat() if f.fecha_emision else None,
                "total": float(f.charge_total_amount) if f.charge_total_amount else 0,
                "estado": "Vencido" if f.fecha_vto and f.fecha_vto < date.today() else "Pendiente",
            }
            for f in facturas
        ]
    
    async def get_score_cliente(
        self,
        db: AsyncSession,
        cliente_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Obtiene score de confianza del cliente"""
        result = await db.execute(
            select(BSSCliente).where(BSSCliente.numero_identificacion_fiscal == cliente_id)
        )
        cliente = result.scalar_one_or_none()
        
        if not cliente:
            return None
        
        return {
            "cliente_id": cliente.numero_identificacion_fiscal,
            "score": float(cliente.score_confianza) if cliente.score_confianza else 0,
            "es_confiable": float(cliente.score_confianza or 0) >= 0.80,
        }
    
    async def validar_factura_manual(
        self,
        db: AsyncSession,
        factura_id: str,
    ) -> bool:
        """Valida manualmente una factura"""
        return True # Not implemented directly
    
    async def get_ofertas(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
        estado: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Obtiene ofertas de negociación"""
        return []
    
    async def aceptar_oferta(self, db: AsyncSession, oferta_id: int) -> bool:
        return True
    
    async def rechazar_oferta(self, db: AsyncSession, oferta_id: int) -> bool:
        return True