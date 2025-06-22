# PROYECTO BASE DE DATOS 💯

Holi grupo, aqui unos datos para conectar a la bd. En el script de Python, pueden usar el siguiente código para conectarse a la base de datos PostgreSQL:

```
pip install faker psycopg2-binary
```

```python
conn = psycopg2.connect(
    dbname="proyecto", # Nombre de la base de datos
    user="postgres", # Usuario de la base de datos
    password="postgres", # Contraseña del usuario
    host="localhost", 
    port="5433" # Puerto de la base de datos, lo configuran en el pgAdmin
)
```

