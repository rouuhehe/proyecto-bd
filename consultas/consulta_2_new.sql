-- Active: 1746627980787@@127.0.0.1@5433@bd
/* CONSULTA 2:
¿Cuál es el tratamiento más común a perros en los últimos seis meses?
*/

SET enable_mergejoin TO OFF;
SET enable_hashjoin TO OFF;
SET enable_bitmapscan TO OFF;
SET enable_sort TO OFF;

VACUUM FULL;

CREATE INDEX idx_fecha_cita ON cita(fecha);
CREATE INDEX idx_veterinario_cita ON cita(dni_veterinario);
CREATE INDEX idx_id_tratamiento_vac ON vacunacion(id_tratamiento);
CREATE INDEX idx_id_tratamiento_trat ON tratamiento(id);
CREATE INDEX idx_id_mascota_recibe ON recibe(id_mascota);

EXPLAIN ANALYZE
SELECT v.especializacion, p.nombre_completo, COUNT(*) AS cant_vacunas
FROM cita c
JOIN veterinario v ON c.dni_veterinario = v.dni_persona
JOIN persona p ON v.dni_persona = p.dni
JOIN recibe r ON c.id_mascota = r.id_mascota
JOIN tratamiento t ON r.id_tratamiento = t.id
JOIN vacunacion vac ON vac.id_tratamiento = t.id
WHERE EXTRACT(YEAR FROM c.fecha) = EXTRACT(YEAR FROM CURRENT_DATE)
GROUP BY v.especializacion, p.nombre_completo
ORDER BY cant_vacunas DESC; 

