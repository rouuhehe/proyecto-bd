from faker import Faker
import random
import psycopg2
from datetime import datetime, timedelta

fake = Faker('es_ES')

# ------------------------ CONFIGURACIÓN ESCALABLE ------------------------

CONFIG = {
    'nPersonas': 250,
    'nPropietarios': 125,
    'nEmpleados': 125,
    'nVeterinarios': 42,
    'nRecepcionistas': 42,
    'nAdministradores': 41,
    'nCitas': 300,
    'nDiagnosticos': 300,
    'nTratamientos': 150,
    'nInsumos': 50,
    'nBoletas': 200,
    'nProveedores': 15,
    'nUsoInsumo': 500
}

# ------------------------ CONEXIÓN ------------------------

conn = psycopg2.connect(
    dbname="proyecto",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5433"
)
cur = conn.cursor()

# -------------------------- ENTIDADES PRINCIPALES ---------------------------

def generar_personas_y_roles():
    personas = []
    for _ in range(CONFIG['nPersonas']):
        dni = str(fake.unique.random_number(digits=8))
        telefono = str(fake.random_number(digits=9))
        nombre = fake.name()
        direccion = fake.address().replace("\\n", " ")
        cur.execute("INSERT INTO Persona (dni, nombre_completo, direccion, telefono) VALUES (%s, %s, %s, %s)", (dni, nombre, direccion, telefono))
        personas.append(dni)
    return personas

def asignar_roles(personas):
    random.shuffle(personas)
    propietarios = personas[:CONFIG['nPropietarios']]
    empleados = personas[CONFIG['nPropietarios']:]  # resto
    for dni in propietarios:
        cur.execute("INSERT INTO Propietario (dni_persona) VALUES (%s)", (dni,))
    for i, dni in enumerate(empleados):
        fecha_ingreso = fake.date_between(start_date='-5y', end_date='today')
        inicio_turno = fake.time()
        fin_turno = fake.time()
        salario = round(random.uniform(1500, 4000), 2)
        cur.execute("INSERT INTO Empleado (dni_persona, fecha_ingreso, inicio_turno, fin_turno, salario) VALUES (%s, %s, %s, %s, %s)",
                    (dni, fecha_ingreso, inicio_turno, fin_turno, salario))
        if i % 3 == 0:
            cur.execute("INSERT INTO Veterinario (dni_persona, num_colegiatura, especializacion) VALUES (%s, %s, %s)",
                        (dni, fake.unique.bothify(text='#######'), fake.word()))
        elif i % 3 == 1:
            cur.execute("INSERT INTO Recepcionista (dni_persona, telefono_fijo) VALUES (%s, %s)", (dni, fake.msisdn()[:5]))
        else:
            cur.execute("INSERT INTO Administrador (dni_persona, rango) VALUES (%s, %s)", (dni, random.choice(["Jefe", "Supervisor", "Gerente"])))
    return propietarios, empleados

