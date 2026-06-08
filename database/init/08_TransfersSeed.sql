-- =========================================================
-- TRANSFERS SEED
-- Personas de prueba + transferencias de recursos y personas
-- para Campamento Caolin.
-- Depende de: 03_CampsSeed.sql, 04_ProfessionsSeed.sql, 06_InventorySeed.sql
-- =========================================================

-- -------------------------------------------------------
-- PERSONAS DE PRUEBA (id_card con prefijo TEST-SEED para
-- distinguirlas de ingresos reales por la app)
-- -------------------------------------------------------

INSERT INTO "person" ("name", "last_name", "birth_date", "background_info", "weight", "height",
    "camp_id", "current_status", "health_status", "camp_entry_date", "photo_url", "is_active", "id_card")
SELECT 'Marco', 'Villanueva', '1992-01-01',
    'Ex-militar reconvertido en explorador. Conoce el terreno al norte del valle.',
    78.50, 1.82,
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    'LIBRE', 'SANO', '2025-01-15 08:00:00+00', '', TRUE, 'TEST-SEED-001'
WHERE NOT EXISTS (SELECT 1 FROM person WHERE id_card = 'TEST-SEED-001');

INSERT INTO "person" ("name", "last_name", "birth_date", "background_info", "weight", "height",
    "camp_id", "current_status", "health_status", "camp_entry_date", "photo_url", "is_active", "id_card")
SELECT 'Sofía', 'Medrano', '1998-01-01',
    'Médica rural con experiencia en zonas de conflicto armado.',
    62.00, 1.65,
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    'TRABAJANDO', 'SANO', '2025-01-20 09:00:00+00', '', TRUE, 'TEST-SEED-002'
WHERE NOT EXISTS (SELECT 1 FROM person WHERE id_card = 'TEST-SEED-002');

INSERT INTO "person" ("name", "last_name", "birth_date", "background_info", "weight", "height",
    "camp_id", "current_status", "health_status", "camp_entry_date", "photo_url", "is_active", "id_card")
SELECT 'Andrés', 'Palacios', '1985-01-01',
    'Agricultor con conocimiento de cultivos de subsistencia en climas áridos.',
    84.00, 1.78,
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    'TRABAJANDO', 'SANO', '2025-02-01 07:30:00+00', '', TRUE, 'TEST-SEED-003'
WHERE NOT EXISTS (SELECT 1 FROM person WHERE id_card = 'TEST-SEED-003');

INSERT INTO "person" ("name", "last_name", "birth_date", "background_info", "weight", "height",
    "camp_id", "current_status", "health_status", "camp_entry_date", "photo_url", "is_active", "id_card")
SELECT 'Valentina', 'Cruz', '2001-01-01',
    'Exploradora con habilidades de cartografía y orientación en terreno hostil.',
    58.00, 1.68,
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    'LIBRE', 'SANO', '2025-02-10 11:00:00+00', '', TRUE, 'TEST-SEED-004'
WHERE NOT EXISTS (SELECT 1 FROM person WHERE id_card = 'TEST-SEED-004');

INSERT INTO "person" ("name", "last_name", "birth_date", "background_info", "weight", "height",
    "camp_id", "current_status", "health_status", "camp_entry_date", "photo_url", "is_active", "id_card")
SELECT 'Rodrigo', 'Fuentes', '1989-01-01',
    'Mecánico y explorador. Especialista en recuperación de equipos en campo abierto.',
    75.00, 1.75,
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    'LIBRE', 'SANO', '2025-02-18 10:00:00+00', '', TRUE, 'TEST-SEED-005'
WHERE NOT EXISTS (SELECT 1 FROM person WHERE id_card = 'TEST-SEED-005');

INSERT INTO "person" ("name", "last_name", "birth_date", "background_info", "weight", "height",
    "camp_id", "current_status", "health_status", "camp_entry_date", "photo_url", "is_active", "id_card")
SELECT 'Carmen', 'Ibáñez', '1981-01-01',
    'Ex-enfermera de campo. Experta en triaje y medicina de emergencia.',
    65.00, 1.60,
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    'LIBRE', 'HERIDO', '2025-03-01 14:00:00+00', '', TRUE, 'TEST-SEED-006'
WHERE NOT EXISTS (SELECT 1 FROM person WHERE id_card = 'TEST-SEED-006');

