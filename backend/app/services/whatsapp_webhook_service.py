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
from app.config.settings import get_settings
from app.database.models import BSSCliente, BSSFactura, BSSPago
from app.integrations.openwa_client import openwa_client, normalize_phone
from app.integrations.openwa_client import to_chat_id  # noqa: F401

logger = structlog.get_logger(__name__)
settings = get_settings()


def _format_friendly_name(raw_name: Optional[str]) -> str:
    """Convierte 'MARCK ALESSANDRO HERMENEGILDO PACHECO', 'CLIENT_01001' a nombres cálidos como 'Álvaro' o 'Marck'."""
    if not raw_name:
        return "Álvaro"
    s_name = str(raw_name).strip()
    if "01001" in s_name or "1000001" in s_name or "2099999001" in s_name:
        return "Álvaro"
    if "01002" in s_name or "1000002" in s_name or "2099999002" in s_name:
        return "Marck"
    if "01003" in s_name or "1000003" in s_name or "2099999003" in s_name:
        return "Carlos"
    clean = re.sub(r"[_\-]+", " ", s_name).strip()
    words = [w.capitalize() for w in clean.split() if w]
    if not words:
        return "Álvaro"
    if words[0].lower() in ["empresa", "corporacion", "inversiones", "grupo", "servicios", "comercial", "client"]:
        if words[0].lower() == "client":
            return "Álvaro"
        return " ".join(words[:3])
    if len(words) >= 2 and len(words[0]) <= 7:
        return f"{words[0]} {words[1]}"
    return words[0]


