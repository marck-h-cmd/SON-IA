import asyncio
import os
import sys
from pathlib import Path
from decimal import Decimal
from datetime import datetime

import pandas as pd
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from app.database.models import Base, BSSCliente, OSSPlantaFija, OSSPlantaMovil, BSSFactura, BSSPago, BSSNotaCredito

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@db:5432/son_ia_db")
DATASET_DIR = backend_dir.parent / "DATASET"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

def parse_date(date_str):
    if pd.isna(date_str) or not date_str:
        return None
    try:
        if len(str(date_str)) == 8 and str(date_str).isdigit():
            # YYYYMMDD
            return datetime.strptime(str(date_str), "%Y%m%d").date()
        return pd.to_datetime(date_str, dayfirst=True).date()
    except:
        return None

def clean_val(val):
    if pd.isna(val):
        return None
    return str(val)

def clean_decimal(val):
    if pd.isna(val):
        return None
    try:
        return Decimal(str(val))
    except:
        return None

async def seed_data():
    async with engine.begin() as conn:
        # Reset the development database schema. CASCADE removes foreign-key
        # dependencies before recreating all tables from SQLAlchemy metadata.
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
        await conn.run_sync(Base.metadata.create_all)

    print("Tables recreated successfully.")
    
    async with AsyncSessionLocal() as session:
        inserted_rucs = set()
        
        def ensure_cliente(ruc):
            if ruc and ruc not in inserted_rucs:
                cliente = BSSCliente(
                    numero_identificacion_fiscal=ruc,
                    razon_social="Unknown Client (Auto-Generated)",
                    tipo_documento="RUC",
                )
                session.add(cliente)
                inserted_rucs.add(ruc)

        # 1. CLIENTES
        print("Loading Clientes...")
        df_clientes = pd.read_csv(DATASET_DIR / "001_TBL_CLIENTES_B2B.csv", sep="|", encoding="latin1")
        for _, row in df_clientes.iterrows():
            ruc = str(row["NUMERO_IDENTIFICACION_FISCAL"])
            if ruc not in inserted_rucs:
                cliente = BSSCliente(
                    numero_identificacion_fiscal=ruc,
                    tipo_documento=clean_val(row.get("TIPO_DOCUMENTO")),
                    razon_social=clean_val(row.get("RAZON_SOCIAL")),
                    segmento_pais=clean_val(row.get("SEGMENTO_PAIS")),
                    sunat_estado_ruc=clean_val(row.get("SUNAT_ESTADO_RUC")),
                    sunat_estado_contribuyente=clean_val(row.get("SUNAT_ESTADO_CONTRIBUYENTE")),
                    sunat_departamento=clean_val(row.get("SUNAT_DEPARTAMENTO")),
                    sunat_provincia=clean_val(row.get("SUNAT_PROVINCIA")),
                    sunat_distrito=clean_val(row.get("SUNAT_DISTRITO")),
                    numero_celular=clean_val(row.get("NUMERO_CELULAR")),
                )
                session.add(cliente)
                inserted_rucs.add(ruc)
        await session.commit()

        # 2. PLANTA FIJA
        print("Loading Planta Fija...")
        df_pf = pd.read_csv(DATASET_DIR / "002_TBL_PLANTA_FIJA_B2B.csv", sep="|", encoding="latin1")
        for _, row in df_pf.iterrows():
            ruc = str(row["NUMERO_IDENTIFICACION_FISCAL"])
            ensure_cliente(ruc)
            pf = OSSPlantaFija(
                numero_identificacion_fiscal=ruc,
                cod_cliente=clean_val(row.get("COD_CLIENTE")),
                cod_cuenta=clean_val(row.get("COD_CUENTA")),
                ciclo=clean_val(row.get("CICLO")),
                fecha_alta=parse_date(row.get("FECHAALTA")),
                status_desc=clean_val(row.get("STATUS_DESC")),
                ln_plan_desc=clean_val(row.get("LN_PLAN_DESC")),
                ln_subscriber_status_desc=clean_val(row.get("LN_SUBSCRIBER_STATUS_DESC")),
                int_plan_desc=clean_val(row.get("INT_PLAN_DESC")),
                int_original_activation_date=parse_date(row.get("INT_ORIGINAL_ACTIVATION_DATE")),
                tv_plan_desc=clean_val(row.get("TV_PLAN_DESC")),
                tv_original_activation_date=parse_date(row.get("TV_ORIGINAL_ACTIVATION_DATE")),
                tv_tecnologia=clean_val(row.get("TV_TECNOLOGIA")),
                tv_service_technology=clean_val(row.get("TV_SERVICE_TECHNOLOGY")),
                tv_subscriber_status_desc=clean_val(row.get("TV_SUBSCRIBER_STATUS_DESC")),
                sub_main_offer_desc=clean_val(row.get("SUB_MAIN_OFFER_DESC")),
                int_subscriber_status_desc=clean_val(row.get("INT_SUBSCRIBER_STATUS_DESC")),
                sub_main_offer_trioduo=clean_val(row.get("SUB_MAIN_OFFER_TRIODUO")),
                es_movistartotal=clean_val(row.get("ES_MOVISTARTOTAL")),
                descuento_promocion_producto_desc=clean_val(row.get("DESCUENTO_PROMOCION_PRODUCTO_DESC")),
                decos_cantidad=clean_val(row.get("DECOS_CANTIDAD")),
            )
            session.add(pf)
        await session.commit()

        # 3. PLANTA MOVIL
        print("Loading Planta Movil...")
        df_pm = pd.read_csv(DATASET_DIR / "003_TBL_PLANTA_MOVIL_B2B.csv", sep="|", encoding="latin1")
        for _, row in df_pm.iterrows():
            ruc = str(row["NUMERO_IDENTIFICACION_FISCAL"])
            ensure_cliente(ruc)
            pm = OSSPlantaMovil(
                numero_identificacion_fiscal=ruc,
                cod_cliente=clean_val(row.get("COD_CLIENTE")),
                cod_cuenta=clean_val(row.get("COD_CUENTA")),
                flag_staff=clean_val(row.get("FLAG_STAFF")),
                producto=clean_val(row.get("PRODUCTO")),
                fecha_alta=parse_date(row.get("FECHA_ALTA")),
                estado_linea=clean_val(row.get("ESTADO_LINEA")),
                estado_telefono_razon=clean_val(row.get("ESTADO_TELEFONO_RAZON")),
                tipo_linea=clean_val(row.get("TIPO_LINEA")),
                product_desc=clean_val(row.get("PRODUCT_DESC")),
                plan_principal=clean_val(row.get("PLAN_PRINCIPAL")),
                cant_promociones=clean_val(row.get("CANT_PROMOCIONES")),
                prom_dscto=clean_val(row.get("PROM_DSCTO")),
                plan_roaming_datos=clean_val(row.get("PLAN_ROAMING_DATOS")),
                fecha_inicio_permanencia=parse_date(row.get("Fecha_Inicio_Permanencia")),
                fecha_fin_permanencia=parse_date(row.get("Fecha_Fin_Permanencia")),
                meses_permanencia=clean_val(row.get("Meses_Permanencia")),
            )
            session.add(pm)
        await session.commit()

        # 4. FACTURAS
        print("Loading Facturas...")
        df_fac = pd.read_csv(DATASET_DIR / "005_TBL_FACTURAS_B2B.csv", sep="|", encoding="latin1")
        for _, row in df_fac.iterrows():
            ruc = str(row["NUMERO_IDENTIFICACION_FISCAL"])
            ensure_cliente(ruc)
            fac = BSSFactura(
                nro_doc_fiscal=str(row["NRO_DOC_FISCAL"]),
                numero_identificacion_fiscal=ruc,
                cod_cliente=clean_val(row.get("COD_CLIENTE")),
                cod_cuenta=clean_val(row.get("COD_CUENTA")),
                fuente=clean_val(row.get("FUENTE")),
                sistema=clean_val(row.get("SISTEMA")),
                fecha_emision=parse_date(row.get("FECHA_EMISION")),
                fecha_vto=parse_date(row.get("FECHA_VTO")),
                moneda=clean_val(row.get("MONEDA")),
                charge_net_amount=clean_decimal(row.get("CHARGE_NET_AMOUNT")),
                charge_igv_invoice=clean_decimal(row.get("CHARGE_IGV_INVOICE")),
                charge_total_amount=clean_decimal(row.get("CHARGE_TOTAL_AMOUNT")),
            )
            session.add(fac)
        await session.commit()

        # 5. PAGOS
        print("Loading Pagos...")
        df_pagos = pd.read_csv(DATASET_DIR / "004_TBL_PAGOS_B2B.csv", sep="|", encoding="latin1")
        for _, row in df_pagos.iterrows():
            ruc = str(row["NRO_IDENTIFICACION_FISCAL"])
            ensure_cliente(ruc)
            pago = BSSPago(
                factura_afectada=str(row["FACTURA_AFECTADA"]),
                numero_identificacion_fiscal=ruc,
                tipo_documento=clean_val(row.get("TIPO_DOCUMENTO")),
                cod_cliente=clean_val(row.get("COD_CLIENTE")),
                cod_cuenta=clean_val(row.get("COD_CUENTA")),
                sistema=clean_val(row.get("SISTEMA")),
                fecha_pago=parse_date(row.get("FECHA_PAGO")),
                moneda_factura=clean_val(row.get("MONEDA_FACTURA")),
                subtotal=clean_decimal(row.get("SUBTOTAL")),
                igv=clean_decimal(row.get("IGV")),
                monto_pagado=clean_decimal(row.get("MONTO_PAGADO")),
            )
            session.add(pago)
        await session.commit()

        # 6. NOTAS DE CREDITO
        print("Loading Notas de Credito...")
        df_nc = pd.read_csv(DATASET_DIR / "006_TBL_NOTAS_CREDITO_B2B.csv", sep="|", encoding="latin1")
        for _, row in df_nc.iterrows():
            ruc = str(row["NUMERO_IDENTIFICACION_FISCAL"])
            ensure_cliente(ruc)
            nc = BSSNotaCredito(
                nro_doc_fiscal=str(row["NRO_DOC_FISCAL"]),
                numero_identificacion_fiscal=ruc,
                factura_afectada=str(row["FACTURA_AFECTADA"]),
                cod_cliente=clean_val(row.get("COD_CLIENTE")),
                cod_cuenta=clean_val(row.get("COD_CUENTA")),
                fuente=clean_val(row.get("FUENTE")),
                sistema=clean_val(row.get("SISTEMA")),
                fecha_emision=parse_date(row.get("FECHAEMISION")),
                moneda=clean_val(row.get("MONEDA")),
                monto_sin_igv=clean_decimal(row.get("MONTO_SIN_IGV")),
                subtotal=clean_decimal(row.get("SUBTOTAL")),
                monto=clean_decimal(row.get("MONTO")),
            )
            session.add(nc)
        await session.commit()

        print("Database seed completed!")

if __name__ == "__main__":
    asyncio.run(seed_data())
    