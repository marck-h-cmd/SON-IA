import asyncio
import httpx
from sqlalchemy import select
from app.database.connection import async_session_factory
from app.database.models import BSSFactura


async def test_endpoint():
    async with async_session_factory() as sess:
        res = await sess.execute(select(BSSFactura).limit(1))
        f = res.scalar_one()
        print(f"Testing PDF download for factura ID: {f.nro_doc_fiscal}")
        
        async with httpx.AsyncClient() as client:
            r = await client.get(f"http://localhost:8000/api/v1/billing/facturas/{f.nro_doc_fiscal}/pdf")
            print(f"Status: {r.status_code}")
            print(f"Content-Type: {r.headers.get('content-type')}")
            print(f"Content-Disposition: {r.headers.get('content-disposition')}")
            print(f"Bytes count: {len(r.content)}")
            print(f"PDF Header: {r.content[:8]}")
            assert r.status_code == 200
            assert r.content.startswith(b"%PDF-")
            print("🎉 ¡Endpoint de descarga de PDF funcionando al 100%!")


if __name__ == "__main__":
    asyncio.run(test_endpoint())
