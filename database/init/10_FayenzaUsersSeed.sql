-- =============================================================
-- SEED: Usuarios y personas (admin + trabajadores + roles faltantes)
-- Campamento: Campamento Fayenza
-- Password todos los usuarios: (hash proporcionado)
-- =============================================================

-- -------------------------------------------------------------
-- 1. Persona y usuario administrador
-- -------------------------------------------------------------
INSERT INTO "person" (
    "name", "last_name", "age", "background_info", "weight", "height",
    "camp_id", "current_status", "health_status", "camp_entry_date",
    "photo_url", "is_active", "id_card"
)
SELECT 'Sofia', 'Garriga', 38,
    'Fundadora y administradora principal del campamento. Exfuncionaria municipal que organizo la evacuacion de civiles durante el colapso.',
    67.00, 1.70,
    (SELECT "id" FROM "camp" WHERE "name" = 'Campamento Fayenza' LIMIT 1),
    'TRABAJANDO', 'SANO', NOW(),
    'uploads/default_admin.jpg', TRUE, 'ADMIN-FAYENZA-001'
WHERE NOT EXISTS (SELECT 1 FROM "person" WHERE "id_card" = 'ADMIN-FAYENZA-001');

INSERT INTO "app_user" ("username", "password_hash", "person_id", "role_id")
SELECT 'adminFayenza',
    '$2b$12$ZLQFgwnHQn1uqycbjamvcOISQ/td0K2JQMp.SYnGL6WBDR1tVTy92',
    (SELECT "id" FROM "person" WHERE "id_card" = 'ADMIN-FAYENZA-001' LIMIT 1),
    (SELECT "id" FROM "role" WHERE "name" = 'ADMINISTRADOR SISTEMA' LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM "app_user" WHERE "username" = 'adminFayenza');

-- -------------------------------------------------------------
-- 2. Personas TRABAJADOR con profesiones distintas
-- -------------------------------------------------------------
INSERT INTO "person" (
    "name", "last_name", "age", "background_info",
    "weight", "height", "camp_id",
    "current_status", "health_status",
    "camp_entry_date", "photo_url", "is_active", "id_card"
)
SELECT 'Pablo', 'Romero', 30,
    'Explorador nato que sobrevivio meses en zonas de alta peligrosidad, experto en orientacion y reconocimiento de terreno.',
    78.00, 1.80,
    (SELECT "id" FROM "camp" WHERE "name" = 'Campamento Fayenza' LIMIT 1),
    'LIBRE', 'SANO',
    NOW(), '/photos/pablo_romero.jpg', TRUE, 'ID-EXPLORADOR-FAYENZA-001'
WHERE NOT EXISTS (SELECT 1 FROM "person" WHERE "id_card" = 'ID-EXPLORADOR-FAYENZA-001');

INSERT INTO "person" (
    "name", "last_name", "age", "background_info",
    "weight", "height", "camp_id",
    "current_status", "health_status",
    "camp_entry_date", "photo_url", "is_active", "id_card"
)
SELECT 'Maria', 'Valverde', 26,
    'Agricultora que domina tecnicas de cultivo en suelos degradados y condiciones de escasez extrema.',
    58.50, 1.62,
    (SELECT "id" FROM "camp" WHERE "name" = 'Campamento Fayenza' LIMIT 1),
    'LIBRE', 'SANO',
    NOW(), '/photos/maria_valverde.jpg', TRUE, 'ID-AGRICULTORA-FAYENZA-002'
WHERE NOT EXISTS (SELECT 1 FROM "person" WHERE "id_card" = 'ID-AGRICULTORA-FAYENZA-002');

INSERT INTO "person" (
    "name", "last_name", "age", "background_info",
    "weight", "height", "camp_id",
    "current_status", "health_status",
    "camp_entry_date", "photo_url", "is_active", "id_card"
)
SELECT 'Diego', 'Vargas', 44,
    'Cirujano de urgencias con experiencia en medicina de campo y tratamiento de trauma severo.',
    83.00, 1.85,
    (SELECT "id" FROM "camp" WHERE "name" = 'Campamento Fayenza' LIMIT 1),
    'LIBRE', 'SANO',
    NOW(), '/photos/diego_vargas.jpg', TRUE, 'ID-MEDICO-FAYENZA-003'
WHERE NOT EXISTS (SELECT 1 FROM "person" WHERE "id_card" = 'ID-MEDICO-FAYENZA-003');

-- -------------------------------------------------------------
-- 3. Usuarios de login para cada persona TRABAJADOR
-- -------------------------------------------------------------
INSERT INTO "app_user" ("username", "password_hash", "person_id", "role_id")
SELECT 'pablo.explorador',
    '$2b$12$ZLQFgwnHQn1uqycbjamvcOISQ/td0K2JQMp.SYnGL6WBDR1tVTy92',
    (SELECT "id" FROM "person" WHERE "id_card" = 'ID-EXPLORADOR-FAYENZA-001' LIMIT 1),
    (SELECT "id" FROM "role" WHERE "name" = 'TRABAJADOR' LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM "app_user" WHERE "username" = 'pablo.explorador');

INSERT INTO "app_user" ("username", "password_hash", "person_id", "role_id")
SELECT 'maria.agricultora',
    '$2b$12$ZLQFgwnHQn1uqycbjamvcOISQ/td0K2JQMp.SYnGL6WBDR1tVTy92',
    (SELECT "id" FROM "person" WHERE "id_card" = 'ID-AGRICULTORA-FAYENZA-002' LIMIT 1),
    (SELECT "id" FROM "role" WHERE "name" = 'TRABAJADOR' LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM "app_user" WHERE "username" = 'maria.agricultora');

