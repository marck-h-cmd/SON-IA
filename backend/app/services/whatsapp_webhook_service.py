"""
Servicio de Webhook WhatsApp (OpenWA -> SON-IA).

Recibe los mensajes entrantes que OpenWA reenvía, identifica al cliente
por su número de celular, interpreta la intención, arma una respuesta
con datos REALES de la base de datos (bss_facturas / bss_pagos) y
responde por WhatsApp usando OpenWAClient.

Rutas de decisión:
- Consulta de saldo/deuda   -> revisa facturas no pagadas
- Consulta de factura       -> detalle de la factura indicada
- Solicitud de negociación  -> genera una oferta de descuento
- Otro                      -> saludo + ayuda general
"""

import re
from datetime import date
from decimal import Decimal
from typing import Any, Dict, Optional, Tuple

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.classifier_agent import classifier_agent
from app.database.models import BSSCliente, BSSFactura, BSSPago
from app.integrations.openwa_client import openwa_client, normalize_phone
from app.integrations.openwa_client import to_chat_id  # noqa: F401  (re-export para conveniencia)

logger = structlog.get_logger(__name__)


class WhatsAppWebhookService:
    """Procesa mensajes entrantes de WhatsApp y responde automáticamente."""

    # ============================================================
    # Entrada
    # ============================================================

    def _parse_message(self, payload: Dict[str, Any]) -> Tuple[Optional[str], Optional[str], bool]:
        """
        Extrae (mensaje, teléfono_emisor, from_me) de un payload de OpenWA.

        Soportamos tanto el envelope de OpenWA:
            {"sessionId":..., "event":"message.received", "deliveryId":..., "data":{...}}
        como payloads planos estilo WhatsApp:
            {"body":..., "from":..., "fromMe":...}
        """
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
            # Remover sufijos tipo "@c.us" / "@s.whatsapp.net"
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

    # ============================================================
    # Interpretación
    # ============================================================

    async def _interpret(self, message: str) -> Dict[str, Any]:
        """
        Determina la intención del mensaje usando el Classifier Agent
        (reglas) + heurísticas propias.
        """
        message_lower = message.lower()

        # Si viene el número de factura exacto de BSS (ej: 21-0001234)
        factura_match = re.search(r"factura\s*#?\s*([a-zA-Z0-9\-]+)", message, re.IGNORECASE)

        intent = "consulta_saldo"

        if any(kw in message_lower for kw in ["cuánto debo", "cuanto debo", "saldo", "deuda", "adeudo",
                                              "cuánto pagar", "cuanto pagar", "pagar mi factura", "pagarla"]):
            intent = "consulta_saldo"
        elif any(kw in message_lower for kw in ["vence", "vencimiento", "mi recibo", "mi factura",
                                                "por qué subió", "porque subio", "subió mi", "recibo"]):
            intent = "consulta_factura"
        elif any(kw in message_lower for kw in ["descuento", "no puedo pagar", "facilidad", "plazo",
                                                "negociar", "rebaja", "mis cuotas", "cuotas"]):
            intent = "negociacion"
        elif any(kw in message_lower for kw in ["hola", "buenas", "saludos", "ayuda", "quién", "quien eres"]):
            intent = "saludo"
        elif any(kw in message_lower for kw in ["gracias", "ok", "listo"]):
            intent = "despedida"

        factura_id = factura_match.group(1) if factura_match else None

        # Registro en el classifier agent (consistencia con el ecosistema)
        try:
            clasificacion = await classifier_agent.execute({
                "type": "classify_message",
                "message": message,
                "canal": "whatsapp",
            })
            logger.info("🏷️ Intención detectada", intent=intent,
                        categoria=clasificacion.get("categoria"))
        except Exception as e:
            logger.warning("⚠️ Classifier agent falló", error=str(e))

        return {"intent": intent, "factura_id": factura_id}

    # ============================================================
    # Generación de respuesta con datos reales
    # ============================================================

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
        """Construye la respuesta de texto usando datos de la BD."""
        if not cliente:
            return (
                "Hola 👋, no pudimos identificarte con este número. "
                "Verifica que estés escribiendo desde el celular registrado en tu cuenta. "
                "Para mayor asistencia comunícate con nuestra central 0800-XXXXX."
            )

        nombre = (cliente.razon_social or "cliente").split("_")[-1]
        intent_type = intent["intent"]
        factura_id = intent.get("factura_id")

        if intent_type == "consulta_saldo":
            return await self._reply_saldo(db, cliente, nombre)
        if intent_type == "consulta_factura":
            return await self._reply_factura(db, cliente, nombre, factura_id)
        if intent_type == "negociacion":
            return await self._reply_oferta(cliente, nombre)
        if intent_type == "saludo":
            return (
                f"Hola {nombre} 👋, soy el asistente virtual de Movistar Empresas. "
                "Puedo ayudarte a saber cuánto debes, cuándo vence tu factura, "
                "o con plazos y descuentos para tu pago. ¿Qué deseas?"
            )
        return (
            f"Entendido ✅. Puedo ayudarte a consultar tu saldo, fechas de vencimiento "
            "o gestionar un plan de pagos. Escríbeme, por ejemplo: \"¿cuánto debo?\""
        )

    async def _reply_saldo(self, db: AsyncSession, cliente: BSSCliente, nombre: str) -> str:
        facturas = await self._unpaid_invoices(db, cliente.numero_identificacion_fiscal)
        if not facturas:
            return f"¡Excelente {nombre}! 🎉 No tienes facturas pendientes de pago."

        deuda_total = sum(
            Decimal(str(f.charge_total_amount or 0)) for f in facturas
        )
        vencidas = [f for f in facturas if f.fecha_vto and f.fecha_vto < date.today()]

        mensaje = (
            f"Hola {nombre} 👋, tu saldo pendiente es de **S/ {deuda_total:,.2f}** "
            f"en {len(facturas)} factura(s).\n"
        )
        for f in facturas[:3]:
            estado = "VENCIDA" if f.fecha_vto and f.fecha_vto < date.today() else "pendiente"
            vto = f.fecha_vto.isoformat() if f.fecha_vto else "s/f"
            mensaje += f"• Factura {f.nro_doc_fiscal}: S/ {float(f.charge_total_amount or 0):,.2f} "
            mensaje += f"({estado}, vence {vto})\n"

        if vencidas:
            mensaje += ("\n⚠️ Tienes facturas vencidas. Podemos ofrecerte un plan de pago "
                        "o descuento. Responde \"negociar\" para ver opciones.")
        return mensaje

    async def _reply_factura(
        self,
        db: AsyncSession,
        cliente: BSSCliente,
        nombre: str,
        factura_id: Optional[str],
    ) -> str:
        facturas = await self._unpaid_invoices(db, cliente.numero_identificacion_fiscal)
        if factura_id:
            matching = [f for f in facturas if factura_id in f.nro_doc_fiscal]
            if not matching:
                return f"No encontré una factura activa con ese número ({factura_id})."
            f = matching[0]
        else:
            if not facturas:
                return f"¡Buenas {nombre}! No tienes facturas pendientes. 🎉"
            f = facturas[0]

        estado = "VENCIDA" if f.fecha_vto and f.fecha_vto < date.today() else "pendiente"
        vto = f.fecha_vto.isoformat() if f.fecha_vto else "sin fecha"
        emision = f.fecha_emision.isoformat() if f.fecha_emision else "s/f"
        return (
            f"Hola {nombre} 👋, aquí el detalle de tu factura {f.nro_doc_fiscal}:\n"
            f"• Emisión: {emision}\n"
            f"• Vencimiento: {vto}\n"
            f"• Total: S/ {float(f.charge_total_amount or 0):,.2f}\n"
            f"• Estado: {estado}\n\n"
            "¿Deseas gestionar una fecha de pago?"
        )

    async def _reply_oferta(self, cliente: BSSCliente, nombre: str) -> str:
        score = float(cliente.score_confianza or 0)
        if score >= 0.80:
            descuento = 5
            mensaje = "un descuento del 5% por pronto pago"
        elif score >= 0.50:
            descuento = 10
            mensaje = "un descuento del 10%"
        else:
            descuento = 15
            mensaje = "facilidades: 15% de descuento y plazo hasta 30 días"

        logger.info("🎯 Oferta generada", score=score, descuento=descuento)

        return (
            f"Hola {nombre} 🤝, para ayudarte a regularizar tu deuda te puedo ofrecer {mensaje}. "
            "¿Deseas que un asesor confirme la propuesta y la enviemos por WhatsApp?"
        )

    # ============================================================
    # Orquestación
    # ============================================================

    async def process_payload(self, payload: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        """Procesa un payload entrante y responde por WhatsApp."""
        body, phone, from_me = self._parse_message(payload)

        # Ignorar mensajes enviados por nosotros mismos o sin texto
        if from_me:
            logger.info("↩️ Mensaje propio ignorado")
            return {"status": "ignored", "reason": "from_me", "success": True}
        if not body or not phone:
            return {"status": "ignored", "reason": "sin_texto_o_numero", "success": True}

        cliente = await self._find_client(db, phone)

        intent = await self._interpret(body)
        reply = await self._build_reply(db, cliente, intent, body)

        # Responder por WhatsApp
        session = payload.get("sessionId") or None
        send_result = await openwa_client.send_message(
            phone_number=phone,
            message=reply,
            session_name=session,
        )

        if not send_result.get("success"):
            logger.error("❌ Falló envío de respuesta WhatsApp", phone=phone,
                         error=send_result.get("error"))

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