import csv
from datetime import datetime
from pathlib import Path

# Datos de los 3 nuevos clientes
new_clients = [
    {
        'COD_CLIENTE': '1000001',
        'NUMERO_IDENTIFICACION_FISCAL': '2099999001',
        'RAZON_SOCIAL': 'CLIENT_01001',
        'NUMERO_CELULAR': '901528082'
    },
    {
        'COD_CLIENTE': '1000002',
        'NUMERO_IDENTIFICACION_FISCAL': '2099999002',
        'RAZON_SOCIAL': 'CLIENT_01002',
        'NUMERO_CELULAR': '904388543'
    },
    {
        'COD_CLIENTE': '1000003',
        'NUMERO_IDENTIFICACION_FISCAL': '2099999003',
        'RAZON_SOCIAL': 'CLIENT_01003',
        'NUMERO_CELULAR': '937239826'
    }
]

# 1. Agregar a 002_TBL_PLANTA_FIJA_B2B.csv
csv_path = Path("/run/media/pandaman/Datos/UNT/PROYECTOS/SON-IA/DATASET/002_TBL_PLANTA_FIJA_B2B.csv")
with open(csv_path, 'r', encoding='latin1') as f:
    reader = csv.DictReader(f, delimiter='|')
    fieldnames = reader.fieldnames
    rows = list(reader)

for client in new_clients:
    new_row = {
        'SEGMENTO_PAIS': 'SEGMENTO_004',
        'NUMERO_IDENTIFICACION_FISCAL': client['NUMERO_IDENTIFICACION_FISCAL'],
        'RAZON_SOCIAL': client['RAZON_SOCIAL'],
        'COD_CLIENTE': client['COD_CLIENTE'],
        'COD_CUENTA': str(int(client['COD_CLIENTE']) + 100000),  # Generar COD_CUENTA único
        'CICLO': '31',
        'FECHAALTA': '2024-01-01 00:00:00',
        'STATUS_DESC': 'Active',
        'LN_PLAN_DESC': 'MOVISTAR VOZ DUO CTRL',
        'LN_SUBSCRIBER_STATUS_DESC': 'Active',
        'INT_PLAN_DESC': 'MOVISTAR INTERNET',
        'INT_ORIGINAL_ACTIVATION_DATE': '2024-01-01 00:00:00',
        'TV_PLAN_DESC': '',
        'TV_ORIGINAL_ACTIVATION_DATE': '',
        'TV_TECNOLOGIA': '',
        'TV_SERVICE_TECHNOLOGY': '',
        'TV_SUBSCRIBER_STATUS_DESC': '',
        'SUB_MAIN_OFFER_DESC': 'Dúo Plano',
        'INT_SUBSCRIBER_STATUS_DESC': 'Active',
        'SUB_MAIN_OFFER_TRIODUO': '0',
        'ES_MOVISTARTOTAL': '',
        'DESCUENTO_PROMOCION_PRODUCTO_DESC': '',
        'DECOS_CANTIDAD': ''
    }
    rows.append(new_row)

with open(csv_path, 'w', newline='', encoding='latin1') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='|')
    writer.writeheader()
    writer.writerows(rows)

print("✓ 002_TBL_PLANTA_FIJA_B2B.csv actualizado (+3 clientes)")

# 2. Agregar a 003_TBL_PLANTA_MOVIL_B2B.csv
csv_path = Path("/run/media/pandaman/Datos/UNT/PROYECTOS/SON-IA/DATASET/003_TBL_PLANTA_MOVIL_B2B.csv")
with open(csv_path, 'r', encoding='latin1') as f:
    reader = csv.DictReader(f, delimiter='|')
    fieldnames = reader.fieldnames
    rows = list(reader)

for i, client in enumerate(new_clients):
    # Agregar 2 líneas móviles por cliente
    for j in range(2):
        new_row = {
            'SEGMENTO_PAIS': 'SEGMENTO_004',
            'NUMERO_IDENTIFICACION_FISCAL': client['NUMERO_IDENTIFICACION_FISCAL'],
            'RAZON_SOCIAL': client['RAZON_SOCIAL'],
            'COD_CLIENTE': client['COD_CLIENTE'],
            'COD_CUENTA': str(int(client['COD_CLIENTE']) + 100000 + j),
            'FLAG_STAFF': 'N',
            'PRODUCTO': 'Movil Abierto' if j == 0 else 'Movil Control',
            'FECHA_ALTA': '2024-01-01' if j == 0 else '2024-02-01',
            'ESTADO_LINEA': 'Activo',
            'ESTADO_TELEFONO_RAZON': 'Pedido de Cliente',
            'TIPO_LINEA': 'M4',
            'PRODUCT_DESC': 'Abierto Elige Todo Emp RD' if j == 0 else 'Control Caribú',
            'PLAN_PRINCIPAL': 'Plan Elige Todo+ S/ 56.90' if j == 0 else 'Plan Ahorro S/ 39.9',
            'CANT_PROMOCIONES': '0',
            'PROM_DSCTO': '',
            'PLAN_ROAMING_DATOS': 'Activación MB Internacionales',
            'Fecha_Inicio_Permanencia': '2024-01-01',
            'Fecha_Fin_Permanencia': '',
            'Meses_Permanencia': ''
        }
        rows.append(new_row)

with open(csv_path, 'w', newline='', encoding='latin1') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='|')
    writer.writeheader()
    writer.writerows(rows)

print("✓ 003_TBL_PLANTA_MOVIL_B2B.csv actualizado (+6 líneas: 2 por cliente)")

