import csv
import random
from pathlib import Path

# Leer el archivo de clientes
DATASET_DIR = Path(__file__).resolve().parent / "DATASET"
csv_path = DATASET_DIR / "001_TBL_CLIENTES_B2B.csv"

# Prefijos de números de celular peruanos realistas
movistar_prefixes = ['901', '910', '914', '915', '916', '961']
claro_prefixes = ['902', '917', '920', '925', '928', '929', '944', '946', '947']
bitel_prefixes = ['930', '931', '936', '937']
vivo_prefixes = ['940', '941', '942', '945']

all_prefixes = movistar_prefixes + claro_prefixes + bitel_prefixes + vivo_prefixes

def generate_phone_number():
    """Genera un número de celular peruano realista"""
    prefix = random.choice(all_prefixes)
    remaining_digits = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    return prefix + remaining_digits

# Leer clientes existentes
with open(csv_path, 'r', encoding='latin1') as f:
    reader = csv.DictReader(f, delimiter='|')
    fieldnames = reader.fieldnames
    rows = list(reader)

# Agregar columna NUMERO_CELULAR
fieldnames_new = fieldnames + ['NUMERO_CELULAR']

# Generar números para clientes existentes
for row in rows:
    row['NUMERO_CELULAR'] = generate_phone_number()

# Encontrar el máximo COD_CLIENTE para crear los nuevos
cliente_nums = [int(row['RAZON_SOCIAL'].replace('CLIENT_', '')) for row in rows]
max_cliente_num = max(cliente_nums)

# Crear 3 nuevos clientes con números específicos
new_phones = ['901528082', '904388543', '937239826']
new_rucs = ['2099999001', '2099999002', '2099999003']  # RUCs ficticios pero válidos

for i, (phone, ruc) in enumerate(zip(new_phones, new_rucs)):
    new_client_num = max_cliente_num + 1 + i
    new_row = {
        'SEGMENTO_PAIS': 'SEGMENTO_004',
        'TIPO_DOCUMENTO': 'RUC',
        'NUMERO_IDENTIFICACION_FISCAL': ruc,
        'RAZON_SOCIAL': f'CLIENT_{str(new_client_num).zfill(5)}',
        'SUNAT_ESTADO_RUC': 'HABIDO',
        'SUNAT_ESTADO_CONTRIBUYENTE': 'ACTIVO',
        'SUNAT_DEPARTAMENTO': 'LIMA',
        'SUNAT_PROVINCIA': 'Lima',
        'SUNAT_DISTRITO': 'San Isidro',
        'NUMERO_CELULAR': phone
    }
    rows.append(new_row)

# Guardar archivo actualizado
with open(csv_path, 'w', newline='', encoding='latin1') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames_new, delimiter='|')
    writer.writeheader()
    writer.writerows(rows)

print(f"✓ Archivo actualizado: {len(rows)} clientes (1000 originales + 3 nuevos)")
print(f"\nClientes nuevos agregados:")
print(f"  - CLIENT_01001: RUC 2099999001, Celular: 901528082")
print(f"  - CLIENT_01002: RUC 2099999002, Celular: 904388543")
print(f"  - CLIENT_01003: RUC 2099999003, Celular: 937239826")
print(f"\nNumeros aleatorios generados para los demás clientes (operadores: Movistar, Claro, Bitel, Vivo)")
