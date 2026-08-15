"""
Endpoints para el Centro de Aprobaciones Human-in-the-Loop (HITL)
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.database.models import BSSRevisionHITL, BSSFactura, BSSCliente
from app.services.audit_service import audit_service

logger = structlog.get_logger(__name__)
router = APIRouter()


# Schemas
class SolicitudHITLResponse(BaseModel):
    id: int
    solicitud_id: str
    tipo_operacion: str
    factura_id: Optional[str] = None
    numero_identificacion_fiscal: str
    cliente_nombre: Optional[str] = None
    monto: float
    score_confianza: float
    agente_origen: str
    motivo_retencion: str
    estado: str
    notas_supervisor: Optional[str] = None
    supervisor_responsable: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None


class DecisionHITLRequest(BaseModel):
    notas: Optional[str] = Field(None, description="Comentarios o justificación del supervisor")
    supervisor_nombre: Optional[str] = Field("Supervisor General", description="Nombre del supervisor")


class MetricasHITLResponse(BaseModel):
    total_pendientes: int
    total_aprobadas: int
    total_rechazadas: int
    monto_total_retenido: float
    score_promedio: float


async def _seed_initial_hitl_records_if_empty(db: AsyncSession) -> None:
    """Genera registros HITL iniciales basados en facturas con bajo score o montos altos si la tabla está vacía."""
    count_res = await db.execute(select(func.count(BSSRevisionHITL.id)))
    if (count_res.scalar() or 0) > 0:
        return
    
    # Buscar facturas para generar solicitudes de prueba realistas
    stmt = (
        select(BSSFactura, BSSCliente)
        .join(BSSCliente, BSSFactura.numero_identificacion_fiscal == BSSCliente.numero_identificacion_fiscal)
        .limit(15)
    )
    res = await db.execute(stmt)
    records = res.all()
    
    for i, (fact, cli) in enumerate(records):
        score = float(cli.score_confianza or 0.75)
        monto = float(fact.charge_total_amount or 0.0)
        
        # Determinar motivo
        if score < 0.60:
            motivo = f"Score de confianza crítico ({score:.2f} < 0.60) - Riesgo de impago elevado"
            tipo = "emision_retenida_riesgo"
        elif monto > 5000:
            motivo = f"Monto elevado (S/ {monto:,.2f}) supera el umbral de verificación automática"
            tipo = "validacion_monto_alto"
        else:
            motivo = f"Validación de prorrateo e inconsistencia de consumo detectada por Facturación AI"
            tipo = "revision_prorrateo"
        
        estado = "pendiente" if i < 10 else ("aprobada" if i % 2 == 0 else "rechazada")
        
        solicitud = BSSRevisionHITL(
            solicitud_id=f"HITL-{fact.nro_doc_fiscal}",
            tipo_operacion=tipo,
            factura_id=fact.nro_doc_fiscal,
            numero_identificacion_fiscal=cli.numero_identificacion_fiscal,
            cliente_nombre=cli.razon_social or f"Cliente_{cli.numero_identificacion_fiscal}",
            monto=Decimal(str(monto)),
            score_confianza=Decimal(str(score)),
            agente_origen="Supervisor Agent",
            motivo_retencion=motivo,
            estado=estado,
            notas_supervisor="Aprobado tras validación con gerencia" if estado == "aprobada" else None,
            supervisor_responsable="Admin HITL" if estado != "pendiente" else None,
            resolved_at=datetime.utcnow() if estado != "pendiente" else None,
        )
        db.add(solicitud)
    
    await db.commit()
    logger.info("🛡️ Registros de prueba de Centro HITL inicializados")


@router.get("/solicitudes", response_model=Dict[str, Any])
async def get_solicitudes(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    estado: Optional[str] = Query(None, description="Filtrar por estado: pendiente, aprobada, rechazada"),
    db: AsyncSession = Depends(get_db),
):
    """Obtiene la lista paginada de solicitudes de aprobación HITL."""
    await _seed_initial_hitl_records_if_empty(db)
    
    query = select(BSSRevisionHITL)
    count_query = select(func.count(BSSRevisionHITL.id))
    
    if estado:
        query = query.where(BSSRevisionHITL.estado == estado.lower())
        count_query = count_query.where(BSSRevisionHITL.estado == estado.lower())
    
    total_res = await db.execute(count_query)
    total = total_res.scalar() or 0
    
    query = query.order_by(desc(BSSRevisionHITL.created_at)).offset(skip).limit(limit)
    res = await db.execute(query)
    solicitudes = res.scalars().all()
    
    items = []
    for s in solicitudes:
        items.append({
            "id": s.id,
            "solicitud_id": s.solicitud_id,
            "tipo_operacion": s.tipo_operacion,
            "factura_id": s.factura_id,
            "numero_identificacion_fiscal": s.numero_identificacion_fiscal,
            "cliente_nombre": s.cliente_nombre,
            "monto": float(s.monto),
            "score_confianza": float(s.score_confianza),
            "agente_origen": s.agente_origen,
            "motivo_retencion": s.motivo_retencion,
            "estado": s.estado,
            "notas_supervisor": s.notas_supervisor,
            "supervisor_responsable": s.supervisor_responsable,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "resolved_at": s.resolved_at.isoformat() if s.resolved_at else None,
        })
    
    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/solicitudes/{solicitud_id}", response_model=Dict[str, Any])
async def get_solicitud_detalle(
    solicitud_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Obtiene el detalle completo de una solicitud HITL."""
    res = await db.execute(
        select(BSSRevisionHITL).where(
            (BSSRevisionHITL.solicitud_id == solicitud_id) | (BSSRevisionHITL.id == int(solicitud_id) if solicitud_id.isdigit() else False)
        )
    )
    s = res.scalars().first()
    if not s:
        raise HTTPException(status_code=404, detail="Solicitud HITL no encontrada")
    
    return {
        "id": s.id,
        "solicitud_id": s.solicitud_id,
        "tipo_operacion": s.tipo_operacion,
        "factura_id": s.factura_id,
        "numero_identificacion_fiscal": s.numero_identificacion_fiscal,
        "cliente_nombre": s.cliente_nombre,
        "monto": float(s.monto),
        "score_confianza": float(s.score_confianza),
        "agente_origen": s.agente_origen,
        "motivo_retencion": s.motivo_retencion,
        "estado": s.estado,
        "notas_supervisor": s.notas_supervisor,
        "supervisor_responsable": s.supervisor_responsable,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "resolved_at": s.resolved_at.isoformat() if s.resolved_at else None,
    }


