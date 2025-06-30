/* CONSULTA 3:
¿Qué día de la semana concentra el mayor número de citas médicas?
*/

SELECT 
  CASE EXTRACT(DOW FROM c.fecha)::int
    WHEN 0 THEN 'Domingo'
    WHEN 1 THEN 'Lunes'
    WHEN 2 THEN 'Martes'
    WHEN 3 THEN 'Miércoles'
    WHEN 4 THEN 'Jueves'
    WHEN 5 THEN 'Viernes'
    WHEN 6 THEN 'Sábado'
  END AS dia_semana,
  COUNT(*) AS cantidad_citas
FROM cita c
GROUP BY dia_semana
ORDER BY cantidad_citas DESC
LIMIT 1;