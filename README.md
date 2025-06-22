# PROYECTO BASE DE DATOS 💯

Holi grupo, aqui unos datos para conectar a la bd que tengan no sé como es. En el script de Python, pueden usar el siguiente código para conectarse a la base de datos PostgreSQL:

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

## Enunciado: Consideraciones

Se nos dice que debemos
considerar que la **“experimentacion**" y "**optimizacion**” debe realizarse mediante 2 o 3 consultas
“**genericas**” con un **nivel aceptable de complejidad en las consultas propuestas**. 

Dichas consultas se
deben realizar en cuatro contextos de 1000(mil) datos, 10000 (diez mil) datos, 100000 (cien mil)
datos y 1 000 000 (un millon) de datos almacenados en la base de datos (deberıan tener 4 dumps de su proyecto).

---

Usaremos estas tres consultas como base para la comparación:
1. ¿Qué veterinarios han atendido la mayor cantidad de mascotas en el último mes?
2. ¿Cuál es el tipo de tratamiento más común a perros en los últimos seis meses?
3. ¿Qué día de la semana concentra el mayor número de citas médicas?


(Extra) ¿Cual serıa la complejidad operacional si escalamos los datos por encima del millon?,
realice una comparativa respecto a la cantidad de datos del p ́arrafo anterior. ¿Es suficiente la arquitectura Cliente-Servidor para procesar millones de datos?

