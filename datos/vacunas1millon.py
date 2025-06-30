from faker import Faker
import psycopg2
from psycopg2.extras import execute_batch, execute_values
import random

fake = Faker("es_ES")

DB_CONFIG = {
    "dbname": "bd",
    "user": "postgres",
    "password": "postgres",
    "host": "127.0.0.1",
    "port": "5433"
}

TOTAL_ADMIN = 50_000
TOTAL_PROVEEDORES = 100_000
TOTAL_INSUMOS = 200_000
TOTAL_VACUNAS = 300_000
CHUNK = 5000

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# === Obtener DNIs ya usados ===
cur.execute("SELECT dni FROM persona")
dnis_usados = set(row[0] for row in cur.fetchall())

dnis_nuevos = set()
while len(dnis_nuevos) < TOTAL_ADMIN * 2:
    dnis_nuevos.add(str(fake.random_number(digits=8, fix_len=True)))
dnis_nuevos = list(dnis_nuevos - dnis_usados)[:TOTAL_ADMIN]

# === Insertar personas y empleados ===
print("Insertando personas y empleados...")
for i in range(0, TOTAL_ADMIN, CHUNK):
    dnis_chunk = dnis_nuevos[i:i+CHUNK]
    personas_data = []
    empleados_data = []
    admin_data = []

    for j, dni in enumerate(dnis_chunk):
        nombre = fake.name()
        direccion = fake.address().replace('\n', ', ')
        telefono = fake.msisdn()[3:12]
        personas_data.append((dni, nombre, direccion, telefono))

        fecha_ingreso = fake.date_between(start_date='-5y', end_date='-1d')
        empleados_data.append((dni, fecha_ingreso, "08:00", "17:00", round(random.uniform(2000, 4000), 2)))
        admin_data.append((dni, f"Rango {j%5}"))

    execute_batch(cur, "INSERT INTO persona VALUES (%s, %s, %s, %s)", personas_data)
    execute_batch(cur, "INSERT INTO empleado VALUES (%s, %s, %s, %s, %s)", empleados_data)
    execute_batch(cur, "INSERT INTO administrador VALUES (%s, %s)", admin_data)
    conn.commit()
    print(f"{i+CHUNK}/{TOTAL_ADMIN} administradores insertados")

# === Insertar proveedores + contacta ===
print("Insertando proveedores...")
proveedores_data = []
contacta_data = []
for i in range(TOTAL_PROVEEDORES):
    ruc = fake.unique.numerify("20#########")
    nombre = f"Proveedor {fake.word().capitalize()}"
    admin = random.choice(dnis_nuevos)
    proveedores_data.append((ruc, nombre, admin))
    contacta_data.append((admin, ruc))

for i in range(0, TOTAL_PROVEEDORES, CHUNK):
    execute_batch(cur, "INSERT INTO proveedor (ruc, nombre, administrador) VALUES (%s, %s, %s)", proveedores_data[i:i+CHUNK])
    execute_batch(cur, "INSERT INTO contacta (dni_persona, ruc_proveedor) VALUES (%s, %s)", contacta_data[i:i+CHUNK])
    conn.commit()
    print(f"{i+CHUNK}/{TOTAL_PROVEEDORES} proveedores insertados")

# === Obtener recepcionistas existentes ===
cur.execute("SELECT dni_persona FROM recepcionista")
recepcionistas = [row[0] for row in cur.fetchall()]
cur.execute("SELECT ruc FROM proveedor")
rucs = [row[0] for row in cur.fetchall()]

# === Insertar insumos + gestiona + provee ===
print("Insertando insumos...")
insumo_ids = []
gestiona = []
provee = []

for i in range(0, TOTAL_INSUMOS, CHUNK):
    insumos = []
    for _ in range(CHUNK):
        dni = random.choice(recepcionistas)
        nombre = f"Insumo {fake.word().capitalize()}"
        ruc = random.choice(rucs)
        stock = random.randint(10, 200)
        precio = round(random.uniform(5, 100), 2)
        insumos.append((dni, nombre, ruc, stock, precio))

    # Insertar insumos y capturar IDs
    insert_query = "INSERT INTO insumo (dni_persona, nombre, ruc_proveedor, stock, precio) VALUES %s RETURNING id"
    ids = execute_values(cur, insert_query, insumos, fetch=True)
    insumo_ids.extend([row[0] for row in ids])

    gestiona.extend([(ins[0], ins_id) for ins, ins_id in zip(insumos, [row[0] for row in ids])])
    provee.extend([(ins[2], ins_id) for ins, ins_id in zip(insumos, [row[0] for row in ids])])

    conn.commit()
    print(f"{i+CHUNK}/{TOTAL_INSUMOS} insumos insertados")

print("Insertando gestiona y provee...")
for i in range(0, len(gestiona), CHUNK):
    execute_batch(cur, "INSERT INTO gestiona VALUES (%s, %s)", gestiona[i:i+CHUNK])
    execute_batch(cur, "INSERT INTO provee VALUES (%s, %s)", provee[i:i+CHUNK])
    conn.commit()

# === Insertar vacunas (300k primeras insumos) ===
print("Insertando vacunas...")
vacunas_data = []
for ins_id in insumo_ids[:TOTAL_VACUNAS]:
    fecha_venc = fake.date_between(start_date='+1M', end_date='+2y')
    vacunas_data.append((ins_id, fecha_venc))

for i in range(0, len(vacunas_data), CHUNK):
    execute_batch(cur, "INSERT INTO vacuna (id_insumo, fecha_venc) VALUES (%s, %s)", vacunas_data[i:i+CHUNK])
    conn.commit()
    print(f"{i+CHUNK}/{TOTAL_VACUNAS} vacunas insertadas")

# === Asociar vacunas a tratamientos tipo 'Vacunación' ===
print("Asociando con tratamientos tipo 'Vacunación'...")
cur.execute("SELECT id FROM tratamiento WHERE LOWER(nombre) = 'vacunación'")
tratamientos_vac = [row[0] for row in cur.fetchall()]
random.shuffle(tratamientos_vac)

asociaciones = list(zip(tratamientos_vac[:TOTAL_VACUNAS], insumo_ids[:TOTAL_VACUNAS]))

for i in range(0, len(asociaciones), CHUNK):
    execute_batch(cur, "INSERT INTO vacunacion VALUES (%s, %s)", asociaciones[i:i+CHUNK])
    conn.commit()

print(f"{len(asociaciones)} tratamientos asociados a vacunas")
cur.close()
conn.close()
