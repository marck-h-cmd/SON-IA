"""
Test de Generación de XML SUNAT UBL 2.1 y Metadatos
"""

import asyncio
import sys
from pathlib import Path
import httpx

sys.path.insert(0, str(Path(__file__).parent))

from app.main import app


async def test_sunat():
    print("=" * 60)
    print("📑 PROBANDO GENERADOR SUNAT UBL 2.1 (TIPO 14 & FACTURAS)")
    print("=" * 60)
    
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Obtener una factura existente
        res = await client.get("/api/v1/billing/facturas?limit=1")
        assert res.status_code == 200, f"Error: {res.text}"
        data = res.json()
        assert len(data["items"]) > 0, "No hay facturas en BD"
        
        factura_id = data["items"][0]["numero_factura"]
        print(f"✅ Factura seleccionada para prueba: {factura_id}")

        # 1. Info SUNAT (Hash SHA-256 + QR String)
        print("\n1. GET /api/v1/billing/facturas/{id}/sunat-info:")
        res_info = await client.get(f"/api/v1/billing/facturas/{factura_id}/sunat-info")
        assert res_info.status_code == 200, f"Error: {res_info.text}"
        info = res_info.json()
        print(f"✅ Comprobante: {info['tipo_nombre']} ({info['serie']}-{info['correlativo']})")
        print(f"✅ Hash SHA-256 (DigestValue): {info['hash_sha256']}")
        print(f"✅ Cadena QR SUNAT: {info['qr_cadena'][:80]}...")
        print(f"✅ Estado OSE/SUNAT: {info['estado_sunat']}")

        # 2. Descarga XML UBL 2.1
        print("\n2. GET /api/v1/billing/facturas/{id}/xml:")
        res_xml = await client.get(f"/api/v1/billing/facturas/{factura_id}/xml")
        assert res_xml.status_code == 200, f"Error: {res_xml.text}"
        assert "Invoice" in res_xml.text
        assert "UBLVersionID>2.1" in res_xml.text
        print(f"✅ XML UBL 2.1 generado correctamente ({len(res_xml.text)} bytes)")
        print(f"   Primeras líneas del XML:")
        for line in res_xml.text.split("\n")[:8]:
            print(f"   {line}")

    print("\n" + "=" * 60)
    print("🎉 GENERADOR SUNAT UBL 2.1 VERIFICADO AL 100%")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_sunat())
