"""
Endpoints de Facturación
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.services.billing_service import BillingService
from app.agents.supervisor_agent import supervisor_agent

router = APIRouter()
billing_service = BillingService()


@router.post("/ciclos/ejecutar")
async def ejecutar_ciclo_facturacion(
    ciclo_id: int = Query(..., description="ID del ciclo de facturación"),
    force_review: bool = Query(False, description="Forzar revisión humana"),
):
    """
    Dispara un ciclo de facturación completo (acción del Agente Supervisor).

    PARA EL FRONTEND:
    - URL:    POST /api/v1/billing/ciclos/ejecutar?ciclo_id=N&force_review=true|false
    - Uso:    botón "Ejecutar ciclo" de la sección Facturación.
    - Cuerpo: no requiere body; usa query params (ciclo_id, force_review).
    - Respuesta: resultado del Supervisor Agent con el estado del flujo
      (facturas generadas, validación, anomalías detectadas).

    El Agente Supervisor orquesta el proceso completo:
    1. Validación de datos de insumos (plantas BSS/OSS)
    2. Cálculo de facturas vía motor simbólico (PxQ e IGV)
    3. Verificación de anomalías (monto 500% superior, etc.)
    4. Decisión HITL si es necesario (envía alerta al dashboard)
    """
    task = {
        "type": "start_billing_cycle",
        "ciclo_id": ciclo_id,
        "force_human_review": force_review,
    }
    
    result = await supervisor_agent.execute(task)
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    
    return result


@router.get("/facturas")
async def listar_facturas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    estado: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Lista paginada de facturas (consumida por la sección Facturación).

    PARA EL FRONTEND:
    - URL:  GET /api/v1/billing/facturas?skip=0&limit=100&estado=Pendiente
    - Uso:  tablas de facturas (paginar con skip/limit).
    - Query params:
      - skip:   registros a saltar (paginación offset)
      - limit:  máx. registros a retornar (1-500)
      - estado: filtro booleano de color (Pendiente, Pagado, Vencido) - opcional
    - Respuesta: lista de facturas de la tabla bss_facturas.

    Args:
        skip: Registros para saltar (paginación)
        limit: Máximo de registros a retornar
        estado: Filtrar por estado (Pendiente, Pagado, Vencido)
    """
    return await billing_service.get_facturas(db, skip, limit, estado)


