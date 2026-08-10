#!/usr/bin/env python3
"""
SON-IA: Script para sembrar datos de prueba
============================================
Genera datos ficticios para desarrollo y testing.
"""

import asyncio
import sys
from pathlib import Path
from datetime import date, timedelta
from decimal import Decimal

# Agregar backend al path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
import structlog

from app.config.settings import get_settings
from app.database.models import (
    BSSCliente,
    BSSCuenta,
    OSSPlanta,
    BSSHistorialPago,
    BSSFacturaCabecera,
    BSSFacturaDetalle,
    BSSOfertaNegociacion,
)
from app.core.calculation_engine import calculation_engine

logger = structlog.get_logger(__name__)
settings = get_settings()


CLIENTES = [
    {
        "id": 1001, "tipo_doc": "6", "num_doc": "20100000001",
        "nombre": "Integratel Tech S.A.C.", "segmento": "B2B",
        "email": "facturacion@integratel-tech.com", "telefono": "+51999888777",
        "score": Decimal("0.92"),
    },
    {
        "id": 1002, "tipo_doc": "6", "num_doc": "20100000002",
        "nombre": "Corporación Financiera del Sur", "segmento": "B2B",
        "email": "pagos@corpfin-sur.com", "telefono": "+51999888778",
        "score": Decimal("0.88"),
    },
    {
        "id": 1003, "tipo_doc": "6", "num_doc": "20100000003",
        "nombre": "Gobierno Regional de Arequipa", "segmento": "Gobierno",
        "email": "tesoreria@regionarequipa.gob.pe", "telefono": "+51999888779",
        "score": Decimal("0.78"),
    },
    {
        "id": 1004, "tipo_doc": "1", "num_doc": "12345678",
        "nombre": "Juan Carlos Pérez López", "segmento": "B2C",
        "email": "juancarlos@gmail.com", "telefono": "+51999888780",
        "score": Decimal("0.75"),
    },
    {
        "id": 1005, "tipo_doc": "1", "num_doc": "87654321",
        "nombre": "María Elena García Romero", "segmento": "B2C",
        "email": "maria.elena@hotmail.com", "telefono": "+51999888781",
        "score": Decimal("0.45"),
    },
    {
        "id": 1006, "tipo_doc": "6", "num_doc": "20100000006",
        "nombre": "Startup Innovadora S.A.C.", "segmento": "B2B",
        "email": "admin@startup-innovadora.com", "telefono": "+51999888782",
        "score": Decimal("0.62"),
    },
]


