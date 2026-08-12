import csv

print("=== VERIFICACIÓN DE DATOS EN 005_TBL_FACTURAS_B2B.csv ===")
csv_path = "/run/media/pandaman/Datos/UNT/PROYECTOS/SON-IA/DATASET/005_TBL_FACTURAS_B2B.csv"
with open(csv_path, 'r', encoding='latin1') as f:
    reader = csv.DictReader(f, delimiter='|')
    for row in reader:
        if 'CLIENT_01001' in row['RAZON_SOCIAL'] or 'CLIENT_01002' in row['RAZON_SOCIAL'] or 'CLIENT_01003' in row['RAZON_SOCIAL']:
            print(f"Cliente: {row['RAZON_SOCIAL']}")
            print(f"  RUC: {row['NUMERO_IDENTIFICACION_FISCAL']}")
            print(f"  Factura: {row['NRO_DOC_FISCAL']}")
            print(f"  Monto: {row['CHARGE_TOTAL_AMOUNT']} {row['MONEDA']}")
            print()

print("=== VERIFICACIÓN DE PLANTAS MÓVILES EN 003_TBL_PLANTA_MOVIL_B2B.csv ===")
csv_path = "/run/media/pandaman/Datos/UNT/PROYECTOS/SON-IA/DATASET/003_TBL_PLANTA_MOVIL_B2B.csv"
count = 0
with open(csv_path, 'r', encoding='latin1') as f:
    reader = csv.DictReader(f, delimiter='|')
    for row in reader:
        if 'CLIENT_01001' in row['RAZON_SOCIAL'] or 'CLIENT_01002' in row['RAZON_SOCIAL'] or 'CLIENT_01003' in row['RAZON_SOCIAL']:
            print(f"Cliente: {row['RAZON_SOCIAL']}")
            print(f"  Producto: {row['PRODUCTO']}")
            print(f"  Plan: {row['PLAN_PRINCIPAL']}")
            print(f"  Estado: {row['ESTADO_LINEA']}")
            print()
            count += 1

print(f"Total de líneas móviles nuevas: {count}")
