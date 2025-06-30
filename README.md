# PROYECTO BASE DE DATOS 💯

## Estructura del proyecto
```
proyecto-bd
├── .vscode
│  └── settings.json
├── consultas
│  ├── consulta_1.sql
│  ├── consulta_2.sql
│  ├── consulta_2_new.sql
│  ├── consulta_3.sql
│  └── consulta_4.sql
├── datos
│  ├── cargar_100m.py
│  ├── cargar_10m.py
│  ├── cargar_1m.py
│  ├── cargar_1MN.py
│  └── vacunas1millon.py
├── DB
│  ├── tablas
│  │  ├── tablas1
│  │  ├── tablas10
│  │  ├── tablas100
│  │  ├── tablasMillon
│  │  └── exportar.py
│  ├── .gitattributes
│  └── poblar.py
├── readme-files
├── resultados
├── scripts
│  ├── crear_tablas.sql
│  ├── droptables.sql
│  └── limpiar_bd.sql
├── .gitattributes
└── README.md
```

## Cargar base de datos

Holi, grupo, asumiendo que ya tienen una base de datos creada, la manera en la que podrán *"clonar"* la base de datos es la siguiente:

En la carpeta `DB` encontrarán el archivo `poblar.py`, en donde tendrán que configurar los datos de la base de datos que han creado en local.

```python
# === CONFIGURA ESTO ===
DB_NAME = "nombre-bd"
USER = "postgres"
PASSWORD = "postgres"
HOST = "localhost"
PORT = "5432" # lo configuraron al momento de instalar pgAdmin
CSV_PARENT_FOLDER = r"RUTA"
# =======================
```

En el apartado de `CSV_PARENT_FOLDER`, la ruta es la dirección del directorio en donde se ecuentran las tablas con los datos.

Por ejemplo, dentro de la carpeta `tablas1` se encuentran los datos de la base de datos con 1000 datos (por tabla) y su ruta, en mi computadora, es algo así: 
- `DB\tablas\tablas10`
- `C:\Users\yarit\Documents\utec\2025-1\bd\proyecto\proyecto-bd\DB\tablas\tablas10`


## Crear base de datos

En caso quieran poblar la base de datos por su cuenta, en el archivo `crear_tablas.sql` encontrarán el script para crear las tablas de la db. Si usan Visual Studio Code pueden instalar la extensión de `SQLTools`, `SQLTools PostgreSQL/otras-cosas` y ejecutar el script directamente desde ahí. En caso de que no tengan la extensión, pueden copiar el script y pegarlo en el editor de consultas de pgAdmin.

## Generar e insertar datos

Para generar datos de prueba, usaremos la librería `Faker` y `psycopg2` para conectarnos a la base de datos PostgreSQL. Asegúrense de tener instalado el paquete `Faker` y `psycopg2-binary`. Pueden instalarlo ejecutando el siguiente comando en su terminal:

```
pip install faker psycopg2-binary
```

Luego en el archivo de python, asegúrense de establecer la conexión a la base de datos. Aquí les dejo un ejemplo de cómo hacerlo (de todas formas en todos los archivos se encuentra esta cabecera, aun así, revisen el puerto):

```python
conn = psycopg2.connect(
    dbname="proyecto", # Nombre de la base de datos
    user="postgres", # Usuario de la base de datos
    password="postgres", # Contraseña del usuario
    host="localhost", 
    port="5433" # Puerto de la base de datos, lo configuraron en el pgAdmin
)
```

Una vez establecida la conexión, pueden ejecutar el script `cargar_nDatos.py` para generar e insertar datos en las tablas. Este script generará datos de prueba para las tablas que utilizaremos en las consultas.

Pueden correr los scripts como mejor se les acomode.

## Eliminar datos
Si necesitan eliminar los datos de las tablas, pueden usar el script `eliminar_datos.sql` que se encuentra en el repositorio. Este script eliminará todos los datos de las tablas sin eliminar las tablas mismas.

# Acerca del enunciado

## Consideraciones

Se nos dice que debemos considerar que la **“experimentacion**" y "**optimizacion**” debe realizarse mediante 2 o 3 consultas
“**genericas**” con un **nivel aceptable de complejidad en las consultas propuestas**. 

Dichas consultas se deben realizar en cuatro contextos de 1000 (mil) datos, 10000 (diez mil) datos, 100000 (cien mil) datos y 1 000 000 (un millon) de datos almacenados en la base de datos (deberıan tener 4 dumps de su proyecto).

---

Usaremos estas tres consultas como base para la comparación:
1. ¿Qué veterinarios han atendido la mayor cantidad de mascotas en el último mes?
2. ¿Cuál es el tipo de tratamiento más común a perros en los últimos seis meses?
3. ¿Qué día de la semana concentra el mayor número de citas médicas?


(Extra) ¿Cual serıa la complejidad operacional si escalamos los datos por encima del millon?,
realice una comparativa respecto a la cantidad de datos del p ́arrafo anterior. ¿Es suficiente la arquitectura Cliente-Servidor para procesar millones de datos?

