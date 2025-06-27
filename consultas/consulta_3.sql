/* CONSULTA 3:
¿Qué día de la semana concentra el mayor número de citas médicas?
*/

SELECT TO_CHAR(c.fecha, 'Day') AS dia_semana, COUNT(*) AS cantidad_citas
FROM cita c
GROUP BY TO_CHAR(c.fecha, 'Day')
ORDER BY COUNT(*) DESC
LIMIT 1