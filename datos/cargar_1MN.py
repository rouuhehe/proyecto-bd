from faker import Faker
import psycopg2
from psycopg2.extras import execute_batch
import random
from datetime import time
from psycopg2.extras import execute_batch, execute_values

fake = Faker('es_ES')

DB_CONFIG = {
    "dbname": "bd",
    "user": "postgres",
    "password": "postgres",
    "host": "127.0.0.1",
    "port": "5433"
}

TOTAL_VETERINARIOS = 100000
TOTAL_RECEPCIONISTAS = 50000
TOTAL_PROPIETARIOS = 850000
TOTAL_MASCOTAS = 1000000
TOTAL_CITAS = 1000000
TOTAL = 1000000
CHUNK_SIZE = 5000
TRATAMIENTOS = ["Vacunación", "Cirugía menor", "Antibióticos", "Desparasitación", "Limpieza dental"]


conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()


def generar_personas_empleados():
    all_dnis = set()
    while len(all_dnis) < (TOTAL_VETERINARIOS + TOTAL_RECEPCIONISTAS + TOTAL_PROPIETARIOS):
        all_dnis.add(str(fake.unique.random_number(digits=8, fix_len=True)))
    all_dnis = list(all_dnis)

    roles = (
        ['veterinario'] * TOTAL_VETERINARIOS +
        ['recepcionista'] * TOTAL_RECEPCIONISTAS +
        ['propietario'] * TOTAL_PROPIETARIOS
    )

    for i in range(0, len(all_dnis), CHUNK_SIZE):
        personas_data = []
        empleados_data = []
        veterinarios_data = []
        recepcionistas_data = []
        propietarios_data = []

        chunk_dnis = all_dnis[i:i + CHUNK_SIZE]
        chunk_roles = roles[i:i + CHUNK_SIZE]

        for dni, rol in zip(chunk_dnis, chunk_roles):
            nombre = fake.name()
            direccion = fake.address().replace("\n", ", ")
            telefono = fake.msisdn()[3:12]
            personas_data.append((dni, nombre, direccion, telefono))

            if rol in ['veterinario', 'recepcionista']:
                fecha_ingreso = fake.date_between(start_date='-5y', end_date='-1y')
                empleados_data.append((dni, fecha_ingreso, '08:00', '17:00', round(random.uniform(2500, 5000), 2)))

            if rol == 'veterinario':
                colegiatura = fake.unique.bothify(text='VET-######')
                especializacion = random.choice(['Dermatología', 'Cirugía', 'Oncología', 'Cardiología', 'Medicina General'])
                veterinarios_data.append((dni, colegiatura, especializacion))

            elif rol == 'recepcionista':
                fijo = fake.random_number(digits=5, fix_len=True)
                recepcionistas_data.append((dni, fijo))

            elif rol == 'propietario':
                propietarios_data.append((dni,))

        execute_batch(cur, "INSERT INTO persona (dni, nombre_completo, direccion, telefono) VALUES (%s, %s, %s, %s)", personas_data)
        execute_batch(cur, "INSERT INTO empleado (dni_persona, fecha_ingreso, inicio_turno, fin_turno, salario) VALUES (%s, %s, %s, %s, %s)", empleados_data)
        execute_batch(cur, "INSERT INTO veterinario (dni_persona, num_colegiatura, especializacion) VALUES (%s, %s, %s)", veterinarios_data)
        execute_batch(cur, "INSERT INTO recepcionista (dni_persona, telefono_fijo) VALUES (%s, %s)", recepcionistas_data)
        execute_batch(cur, "INSERT INTO propietario (dni_persona) VALUES (%s)", propietarios_data)

        conn.commit()
        print(f"Insertados: {i + CHUNK_SIZE} / {len(all_dnis)} personas")

generar_personas_empleados()

cur.execute("SELECT dni_persona FROM propietario LIMIT %s", (TOTAL_MASCOTAS,))
propietarios = [row[0] for row in cur.fetchall()]