-- Asignaciones de profesión para las personas de prueba
INSERT INTO "profession_assignment" ("start_date", "reason", "is_main_profession", "profession_id", "person_id", "is_active")
SELECT '2025-01-15', 'Asignación inicial al ingreso al campamento', TRUE,
    (SELECT id FROM profession WHERE name = 'EXPLORADOR' LIMIT 1),
    (SELECT id FROM person WHERE id_card = 'TEST-SEED-001' LIMIT 1), TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM profession_assignment WHERE person_id = (SELECT id FROM person WHERE id_card = 'TEST-SEED-001' LIMIT 1) AND is_active = TRUE
);

INSERT INTO "profession_assignment" ("start_date", "reason", "is_main_profession", "profession_id", "person_id", "is_active")
SELECT '2025-01-20', 'Asignación inicial al ingreso al campamento', TRUE,
    (SELECT id FROM profession WHERE name = 'MEDICO' LIMIT 1),
    (SELECT id FROM person WHERE id_card = 'TEST-SEED-002' LIMIT 1), TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM profession_assignment WHERE person_id = (SELECT id FROM person WHERE id_card = 'TEST-SEED-002' LIMIT 1) AND is_active = TRUE
);

INSERT INTO "profession_assignment" ("start_date", "reason", "is_main_profession", "profession_id", "person_id", "is_active")
SELECT '2025-02-01', 'Asignación inicial al ingreso al campamento', TRUE,
    (SELECT id FROM profession WHERE name = 'AGRICULTOR' LIMIT 1),
    (SELECT id FROM person WHERE id_card = 'TEST-SEED-003' LIMIT 1), TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM profession_assignment WHERE person_id = (SELECT id FROM person WHERE id_card = 'TEST-SEED-003' LIMIT 1) AND is_active = TRUE
);

INSERT INTO "profession_assignment" ("start_date", "reason", "is_main_profession", "profession_id", "person_id", "is_active")
SELECT '2025-02-10', 'Asignación inicial al ingreso al campamento', TRUE,
    (SELECT id FROM profession WHERE name = 'EXPLORADOR' LIMIT 1),
    (SELECT id FROM person WHERE id_card = 'TEST-SEED-004' LIMIT 1), TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM profession_assignment WHERE person_id = (SELECT id FROM person WHERE id_card = 'TEST-SEED-004' LIMIT 1) AND is_active = TRUE
);

INSERT INTO "profession_assignment" ("start_date", "reason", "is_main_profession", "profession_id", "person_id", "is_active")
SELECT '2025-02-18', 'Asignación inicial al ingreso al campamento', TRUE,
    (SELECT id FROM profession WHERE name = 'EXPLORADOR' LIMIT 1),
    (SELECT id FROM person WHERE id_card = 'TEST-SEED-005' LIMIT 1), TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM profession_assignment WHERE person_id = (SELECT id FROM person WHERE id_card = 'TEST-SEED-005' LIMIT 1) AND is_active = TRUE
);

INSERT INTO "profession_assignment" ("start_date", "reason", "is_main_profession", "profession_id", "person_id", "is_active")
SELECT '2025-03-01', 'Asignación inicial al ingreso al campamento', TRUE,
    (SELECT id FROM profession WHERE name = 'MEDICO' LIMIT 1),
    (SELECT id FROM person WHERE id_card = 'TEST-SEED-006' LIMIT 1), TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM profession_assignment WHERE person_id = (SELECT id FROM person WHERE id_card = 'TEST-SEED-006' LIMIT 1) AND is_active = TRUE
);

-- -------------------------------------------------------
-- TRANSFERENCIAS DE RECURSOS
-- -------------------------------------------------------

-- [REC-1] Caolin → Fayenza | APROBADO + LLEGÓ | feb 2025
INSERT INTO "transfer_request" ("from_camp_id", "to_camp_id", "request_status", "transfer_status",
    "departure_date", "arrival_date", "authorized_by", "is_resource_transfer", "created_at")
VALUES (
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    (SELECT id FROM camp WHERE name = 'Campamento Fayenza' LIMIT 1),
    'APROBADO', 'LLEGÓ', '2025-02-05', '2025-02-07', 'admin_caolin', TRUE,
    '2025-02-04 09:30:00+00'
);