async def seed_database():
    """Sembrar datos de prueba en la base de datos"""
    
    engine = create_async_engine(
        settings.DATABASE_URL.replace("postgresql+asyncpg://", "sqlite+aiosqlite:///")
        if "postgresql" in settings.DATABASE_URL
        else settings.DATABASE_URL
    )
    
    async with AsyncSession(engine) as session:
        logger.info("🌱 Iniciando seed de datos SON-IA...")
        
        # Crear tablas
        from app.database.models import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # ============================================
        # 1. CLIENTES
        # ============================================
        for c in CLIENTES:
            cliente = BSSCliente(
                id_cliente=c["id"],
                tipo_doc=c["tipo_doc"],
                num_doc=c["num_doc"],
                nombre_razon_social=c["nombre"],
                segmento=c["segmento"],
                email_contacto=c["email"],
                telefono_contacto=c["telefono"],
                score_confianza=c["score"],
            )
            session.add(cliente)
        
        await session.flush()
        logger.info(f"✅ {len(CLIENTES)} clientes creados")
        
        # ============================================
        # 2. CUENTAS
        # ============================================
        cuentas_data = [
            (2001, 1001, 15, "Transferencia", Decimal("50000.00"), 15),
            (2002, 1002, 5, "Débito Automático", Decimal("100000.00"), 30),
            (2003, 1003, 25, "Transferencia", Decimal("200000.00"), 30),
            (2004, 1004, 20, "Tarjeta de Crédito", Decimal("3000.00"), 8),
            (2005, 1005, 10, "Pago Fácil", Decimal("2000.00"), 8),
            (2006, 1006, 15, "Transferencia", Decimal("15000.00"), 15),
        ]
        
        for cuenta_data in cuentas_data:
            cuenta = BSSCuenta(
                id_cuenta=cuenta_data[0],
                id_cliente=cuenta_data[1],
                ciclo_facturacion=cuenta_data[2],
                metodo_pago=cuenta_data[3],
                estado_cuenta="Activo",
                limite_credito=cuenta_data[4],
                dias_plazo_estandar=cuenta_data[5],
            )
            session.add(cuenta)
        
        await session.flush()
        logger.info(f"✅ {len(cuentas_data)} cuentas creadas")
        
        # ============================================
        # 3. SERVICIOS (PLANTA)
        # ============================================
        servicios_data = [
            (3001, 2001, "Fibra Óptica", "FO-LIMA-001", Decimal("2500.00"), date(2023, 1, 15)),
            (3002, 2001, "Cloud", "CLOUD-001", Decimal("1800.00"), date(2023, 3, 1)),
            (3003, 2002, "Fibra Óptica", "FO-LIMA-002", Decimal("5000.00"), date(2022, 6, 10)),
            (3004, 2003, "Fibra Óptica", "FO-ARQ-001", Decimal("8000.00"), date(2021, 1, 1)),
            (3005, 2004, "ADSL", "ADSL-LIMA-001", Decimal("150.00"), date(2024, 1, 20)),
            (3006, 2005, "ADSL", "ADSL-LIMA-002", Decimal("120.00"), date(2024, 6, 15)),
            (3007, 2006, "Fibra Óptica", "FO-LIMA-003", Decimal("1200.00"), date(2024, 3, 1)),
        ]
        
        for s in servicios_data:
            servicio = OSSPlanta(
                id_servicio=s[0],
                id_cuenta=s[1],
                tecnologia=s[2],
                identificador_recurso=s[3],
                cargo_fijo_mensual=s[4],
                fecha_alta=s[5],
                estado_servicio="Activo",
            )
            session.add(servicio)
        
        await session.flush()
        logger.info(f"✅ {len(servicios_data)} servicios creados")
        
        # ============================================
        # 4. FACTURAS DE EJEMPLO
        # ============================================
        factura = BSSFacturaCabecera(
            id_factura=4001,
            id_cuenta=2001,
            serie="F001",
            correlativo=1,
            f_emision=date.today(),
            f_vencimiento=date.today() + timedelta(days=15),
            subtotal_gravado=Decimal("3644.07"),
            igv_total=Decimal("655.93"),
            importe_total=Decimal("4300.00"),
            estado_pago="Pendiente",
            validacion_automatica=True,
        )
        session.add(factura)
        await session.flush()
        
        detalles = [
            BSSFacturaDetalle(
                id_factura=4001, id_servicio=3001,
                concepto="Servicio Fibra Óptica - Octubre 2024",
                periodo_inicio=date.today().replace(day=1),
                periodo_fin=date.today().replace(day=1) + timedelta(days=30),
                monto_linea=Decimal("2500.00"),
            ),
            BSSFacturaDetalle(
                id_factura=4001, id_servicio=3002,
                concepto="Servicio Cloud - Octubre 2024",
                periodo_inicio=date.today().replace(day=1),
                periodo_fin=date.today().replace(day=1) + timedelta(days=30),
                monto_linea=Decimal("1800.00"),
            ),
        ]
        session.add_all(detalles)
        logger.info("✅ Factura de ejemplo creada")
        
        # ============================================
        # 5. OFERTA DE NEGOCIACIÓN
        # ============================================
        oferta = BSSOfertaNegociacion(
            id_factura=4001,
            fecha_oferta=date.today(),
            descuento_ofrecido=Decimal("5.00"),
            nuevo_plazo_dias=5,
            fecha_limite_aceptacion=date.today() + timedelta(days=3),
            estado="pendiente",
        )
        session.add(oferta)
        logger.info("✅ Oferta de negociación creada")
        
        await session.commit()
        logger.info("🎉 Seed de datos completado exitosamente!")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())