print("Insertando mascotas y relaciones...")
for i in range(0, TOTAL_MASCOTAS, CHUNK_SIZE):
    chunk_propietarios = propietarios[i:i + CHUNK_SIZE]
    mascotas_data = []

    for _ in chunk_propietarios:
        nombre = fake.first_name()
        especie = random.choices(['Perro', 'Gato', 'Conejo'], weights=[0.6, 0.3, 0.1])[0]
        raza = fake.word()
        sexo = random.choice(['M', 'F'])
        fecha_nac = fake.date_between(start_date='-10y', end_date='-3m')
        mascotas_data.append((nombre, especie, raza, sexo, fecha_nac))

    # Use execute_values to insert and RETURN ids
    insert_query = """
        INSERT INTO mascota (nombre, especie, raza, sexo, fecha_nac)
        VALUES %s RETURNING id
    """
    ids_mascotas = execute_values(cur, insert_query, mascotas_data, fetch=True)
    ids_mascotas = [row[0] for row in ids_mascotas]
    relaciones_data = list(zip(chunk_propietarios, ids_mascotas))

    execute_batch(cur, """
        INSERT INTO propietariotienemascota (dni_propietario, id_mascota)
        VALUES (%s, %s)
    """, relaciones_data)

    conn.commit()
    print(f"Insertados: {i + CHUNK_SIZE} / {TOTAL_MASCOTAS}")


cur.execute("SELECT dni_persona FROM veterinario")
veterinarios = [row[0] for row in cur.fetchall()]

cur.execute("SELECT dni_persona FROM recepcionista")
recepcionistas = [row[0] for row in cur.fetchall()]

cur.execute("SELECT id FROM mascota LIMIT %s", (TOTAL_CITAS,))
mascotas = [row[0] for row in cur.fetchall()]