@router.get("/facturas/{factura_id}")
async def obtener_factura(
    factura_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Detalle completo de una factura (consumida por Facturación / Portal).

    PARA EL FRONTEND:
    - URL:  GET /api/v1/billing/facturas/{factura_id}
    - Uso:  vista de detalle de factura (cabecera + detalle + ofertas activas).
    - Path param: factura_id (ej: S9AA-0082761955).
    - Respuesta: 404 si no existe; si no, cabecera, líneas y ofertas.
    
    Incluye:
    - Cabecera de factura
    - Líneas de detalle
    - Ofertas de negociación activas
    """
    factura = await billing_service.get_factura(db, factura_id)
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return factura


from fastapi.responses import Response
from sqlalchemy import select
from app.database.models import BSSFactura, BSSCliente
from app.services.sunat_service import sunat_service


@router.post("/facturas/{factura_id}/validar")
async def validar_factura(
    factura_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Validación manual (HITL) de una factura marcada como excepción."""
    result = await billing_service.validar_factura_manual(db, factura_id)
    if not result:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return {"status": "success", "message": "Factura validada manualmente"}


@router.get("/facturas/{factura_id}/sunat-info")
async def obtener_sunat_info(
    factura_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene los metadatos de facturación electrónica SUNAT UBL 2.1
    (Código Hash SHA-256, cadena QR, serie, correlativo y estado OSE).
    """
    res = await db.execute(select(BSSFactura).where(BSSFactura.nro_doc_fiscal == factura_id))
    factura = res.scalar_one_or_none()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    res_cli = await db.execute(
        select(BSSCliente).where(BSSCliente.numero_identificacion_fiscal == factura.numero_identificacion_fiscal)
    )
    cliente = res_cli.scalar_one_or_none()
    if not cliente:
        cliente = BSSCliente(
            numero_identificacion_fiscal=factura.numero_identificacion_fiscal,
            razon_social="CLIENTE B2B INTEGRATEL",
        )

    sunat_data = sunat_service.generar_xml_ubl21_recibo_tipo14(factura, cliente)
    return {
        "factura_id": factura.nro_doc_fiscal,
        "tipo_comprobante": sunat_data["tipo_comprobante"],
        "tipo_nombre": sunat_data["tipo_nombre"],
        "serie": sunat_data["serie"],
        "correlativo": sunat_data["correlativo"],
        "hash_sha256": sunat_data["hash"],
        "qr_cadena": sunat_data["qr_cadena"],
        "estado_sunat": sunat_data["estado_sunat"],
        "fecha_emision": sunat_data["fecha_emision"],
        "monto_neto": sunat_data["monto_neto"],
        "igv": sunat_data["igv"],
        "monto_total": sunat_data["monto_total"],
        "moneda": sunat_data["moneda"],
        "xml_filename": sunat_data["filename"],
    }


@router.get("/facturas/{factura_id}/xml")
async def descargar_xml_sunat(
    factura_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Descarga el archivo XML estándar SUNAT UBL 2.1 del comprobante.
    """
    res = await db.execute(select(BSSFactura).where(BSSFactura.nro_doc_fiscal == factura_id))
    factura = res.scalar_one_or_none()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    res_cli = await db.execute(
        select(BSSCliente).where(BSSCliente.numero_identificacion_fiscal == factura.numero_identificacion_fiscal)
    )
    cliente = res_cli.scalar_one_or_none()
    if not cliente:
        cliente = BSSCliente(
            numero_identificacion_fiscal=factura.numero_identificacion_fiscal,
            razon_social="CLIENTE B2B INTEGRATEL",
        )

    sunat_data = sunat_service.generar_xml_ubl21_recibo_tipo14(factura, cliente)
    
    return Response(
        content=sunat_data["xml"],
        media_type="application/xml",
        headers={
            "Content-Disposition": f"attachment; filename={sunat_data['filename']}"
        },
    )


@router.get("/facturas/{factura_id}/pdf")
async def descargar_pdf_movistar(
    factura_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Genera y descarga el archivo PDF oficial del Recibo Movistar con membrete y diseño gráfico corporativo.
    """
    from app.services.pdf_service import pdf_generator

    res = await db.execute(select(BSSFactura).where(BSSFactura.nro_doc_fiscal == factura_id))
    factura = res.scalar_one_or_none()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    res_cli = await db.execute(
        select(BSSCliente).where(BSSCliente.numero_identificacion_fiscal == factura.numero_identificacion_fiscal)
    )
    cliente = res_cli.scalar_one_or_none()
    if not cliente:
        cliente = BSSCliente(
            numero_identificacion_fiscal=factura.numero_identificacion_fiscal,
            razon_social="CLIENTE B2B INTEGRATEL",
        )

    pdf_bytes = pdf_generator.generar_pdf_recibo(factura, cliente)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=Recibo_Movistar_{factura.nro_doc_fiscal}.pdf"
        },
    )


@router.post("/facturas/{factura_id}/enviar-email")
async def enviar_factura_por_email(
    factura_id: str,
    email_destino: Optional[str] = Query(None, description="Correo electrónico de destino opcional"),
    db: AsyncSession = Depends(get_db),
):
    """
    Envía el Recibo Oficial Movistar en PDF (3 Páginas) con la plantilla corporativa oficial
    al correo del cliente o al correo de prueba indicado.
    """
    from app.services.pdf_service import pdf_generator
    from app.services.notification_service import notification_service
    from app.services.audit_service import audit_service

    res = await db.execute(select(BSSFactura).where(BSSFactura.nro_doc_fiscal == factura_id))
    factura = res.scalar_one_or_none()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    res_cli = await db.execute(
        select(BSSCliente).where(BSSCliente.numero_identificacion_fiscal == factura.numero_identificacion_fiscal)
    )
    cliente = res_cli.scalar_one_or_none()
    if not cliente:
        cliente = BSSCliente(
            numero_identificacion_fiscal=factura.numero_identificacion_fiscal,
            razon_social="MARCK ALESSANDRO HERMENEGILDO PACHECO",
            numero_celular="904388543",
        )

    # Generar el PDF oficial de 3 páginas
    pdf_bytes = pdf_generator.generar_pdf_recibo(factura, cliente)

    # Determinar destinatario
    to_email = email_destino or f"pagos@{cliente.numero_identificacion_fiscal}.com"
    mes_nombre = (factura.fecha_emision or date.today()).strftime("%B")
    meses_es = {
        "January": "Enero", "February": "Febrero", "March": "Marzo", "April": "Abril",
        "May": "Mayo", "June": "Junio", "July": "Julio", "August": "Agosto",
        "September": "Setiembre", "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
    }
    mes_es = meses_es.get(mes_nombre, mes_nombre)
    fecha_vto_str = (factura.fecha_vto or date.today()).strftime("%d/%m")

    # Enviar correo con el PDF adjunto (sin XML)
    resultado = await notification_service.send_invoice_email(
        to_email=to_email,
        cliente_nombre=cliente.razon_social or "Cliente Corporativo",
        numero_factura=factura.nro_doc_fiscal,
        monto_total=float(factura.charge_total_amount or 39.90),
        fecha_vencimiento=fecha_vto_str,
        segmento="Móvil / Fijo",
        mes=mes_es,
        codigo_pago=(cliente.numero_identificacion_fiscal or "904388543")[:10],
        costo_reconexion=10.00,
        pdf_bytes=pdf_bytes,
    )

    # Registro de auditoría
    await audit_service.log_action(
        tipo_accion="enviar_email",
        usuario_id="supervisor_agente",
        detalles={
            "factura_id": factura.nro_doc_fiscal,
            "destinatario": to_email,
            "resultado": resultado.get("status"),
            "modo": resultado.get("modo", "sandbox"),
        },
    )

    return {
        "status": "success",
        "mensaje": f"Recibo {factura.nro_doc_fiscal} despachado hacia {to_email}",
        "destinatario": to_email,
        "detalles": resultado,
    }