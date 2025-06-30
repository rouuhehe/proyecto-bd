
/* CONSULTA:
¿Qué veterinarios, agrupados por especialización, 
han atendido la mayor cantidad de citas en el último mes?
*/

SELECT v.especializacion, p.nombre_completo, COUNT(*) AS cantidad_citas
FROM cita c
JOIN veterinario v ON c.dni_veterinario = v.dni_persona
JOIN persona p ON v.dni_persona = p.dni
WHERE c.fecha >= CURRENT_DATE - INTERVAL '1 month'
GROUP BY v.especializacion, p.nombre_completo
ORDER BY cantidad_citas DESC;


