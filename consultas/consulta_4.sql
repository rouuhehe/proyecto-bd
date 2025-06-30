SELECT v.especializacion, p.nombre_completo, COUNT(*) AS cant_vacunas
FROM vacunacion vac
JOIN tratamiento t ON vac.id_tratamiento = t.id
JOIN recibe r ON t.id = r.id_tratamiento
JOIN cita c ON r.id_mascota = c.id_mascota
JOIN veterinario v ON c.dni_veterinario = v.dni_persona
JOIN persona p ON v.dni_persona = p.dni
WHERE EXTRACT(YEAR FROM c.fecha) = EXTRACT(YEAR FROM CURRENT_DATE)
GROUP BY v.especializacion, p.nombre_completo
ORDER BY cant_vacunas DESC
LIMIT 5;