"""
Servicio de Webhook WhatsApp (OpenWA -> SON-IA).

Recibe los mensajes entrantes que OpenWA reenvía, identifica al cliente
por su número de celular, interpreta la intención, recupera contexto con RAG
(CustomerAgent) y datos REALES de la base de datos (bss_facturas / bss_pagos) y
responde por WhatsApp usando OpenWAClient.

Rutas de decisión:
- Consulta de saldo/deuda    -> revisa facturas no pagadas
- Consulta de factura        -> detalle de la factura indicada + explicación RAG
- Solicitud de negociación   -> genera una oferta de descuento según score
- Consulta de planes / RAG   -> CustomerAgent con Base de Conocimiento RAG
- Otro / Ayuda general       -> saludo + menú guiado
"""

import re
from datetime import date
from decimal import Decimal
from typing import Any, Dict, Optional, Tuple
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.classifier_agent import classifier_agent
from app.agents.customer_agent import customer_agent
from app.database.models import BSSCliente, BSSFactura, BSSPago
from app.integrations.openwa_client import openwa_client, normalize_phone
from app.integrations.openwa_client import to_chat_id  # noqa: F401

logger = structlog.get_logger(__name__)


class WhatsAppWebhookService:
    """Procesa mensajes entrantes de WhatsApp y responde automáticamente con datos y RAG."""

    def _parse_message(self, payload: Dict[str, Any]) -> Tuple[Optional[str], Optional[str], bool]:
        """Extrae (mensaje, teléfono_emisor, from_me) de un payload de OpenWA."""
        data = payload.get("data") or payload.get("message") or payload

        body = (
            data.get("body")
            or data.get("text")
            or data.get("content")
            or data.get("caption")
        )
        body = str(body).strip() if body else ""

        from_wid = (
            data.get("from")
            or data.get("chatId")
            or data.get("fromMe")
            or (data.get("key") or {}).get("remoteJid")
            or (data.get("sender") or {}).get("id")
        )

        from_me = bool(
            data.get("fromMe")
            or (data.get("sender") or {}).get("isMe")
            or data.get("from_me")
        )

        phone = None
        if from_wid:
            wid = str(from_wid).split("@")[0]
            phone = normalize_phone(wid)

        logger.info("📥 WhatsApp: mensaje entrante",
                    phone=phone, body=body[:80], from_me=from_me, event_type=payload.get("event"))
        return body, phone, from_me

    async def _find_client(self, db: AsyncSession, phone: str) -> Optional[BSSCliente]:
        """Busca al cliente por su número de celular (columna numero_celular)."""
        result = await db.execute(
            select(BSSCliente).where(
                BSSCliente.numero_celular.like(f"%{phone[-9:]}") if phone else False
            )
        )
        cliente = result.scalars().first()
        if cliente:
            logger.info("👤 Cliente identificado", ruc=cliente.numero_identificacion_fiscal,
                        nombre=cliente.razon_social)
        else:
            logger.warning("🚫 Cliente NO encontrado para teléfono", phone=phone)
        return cliente

    async def _interpret(self, message: str) -> Dict[str, Any]:
        """
        Determina la intención del mensaje usando el Classifier Agent y heurísticas.
        """
        message_lower = message.lower()
        factura_match = re.search(r"factura\s*#?\s*([a-zA-Z0-9\-]+)", message, re.IGNORECASE)

        intent = "consulta_general"

        if any(kw in message_lower for kw in ["cuánto debo", "cuanto debo", "saldo", "deuda", "adeudo",
                                              "cuánto pagar", "cuanto pagar", "pagar mi factura", "pagarla"]):
            intent = "consulta_saldo"
        elif any(kw in message_lower for kw in ["vence", "vencimiento", "mi recibo", "mi factura",
                                                "por qué subió", "porque subio", "desglose"]):
            intent = "consulta_factura"
        elif any(kw in message_lower for kw in ["descuento", "no puedo pagar", "facilidad", "plazo",
                                                "negociar", "rebaja", "mis cuotas", "cuotas", "fraccionar"]):
            intent = "negociacion"
        elif any(kw in message_lower for kw in ["plan", "planes", "fibra", "velocidad", "roaming",
                                                "tarifa", "duo", "tamn", "mora", "interes", "reclamo", "sunat"]):
            intent = "consulta_rag"
        elif any(kw in message_lower for kw in ["hola", "buenas", "saludos", "ayuda", "quién", "quien eres"]):
            intent = "saludo"
        elif any(kw in message_lower for kw in ["gracias", "ok", "listo", "perfecto"]):
            intent = "despedida"

        factura_id = factura_match.group(1) if factura_match else None

        try:
            clasificacion = await classifier_agent.execute({
                "type": "classify_message",
                "message": message,
                "canal": "whatsapp",
            })
            logger.info("🏷️ Intención clasificada", intent=intent, categoria=clasificacion.get("categoria"))
        except Exception as e:
            logger.warning("⚠️ Classifier agent warning", error=str(e))

        return {"intent": intent, "factura_id": factura_id}

    async def _unpaid_invoices(self, db: AsyncSession, ruc: str) -> list:
        """Facturas del cliente sin pago registrado en bss_pagos."""
        result = await db.execute(
            select(BSSFactura).where(BSSFactura.numero_identificacion_fiscal == ruc)
        )
        facturas = result.scalars().all()

        pagos_result = await db.execute(
            select(BSSPago.factura_afectada).where(BSSPago.numero_identificacion_fiscal == ruc)
        )
        pagadas = set(pagos_result.scalars().all())

        return [f for f in facturas if f.nro_doc_fiscal not in pagadas]

    async def _build_reply(
        self,
        db: AsyncSession,
        cliente: Optional[BSSCliente],
        intent: Dict[str, Any],
        message: str,
    ) -> str:
        """Construye la respuesta usando datos de BD y RAG."""
        if not cliente:
            # Aunque el cliente no esté en la BD, si hace una pregunta de planes o políticas, responder con RAG
            if intent.get("intent") in ("consulta_rag", "consulta_general"):
                rag_res = await customer_agent.execute({
                    "type": "answer_question",
                    "pregunta": message,
                    "cliente_nombre": "Estimado cliente",
                })
                return rag_res.get("respuesta", "Hola 👋, para consultas de cuenta proporcione su RUC registrado.")
            
            return (
                "Hola 👋, no pudimos identificar una cuenta registrada con este número. "
                "Si deseas información sobre nuestros planes de Fibra Óptica, Móvil B2B o políticas de pago, "
                "escríbenos tu consulta."
            )

        nombre = (cliente.razon_social or "cliente").split("_")[-1]
        intent_type = intent["intent"]
        factura_id = intent.get("factura_id")

        if intent_type == "consulta_saldo":
            return await self._reply_saldo(db, cliente, nombre)
        if intent_type == "consulta_factura":
            return await self._reply_factura(db, cliente, nombre, factura_id, message)
        if intent_type == "negociacion":
            return await self._reply_oferta(cliente, nombre)
        if intent_type == "consulta_rag":
            # Responder usando el RAG institucional enriquecido
            rag_res = await customer_agent.execute({
                "type": "answer_question",
                "pregunta": message,
                "cliente_nombre": nombre,
            })
            return rag_res.get("respuesta", "")
        if intent_type == "saludo":
            return (
                f"Hola {nombre} 👋, soy SON-IA, tu asistente virtual de Integratel / Movistar Empresas.\n\n"
                "Puedo ayudarte a:\n"
                "• Consultar tu saldo y facturas pendientes\n"
                "• Gestionar descuentos y acuerdos de pago\n"
                "• Explicar detalles de tus planes y servicios B2B\n\n"
                "¿En qué puedo orientarte hoy?"
            )
        if intent_type == "despedida":
            return f"¡Con gusto {nombre}! Que tengas un excelente día. Quedo atento si necesitas algo más. 👋"

        # Fallback a RAG contextual para preguntas no estructuradas
        rag_res = await customer_agent.execute({
            "type": "answer_question",
            "pregunta": message,
            "cliente_nombre": nombre,
        })
        return rag_res.get("respuesta", f"Entendido {nombre} ✅. ¿En qué más puedo ayudarte?")

    async def _reply_saldo(self, db: AsyncSession, cliente: BSSCliente, nombre: str) -> str:
        facturas = await self._unpaid_invoices(db, cliente.numero_identificacion_fiscal)
        if not facturas:
            return f"¡Excelente {nombre}! 🎉 No tienes facturas pendientes de pago al día de hoy."

        deuda_total = sum(Decimal(str(f.charge_total_amount or 0)) for f in facturas)
        vencidas = [f for f in facturas if f.fecha_vto and f.fecha_vto < date.today()]

        mensaje = (
            f"Hola {nombre} 👋, tu saldo pendiente es de *S/ {deuda_total:,.2f}* "
            f"en {len(facturas)} factura(s).\n\n"
        )
        for f in facturas[:3]:
            estado = "⚠️ VENCIDA" if f.fecha_vto and f.fecha_vto < date.today() else "vigente"
            vto = f.fecha_vto.strftime("%d/%m/%Y") if f.fecha_vto else "s/f"
            mensaje += f"• Factura *{f.nro_doc_fiscal}*: S/ {float(f.charge_total_amount or 0):,.2f} ({estado}, vence {vto})\n"

        if vencidas:
            mensaje += ("\n💡 Tienes facturas con mora. Podemos ofrecerte facilidades de pago o "
                        "descuento por pronto pago. Responde *'negociar'* para ver opciones.")
        return mensaje

    async def _reply_factura(
        self,
        db: AsyncSession,
        cliente: BSSCliente,
        nombre: str,
        factura_id: Optional[str],
        message: str,
    ) -> str:
        facturas = await self._unpaid_invoices(db, cliente.numero_identificacion_fiscal)
        if factura_id:
            matching = [f for f in facturas if factura_id in f.nro_doc_fiscal]
            if not matching:
                return f"No encontré una factura activa con el identificador '{factura_id}'."
            f = matching[0]
        else:
            if not facturas:
                return f"¡Buenas {nombre}! No tienes facturas pendientes en este momento. 🎉"
            f = facturas[0]

        # Si el usuario pregunta "por qué subió" o pide desglose, usar la explicación detallada
        if "por qué" in message.lower() or "porque" in message.lower() or "desglose" in message.lower():
            exp_res = await customer_agent.execute({
                "type": "explain_invoice",
                "factura": {
                    "nro_doc_fiscal": f.nro_doc_fiscal,
                    "charge_total_amount": float(f.charge_total_amount or 0.0),
                }
            })
            return exp_res.get("respuesta", "")

        estado = "VENCIDA" if f.fecha_vto and f.fecha_vto < date.today() else "al día"
        vto = f.fecha_vto.strftime("%d/%m/%Y") if f.fecha_vto else "sin fecha"
        emision = f.fecha_emision.strftime("%d/%m/%Y") if f.fecha_emision else "s/f"
        
        return (
            f"Hola {nombre} 👋, aquí el detalle de tu factura *{f.nro_doc_fiscal}*:\n\n"
            f"• Fecha de Emisión: {emision}\n"
            f"• Fecha de Vencimiento: {vto}\n"
            f"• Monto Total: *S/ {float(f.charge_total_amount or 0):,.2f}*\n"
            f"• Estado: {estado}\n\n"
            "¿Deseas conocer los métodos de pago disponibles o solicitar facilidades?"
        )

    async def _reply_oferta(self, cliente: BSSCliente, nombre: str) -> str:
        score = float(cliente.score_confianza or 0.80)
        if score >= 0.80:
            descuento = 5
            propuesta = "un descuento del 5% por pronto pago dentro de las próximas 48 horas"
        elif score >= 0.50:
            descuento = 10
            propuesta = "un descuento especial del 10% para regularizar tu saldo"
        else:
            descuento = 15
            propuesta = "un plan de facilidades: 15% de descuento sobre intereses y fraccionamiento"

        logger.info("🎯 Oferta predictiva calculada", ruc=cliente.numero_identificacion_fiscal, score=score, descuento=descuento)

        return (
            f"Hola {nombre} 🤝, revisando tu historial en SON-IA, podemos ofrecerte {propuesta}.\n\n"
            "¿Te gustaría confirmar esta opción para registrar tu acuerdo de pago?"
        )

    async def process_payload(self, payload: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        """Procesa un payload entrante de WhatsApp y despacha la respuesta."""
        body, phone, from_me = self._parse_message(payload)

        if from_me:
            logger.info("↩️ Mensaje saliente ignorado")
            return {"status": "ignored", "reason": "from_me", "success": True}
        if not body or not phone:
            return {"status": "ignored", "reason": "sin_texto_o_numero", "success": True}

        # 🛡️ PROTECCIÓN DEMO: Si está configurado WHATSAPP_DEMO_ALLOWED_PHONE,
        # solo responder automáticamente a este número para no responder a chats personales.
        allowed_demo = settings.WHATSAPP_DEMO_ALLOWED_PHONE.strip()
        if allowed_demo:
            allowed_list = [normalize_phone(n.strip()) for n in allowed_demo.split(",") if n.strip()]
            sender_normalized = normalize_phone(phone)
            if sender_normalized not in allowed_list:
                logger.info(
                    "🛡️ [Demo Sandbox] Mensaje entrante ignorado para proteger chats personales",
                    remitente=phone,
                    remitente_normalizado=sender_normalized,
                    numeros_autorizados=allowed_list,
                )
                return {
                    "status": "ignored",
                    "reason": "demo_protection_active",
                    "mensaje": "Mensaje recibido pero ignorado por filtro de seguridad de Demo",
                    "remitente": phone,
                    "success": True,
                }

        cliente = await self._find_client(db, phone)
        intent = await self._interpret(body)
        reply = await self._build_reply(db, cliente, intent, body)

        session = payload.get("sessionId") or None
        send_result = await openwa_client.send_message(
            phone_number=phone,
            message=reply,
            session_name=session,
        )

        if not send_result.get("success"):
            logger.error("❌ Falló envío de respuesta WhatsApp", phone=phone, error=send_result.get("error"))

        return {
            "status": "processed",
            "success": True,
            "phone": phone,
            "intent": intent["intent"],
            "client_found": cliente is not None,
            "reply": reply,
            "send_result": send_result,
        }


# Singleton
whatsapp_webhook_service = WhatsAppWebhookService()