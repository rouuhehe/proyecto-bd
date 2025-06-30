import psycopg2
import pandas as pd
import os

DB_NAME = "mil"
USER = "postgres"
PASSWORD = "postgres"
HOST = "localhost"
PORT = "5433"
EXPORT_FOLDER = "tablas1"

# =======================

# Crea la carpeta si no existe
os.makedirs(EXPORT_FOLDER, exist_ok=True)

# Conecta a la base de datos
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT
)

cursor = conn.cursor()

# Obtiene todas las tablas del esquema public
cursor.execute("""
    SELECT tablename FROM pg_tables
    WHERE schemaname = 'public';
""")

tablas = cursor.fetchall()

for (tabla,) in tablas:
    print(f"Exportando tabla: {tabla}")
    df = pd.read_sql(f"SELECT * FROM {tabla}", conn)
    df.to_csv(f"{EXPORT_FOLDER}/{tabla}.csv", index=False)

cursor.close()
conn.close()

print("¡Todas las tablas fueron exportadas a CSV!")