INSERT INTO "app_user" ("username", "password_hash", "person_id", "role_id")
SELECT 'diego.medico',
    '$2b$12$ZLQFgwnHQn1uqycbjamvcOISQ/td0K2JQMp.SYnGL6WBDR1tVTy92',
    (SELECT "id" FROM "person" WHERE "id_card" = 'ID-MEDICO-FAYENZA-003' LIMIT 1),
    (SELECT "id" FROM "role" WHERE "name" = 'TRABAJADOR' LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM "app_user" WHERE "username" = 'diego.medico');

-- -------------------------------------------------------------
-- 4. Asignar profesion a cada persona via profession_assignment
--    is_main_profession = TRUE, is_active = TRUE
-- -------------------------------------------------------------

-- Pablo -> EXPLORADOR
INSERT INTO "profession_assignment" (
    "start_date", "end_date", "reason",
    "is_main_profession", "profession_id", "person_id", "is_active"
)
VALUES (
    CURRENT_DATE, NULL,
    'Asignado como explorador principal del campamento.',
    TRUE,
    (SELECT "id" FROM "profession" WHERE "name" = 'EXPLORADOR' LIMIT 1),
    (SELECT "id" FROM "person" WHERE "id_card" = 'ID-EXPLORADOR-FAYENZA-001' LIMIT 1),
    TRUE
);

-- Maria -> AGRICULTOR
INSERT INTO "profession_assignment" (
    "start_date", "end_date", "reason",
    "is_main_profession", "profession_id", "person_id", "is_active"
)
VALUES (
    CURRENT_DATE, NULL,
    'Asignada como agricultora principal del campamento.',
    TRUE,
    (SELECT "id" FROM "profession" WHERE "name" = 'AGRICULTOR' LIMIT 1),
    (SELECT "id" FROM "person" WHERE "id_card" = 'ID-AGRICULTORA-FAYENZA-002' LIMIT 1),
    TRUE
);

-- Diego -> MEDICO
INSERT INTO "profession_assignment" (
    "start_date", "end_date", "reason",
    "is_main_profession", "profession_id", "person_id", "is_active"
)
VALUES (
    CURRENT_DATE, NULL,
    'Asignado como medico principal del campamento.',
    TRUE,
    (SELECT "id" FROM "profession" WHERE "name" = 'MEDICO' LIMIT 1),
    (SELECT "id" FROM "person" WHERE "id_card" = 'ID-MEDICO-FAYENZA-003' LIMIT 1),
    TRUE
);

-- -------------------------------------------------------------
-- 5. Personas para roles faltantes
-- -------------------------------------------------------------
INSERT INTO "person" (
    "name", "last_name", "age", "background_info", "weight", "height",
    "camp_id", "current_status", "health_status", "camp_entry_date",
    "photo_url", "is_active", "id_card"
)
SELECT 'Elena', 'Fuentes', 36,
    'Exlogistica de supermercado, responsable del control de inventario y distribucion de recursos del campamento.',
    61.00, 1.67,
    (SELECT "id" FROM "camp" WHERE "name" = 'Campamento Fayenza' LIMIT 1),
    'TRABAJANDO', 'SANO', NOW(),
    '/photos/elena_fuentes.jpg', TRUE, 'ID-RECURSOS-FAYENZA-001'
WHERE NOT EXISTS (SELECT 1 FROM "person" WHERE "id_card" = 'ID-RECURSOS-FAYENZA-001');

INSERT INTO "person" (
    "name", "last_name", "age", "background_info", "weight", "height",
    "camp_id", "current_status", "health_status", "camp_entry_date",
    "photo_url", "is_active", "id_card"
)
SELECT 'Juan', 'Herrera', 31,
    'Exmilitar con experiencia en comunicaciones y coordinacion de operaciones entre bases.',
    74.00, 1.76,
    (SELECT "id" FROM "camp" WHERE "name" = 'Campamento Fayenza' LIMIT 1),
    'TRABAJANDO', 'SANO', NOW(),
    '/photos/juan_herrera.jpg', TRUE, 'ID-VIAJES-FAYENZA-002'
WHERE NOT EXISTS (SELECT 1 FROM "person" WHERE "id_card" = 'ID-VIAJES-FAYENZA-002');

-- -------------------------------------------------------------
-- 6. Usuarios de login para roles faltantes
-- -------------------------------------------------------------
INSERT INTO "app_user" ("username", "password_hash", "person_id", "role_id")
SELECT 'elena.recursos',
    '$2b$12$ZLQFgwnHQn1uqycbjamvcOISQ/td0K2JQMp.SYnGL6WBDR1tVTy92',
    (SELECT "id" FROM "person" WHERE "id_card" = 'ID-RECURSOS-FAYENZA-001' LIMIT 1),
    (SELECT "id" FROM "role" WHERE "name" = 'GESTIÓN RECURSOS' LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM "app_user" WHERE "username" = 'elena.recursos');

INSERT INTO "app_user" ("username", "password_hash", "person_id", "role_id")
SELECT 'juan.viajes',
    '$2b$12$ZLQFgwnHQn1uqycbjamvcOISQ/td0K2JQMp.SYnGL6WBDR1tVTy92',
    (SELECT "id" FROM "person" WHERE "id_card" = 'ID-VIAJES-FAYENZA-002' LIMIT 1),
    (SELECT "id" FROM "role" WHERE "name" = 'ENCARGADO VIAJES Y COMUNICACIÓN' LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM "app_user" WHERE "username" = 'juan.viajes');