INSERT INTO "transfer_resource" ("transfer_amount", "resource_id", "request_id")
VALUES
(50, (SELECT id FROM resource WHERE name = 'Agua Embotellada' LIMIT 1),
     (SELECT id FROM transfer_request WHERE created_at = '2025-02-04 09:30:00+00' LIMIT 1)),
(30, (SELECT id FROM resource WHERE name = 'Latas de Frijoles' LIMIT 1),
     (SELECT id FROM transfer_request WHERE created_at = '2025-02-04 09:30:00+00' LIMIT 1));

INSERT INTO "inventory_movement" ("quantity", "inventory_resource_id", "movement_type", "transfer_request_id", "created_at")
VALUES
(
    50,
    (SELECT ir.id FROM inventory_resource ir
     JOIN inventory i ON i.id = ir.inventory_id
     JOIN camp c ON c.id = i.camp_id
     JOIN resource r ON r.id = ir.resource_id
     WHERE c.name = 'Campamento Caolin' AND r.name = 'Agua Embotellada' LIMIT 1),
    'TRANSFERENCIA',
    (SELECT id FROM transfer_request WHERE created_at = '2025-02-04 09:30:00+00' LIMIT 1),
    '2025-02-05 10:00:00+00'
),
(
    30,
    (SELECT ir.id FROM inventory_resource ir
     JOIN inventory i ON i.id = ir.inventory_id
     JOIN camp c ON c.id = i.camp_id
     JOIN resource r ON r.id = ir.resource_id
     WHERE c.name = 'Campamento Caolin' AND r.name = 'Latas de Frijoles' LIMIT 1),
    'TRANSFERENCIA',
    (SELECT id FROM transfer_request WHERE created_at = '2025-02-04 09:30:00+00' LIMIT 1),
    '2025-02-05 10:00:00+00'
);

-- [REC-2] Caolin → Fayenza | APROBADO + LLEGÓ | feb 2025
INSERT INTO "transfer_request" ("from_camp_id", "to_camp_id", "request_status", "transfer_status",
    "departure_date", "arrival_date", "authorized_by", "is_resource_transfer", "created_at")
VALUES (
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    (SELECT id FROM camp WHERE name = 'Campamento Fayenza' LIMIT 1),
    'APROBADO', 'LLEGÓ', '2025-02-20', '2025-02-22', 'admin_caolin', TRUE,
    '2025-02-19 11:00:00+00'
);

INSERT INTO "transfer_resource" ("transfer_amount", "resource_id", "request_id")
VALUES
(40, (SELECT id FROM resource WHERE name = 'Arroz' LIMIT 1),
     (SELECT id FROM transfer_request WHERE created_at = '2025-02-19 11:00:00+00' LIMIT 1)),
(25, (SELECT id FROM resource WHERE name = 'Vendajes' LIMIT 1),
     (SELECT id FROM transfer_request WHERE created_at = '2025-02-19 11:00:00+00' LIMIT 1));

INSERT INTO "inventory_movement" ("quantity", "inventory_resource_id", "movement_type", "transfer_request_id", "created_at")
VALUES
(
    40,
    (SELECT ir.id FROM inventory_resource ir
     JOIN inventory i ON i.id = ir.inventory_id
     JOIN camp c ON c.id = i.camp_id
     JOIN resource r ON r.id = ir.resource_id
     WHERE c.name = 'Campamento Caolin' AND r.name = 'Arroz' LIMIT 1),
    'TRANSFERENCIA',
    (SELECT id FROM transfer_request WHERE created_at = '2025-02-19 11:00:00+00' LIMIT 1),
    '2025-02-20 08:30:00+00'
),
(
    25,
    (SELECT ir.id FROM inventory_resource ir
     JOIN inventory i ON i.id = ir.inventory_id
     JOIN camp c ON c.id = i.camp_id
     JOIN resource r ON r.id = ir.resource_id
     WHERE c.name = 'Campamento Caolin' AND r.name = 'Vendajes' LIMIT 1),
    'TRANSFERENCIA',
    (SELECT id FROM transfer_request WHERE created_at = '2025-02-19 11:00:00+00' LIMIT 1),
    '2025-02-20 08:30:00+00'
);

-- [REC-3] Caolin → Azulejo | APROBADO + LLEGÓ | mar 2025
INSERT INTO "transfer_request" ("from_camp_id", "to_camp_id", "request_status", "transfer_status",
    "departure_date", "arrival_date", "authorized_by", "is_resource_transfer", "created_at")
