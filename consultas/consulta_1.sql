
/* CONSULTA:
¿Qué veterinarios, agrupados por especialización, 
han atendido la mayor cantidad de citas en el último mes?
*/

SELECT especializacion, p.nombre_completo, COUNT(*) AS cantidad_citas
FROM veterinario
JOIN persona p ON veterinario.dni_persona = p.dni
JOIN cita ON veterinario.dni_persona = cita.dni_veterinario
WHERE fecha >= CURRENT_DATE - INTERVAL '1 month'
GROUP BY especializacion, p.nombre_completo
ORDER BY COUNT(*) DESC


