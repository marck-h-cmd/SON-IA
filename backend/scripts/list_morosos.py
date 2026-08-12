"""
Lista clientes con facturas impagas (misma lógica de whatasapp_webhook_service).
Uso: python -m scripts.list_morosos  (dentro del contenedor backend, cwd=/app)
"""

import asyncio

from sqlalchemy import select

from app.database.connection import AsyncSessionLocal
from app.database.models import BSSCliente, BSSFactura, BSSPago

from datetime import date


async def main() -> None:
    async with AsyncSessionLocal() as db:
        facturas = (await db.execute(select(BSSFactura))).scalars().all()
        pagadas = set((await db.execute(select(BSSPago.factura_afectada))).scalars().all())
        impagas = [f for f in facturas if f.nro_doc_fiscal not in pagadas]

        por_ruc: dict = {}
        for f in impagas:
            por_ruc.setdefault(f.numero_identificacion_fiscal, []).append(f)

        hoy = date.today()
        print(f"TOTAL facturas en BD: {len(facturas)} | pagadas: {len(pagadas)} | impagas: {len(impagas)}")
        print(f"Clientes con deuda: {len(por_ruc)}\n")
        header = f"{'RUC':<12}{'Cliente':<15}{'Facts':<7}{'Total S/':<13}{'Venc':<6}{'Celular'}"
        print(header)
        print("-" * 70)
        for ruc, fs in sorted(por_ruc.items(), key=lambda kv: -sum(float(f.charge_total_amount or 0) for f in kv[1])):
            cli = (await db.execute(select(BSSCliente).where(BSSCliente.numero_identificacion_fiscal == ruc))).scalars().first()
            total = sum(float(f.charge_total_amount or 0) for f in fs)
            venc = sum(1 for f in fs if f.fecha_vto and f.fecha_vto < hoy)
            nombre = (cli.razon_social or "-").split("_")[-1] if cli else "-"
            cel = (cli.numero_celular or "-") if cli else "-"
            print(f"{ruc:<12}{str(nombre)[:14]:<15}{len(fs):<7}{total:,.2f}     {venc:<6}{cel}")


if __name__ == "__main__":
    asyncio.run(main())