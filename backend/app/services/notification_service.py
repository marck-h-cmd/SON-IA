"""
Servicio de Notificaciones
"""

from typing import Dict, Any, Optional
import httpx
import structlog

from app.config.settings import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class NotificationService:
    """
    Servicio para enviar notificaciones a clientes.
    
    Canales:
    - Email (SMTP)
    - WhatsApp (Twilio)
    - SMS (Twilio)
    - Portal web (WebSocket)
    """
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        template: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Envía notificación por email
        """
        logger.info(f"📧 Enviando email a {to_email}: {subject}")
        
        # Simulación - En producción usaría SMTP
        return {
            "status": "sent",
            "canal": "email",
            "to": to_email,
            "subject": subject,
        }
    
    async def send_whatsapp(
        self,
        to_phone: str,
        message: str,
    ) -> Dict[str, Any]:
        """
        Envía notificación por WhatsApp
        """
        logger.info(f"💬 Enviando WhatsApp a {to_phone}")
        
        if settings.ENVIRONMENT == "development":
            try:
                # Usa OpenWA en development
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        settings.OPENWA_WEBHOOK_URL,
                        json={
                            "to": to_phone,
                            "message": message
                        },
                        timeout=10.0
                    )
                    response.raise_for_status()
                    
                    logger.info("✅ WhatsApp enviado vía OpenWA webhook")
                    return {
                        "status": "sent",
                        "canal": "whatsapp",
                        "to": to_phone,
                        "provider": "openwa"
                    }
            except Exception as e:
                logger.error(f"❌ Error enviando WhatsApp por OpenWA: {e}")
                return {
                    "status": "error",
                    "canal": "whatsapp",
                    "to": to_phone,
                    "error": str(e)
                }
        else:
            # Simulación o producción con Twilio
            return {
                "status": "sent",
                "canal": "whatsapp",
                "to": to_phone,
                "provider": "twilio"
            }
    
    async def send_sms(
        self,
        to_phone: str,
        message: str,
    ) -> Dict[str, Any]:
        """
        Envía notificación por SMS
        """
        logger.info(f"📱 Enviando SMS a {to_phone}")
        
        return {
            "status": "sent",
            "canal": "sms",
            "to": to_phone,
        }
    
    async def send_payment_reminder(
        self,
        cliente_email: str,
        cliente_nombre: str,
        factura_id: int,
        monto: float,
        fecha_vencimiento: str,
    ) -> Dict[str, Any]:
        """
        Envía recordatorio de pago personalizado
        """
        subject = f"Recordatorio de pago - Factura #{factura_id}"
        body = (
            f"Hola {cliente_nombre},\n\n"
            f"Te recordamos que tu factura #{factura_id} por S/ {monto:.2f} "
            f"vence el {fecha_vencimiento}.\n\n"
            f"Puedes pagar en línea desde nuestro portal de autogestión.\n\n"
            f"Saludos,\nSON-IA | Integratel"
        )
        
        return await self.send_email(cliente_email, subject, body)
    
    async def send_negotiation_offer(
        self,
        cliente_email: str,
        cliente_nombre: str,
        descuento: float,
        fecha_limite: str,
    ) -> Dict[str, Any]:
        """
        Envía oferta de negociación personalizada
        """
        subject = "¡Oferta especial para ti! Descuento en tu factura"
        body = (
            f"Hola {cliente_nombre},\n\n"
            f"Tienes un descuento del {descuento}% disponible en tu factura.\n"
            f"Esta oferta vence el {fecha_limite}.\n\n"
            f"¡Aprovecha ahora!\n\n"
            f"Saludos,\nSON-IA | Integratel"
        )
        
        return await self.send_email(cliente_email, subject, body)


# Singleton
notification_service = NotificationService()