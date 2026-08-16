"""
Endpoints de Auditoría
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.services.audit_service import AuditService

router = APIRouter()
audit_service = AuditService()


@router.get("/logs")
@router.get("/log")
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    tipo_accion: Optional[str] = Query(None),
    usuario_id: Optional[str] = Query(None),
    fecha_desde: Optional[str] = Query(None),
    fecha_hasta: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Log de auditoría paginado de todas las acciones de los agentes y usuarios.
    """
    return await audit_service.get_audit_logs(
        db,
        skip=skip,
        limit=limit,
        tipo_accion=tipo_accion,
        usuario_id=usuario_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        search=search,
    )


@router.get("/logs/export")
@router.get("/log/export")
async def exportar_audit_logs(
    tipo_accion: Optional[str] = Query(None),
    usuario_id: Optional[str] = Query(None),
    fecha_desde: Optional[str] = Query(None),
    fecha_hasta: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Exportación de logs en formato CSV.
    """
    import io
    import csv
    from fastapi.responses import Response

    result = await audit_service.get_audit_logs(
        db,
        skip=0,
        limit=500,
        tipo_accion=tipo_accion,
        usuario_id=usuario_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        search=search,
    )
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Fecha", "Usuario ID", "Usuario", "Accion", "Descripcion", "Entidad", "Entidad ID", "Resultado", "IP"])
    
    for item in result["items"]:
        writer.writerow([
            item.get("id"),
            item.get("fecha_accion"),
            item.get("usuario_id"),
            item.get("usuario_nombre"),
            item.get("tipo_accion"),
            item.get("descripcion"),
            item.get("entidad_tipo"),
            item.get("entidad_id"),
            item.get("resultado"),
            item.get("ip_origen"),
        ])
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_logs.csv"}
    )


@router.get("/logs/{action_id}")
@router.get("/log/{action_id}")
async def get_audit_detail(
    action_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Detalle de una acción de auditoría específica.
    """
    from fastapi import HTTPException
    detail = await audit_service.get_audit_detail(db, action_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Acción no encontrada")
    return detail