@router.post("/solicitudes/{solicitud_id}/aprobar", response_model=Dict[str, Any])
async def aprobar_solicitud(
    solicitud_id: str,
    body: DecisionHITLRequest,
    db: AsyncSession = Depends(get_db),
):
    """Aprueba una solicitud retenida por el agente y autoriza la emisión/descuento."""
    res = await db.execute(
        select(BSSRevisionHITL).where(
            (BSSRevisionHITL.solicitud_id == solicitud_id) | (BSSRevisionHITL.id == int(solicitud_id) if solicitud_id.isdigit() else False)
        )
    )
    s = res.scalars().first()
    if not s:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    
    s.estado = "aprobada"
    s.notas_supervisor = body.notas or "Aprobado manualmente por supervisor"
    s.supervisor_responsable = body.supervisor_nombre or "Supervisor HITL"
    s.resolved_at = datetime.utcnow()
    
    await db.commit()
    
    # Registrar en auditoría
    await audit_service.log_action(
        db=db,
        tipo_accion="APROBACION_HITL",
        usuario=s.supervisor_responsable,
        modulo="HITL",
        descripcion=f"Aprobación manual de solicitud {s.solicitud_id} (Factura {s.factura_id})",
        metadata={
            "solicitud_id": s.solicitud_id,
            "factura_id": s.factura_id,
            "monto": float(s.monto),
            "notas": s.notas_supervisor,
        },
    )
    
    logger.info("✅ Solicitud HITL aprobada", solicitud_id=s.solicitud_id)
    return {
        "status": "success",
        "message": f"Solicitud {s.solicitud_id} aprobada exitosamente",
        "solicitud_id": s.solicitud_id,
        "estado": s.estado,
    }


@router.post("/solicitudes/{solicitud_id}/rechazar", response_model=Dict[str, Any])
async def rechazar_solicitud(
    solicitud_id: str,
    body: DecisionHITLRequest,
    db: AsyncSession = Depends(get_db),
):
    """Rechaza una solicitud retenida bloqueando la emisión/descuento."""
    res = await db.execute(
        select(BSSRevisionHITL).where(
            (BSSRevisionHITL.solicitud_id == solicitud_id) | (BSSRevisionHITL.id == int(solicitud_id) if solicitud_id.isdigit() else False)
        )
    )
    s = res.scalars().first()
    if not s:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    
    s.estado = "rechazada"
    s.notas_supervisor = body.notas or "Rechazado por supervisor"
    s.supervisor_responsable = body.supervisor_nombre or "Supervisor HITL"
    s.resolved_at = datetime.utcnow()
    
    await db.commit()
    
    # Registrar en auditoría
    await audit_service.log_action(
        db=db,
        tipo_accion="RECHAZO_HITL",
        usuario=s.supervisor_responsable,
        modulo="HITL",
        descripcion=f"Rechazo manual de solicitud {s.solicitud_id} (Factura {s.factura_id})",
        metadata={
            "solicitud_id": s.solicitud_id,
            "factura_id": s.factura_id,
            "monto": float(s.monto),
            "notas": s.notas_supervisor,
        },
    )
    
    logger.info("🚫 Solicitud HITL rechazada", solicitud_id=s.solicitud_id)
    return {
        "status": "success",
        "message": f"Solicitud {s.solicitud_id} rechazada",
        "solicitud_id": s.solicitud_id,
        "estado": s.estado,
    }


@router.get("/metricas", response_model=MetricasHITLResponse)
async def get_metricas_hitl(db: AsyncSession = Depends(get_db)):
    """Obtiene métricas resumidas del centro de aprobaciones HITL."""
    await _seed_initial_hitl_records_if_empty(db)
    
    pendientes_q = select(func.count(BSSRevisionHITL.id), func.coalesce(func.sum(BSSRevisionHITL.monto), 0.0)).where(BSSRevisionHITL.estado == "pendiente")
    aprobadas_q = select(func.count(BSSRevisionHITL.id)).where(BSSRevisionHITL.estado == "aprobada")
    rechazadas_q = select(func.count(BSSRevisionHITL.id)).where(BSSRevisionHITL.estado == "rechazada")
    score_q = select(func.coalesce(func.avg(BSSRevisionHITL.score_confianza), 0.80))
    
    pend_res = await db.execute(pendientes_q)
    aprob_res = await db.execute(aprobadas_q)
    rech_res = await db.execute(rechazadas_q)
    score_res = await db.execute(score_q)
    
    total_pend, monto_pend = pend_res.first() or (0, 0.0)
    total_aprob = aprob_res.scalar() or 0
    total_rech = rech_res.scalar() or 0
    score_prom = score_res.scalar() or 0.80
    
    return {
        "total_pendientes": total_pend,
        "total_aprobadas": total_aprob,
        "total_rechazadas": total_rech,
        "monto_total_retenido": float(monto_pend),
        "score_promedio": round(float(score_prom), 2),
    }
