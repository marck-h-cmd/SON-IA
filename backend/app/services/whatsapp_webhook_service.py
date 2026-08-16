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


def _format_friendly_name(raw_name: Optional[str]) -> str:
    """Convierte 'MARCK ALESSANDRO HERMENEGILDO PACHECO' o 'EMPRESA_SAC' a 'Marck' o 'Marck Alessandro'."""
    if not raw_name:
        return ""
    clean = re.sub(r"[_\-]+", " ", str(raw_name)).strip()
    words = [w.capitalize() for w in clean.split() if w]
    if not words:
        return ""
    # Si es empresa con palabras comunes, mantener nombre legible
    if words[0].lower() in ["empresa", "corporacion", "inversiones", "grupo", "servicios", "comercial"]:
        return " ".join(words[:3])
    # Si es nombre de persona, devolver primer nombre o dos nombres cortos
    if len(words) >= 2 and len(words[0]) <= 7:
        return f"{words[0]} {words[1]}"
    return words[0]


class WhatsAppWebhookService:
    """Procesa mensajes entrantes de WhatsApp y responde automáticamente con datos y RAG."""

    def _parse_message(self, payload: Dict[str, Any]) -> Tuple[Optional[str], Optional[str], Optional[str], bool, bool]:
        """
        Extrae (mensaje, teléfono_autor, target_chat_id, es_grupo, from_me) de un payload de OpenWA.
        """
        data = payload.get("data") or payload.get("message") or payload

        body = (
            data.get("body")
            or data.get("text")
            or data.get("content")
            or data.get("caption")
        )
        body = str(body).strip() if body else ""

        from_me = bool(
            data.get("fromMe")
            or (data.get("sender") or {}).get("isMe")
            or data.get("from_me")
            or payload.get("event") == "message.sent"
        )

        # Buscar el ID del chat / grupo en varios campos posibles de OpenWA
        chat_id_candidates = [
            data.get("chatId"),
            (data.get("chat") or {}).get("id") if isinstance(data.get("chat"), dict) else None,
            (data.get("key") or {}).get("remoteJid") if isinstance(data.get("key"), dict) else None,
            data.get("to"),
            data.get("from"),
            (data.get("sender") or {}).get("id") if isinstance(data.get("sender"), dict) else None,
        ]

        # Priorizar el que sea un grupo (@g.us) si existe
        group_candidate = next((str(c) for c in chat_id_candidates if c and "@g.us" in str(c)), None)
        chat_id_str = group_candidate or next((str(c) for c in chat_id_candidates if c), "")

        is_group = "@g.us" in chat_id_str or bool(data.get("isGroupMsg") or data.get("isGroup"))

        # Determinar el autor del mensaje (si es grupo, buscar quién escribió)
        author_wid = (
            data.get("author")
            or data.get("participant")
            or ((data.get("key") or {}).get("participant") if isinstance(data.get("key"), dict) else None)
            or data.get("from")
        )

        phone = None
        if author_wid:
            wid = str(author_wid).split("@")[0]
            phone = normalize_phone(wid)
        elif chat_id_str and not is_group:
            wid = str(chat_id_str).split("@")[0]
            phone = normalize_phone(wid)

        target_chat = chat_id_str if is_group else (phone or chat_id_str)

        logger.info(
            "📥 WhatsApp: mensaje recibido",
            body=body[:80],
            phone=phone,
            chat_id=chat_id_str,
            is_group=is_group,
            group_id=chat_id_str if is_group else None,
            from_me=from_me,
            event_type=payload.get("event")
        )
        return body, phone, target_chat, is_group, from_me
        return body, phone, target_chat, is_group, from_me

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
                                              "cuánto pagar", "cuanto pagar", "pagar mi factura", "pagarla", "mis recibos"]):
            intent = "consulta_saldo"
        elif any(kw in message_lower for kw in ["vence", "vencimiento", "mi recibo", "mi factura",
                                                "por qué subió", "porque subio", "desglose", "detalle recibo"]):
            intent = "consulta_factura"
        elif any(kw in message_lower for kw in ["descuento", "no puedo pagar", "facilidad", "plazo",
                                                "negociar", "rebaja", "mis cuotas", "cuotas", "fraccionar", "acuerdo"]):
            intent = "negociacion"
        elif any(kw in message_lower for kw in ["plan", "planes", "fibra", "velocidad", "roaming",
                                                "tarifa", "duo", "tamn", "mora", "interes", "reclamo", "sunat", "requisitos"]):
            intent = "consulta_rag"
        elif any(kw in message_lower for kw in ["hola", "buenas", "saludos", "ayuda", "buen dia", "buenos dias", "buenas tardes"]):
            intent = "saludo"
        elif any(kw in message_lower for kw in ["gracias", "ok", "listo", "perfecto", "muchas gracias", "vale"]):
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
        """Construye la respuesta de forma cálida, humana y sin metadatos técnicos."""
        nombre = _format_friendly_name(cliente.razon_social) if cliente else "amigo(a)"
        intent_type = intent["intent"]
        factura_id = intent.get("factura_id")

        if not cliente:
            # Si hace una pregunta general de planes o servicios
            if intent_type in ("consulta_rag", "consulta_general"):
                rag_res = await customer_agent.execute({
                    "type": "answer_question",
                    "pregunta": message,
                    "cliente_nombre": "",
                })
                return rag_res.get("respuesta", "¡Hola! 😊 Con gusto te ayudamos. ¿En qué servicio o plan estás interesado?")
            
            return (
                "¡Hola! 😊 Un gusto saludarte. Te damos la bienvenida a Movistar Empresas.\n\n"
                "Para consultas sobre tu cuenta o facturación, por favor indícanos tu número de RUC o documento registrado. "
                "Si deseas conocer nuestros planes de Fibra Óptica y servicios corporativos, ¡cuéntanos qué necesitas y con gusto te orientamos!"
            )

        if intent_type == "consulta_saldo":
            return await self._reply_saldo(db, cliente, nombre)
        if intent_type == "consulta_factura":
            return await self._reply_factura(db, cliente, nombre, factura_id, message)
        if intent_type == "negociacion":
            return await self._reply_oferta(cliente, nombre)
        if intent_type == "consulta_rag":
            rag_res = await customer_agent.execute({
                "type": "answer_question",
                "pregunta": message,
                "cliente_nombre": nombre,
            })
            return rag_res.get("respuesta", "")
        if intent_type == "saludo":
            return (
                f"¡Hola {nombre}! 😊 Un gusto saludarte. ¿Cómo te podemos ayudar hoy?\n\n"
                "Podemos ayudarte con:\n"
                "• Ver tu saldo o fecha de vencimiento\n"
                "• Consultar el detalle de tus recibos\n"
                "• Facilidades y acuerdos de pago\n"
                "• Información sobre planes y servicios para tu empresa"
            )
        if intent_type == "despedida":
            return f"¡Con muchísimo gusto, {nombre}! Que tengas un excelente día. Si necesitas cualquier otra cosa, aquí estamos para ayudarte. 👋✨"

        # Fallback contextual natural
        rag_res = await customer_agent.execute({
            "type": "answer_question",
            "pregunta": message,
            "cliente_nombre": nombre,
        })
        return rag_res.get("respuesta", f"Entendido, {nombre} 😊. ¿Hay algo más en lo que te podamos orientar?")

    async def _reply_saldo(self, db: AsyncSession, cliente: BSSCliente, nombre: str) -> str:
        facturas = await self._unpaid_invoices(db, cliente.numero_identificacion_fiscal)
        if not facturas:
            return f"¡Excelentes noticias, {nombre}! 🎉 No tienes recibos pendientes de pago al día de hoy. Tu cuenta está completamente al día."

        deuda_total = sum(Decimal(str(f.charge_total_amount or 0)) for f in facturas)
        vencidas = [f for f in facturas if f.fecha_vto and f.fecha_vto < date.today()]

        mensaje = (
            f"¡Hola {nombre}! 😊 Tu saldo pendiente es de *S/ {deuda_total:,.2f}* "
            f"en {len(facturas)} recibo(s):\n\n"
        )
        for f in facturas[:3]:
            estado = "⚠️ Vencido" if f.fecha_vto and f.fecha_vto < date.today() else "Vigente"
            vto = f.fecha_vto.strftime("%d/%m/%Y") if f.fecha_vto else "por confirmar"
            mensaje += f"• Recibo *{f.nro_doc_fiscal}*: S/ {float(f.charge_total_amount or 0):,.2f} ({estado}, vence {vto})\n"

        codigo_pago = (cliente.numero_identificacion_fiscal or "")[:10]
        mensaje += f"\nPuedes pagar fácil con tu código de pago *{codigo_pago}* desde Yape, BCP o tu banca móvil."

        if vencidas:
            mensaje += "\n\n💡 Si necesitas facilidades de pago o un descuento especial por pronto pago, solo avísanos y con gusto te brindamos opciones."
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
                return f"No encontré un recibo pendiente con el número '{factura_id}'. Si deseas, indícanos el número exacto para revisarlo de inmediato."
            f = matching[0]
        else:
            if not facturas:
                return f"¡Hola {nombre}! No tienes recibos pendientes en este momento. Tu cuenta está al día. 🎉"
            f = facturas[0]

        # Si el usuario pregunta "por qué subió" o pide desglose
        if "por qué" in message.lower() or "porque" in message.lower() or "desglose" in message.lower():
            exp_res = await customer_agent.execute({
                "type": "explain_invoice",
                "factura": {
                    "nro_doc_fiscal": f.nro_doc_fiscal,
                    "charge_total_amount": float(f.charge_total_amount or 0.0),
                }
            })
            return exp_res.get("respuesta", "")

        estado = "Vencido" if f.fecha_vto and f.fecha_vto < date.today() else "Vigente"
        vto = f.fecha_vto.strftime("%d/%m/%Y") if f.fecha_vto else "por confirmar"
        emision = f.fecha_emision.strftime("%d/%m/%Y") if f.fecha_emision else "reciente"
        
        return (
            f"¡Hola {nombre}! Aquí tienes el detalle de tu recibo *{f.nro_doc_fiscal}*:\n\n"
            f"• Monto a pagar: *S/ {float(f.charge_total_amount or 0):,.2f}*\n"
            f"• Fecha de emisión: {emision}\n"
            f"• Último día de pago: {vto} ({estado})\n\n"
            "Puedes pagarlo cómodamente por tu banca móvil o Yape. ¿Tienes alguna consulta sobre tus consumos o deseas facilidades de pago?"
        )

    async def _reply_oferta(self, cliente: BSSCliente, nombre: str) -> str:
        score = float(cliente.score_confianza or 0.80)
        if score >= 0.80:
            propuesta = "un descuento del 5% por pronto pago si regularizas dentro de las próximas 48 horas"
        elif score >= 0.50:
            propuesta = "un descuento especial del 10% para regularizar tu saldo hoy mismo"
        else:
            propuesta = "un plan de facilidades con 15% de descuento sobre recargos y opción de pago fraccionado"

        logger.info("🎯 Oferta personalizada generada", ruc=cliente.numero_identificacion_fiscal)

        return (
            f"¡Hola {nombre}! 🤝 Con gusto te ayudamos. Revisando tu cuenta, tenemos una facilidad especial disponible para ti:\n\n"
            f"👉 *{propuesta}*.\n\n"
            "Puedes realizar tu pago directo y seguro aquí: https://www.movistar.com.pe/pagos\n\n"
            "¿Te gustaría que apliquemos esta opción a tu cuenta?"
        )

    async def process_payload(self, payload: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        """Procesa un payload entrante de WhatsApp y despacha la respuesta."""
        body, phone, target_chat, is_group, from_me = self._parse_message(payload)

        if from_me:
            logger.info("↩️ Mensaje saliente ignorado")
            return {"status": "ignored", "reason": "from_me", "success": True}
        if not body or not target_chat:
            return {"status": "ignored", "reason": "sin_texto_o_destino", "success": True}

        # 🛡️ PROTECCIÓN DEMO: Si está configurado WHATSAPP_DEMO_ALLOWED_PHONE,
        # puede ser un número de celular (ej: 904388543) o un ID de grupo (ej: 120363024823948293@g.us o 120363024823948293)
        allowed_demo = settings.WHATSAPP_DEMO_ALLOWED_PHONE.strip()
        if allowed_demo:
            allowed_items = [n.strip() for n in allowed_demo.split(",") if n.strip()]
            allowed_normalized_phones = [normalize_phone(n) for n in allowed_items if "@g.us" not in n]
            allowed_groups = [n.lower() for n in allowed_items if "@g.us" in n or len(n) > 15]

            sender_normalized = normalize_phone(phone) if phone else ""
            target_chat_lower = target_chat.lower()

            matches_phone = bool(sender_normalized and sender_normalized in allowed_normalized_phones)
            matches_group = any(g in target_chat_lower for g in allowed_groups)

            if not (matches_phone or matches_group):
                logger.info(
                    "🛡️ [Demo Sandbox] Mensaje ignorado para proteger chats/grupos personales",
                    remitente=phone,
                    target_chat=target_chat,
                    is_group=is_group,
                    autorizados=allowed_items,
                )
                return {
                    "status": "ignored",
                    "reason": "demo_protection_active",
                    "mensaje": "Mensaje recibido pero ignorado por filtro de seguridad de Demo",
                    "remitente": phone,
                    "target_chat": target_chat,
                    "success": True,
                }

        cliente = await self._find_client(db, phone) if phone else None
        intent = await self._interpret(body)
        reply = await self._build_reply(db, cliente, intent, body)

        session = payload.get("sessionId") or None
        send_result = await openwa_client.send_message(
            phone_number=target_chat,
            message=reply,
            session_name=session,
        )

        if not send_result.get("success"):
            logger.error("❌ Falló envío de respuesta WhatsApp", target_chat=target_chat, error=send_result.get("error"))

        return {
            "status": "processed",
            "success": True,
            "phone": phone,
            "target_chat": target_chat,
            "is_group": is_group,
            "intent": intent["intent"],
            "client_found": cliente is not None,
            "reply": reply,
            "send_result": send_result,
        }


# Singleton
whatsapp_webhook_service = WhatsAppWebhookService()