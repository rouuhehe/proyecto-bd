/* CONSULTA 2:
¿Cuál es el tratamiento más común a perros en los últimos seis meses?
*/

SELECT t.nombre AS tratamiento, COUNT(*) AS cantidad
FROM tratamiento t
JOIN recibe r ON t.id = r.id_tratamiento
JOIN cita c ON r.id_cita = c.id
JOIN mascota m ON c.id_mascota = m.id
WHERE m.especie = 'Perro' 
GROUP BY t.nombre
ORDER BY COUNT(*) DESC
LIMIT 1