print("Insertando citas...")
for i in range(0, TOTAL_CITAS, CHUNK_SIZE):
    citas_data = []
    chunk_mascotas = mascotas[i:i + CHUNK_SIZE]

    for id_mascota in chunk_mascotas:
        dni_vet = random.choice(veterinarios)
        hora = time(hour=random.randint(8, 17), minute=random.choice([0, 15, 30, 45]))
        fecha = fake.date_between(start_date='-6M', end_date='today')
        recep = random.choice(recepcionistas)
        estado = random.choices(['Realizada', 'Cancelada', 'Pendiente'], weights=[0.7, 0.1, 0.2])[0]
        precio = round(random.uniform(30, 300), 2)
        motivo = fake.sentence(nb_words=5)
        citas_data.append((dni_vet, hora, fecha, id_mascota, recep, estado, precio, motivo))

    execute_batch(cur, """
        INSERT INTO cita (dni_veterinario, hora, fecha, id_mascota, dni_recepcionista, estado, precio, motivo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, citas_data)

    conn.commit()
    print(f"Insertadas: {i + CHUNK_SIZE} / {TOTAL_CITAS}")

cur.execute("SELECT id FROM mascota LIMIT %s", (TOTAL,))
mascotas = [row[0] for row in cur.fetchall()]

cur.execute("SELECT id FROM tratamiento LIMIT %s", (TOTAL,))
tratamientos = [row[0] for row in cur.fetchall()]

cur.execute("SELECT id FROM cita LIMIT %s", (TOTAL,))
citas = [row[0] for row in cur.fetchall()]

# Obtener lista de clientes (propietarios) para boletas
cur.execute("SELECT dni_persona FROM propietario LIMIT %s", (TOTAL,))
clientes = [row[0] for row in cur.fetchall()]

# Obtener insumos y preparar vacunas
cur.execute("SELECT id FROM insumo ORDER BY id ASC LIMIT %s", (TOTAL,))  # Asumimos que ya hay insumos
insumos = [row[0] for row in cur.fetchall()]
insumo_index = 0

# Seleccionamos 1000 insumos para que sean vacunas
VACUNAS_ASIGNADAS = 1000
vacuna_insumos = insumos[:VACUNAS_ASIGNADAS]

# Insertar en tabla vacuna
vacuna_data = [(id_insumo, fake.date_between(start_date='today', end_date='+1y')) for id_insumo in vacuna_insumos]
execute_batch(cur, """
    INSERT INTO vacuna (id_insumo, fecha_venc)
    VALUES (%s, %s)
""", vacuna_data)
conn.commit()
print("Vacunas insertadas")

print("Insertando boletas y tratamientos + especializados...")
for i in range(0, TOTAL, CHUNK_SIZE):
    boletas_chunk = []
    tratamientos_chunk = []
    cirugias_chunk = []
    recetas_chunk = []
    terapias_chunk = []
    vacunaciones_chunk = []

    for _ in range(CHUNK_SIZE):
        fecha = fake.date_between(start_date='-6M', end_date='today')
        cliente = random.choice(clientes)
        recep = random.choice(recepcionistas)
        monto = round(random.uniform(30, 300), 2)
        boletas_chunk.append((fecha, cliente, recep, monto))

    execute_batch(cur, """
        INSERT INTO boleta (fecha, dni_persona_cliente, dni_persona_recepcionista, monto)
        VALUES (%s, %s, %s, %s)
    """, boletas_chunk)

    cur.execute("SELECT id FROM boleta ORDER BY id DESC LIMIT %s", (CHUNK_SIZE,))
    boleta_ids = [row[0] for row in cur.fetchall()][::-1]

    for id_boleta in boleta_ids:
        tipo = random.choice(TRATAMIENTOS)
        tratamientos_chunk.append((tipo, id_boleta))

    execute_batch(cur, """
        INSERT INTO tratamiento (nombre, id_boleta)
        VALUES (%s, %s)
    """, tratamientos_chunk)

    cur.execute("SELECT id FROM tratamiento ORDER BY id DESC LIMIT %s", (CHUNK_SIZE,))
    tratamiento_ids = [row[0] for row in cur.fetchall()][::-1]

    for id_tratamiento, (tipo, _) in zip(tratamiento_ids, tratamientos_chunk):
        if tipo == "Vacunación":
            if insumo_index >= len(vacuna_insumos):
                continue  # No más vacunas disponibles
            id_insumo = vacuna_insumos[insumo_index]
            vacunaciones_chunk.append((id_tratamiento, id_insumo))
            insumo_index += 1
        elif tipo == "Cirugía menor":
            duracion = round(random.uniform(0.5, 5.0), 2)
            cirugias_chunk.append((id_tratamiento, duracion))
        elif tipo == "Antibióticos":
            frecuencia = random.choice(["Cada 8h", "Cada 12h", "Diaria"])
            recetas_chunk.append((id_tratamiento, frecuencia))
        elif tipo == "Desparasitación":
            fecha_ini = fake.date_between(start_date='-3M', end_date='-1M')
            fecha_fin = fake.date_between(start_date='-1M', end_date='today')
            terapias_chunk.append((id_tratamiento, fecha_ini, fecha_fin))
        elif tipo == "Limpieza dental":
            duracion = round(random.uniform(0.5, 2.0), 2)
            cirugias_chunk.append((id_tratamiento, duracion))  # Asumimos como cirugía menor

    if vacunaciones_chunk:
        execute_batch(cur, "INSERT INTO vacunacion (id_tratamiento, id_insumo) VALUES (%s, %s)", vacunaciones_chunk)
    if cirugias_chunk:
        execute_batch(cur, "INSERT INTO cirugia (id_tratamiento, duracion) VALUES (%s, %s)", cirugias_chunk)
    if recetas_chunk:
        execute_batch(cur, "INSERT INTO receta (id_tratamiento, frecuencia) VALUES (%s, %s)", recetas_chunk)
    if terapias_chunk:
        execute_batch(cur, "INSERT INTO terapia (id_tratamiento, fechaInicio, fechaFin) VALUES (%s, %s, %s)", terapias_chunk)

    conn.commit()
    print(f"Insertados tratamientos y especializados: {i + CHUNK_SIZE} / {TOTAL}")


cur.execute("SELECT id FROM mascota ORDER BY id ASC LIMIT %s", (TOTAL,))
mascotas = [row[0] for row in cur.fetchall()]

cur.execute("SELECT id FROM tratamiento ORDER BY id ASC LIMIT %s", (TOTAL,))
tratamientos = [row[0] for row in cur.fetchall()]

cur.execute("SELECT id FROM cita ORDER BY id ASC LIMIT %s", (TOTAL,))
citas = [row[0] for row in cur.fetchall()]


print("Insertando registros en RECIBE...")
for i in range(0, TOTAL, CHUNK_SIZE):
    chunk_data = list(zip(
        mascotas[i:i + CHUNK_SIZE],
        tratamientos[i:i + CHUNK_SIZE],
        citas[i:i + CHUNK_SIZE]
    ))

    execute_batch(cur, """
        INSERT INTO recibe (id_mascota, id_tratamiento, id_cita)
        VALUES (%s, %s, %s)
    """, chunk_data)

    conn.commit()
    print(f"Insertados: {i + CHUNK_SIZE} / {TOTAL}")

cur.close()
conn.close()
