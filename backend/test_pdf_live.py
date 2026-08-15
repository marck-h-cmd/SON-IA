"""
Test para validar la generación real de PDF con diseño Movistar
"""
import asyncio
from datetime import date
from sqlalchemy import select
from app.database.connection import async_session_factory
from app.database.models import BSSFactura, BSSCliente
from app.services.pdf_service import pdf_generator


async def test_pdf_generation():
    print("🧪 Probando generador de PDF Oficial Movistar...")
    async with async_session_factory() as session:
        res = await session.execute(select(BSSFactura).limit(1))
        factura = res.scalar_one_or_none()
        
        if not factura:
            print("⚠️ No hay facturas en BD para probar, creando mock...")
            factura = BSSFactura(
                nro_doc_fiscal="S1AA-0053100009",
                numero_identificacion_fiscal="20601234567",
                charge_net_amount=33.81,
                charge_igv_invoice=6.09,
                charge_total_amount=39.90,
                fecha_emision=date(2026, 8, 5),
                fecha_vto=date(2026, 8, 18),
                cod_cuenta="746452202",
                cod_cliente="904388543",
            )
            cliente = BSSCliente(
                numero_identificacion_fiscal="20601234567",
                razon_social="MARCK ALESSANDRO HERMENEGILDO PACHECO",
                numero_celular="904388543",
                sunat_departamento="LIMA",
                sunat_provincia="LIMA",
            )
        else:
            res_cli = await session.execute(
                select(BSSCliente).where(BSSCliente.numero_identificacion_fiscal == factura.numero_identificacion_fiscal)
            )
            cliente = res_cli.scalar_one_or_none()
            if not cliente:
                cliente = BSSCliente(
                    numero_identificacion_fiscal=factura.numero_identificacion_fiscal,
                    razon_social="MARCK ALESSANDRO HERMENEGILDO PACHECO",
                    numero_celular="904388543",
                )

        pdf_bytes = pdf_generator.generar_pdf_recibo(factura, cliente)
        assert len(pdf_bytes) > 1000, "El PDF generado está vacío o es muy pequeño"
        assert pdf_bytes.startswith(b"%PDF-"), "El encabezado no es un PDF válido"
        print(f"✅ PDF generado exitosamente: {len(pdf_bytes)} bytes con encabezado {pdf_bytes[:8].decode('latin1')}")


if __name__ == "__main__":
    asyncio.run(test_pdf_generation())
