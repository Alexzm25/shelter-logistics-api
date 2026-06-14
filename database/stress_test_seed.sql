-- ==============================================================
-- SHELTER LOGISTICS — SCRIPT DE ESTRÉS (Stress Test Seed)
-- Requisito: ejecutar DESPUÉS de los seeds base (01–12)
-- Compatible con Neon (PostgreSQL)
-- Ejecutar una sola vez.
-- ==============================================================
--
-- DISTRIBUCIÓN DE REGISTROS:
--   person                :  2 000
--   profession_assignment :  2 000  (1 por persona)
--   exploration           :  1 000
--                          -------
--   TOTAL                 :  5 000
-- ==============================================================

-- Bloquear ejecución doble
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM person WHERE id_card LIKE 'ID-STRESS-%' LIMIT 1) THEN
    RAISE EXCEPTION
      'El script de estrés ya fue aplicado. '
      'Elimine los registros con id_card LIKE ''ID-STRESS-%%'' antes de volver a ejecutar.';
  END IF;
END $$;

BEGIN;

DROP TABLE IF EXISTS _sp CASCADE;

-- ================================================================
-- 1. PERSONAS — 2 000 registros
-- ================================================================
CREATE TEMP TABLE _sp AS
WITH ins AS (
  INSERT INTO person (
    name, last_name, birth_date, background_info,
    weight, height, camp_id,
    current_status, health_status,
    camp_entry_date, photo_url, is_active, id_card
  )
  SELECT
    'Nombre'   || LPAD(gs::TEXT, 4, '0'),
    'Apellido' || LPAD(gs::TEXT, 4, '0'),
    (DATE '1965-01-01' + ((gs * 37) % 14600) * INTERVAL '1 day')::DATE,
    'Sobreviviente de ingreso estándar. Registro de prueba de carga #' || gs || '.',
    (45.00 + (gs % 55))::NUMERIC(5,2),
    (1.45   + ((gs % 40) * 0.01))::NUMERIC(5,2),
    (SELECT id FROM camp ORDER BY id OFFSET (gs % 3) LIMIT 1),
    CASE gs % 4
      WHEN 0 THEN 'TRABAJANDO'
      WHEN 1 THEN 'EN EXPLORACIÓN'
      WHEN 2 THEN 'TRASLADANDO RECURSOS'
      ELSE        'LIBRE'
    END::current_status_enum,
    CASE gs % 5
      WHEN 0 THEN 'HERIDO'
      WHEN 1 THEN 'ENFERMO'
      ELSE        'SANO'
    END::health_status_enum,
    NOW() - ((gs % 730 + 1) * INTERVAL '1 day'),
    'https://ui-avatars.com/api/?name=S' || gs || '&size=128&background=random',
    (gs % 12 != 0),
    'ID-STRESS-' || LPAD(gs::TEXT, 6, '0')
  FROM generate_series(1, 2000) AS gs
  RETURNING id
)
SELECT id, ROW_NUMBER() OVER (ORDER BY id) AS rn FROM ins;

-- ================================================================
-- 2. ASIGNACIONES DE PROFESIÓN — 2 000 registros (1 por persona)
-- ================================================================
INSERT INTO profession_assignment (
  start_date, end_date, reason,
  is_main_profession, profession_id, person_id, is_active
)
SELECT
  (DATE '2024-01-01' + (sp.rn * 7 % 365) * INTERVAL '1 day')::DATE,
  NULL,
  'Asignación principal al ingreso al campamento',
  TRUE,
  (SELECT id FROM profession ORDER BY id OFFSET (sp.rn % 3) LIMIT 1),
  sp.id,
  TRUE
FROM _sp sp;

-- ================================================================
-- 3. EXPLORACIONES — 1 000 registros
-- ================================================================
INSERT INTO exploration (
  start_date, return_date, exploration_status,
  camp_id, extra_days, ration_per_person, max_extra_days, estimated_days
)
SELECT
  NOW() - ((gs % 365) * INTERVAL '1 day') - (gs % 24 * INTERVAL '1 hour'),
  CASE gs % 3
    WHEN 0 THEN NULL
    ELSE NOW() - ((gs % 180) * INTERVAL '1 day')
  END,
  CASE gs % 3
    WHEN 0 THEN 'EN PROCESO'
    WHEN 1 THEN 'COMPLETADA'
    ELSE        'CANCELADA'
  END::exploration_status_enum,
  (SELECT id FROM camp ORDER BY id OFFSET (gs % 3) LIMIT 1),
  gs % 5,
  1 + (gs % 3),
  3 + (gs % 7),
  3 + (gs % 10)
FROM generate_series(1, 1000) AS gs;

-- ================================================================
-- Limpieza
-- ================================================================
DROP TABLE IF EXISTS _sp CASCADE;

COMMIT;