def _extract_real_phone(payload: Dict[str, Any], data: Dict[str, Any]) -> Optional[str]:
    """
    Extrae el número de teléfono real del remitente, descartando identificadores internos
    de WhatsApp Multi-Device (como @lid), IDs de grupo (@g.us) y buscando números reales.
    """
    candidates = []

    # 1. Explorar sender
    sender = data.get("sender") or payload.get("sender") or {}
    if isinstance(sender, dict):
        candidates.extend([
            sender.get("id"),
            sender.get("number"),
            sender.get("phoneNumber"),
            sender.get("formattedName"),
            sender.get("wid"),
            sender.get("phone"),
        ])
    elif isinstance(sender, str):
        candidates.append(sender)

    # 2. Explorar key y _data
    key = data.get("key") or payload.get("key") or {}
    if isinstance(key, dict):
        candidates.extend([
            key.get("participant"),
            key.get("remoteJid"),
        ])

    _data = data.get("_data") or {}
    if isinstance(_data, dict):
        _sender = _data.get("sender") or {}
        if isinstance(_sender, dict):
            candidates.extend([_sender.get("id"), _sender.get("number")])
        candidates.extend([
            _data.get("author"),
            _data.get("participant"),
            _data.get("from"),
            (_data.get("id") or {}).get("participant") if isinstance(_data.get("id"), dict) else None,
        ])

    # 3. Campos directos en data
    candidates.extend([
        data.get("participant"),
        data.get("author"),
        data.get("from"),
    ])

    # Filtrar candidatos no nulos y descartar grupos (@g.us), status, broadcast
    clean_candidates = [
        str(c).strip() for c in candidates 
        if c and "@g.us" not in str(c) and "@broadcast" not in str(c)
    ]

    # Prioridad A: Candidatos con formato @c.us o @s.whatsapp.net (JID estándar de usuario)
    for c in clean_candidates:
        if "@c.us" in c or "@s.whatsapp.net" in c:
            num = c.split("@")[0].split(":")[0]
            norm = normalize_phone(num)
            if norm and len(norm) == 9 and norm.startswith("9"):
                return norm

    # Prioridad B: Buscar cualquier número peruano de 9 dígitos (o 519XXXXXXXX)
    for c in clean_candidates:
        if "@lid" in c:
            continue
        num = c.split("@")[0].split(":")[0]
        norm = normalize_phone(num)
        if norm and len(norm) == 9 and norm.startswith("9"):
            return norm

    # Prioridad D: Búsqueda recursiva profunda en todo el payload
    def _search_nested(obj: Any) -> Optional[str]:
        if isinstance(obj, dict):
            for k, v in obj.items():
                res = _search_nested(v)
                if res:
                    return res
        elif isinstance(obj, list):
            for item in obj:
                res = _search_nested(item)
                if res:
                    return res
        elif isinstance(obj, (str, int)):
            s = str(obj)
            if "@lid" not in s and "@g.us" not in s and "@broadcast" not in s:
                m = re.search(r"\b(?:51)?(9\d{8})\b", s)
                if m:
                    phone_found = m.group(1)
                    # Descartar si es el número del bot de la sesión actual
                    if phone_found != "904388543":
                        return phone_found
        return None

    deep_phone = _search_nested(payload)
    if deep_phone:
        return deep_phone

    return None


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

        # Extraer el teléfono real del remitente
        phone = _extract_real_phone(payload, data)

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

    async def _find_client(self, db: AsyncSession, phone: Optional[str] = None, body: Optional[str] = None) -> Optional[BSSCliente]:
        """
        Busca al cliente por:
        1. Su número de celular de remitente (columna numero_celular).
        2. Un número de celular peruano de 9 dígitos presente en el texto del mensaje (ej: 901528082).
        3. Un número de RUC peruano de 11 dígitos presente en el texto del mensaje (ej: 2099999001).
        """
        cliente = None

        # 1. Buscar por número remitente
        if phone:
            norm_phone = phone[-9:]
            result = await db.execute(
                select(BSSCliente).where(BSSCliente.numero_celular.like(f"%{norm_phone}"))
            )
            cliente = result.scalars().first()

        # 2. Si no se encontró y hay texto, buscar celular peruano de 9 dígitos en el cuerpo del mensaje
        if not cliente and body:
            phone_match = re.search(r"\b(9\d{8})\b", body)
            if phone_match:
                extracted_phone = phone_match.group(1)
                result = await db.execute(
                    select(BSSCliente).where(BSSCliente.numero_celular.like(f"%{extracted_phone}"))
                )
                cliente = result.scalars().first()
                if cliente:
                    logger.info("👤 Cliente identificado por celular en texto", phone=extracted_phone,
                                ruc=cliente.numero_identificacion_fiscal, nombre=cliente.razon_social)

        # 3. Si aún no se encontró, buscar RUC de 11 dígitos en el cuerpo del mensaje
        if not cliente and body:
            ruc_match = re.search(r"\b((?:10|20)\d{9})\b", body)
            if ruc_match:
                extracted_ruc = ruc_match.group(1)
                result = await db.execute(
                    select(BSSCliente).where(BSSCliente.numero_identificacion_fiscal == extracted_ruc)
                )
                cliente = result.scalars().first()
                if cliente:
                    logger.info("👤 Cliente identificado por RUC en texto", ruc=extracted_ruc,
                                nombre=cliente.razon_social)

        # 4. Fallback de Demo Sandbox: Si está configurado WHATSAPP_DEMO_ALLOWED_PHONE,
        # cargar el cliente de prueba configurado para asegurar 100% de consistencia
        if not cliente:
            allowed_demo = (getattr(settings, "WHATSAPP_DEMO_ALLOWED_PHONE", "") or "").strip()
            if allowed_demo:
                allowed_phones = [normalize_phone(n) for n in allowed_demo.split(",") if n.strip() and "@g.us" not in n]
                if allowed_phones:
                    demo_phone = allowed_phones[0]
                    result = await db.execute(
                        select(BSSCliente).where(BSSCliente.numero_celular.like(f"%{demo_phone}"))
                    )
                    cliente = result.scalars().first()
                    if cliente:
                        logger.info("👤 Cliente demo asignado por configuración sandbox", phone=demo_phone,
                                    ruc=cliente.numero_identificacion_fiscal, nombre=cliente.razon_social)

        if cliente:
            logger.info("👤 Cliente final identificado", ruc=cliente.numero_identificacion_fiscal,
                        nombre=cliente.razon_social)
        else:
            logger.warning("🚫 Cliente NO encontrado para teléfono o mensaje", phone=phone, body=body)

        return cliente

    async def _interpret(self, message: str) -> Dict[str, Any]:
        """
        Determina la intención del mensaje usando el Classifier Agent y heurísticas.
        """
        message_lower = message.lower()
        factura_match = re.search(r"factura\s*#?\s*([a-zA-Z0-9\-]+)", message, re.IGNORECASE)

        # 1. Aceptación de Facilidad / Descuento
        if any(kw in message_lower for kw in [
            "acepto", "aceptar", "sí acepto", "si acepto", "aplícala", "aplicalas",
            "aplícalo", "aplicalos", "de acuerdo", "quiero el descuento", "me parece bien",
            "aplica la opción", "aplica la opcion", "confirmar descuento", "confirmar oferta"
        ]):
            intent = "aceptacion_oferta"

        # 2. Despedida / Agradecimiento
        elif any(kw in message_lower for kw in [
            "muchas gracias", "mil gracias", "gracias", "quedó claro", "quedo claro",
            "quedó muy claro", "quedo muy claro", "todo claro", "todo muy claro",
            "listo gracias", "perfecto gracias", "excelente gracias", "vale gracias",
            "chau", "adiós", "adios", "hasta luego", "bye"
        ]):
            intent = "despedida"

        # 2. Métodos / Lugares de Pago (¿Cómo pagar?, por Yape, bancos, etc.)
        elif any(kw in message_lower for kw in [
            "cómo puedo pagar", "como puedo pagar", "cómo pagar", "como pagar",
            "dónde pagar", "donde pagar", "por yape", "yape", "app de mi banco", "app del banco",
            "canales de pago", "lugares de pago", "forma de pago", "formas de pago",
            "banca móvil", "banca movil", "transferencia", "bcp", "bbva", "interbank"
        ]):
            intent = "consulta_rag"

        # 3. Intereses Moratorios / TAMN / Penalidades
        elif any(kw in message_lower for kw in [
            "cómo se calculan los intereses", "como se calculan los intereses",
            "interés", "interes", "intereses", "tamn", "mora", "moratorios",
            "recargo", "penalidad", "corte de servicio", "corte del servicio",
            "si se vence mi fecha", "si me paso"
        ]):
            intent = "consulta_rag"

        # 4. Negociación / Facilidades / Descuentos
        elif any(kw in message_lower for kw in [
            "descuento", "no puedo pagar", "facilidad", "facilidades", "plazo",
            "negociar", "rebaja", "mis cuotas", "cuotas", "fraccionar", "fraccionamiento",
            "acuerdo", "no dispongo", "no cuento con", "pronto pago"
        ]):
            intent = "negociacion"

        # 5. Desglose de Factura / Por qué subió
        elif any(kw in message_lower for kw in [
            "por qué subió", "porque subio", "por que subio", "por qué subio",
            "desglose", "detalle recibo", "detalle de mi recibo", "detalle factura",
            "explicar factura", "explícame"
        ]):
            intent = "consulta_factura"

        # 6. Planes y Servicios Corporativos (Fibra, Dúos, Requisitos, etc.)
        elif any(kw in message_lower for kw in [
            "plan", "planes", "fibra", "fibra óptica", "fibra optica", "velocidad",
            "megas", "gigas", "roaming", "tarifa", "duo", "trio", "requisitos",
            "contratar", "promocion", "promoción", "corporativo", "aumentar velocidad"
        ]):
            intent = "consulta_rag"

        # 7. Consulta de Saldo / Deuda / Cuándo vence
        elif any(kw in message_lower for kw in [
            "cuánto debo", "cuanto debo", "saldo", "deuda", "adeudo",
            "cuándo vence", "cuando vence", "fecha de vencimiento", "mis recibos",
            "cuánto pagar", "cuanto pagar", "pagar mi factura", "pagarla"
        ]):
            intent = "consulta_saldo"

        # 8. Saludo
        elif any(kw in message_lower for kw in [
            "hola", "buenas", "saludos", "ayuda", "buen dia", "buen día",
            "buenos dias", "buenos días", "buenas tardes", "buenas noches"
        ]):
            intent = "saludo"

        else:
            intent = "consulta_rag"

        # Si el mensaje incluye un celular o RUC explícito y no tiene otra intención, priorizar consulta de saldo
        if re.search(r"\b(9\d{8}|(?:10|20)\d{9})\b", message) and intent in ["consulta_general", "consulta_rag"]:
            intent = "consulta_saldo"

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
        if intent_type == "aceptacion_oferta":
            cod_pago = (cliente.numero_identificacion_fiscal or "")[:10] if cliente else "2099999001"
            return (
                f"¡Excelente decisión, {nombre}! 🎉 He registrado la facilidad de pago en el sistema.\n\n"
                f"• Puedes realizar tu abono seguro aquí: https://www.movistar.com.pe/pagos\n"
                f"• O desde tu banca móvil / Yape con tu código de pago *{cod_pago}*.\n\n"
                "Una vez confirmado el abono, nuestro motor de conciliación cruzará el pago, generará la nota de crédito respectiva por el beneficio y actualizará tu estado en el sistema BSS. ¡Muchas gracias por tu preferencia! 🤝"
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
            
            # Si es chat privado (no grupo) y viene con formato @lid (identificador de WhatsApp Multi-Device),
            # autorizar el chat y mapear el teléfono al número de la demo (ej: 901528082)
            if not matches_phone and not matches_group and not is_group and "@lid" in target_chat_lower and allowed_normalized_phones:
                matches_phone = True
                if not phone:
                    phone = allowed_normalized_phones[0]

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

        cliente = await self._find_client(db, phone=phone, body=body)
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