def crear_mascotas(propietarios):
    mascotas = []
    for dni in propietarios:
        for _ in range(random.randint(1, 2)):
            nombre = fake.first_name()
            especie = random.choice(["Perro", "Gato", "Ave"])
            raza = fake.word()
            sexo = random.choice(["M", "F"])
            fecha_nac = fake.date_of_birth(minimum_age=0, maximum_age=15)
            cur.execute("INSERT INTO Mascota (nombre, especie, raza, sexo, fecha_nac) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                        (nombre, especie, raza, sexo, fecha_nac))
            id_mascota = cur.fetchone()[0]
            mascotas.append(id_mascota)
            cur.execute("INSERT INTO PropietarioTieneMascota (dni_propietario, id_mascota) VALUES (%s, %s)", (dni, id_mascota))
    return mascotas

# ------------------------ CITAS Y DIAGNÓSTICOS ------------------------

def crear_citas_y_diagnosticos(veterinarios, recepcionistas, mascotas):
    citas = []
    for _ in range(CONFIG['nCitas']):
        vet_dni = random.choice(veterinarios)
        rec_dni = random.choice(recepcionistas)
        mascota = random.choice(mascotas)
        hora = fake.time()
        fecha = fake.date_this_year()
        estado = random.choice(["Programada", "Completada"])
        precio = round(random.uniform(50, 150), 2)
        motivo = fake.sentence(nb_words=6)
        cur.execute("INSERT INTO Cita (dni_veterinario, hora, fecha, id_mascota, dni_recepcionista, estado, precio, motivo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
                    (vet_dni, hora, fecha, mascota, rec_dni, estado, precio, motivo))
        id_cita = cur.fetchone()[0]
        citas.append(id_cita)
        sintomas = fake.sentence()
        observaciones = fake.text(max_nb_chars=50)
        cur.execute("INSERT INTO Diagnostico (id_cita, fecha, sintomas, observaciones) VALUES (%s, %s, %s, %s)",
                    (id_cita, fecha, sintomas, observaciones))
    return citas

# ------------------------ TRATAMIENTOS Y DERIVACIONES ------------------------

def crear_tratamientos():
    tratamientos = []
    for _ in range(CONFIG['nTratamientos']):
        nombre = fake.word().capitalize()
        cur.execute("INSERT INTO Tratamiento (nombre) VALUES (%s) RETURNING id", (nombre,))
        id_tratamiento = cur.fetchone()[0]
        tratamientos.append(id_tratamiento)
    return tratamientos

def vincular_tratamientos(mascotas, tratamientos, citas):
    for tratamiento in tratamientos:
        mascota = random.choice(mascotas)
        cita = random.choice(citas)
        cur.execute("INSERT INTO Recibe (id_mascota, id_tratamiento) VALUES (%s, %s)", (mascota, tratamiento))
        cur.execute("SELECT id FROM Diagnostico ORDER BY RANDOM() LIMIT 1")
        diag = cur.fetchone()[0]
        cur.execute("INSERT INTO Resulta (id_tratamiento, id_diagnostico) VALUES (%s, %s)", (tratamiento, diag))
        cur.execute("SELECT 1 FROM Deriva WHERE id_diagnostico = %s AND id_cita = %s", (diag, cita))
        if not cur.fetchone():
            cur.execute("INSERT INTO Deriva (id_diagnostico, id_cita) VALUES (%s, %s)", (diag, cita))

# ------------------------ INSUMOS Y BOLETAS ------------------------

def crear_insumos_y_boletas(propietarios, recepcionistas):
    insumos = []
    proveedores = []
    for _ in range(CONFIG['nProveedores']):
        ruc = str(fake.unique.random_number(digits=11))
        nombre = fake.company()
        proveedores.append(ruc)
        cur.execute("INSERT INTO Proveedor (ruc, nombre) VALUES (%s, %s)", (ruc, nombre))
    for _ in range(CONFIG['nInsumos']):
        dni_rec = random.choice(recepcionistas)
        nombre = fake.word()
        stock = random.randint(5, 100)
        precio = round(random.uniform(5, 100), 2)
        ruc = random.choice(proveedores)
        cur.execute("INSERT INTO Insumo (dni_persona, nombre, ruc_proveedor, stock, precio) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                    (dni_rec, nombre, ruc, stock, precio))
        id_insumo = cur.fetchone()[0]
        insumos.append(id_insumo)
        cur.execute("INSERT INTO Provee (ruc_proveedor, id_insumo) VALUES (%s, %s)", (ruc, id_insumo))
        cur.execute("INSERT INTO Gestiona (dni_persona, id_insumo) VALUES (%s, %s)", (dni_rec, id_insumo))
    boletas = []
    for _ in range(CONFIG['nBoletas']):
        fecha = fake.date_this_year()
        dni_cli = random.choice(propietarios)
        dni_rec = random.choice(recepcionistas)
        monto = round(random.uniform(50, 300), 2)
        cur.execute("INSERT INTO Boleta (fecha, dni_persona_cliente, monto, dni_persona_recepcionista) VALUES (%s, %s, %s, %s) RETURNING id",
                    (fecha, dni_cli, monto, dni_rec))
        id_boleta = cur.fetchone()[0]
        boletas.append(id_boleta)
        cur.execute("INSERT INTO Compra (dni_persona, id_boleta) VALUES (%s, %s)", (dni_cli, id_boleta))
    return insumos, boletas

def uso_de_insumos(insumos, boletas):
    for _ in range(CONFIG['nUsoInsumo']):
        insumo = random.choice(insumos)
        boleta = random.choice(boletas)
        cantidad = random.randint(1, 5)
        motivo = fake.sentence(nb_words=3)
        cur.execute("SELECT 1 FROM UsoInsumo WHERE id_boleta = %s AND id_insumo = %s", (boleta, insumo))
        if not cur.fetchone():
            cur.execute("INSERT INTO UsoInsumo (id_boleta, id_insumo, motivo, cantidad) VALUES (%s, %s, %s, %s)",
                        (boleta, insumo, motivo, cantidad))

# ------------------------ FINALIZAR ------------------------

def finalizar():
    conn.commit()
    cur.close()
    conn.close()
    print("Base de datos poblada exitosamente.")

# ------------------------ EJECUCIÓN ------------------------

if __name__ == "__main__":
    personas = generar_personas_y_roles()
    propietarios, empleados = asignar_roles(personas)
    veterinarios = empleados[::3]
    recepcionistas = empleados[1::3]
    mascotas = crear_mascotas(propietarios)
    citas = crear_citas_y_diagnosticos(veterinarios, recepcionistas, mascotas)
    tratamientos = crear_tratamientos()
    vincular_tratamientos(mascotas, tratamientos, citas)
    insumos, boletas = crear_insumos_y_boletas(propietarios, recepcionistas)
    uso_de_insumos(insumos, boletas)
    finalizar()
