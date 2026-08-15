"""
Test de Endpoints y Operaciones HITL (Human-in-the-Loop) vía ASGI Test Client
"""

import asyncio
import sys
from pathlib import Path
import httpx

sys.path.insert(0, str(Path(__file__).parent))

from app.main import app
from app.database.connection import init_db


async def test_hitl_api():
    print("=" * 60)
    print("🛡️ PROBANDO ENDPOINTS HITL (HUMAN-IN-THE-LOOP)")
    print("=" * 60)
    
    await init_db()
    
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # 1. Metricas
        print("\n1. GET /api/v1/hitl/metricas:")
        res = await client.get("/api/v1/hitl/metricas")
        assert res.status_code == 200, f"Error {res.status_code}: {res.text}"
        metricas = res.json()
        print(f"✅ Métricas obtenidas: Pendientes={metricas['total_pendientes']}, Aprobadas={metricas['total_aprobadas']}, Monto Retenido=S/ {metricas['monto_total_retenido']:,.2f}")

        # 2. Solicitudes paginadas
        print("\n2. GET /api/v1/hitl/solicitudes?limit=5:")
        res = await client.get("/api/v1/hitl/solicitudes?limit=5")
        assert res.status_code == 200, f"Error {res.status_code}: {res.text}"
        data = res.json()
        print(f"✅ Solicitudes obtenidas: Total={data['total']}, Retornadas={len(data['items'])}")
        
        if data['items']:
            first = data['items'][0]
            sid = first['solicitud_id']
            print(f"   Primer item: {sid} | Cliente: {first['cliente_nombre']} | Monto: S/ {first['monto']:,.2f}")
            
            # 3. Detalle
            print(f"\n3. GET /api/v1/hitl/solicitudes/{sid}:")
            res_det = await client.get(f"/api/v1/hitl/solicitudes/{sid}")
            assert res_det.status_code == 200
            print(f"✅ Detalle obtenido: Motivo='{res_det.json()['motivo_retencion']}'")

            # 4. Aprobar
            print(f"\n4. POST /api/v1/hitl/solicitudes/{sid}/aprobar:")
            res_appr = await client.post(
                f"/api/v1/hitl/solicitudes/{sid}/aprobar",
                json={"notas": "Aprobación verificada con el supervisor de turno", "supervisor_nombre": "Carlos Mendoza"}
            )
            assert res_appr.status_code == 200
            print(f"✅ Resultado aprobación: {res_appr.json()['message']}")

    print("\n" + "=" * 60)
    print("🎉 TODOS LOS ENDPOINTS HITL FUNCIONAN AL 100%")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_hitl_api())
