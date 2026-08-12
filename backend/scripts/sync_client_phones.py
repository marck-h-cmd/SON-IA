"""
Sincroniza los NUMERO_CELULAR del CSV de clientes hacia la tabla bss_clientes.

Agrega la columna numero_celular si no existe y la pobla leyendo
001_TBL_CLIENTES_B2B.csv (delimitador |, codificación latin1).

Uso (dentro del contenedor backend):
    python scripts/sync_client_phones.py
"""

import asyncio
import os
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.database.connection import AsyncSessionLocal  # noqa: E402

DATASET_DIR = backend_dir.parent / "DATASET"
CLIENTS_CSV = DATASET_DIR / "001_TBL_CLIENTES_B2B.csv"


async def migrate_and_sync() -> None:
    async with AsyncSessionLocal() as session:
        # 1. Agregar la columna si no existe
        await session.execute(
            text("ALTER TABLE bss_clientes ADD COLUMN IF NOT EXISTS numero_celular VARCHAR(20)")
        )

        # 2. Leer teléfonos del CSV (RUC -> celular)
        df = pd.read_csv(CLIENTS_CSV, sep="|", encoding="latin1")
        phone_by_ruc = {
            str(row["NUMERO_IDENTIFICACION_FISCAL"]).strip(): str(row["NUMERO_CELULAR"]).strip()
            for _, row in df.iterrows()
            if pd.notna(row.get("NUMERO_CELULAR")) and str(row["NUMERO_CELULAR"]).strip()
        }

        # 3. Actualizar la BD
        updated = 0
        for ruc, phone in phone_by_ruc.items():
            result = await session.execute(
                text(
                    "UPDATE bss_clientes SET numero_celular = :phone "
                    "WHERE numero_identificacion_fiscal = :ruc"
                ),
                {"phone": phone, "ruc": ruc},
            )
            updated += result.rowcount or 0

        await session.commit()
        print(f"✓ Columna agregada y {updated} clientes actualizados con teléfono")
        print(f"  Total de teléfonos en CSV: {len(phone_by_ruc)}")

        # Mostrar los 3 clientes de prueba
        rows = await session.execute(
            text(
                "SELECT numero_identificacion_fiscal, razon_social, numero_celular "
                "FROM bss_clientes WHERE numero_celular IN "
                "('901528082','904388543','937239826')"
            )
        )
        for r in rows:
            print(f"  TEST: {r.razon_social} {r.numero_identificacion_fiscal} -> {r.numero_celular}")


if __name__ == "__main__":
    asyncio.run(migrate_and_sync())