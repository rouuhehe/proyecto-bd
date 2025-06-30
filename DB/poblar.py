import psycopg2
import pandas as pd
import os
import glob

# === CONFIGURA ESTO ===
DB_NAME = "PRUEBA2"
USER = "postgres"
PASSWORD = "postgres"
HOST = "localhost"
PORT = "5433"
CSV_PARENT_FOLDER = r"C:\Users\yarit\Documents\utec\2025-1\bd\proyecto\proyecto-bd\DB\tablas\tablas1"
# =======================

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT
)
cursor = conn.cursor()

csv_files = glob.glob(os.path.join(CSV_PARENT_FOLDER, "**", "*.csv"), recursive=True)

def inferir_tipo(col):
    if pd.api.types.is_integer_dtype(col):
        return "INTEGER"
    elif pd.api.types.is_float_dtype(col):
        return "REAL"
    elif pd.api.types.is_bool_dtype(col):
        return "BOOLEAN"
    elif pd.api.types.is_datetime64_any_dtype(col):
        return "TIMESTAMP"
    else:
        return "TEXT"

for file_path in csv_files:
    table_name = os.path.splitext(os.path.basename(file_path))[0]
    print(f"\nProcesando archivo: {file_path}")

    try:
        df = pd.read_csv(file_path)

        # === Crear tabla ===
        columnas_sql = []
        for col in df.columns:
            tipo_pg = inferir_tipo(df[col])
            columnas_sql.append(f'"{col}" {tipo_pg}')
        columnas_str = ", ".join(columnas_sql)
        create_table_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columnas_str});'

        cursor.execute(create_table_sql)
        conn.commit()
        print(f"Tabla '{table_name}' creada")

        # === Insertar datos ===
        if not df.empty:
            cols = ', '.join(f'"{c}"' for c in df.columns)
            placeholders = ', '.join(['%s'] * len(df.columns))
            insert_sql = f'INSERT INTO "{table_name}" ({cols}) VALUES ({placeholders})'

            data = [tuple(row) for row in df.itertuples(index=False, name=None)]
            for row in data:
                cursor.execute(insert_sql, row)

            conn.commit()
            print(f"Insertados {len(data)} registros en '{table_name}'")
        else:
            print(f"El archivo '{table_name}' está vacío, no se insertaron datos.")

    except Exception as e:
        print(f"Error en '{table_name}': {e}")
        conn.rollback()

cursor.close()
conn.close()
print("\n¡Todo listo! Tablas creadas e información insertada.")