VALUES (
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    (SELECT id FROM camp WHERE name = 'Campamento Azulejo' LIMIT 1),
    'APROBADO', 'LLEGÓ', '2025-03-10', '2025-03-13', 'admin_caolin', TRUE,
    '2025-03-09 14:00:00+00'
);

INSERT INTO "transfer_resource" ("transfer_amount", "resource_id", "request_id")
VALUES
(80, (SELECT id FROM resource WHERE name = 'Agua Embotellada' LIMIT 1),
     (SELECT id FROM transfer_request WHERE created_at = '2025-03-09 14:00:00+00' LIMIT 1)),
(15, (SELECT id FROM resource WHERE name = 'Antibióticos' LIMIT 1),
     (SELECT id FROM transfer_request WHERE created_at = '2025-03-09 14:00:00+00' LIMIT 1));

INSERT INTO "inventory_movement" ("quantity", "inventory_resource_id", "movement_type", "transfer_request_id", "created_at")
VALUES
(
    80,
    (SELECT ir.id FROM inventory_resource ir
     JOIN inventory i ON i.id = ir.inventory_id
     JOIN camp c ON c.id = i.camp_id
     JOIN resource r ON r.id = ir.resource_id
     WHERE c.name = 'Campamento Caolin' AND r.name = 'Agua Embotellada' LIMIT 1),
    'TRANSFERENCIA',
    (SELECT id FROM transfer_request WHERE created_at = '2025-03-09 14:00:00+00' LIMIT 1),
    '2025-03-10 07:00:00+00'
),
(
    15,
    (SELECT ir.id FROM inventory_resource ir
     JOIN inventory i ON i.id = ir.inventory_id
     JOIN camp c ON c.id = i.camp_id
     JOIN resource r ON r.id = ir.resource_id
     WHERE c.name = 'Campamento Caolin' AND r.name = 'Antibióticos' LIMIT 1),
    'TRANSFERENCIA',
    (SELECT id FROM transfer_request WHERE created_at = '2025-03-09 14:00:00+00' LIMIT 1),
    '2025-03-10 07:00:00+00'
);

-- [REC-4] Fayenza → Caolin | APROBADO + LLEGÓ (ingreso a Caolin) | mar 2025
INSERT INTO "transfer_request" ("from_camp_id", "to_camp_id", "request_status", "transfer_status",
    "departure_date", "arrival_date", "authorized_by", "is_resource_transfer", "created_at")
VALUES (
    (SELECT id FROM camp WHERE name = 'Campamento Fayenza' LIMIT 1),
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    'APROBADO', 'LLEGÓ', '2025-03-01', '2025-03-03', 'admin_fayenza', TRUE,
    '2025-02-28 16:00:00+00'
);

INSERT INTO "transfer_resource" ("transfer_amount", "resource_id", "request_id")
VALUES
(100, (SELECT id FROM resource WHERE name = 'Agua Embotellada' LIMIT 1),
      (SELECT id FROM transfer_request WHERE created_at = '2025-02-28 16:00:00+00' LIMIT 1));

INSERT INTO "inventory_movement" ("quantity", "inventory_resource_id", "movement_type", "transfer_request_id", "created_at")
VALUES
(
    100,
    (SELECT ir.id FROM inventory_resource ir
     JOIN inventory i ON i.id = ir.inventory_id
     JOIN camp c ON c.id = i.camp_id
     JOIN resource r ON r.id = ir.resource_id
     WHERE c.name = 'Campamento Caolin' AND r.name = 'Agua Embotellada' LIMIT 1),
    'INGRESO',
    (SELECT id FROM transfer_request WHERE created_at = '2025-02-28 16:00:00+00' LIMIT 1),
    '2025-03-03 09:00:00+00'
);

-- [REC-5] Caolin → Azulejo | APROBADO + DE CAMINO | abr 2025
INSERT INTO "transfer_request" ("from_camp_id", "to_camp_id", "request_status", "transfer_status",
    "departure_date", "authorized_by", "is_resource_transfer", "created_at")
VALUES (
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    (SELECT id FROM camp WHERE name = 'Campamento Azulejo' LIMIT 1),
    'APROBADO', 'DE CAMINO', '2025-04-01', 'admin_caolin', TRUE,
    '2025-03-30 10:00:00+00'
);