# 3. Agregar a 004_TBL_PAGOS_B2B.csv
csv_path = Path("/run/media/pandaman/Datos/UNT/PROYECTOS/SON-IA/DATASET/004_TBL_PAGOS_B2B.csv")
with open(csv_path, 'r', encoding='latin1') as f:
    reader = csv.DictReader(f, delimiter='|')
    fieldnames = reader.fieldnames
    rows = list(reader)

for client in new_clients:
    new_row = {
        'TIPO_DOCUMENTO': 'RUC',
        'NRO_IDENTIFICACION_FISCAL': client['NUMERO_IDENTIFICACION_FISCAL'],
        'RAZON_SOCIAL': client['RAZON_SOCIAL'],
        'COD_CLIENTE': client['COD_CLIENTE'],
        'COD_CUENTA': str(int(client['COD_CLIENTE']) + 100000),
        'SISTEMA': 'AMDOCS',
        'FACTURA_AFECTADA': f"S8AA-{str(int(client['COD_CLIENTE']) + 10000000).zfill(10)}",
        'FECHA_PAGO': '2026-07-15',
        'MONEDA_FACTURA': 'PEN',
        'SUBTOTAL': '100.00',
        'IGV': '18.00',
        'MONTO_PAGADO': '118.00'
    }
    rows.append(new_row)

with open(csv_path, 'w', newline='', encoding='latin1') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='|')
    writer.writeheader()
    writer.writerows(rows)

print("✓ 004_TBL_PAGOS_B2B.csv actualizado (+3 clientes)")

# 4. Agregar a 005_TBL_FACTURAS_B2B.csv
csv_path = Path("/run/media/pandaman/Datos/UNT/PROYECTOS/SON-IA/DATASET/005_TBL_FACTURAS_B2B.csv")
with open(csv_path, 'r', encoding='latin1') as f:
    reader = csv.DictReader(f, delimiter='|')
    fieldnames = reader.fieldnames
    rows = list(reader)

for client in new_clients:
    new_row = {
        'NUMERO_IDENTIFICACION_FISCAL': client['NUMERO_IDENTIFICACION_FISCAL'],
        'RAZON_SOCIAL': client['RAZON_SOCIAL'],
        'COD_CLIENTE': client['COD_CLIENTE'],
        'COD_CUENTA': str(int(client['COD_CLIENTE']) + 100000),
        'NRO_DOC_FISCAL': f"S8AA-{str(int(client['COD_CLIENTE']) + 10000000).zfill(10)}",
        'FUENTE': 'FACTURACION CICLICA',
        'SISTEMA': 'AMDOCS',
        'FECHA_EMISION': '20260627',
        'FECHA_VTO': '2026-07-13',
        'MONEDA': 'PEN',
        'CHARGE_NET_AMOUNT': '100.00',
        'CHARGE_IGV_INVOICE': '18.00',
        'CHARGE_TOTAL_AMOUNT': '118.00'
    }
    rows.append(new_row)

with open(csv_path, 'w', newline='', encoding='latin1') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='|')
    writer.writeheader()
    writer.writerows(rows)

print("✓ 005_TBL_FACTURAS_B2B.csv actualizado (+3 clientes)")

# 5. Agregar a 006_TBL_NOTAS_CREDITO_B2B.csv
csv_path = Path("/run/media/pandaman/Datos/UNT/PROYECTOS/SON-IA/DATASET/006_TBL_NOTAS_CREDITO_B2B.csv")
with open(csv_path, 'r', encoding='latin1') as f:
    reader = csv.DictReader(f, delimiter='|')
    fieldnames = reader.fieldnames
    rows = list(reader)

for client in new_clients:
    new_row = {
        'NUMERO_IDENTIFICACION_FISCAL': client['NUMERO_IDENTIFICACION_FISCAL'],
        'RAZON_SOCIAL': client['RAZON_SOCIAL'],
        'COD_CLIENTE': client['COD_CLIENTE'],
        'COD_CUENTA': str(int(client['COD_CLIENTE']) + 100000),
        'NRO_DOC_FISCAL': f"SJFE-{str(int(client['COD_CLIENTE']) + 31000000).zfill(10)}",
        'FUENTE': 'NOTA DE CREDITO',
        'SISTEMA': 'AMDOCS',
        'FACTURA_AFECTADA': f"S8AA-{str(int(client['COD_CLIENTE']) + 10000000).zfill(10)}",
        'FECHAEMISION': '20260728',
        'MONEDA': 'PEN',
        'MONTO_SIN_IGV': '5.00',
        'SUBTOTAL': '.90',
        'MONTO': '5.90'
    }
    rows.append(new_row)

with open(csv_path, 'w', newline='', encoding='latin1') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='|')
    writer.writeheader()
    writer.writerows(rows)

print("✓ 006_TBL_NOTAS_CREDITO_B2B.csv actualizado (+3 clientes)")

print("\n" + "="*60)
print("✓ TODOS LOS DATASETS ACTUALIZADOS CON LOS 3 NUEVOS CLIENTES")
print("="*60)
print("\nClientes agregados:")
print("  1. CLIENT_01001 (RUC: 2099999001) - Celular: 901528082 - Movistar")
print("  2. CLIENT_01002 (RUC: 2099999002) - Celular: 904388543 - Claro")
print("  3. CLIENT_01003 (RUC: 2099999003) - Celular: 937239826 - Bitel")
print("\nAhora tienes datos de prueba para tu agente IA con OpenWA!")
