"""
Test de verificación del filtro de seguridad para la Demo de WhatsApp (Whitelist de protección de chats personales)
"""

import asyncio
from app.config.settings import get_settings
from app.services.whatsapp_webhook_service import whatsapp_webhook_service
from app.database.connection import async_session_factory

settings = get_settings()


async def test_whitelist():
    print("🧪 Verificando filtro de seguridad de WhatsApp para Demo...")
    
    # Configuramos el número de prueba autorizado
    settings.WHATSAPP_DEMO_ALLOWED_PHONE = "904388543"
    print(f"Número autorizado configurado: {settings.WHATSAPP_DEMO_ALLOWED_PHONE}")

    async with async_session_factory() as db:
        # Caso 1: Mensaje de un chat ajeno / amigo / familiar (NO autorizado)
        payload_ajeno = {
            "event": "message.received",
            "data": {
                "body": "Hola amigo, vamos a jugar fútbol?",
                "from": "51987654321@c.us",
                "fromMe": False,
            }
        }
        res_ajeno = await whatsapp_webhook_service.process_payload(payload_ajeno, db)
        print("Caso 1 (Chat personal no autorizado):", res_ajeno)
        assert res_ajeno["status"] == "ignored", "El chat personal ajeno debe ser ignorado"
        assert res_ajeno["reason"] == "demo_protection_active", "La razón debe ser demo_protection_active"
        print("✅ Chat personal protegido e ignorado exitosamente!")

        # Caso 2: Mensaje del número de prueba de la demo (Autorizado)
        payload_demo = {
            "event": "message.received",
            "data": {
                "body": "Hola, ¿cuánto debo de mi recibo?",
                "from": "51904388543@c.us",
                "fromMe": False,
            }
        }
        res_demo = await whatsapp_webhook_service.process_payload(payload_demo, db)
        print("\nCaso 2 (Número autorizado para la Demo):", res_demo)
        assert res_demo["status"] == "processed", "El número de la demo debe ser procesado"
        assert res_demo["intent"] == "consulta_saldo", "La intención debe ser consulta_saldo"
        print("✅ Número de demo procesado y respondido con éxito!")

    print("\n🎉 ¡Filtro de seguridad de WhatsApp para Demo 100% verificado!")


if __name__ == "__main__":
    asyncio.run(test_whitelist())