INSERT INTO "transfer_resource" ("transfer_amount", "resource_id", "request_id")
VALUES
(45, (SELECT id FROM resource WHERE name = 'Semillas de Maíz' LIMIT 1),
     (SELECT id FROM transfer_request WHERE created_at = '2025-03-30 10:00:00+00' LIMIT 1)),
(30, (SELECT id FROM resource WHERE name = 'Semillas de Papa' LIMIT 1),
     (SELECT id FROM transfer_request WHERE created_at = '2025-03-30 10:00:00+00' LIMIT 1));

-- [REC-6] Caolin → Fayenza | APROBADO + EN PREPARACIÓN | abr 2025
INSERT INTO "transfer_request" ("from_camp_id", "to_camp_id", "request_status", "transfer_status",
    "departure_date", "authorized_by", "is_resource_transfer", "created_at")
VALUES (
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    (SELECT id FROM camp WHERE name = 'Campamento Fayenza' LIMIT 1),
    'APROBADO', 'EN PREPARACIÓN', '2025-04-10', 'admin_caolin', TRUE,
    '2025-04-08 08:00:00+00'
);

INSERT INTO "transfer_resource" ("transfer_amount", "resource_id", "request_id")
VALUES
(60, (SELECT id FROM resource WHERE name = 'Arroz' LIMIT 1),
     (SELECT id FROM transfer_request WHERE created_at = '2025-04-08 08:00:00+00' LIMIT 1)),
(10, (SELECT id FROM resource WHERE name = 'Botiquín Básico' LIMIT 1),
     (SELECT id FROM transfer_request WHERE created_at = '2025-04-08 08:00:00+00' LIMIT 1));

-- [REC-7] Fayenza → Caolin | PENDIENTE | abr 2025
INSERT INTO "transfer_request" ("from_camp_id", "to_camp_id", "request_status",
    "departure_date", "is_resource_transfer", "created_at")
VALUES (
    (SELECT id FROM camp WHERE name = 'Campamento Fayenza' LIMIT 1),
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    'PENDIENTE', '2025-04-15', TRUE,
    '2025-04-14 13:00:00+00'
);

INSERT INTO "transfer_resource" ("transfer_amount", "resource_id", "request_id")
VALUES
(30, (SELECT id FROM resource WHERE name = 'Semillas de Papa' LIMIT 1),
     (SELECT id FROM transfer_request WHERE created_at = '2025-04-14 13:00:00+00' LIMIT 1)),
(20, (SELECT id FROM resource WHERE name = 'Antibióticos' LIMIT 1),
     (SELECT id FROM transfer_request WHERE created_at = '2025-04-14 13:00:00+00' LIMIT 1));

-- [REC-8] Azulejo → Caolin | PENDIENTE | abr 2025
INSERT INTO "transfer_request" ("from_camp_id", "to_camp_id", "request_status",
    "departure_date", "is_resource_transfer", "created_at")
VALUES (
    (SELECT id FROM camp WHERE name = 'Campamento Azulejo' LIMIT 1),
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    'PENDIENTE', '2025-04-18', TRUE,
    '2025-04-17 09:30:00+00'
);

INSERT INTO "transfer_resource" ("transfer_amount", "resource_id", "request_id")
VALUES
(50, (SELECT id FROM resource WHERE name = 'Arroz' LIMIT 1),
     (SELECT id FROM transfer_request WHERE created_at = '2025-04-17 09:30:00+00' LIMIT 1));

-- [REC-9] Caolin → Fayenza | RECHAZADO | mar 2025 (cantidad excesiva)
INSERT INTO "transfer_request" ("from_camp_id", "to_camp_id", "request_status",
    "departure_date", "authorized_by", "is_resource_transfer", "created_at")
VALUES (
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    (SELECT id FROM camp WHERE name = 'Campamento Fayenza' LIMIT 1),
    'RECHAZADO', '2025-03-20', 'admin_caolin', TRUE,
    '2025-03-18 15:00:00+00'
);

INSERT INTO "transfer_resource" ("transfer_amount", "resource_id", "request_id")
VALUES
(200, (SELECT id FROM resource WHERE name = 'Agua Embotellada' LIMIT 1),
      (SELECT id FROM transfer_request WHERE created_at = '2025-03-18 15:00:00+00' LIMIT 1));

