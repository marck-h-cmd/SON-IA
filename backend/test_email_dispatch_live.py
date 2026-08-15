"""
Test de integración para el despacho de correos con plantilla Movistar y PDF adjunto (sin XML)
"""

import asyncio
import httpx
from sqlalchemy import select
from app.database.connection import async_session_factory
from app.database.models import BSSFactura, BSSCliente
from app.services.notification_service import notification_service
from app.services.pdf_service import pdf_generator


async def test_email_dispatch():
    print("🧪 Probando despacho de correo con plantilla Movistar y PDF adjunto...")
    async with async_session_factory() as sess:
        res = await sess.execute(select(BSSFactura).limit(1))
        factura = res.scalar_one_or_none()
        assert factura is not None, "No hay facturas en BD"

        res_cli = await sess.execute(
            select(BSSCliente).where(BSSCliente.numero_identificacion_fiscal == factura.numero_identificacion_fiscal)
        )
        cliente = res_cli.scalar_one_or_none()
        if not cliente:
            cliente = BSSCliente(
                numero_identificacion_fiscal=factura.numero_identificacion_fiscal,
                razon_social="MARCK ALESSANDRO HERMENEGILDO PACHECO",
            )

        # 1. Generar PDF de 3 páginas
        pdf_bytes = pdf_generator.generar_pdf_recibo(factura, cliente)
        assert len(pdf_bytes) > 2000, "PDF muy pequeño"

        # 2. Despachar email
        resultado = await notification_service.send_invoice_email(
            to_email="test.marck@gmail.com",
            cliente_nombre=cliente.razon_social,
            numero_factura=factura.nro_doc_fiscal,
            monto_total=float(factura.charge_total_amount or 39.90),
            fecha_vencimiento="18/08",
            segmento="Móvil",
            mes="Agosto",
            codigo_pago="904388543",
            costo_reconexion=10.00,
            pdf_bytes=pdf_bytes,
        )

        print("Resultado del envío:", resultado)
        assert resultado["status"] in ["sent", "ok"], "El estado debe ser sent"
        assert resultado["pdf_adjunto"].endswith(".pdf"), "Debe adjuntar solo el PDF"
        print("✅ Despacho de correo validado con éxito!")


async def test_http_endpoint():
    print("\n🧪 Probando endpoint HTTP POST /api/v1/billing/facturas/{id}/enviar-email...")
    async with async_session_factory() as sess:
        res = await sess.execute(select(BSSFactura).limit(1))
        f = res.scalar_one()
        
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"http://localhost:8000/api/v1/billing/facturas/{f.nro_doc_fiscal}/enviar-email",
                params={"email_destino": "demo.evaluador@movistar.pe"},
            )
            print(f"Status HTTP: {r.status_code}")
            print(f"Response: {r.json()}")
            assert r.status_code == 200
            assert r.json()["status"] == "success"
            print("🎉 ¡Endpoint de envío de correo funcionando al 100%!")


async def main():
    await test_email_dispatch()
    await test_http_endpoint()


if __name__ == "__main__":
    asyncio.run(main())