-- [REC-10] Azulejo → Caolin | RECHAZADO | mar 2025
INSERT INTO "transfer_request" ("from_camp_id", "to_camp_id", "request_status",
    "departure_date", "authorized_by", "is_resource_transfer", "created_at")
VALUES (
    (SELECT id FROM camp WHERE name = 'Campamento Azulejo' LIMIT 1),
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    'RECHAZADO', '2025-03-25', 'admin_azulejo', TRUE,
    '2025-03-24 12:00:00+00'
);

INSERT INTO "transfer_resource" ("transfer_amount", "resource_id", "request_id")
VALUES
(50, (SELECT id FROM resource WHERE name = 'Botiquín Básico' LIMIT 1),
     (SELECT id FROM transfer_request WHERE created_at = '2025-03-24 12:00:00+00' LIMIT 1));

-- -------------------------------------------------------
-- TRANSFERENCIAS DE PERSONAS
-- -------------------------------------------------------

-- [PER-1] Caolin → Fayenza | APROBADO + LLEGÓ | Marco Villanueva
INSERT INTO "transfer_request" ("from_camp_id", "to_camp_id", "request_status", "transfer_status",
    "departure_date", "arrival_date", "authorized_by", "is_resource_transfer", "created_at")
VALUES (
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    (SELECT id FROM camp WHERE name = 'Campamento Fayenza' LIMIT 1),
    'APROBADO', 'LLEGÓ', '2025-03-05', '2025-03-07', 'admin_caolin', FALSE,
    '2025-03-04 08:00:00+00'
);

INSERT INTO "transfer_participants" ("person_id", "request_id", "is_transfer_active")
SELECT (SELECT id FROM person WHERE id_card = 'TEST-SEED-001' LIMIT 1),
    (SELECT id FROM transfer_request WHERE created_at = '2025-03-04 08:00:00+00' LIMIT 1),
    FALSE
WHERE NOT EXISTS (
    SELECT 1 FROM "transfer_participants" tp
    WHERE tp.person_id = (SELECT id FROM person WHERE id_card = 'TEST-SEED-001' LIMIT 1)
      AND tp.request_id = (SELECT id FROM transfer_request WHERE created_at = '2025-03-04 08:00:00+00' LIMIT 1)
);

-- [PER-2] Caolin → Azulejo | APROBADO + DE CAMINO | Valentina Cruz
INSERT INTO "transfer_request" ("from_camp_id", "to_camp_id", "request_status", "transfer_status",
    "departure_date", "authorized_by", "is_resource_transfer", "created_at")
VALUES (
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    (SELECT id FROM camp WHERE name = 'Campamento Azulejo' LIMIT 1),
    'APROBADO', 'DE CAMINO', '2025-04-12', 'admin_caolin', FALSE,
    '2025-04-11 10:00:00+00'
);

INSERT INTO "transfer_participants" ("person_id", "request_id", "is_transfer_active")
SELECT (SELECT id FROM person WHERE id_card = 'TEST-SEED-004' LIMIT 1),
    (SELECT id FROM transfer_request WHERE created_at = '2025-04-11 10:00:00+00' LIMIT 1),
    TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM "transfer_participants" tp
    WHERE tp.person_id = (SELECT id FROM person WHERE id_card = 'TEST-SEED-004' LIMIT 1)
      AND tp.request_id = (SELECT id FROM transfer_request WHERE created_at = '2025-04-11 10:00:00+00' LIMIT 1)
);

-- [PER-3] Fayenza → Caolin | PENDIENTE | solicitud de refuerzo médico
INSERT INTO "transfer_request" ("from_camp_id", "to_camp_id", "request_status",
    "departure_date", "is_resource_transfer", "created_at")
VALUES (
    (SELECT id FROM camp WHERE name = 'Campamento Fayenza' LIMIT 1),
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    'PENDIENTE', '2025-04-20', FALSE,
    '2025-04-19 09:00:00+00'
);

-- [PER-4] Azulejo → Caolin | RECHAZADO | sin capacidad disponible
INSERT INTO "transfer_request" ("from_camp_id", "to_camp_id", "request_status",
    "departure_date", "authorized_by", "is_resource_transfer", "created_at")
VALUES (
    (SELECT id FROM camp WHERE name = 'Campamento Azulejo' LIMIT 1),
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    'RECHAZADO', '2025-04-05', 'admin_azulejo', FALSE,
    '2025-04-04 11:00:00+00'
);
