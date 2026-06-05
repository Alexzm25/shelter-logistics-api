-- =============================================================
-- SEED: Usuarios y personas (admin + trabajadores + roles faltantes)
-- Campamento: Campamento Caolinaa
-- =============================================================

-- -------------------------------------------------------------
-- 1. Persona y usuario administrador
-- -------------------------------------------------------------
INSERT INTO "person" (
    "name", "last_name", "age", "background_info", "weight", "height",
    "camp_id", "current_status", "health_status", "camp_entry_date",
    "photo_url", "is_active", "id_card"
)
SELECT 'Admin', 'Sistema', 35,
    'Fundador y administrador principal del campamento. Sobreviviente desde el dia 1 del apocalipsis.',
    75.00, 1.75,
    (SELECT "id" FROM "camp" WHERE "name" = 'Campamento Caolin' LIMIT 1),
    'TRABAJANDO', 'SANO', NOW(),
    'uploads/default_admin.jpg', TRUE, 'ADMIN-001'
WHERE NOT EXISTS (SELECT 1 FROM "person" WHERE "id_card" = 'ADMIN-001');

INSERT INTO "app_user" ("username", "password_hash", "person_id", "role_id")
SELECT 'adminCaolin',
    '$2b$12$mKZBL.5MaP/PJa7y1CcyqO0.BuDOFIIfX2czeSoX7zn1QBfe1iFvm',
    (SELECT "id" FROM "person" WHERE "id_card" = 'ADMIN-001' LIMIT 1),
    (SELECT "id" FROM "role" WHERE "name" = 'ADMINISTRADOR SISTEMA' LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM "app_user" WHERE "username" = 'adminCaolin');

-- -------------------------------------------------------------
-- 2. Personas TRABAJADOR con profesiones distintas
-- -------------------------------------------------------------
INSERT INTO "person" (
    "name", "last_name", "age", "background_info",
    "weight", "height", "camp_id",
    "current_status", "health_status",
    "camp_entry_date", "photo_url", "is_active", "id_card"
)
SELECT 'Carlos', 'Mendoza', 34,
    'Explorador experimentado que sobrevivio cruzando zonas contaminadas durante meses.',
    75.50, 1.78,
    (SELECT "id" FROM "camp" WHERE "name" = 'Campamento Caolin' LIMIT 1),
    'LIBRE', 'SANO',
    NOW(), '/photos/carlos_mendoza.jpg', TRUE, 'ID-EXPLORADOR-001'
WHERE NOT EXISTS (SELECT 1 FROM "person" WHERE "id_card" = 'ID-EXPLORADOR-001');

INSERT INTO "person" (
    "name", "last_name", "age", "background_info",
    "weight", "height", "camp_id",
    "current_status", "health_status",
    "camp_entry_date", "photo_url", "is_active", "id_card"
)
SELECT 'Lucia', 'Ramirez', 28,
    'Agricultora que mantuvo vivos a su comunidad cultivando en condiciones extremas.',
    62.30, 1.65,
    (SELECT "id" FROM "camp" WHERE "name" = 'Campamento Caolin' LIMIT 1),
    'LIBRE', 'SANO',
    NOW(), '/photos/lucia_ramirez.jpg', TRUE, 'ID-AGRICULTORA-002'
WHERE NOT EXISTS (SELECT 1 FROM "person" WHERE "id_card" = 'ID-AGRICULTORA-002');

INSERT INTO "person" (
    "name", "last_name", "age", "background_info",
    "weight", "height", "camp_id",
    "current_status", "health_status",
    "camp_entry_date", "photo_url", "is_active", "id_card"
)
SELECT 'Andres', 'Torres', 41,
    'Medico de campo que atendio heridos durante el colapso de las ciudades.',
    80.10, 1.82,
    (SELECT "id" FROM "camp" WHERE "name" = 'Campamento Caolin' LIMIT 1),
    'LIBRE', 'SANO',
    NOW(), '/photos/andres_torres.jpg', TRUE, 'ID-MEDICO-003'
WHERE NOT EXISTS (SELECT 1 FROM "person" WHERE "id_card" = 'ID-MEDICO-003');

-- -------------------------------------------------------------
-- 3. Usuarios de login para cada persona TRABAJADOR
--    password_hash corresponde a 'caolin123'
-- -------------------------------------------------------------
INSERT INTO "app_user" ("username", "password_hash", "person_id", "role_id")
SELECT 'carlos.explorador',
    '$2b$12$p9RxFJK2P81vrMuKPl8UZOWessPa3ovxyOTC/snmIxGCyqDHKLR8m',
    (SELECT "id" FROM "person" WHERE "id_card" = 'ID-EXPLORADOR-001' LIMIT 1),
    (SELECT "id" FROM "role" WHERE "name" = 'TRABAJADOR' LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM "app_user" WHERE "username" = 'carlos.explorador');

INSERT INTO "app_user" ("username", "password_hash", "person_id", "role_id")
SELECT 'lucia.agricultora',
    '$2b$12$p9RxFJK2P81vrMuKPl8UZOWessPa3ovxyOTC/snmIxGCyqDHKLR8m',
    (SELECT "id" FROM "person" WHERE "id_card" = 'ID-AGRICULTORA-002' LIMIT 1),
    (SELECT "id" FROM "role" WHERE "name" = 'TRABAJADOR' LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM "app_user" WHERE "username" = 'lucia.agricultora');

INSERT INTO "app_user" ("username", "password_hash", "person_id", "role_id")
SELECT 'andres.medico',
    '$2b$12$p9RxFJK2P81vrMuKPl8UZOWessPa3ovxyOTC/snmIxGCyqDHKLR8m',
    (SELECT "id" FROM "person" WHERE "id_card" = 'ID-MEDICO-003' LIMIT 1),
    (SELECT "id" FROM "role" WHERE "name" = 'TRABAJADOR' LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM "app_user" WHERE "username" = 'andres.medico');

-- -------------------------------------------------------------
-- 4. Asignar profesion a cada persona via profession_assignment
--    is_main_profession = TRUE, is_active = TRUE
-- -------------------------------------------------------------

-- Carlos -> EXPLORADOR
INSERT INTO "profession_assignment" (
    "start_date", "end_date", "reason",
    "is_main_profession", "profession_id", "person_id", "is_active"
)
SELECT CURRENT_DATE, NULL,
    'Asignado como explorador principal del campamento.',
    TRUE,
    (SELECT "id" FROM "profession" WHERE "name" = 'EXPLORADOR' LIMIT 1),
    (SELECT "id" FROM "person" WHERE "id_card" = 'ID-EXPLORADOR-001' LIMIT 1),
    TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM "profession_assignment"
    WHERE person_id = (SELECT "id" FROM "person" WHERE "id_card" = 'ID-EXPLORADOR-001' LIMIT 1)
    AND is_active = TRUE
);

-- Lucia -> AGRICULTOR
INSERT INTO "profession_assignment" (
    "start_date", "end_date", "reason",
    "is_main_profession", "profession_id", "person_id", "is_active"
)
SELECT CURRENT_DATE, NULL,
    'Asignada como agricultora principal del campamento.',
    TRUE,
    (SELECT "id" FROM "profession" WHERE "name" = 'AGRICULTOR' LIMIT 1),
    (SELECT "id" FROM "person" WHERE "id_card" = 'ID-AGRICULTORA-002' LIMIT 1),
    TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM "profession_assignment"
    WHERE person_id = (SELECT "id" FROM "person" WHERE "id_card" = 'ID-AGRICULTORA-002' LIMIT 1)
    AND is_active = TRUE
);

-- Andres -> MEDICO
INSERT INTO "profession_assignment" (
    "start_date", "end_date", "reason",
    "is_main_profession", "profession_id", "person_id", "is_active"
)
SELECT CURRENT_DATE, NULL,
    'Asignado como medico principal del campamento.',
    TRUE,
    (SELECT "id" FROM "profession" WHERE "name" = 'MEDICO' LIMIT 1),
    (SELECT "id" FROM "person" WHERE "id_card" = 'ID-MEDICO-003' LIMIT 1),
    TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM "profession_assignment"
    WHERE person_id = (SELECT "id" FROM "person" WHERE "id_card" = 'ID-MEDICO-003' LIMIT 1)
    AND is_active = TRUE
);

-- -------------------------------------------------------------
-- 5. Personas para roles faltantes
-- -------------------------------------------------------------
INSERT INTO "person" (
    "name", "last_name", "age", "background_info", "weight", "height",
    "camp_id", "current_status", "health_status", "camp_entry_date",
    "photo_url", "is_active", "id_card"
)
SELECT 'Rosa', 'Ibarra', 39,
    'Encargada de logistica y control de recursos del campamento.',
    63.20, 1.66,
    (SELECT "id" FROM "camp" WHERE "name" = 'Campamento Caolin' LIMIT 1),
    'TRABAJANDO', 'SANO', NOW(),
    '/photos/rosa_ibarra.jpg', TRUE, 'ID-RECURSOS-CAOLIN-001'
WHERE NOT EXISTS (SELECT 1 FROM "person" WHERE "id_card" = 'ID-RECURSOS-CAOLIN-001');

INSERT INTO "person" (
    "name", "last_name", "age", "background_info", "weight", "height",
    "camp_id", "current_status", "health_status", "camp_entry_date",
    "photo_url", "is_active", "id_card"
)
SELECT 'Miguel', 'Soto', 33,
    'Coordinador de viajes y comunicaciones con otros campamentos.',
    71.40, 1.74,
    (SELECT "id" FROM "camp" WHERE "name" = 'Campamento Caolin' LIMIT 1),
    'TRABAJANDO', 'SANO', NOW(),
    '/photos/miguel_soto.jpg', TRUE, 'ID-VIAJES-CAOLIN-002'
WHERE NOT EXISTS (SELECT 1 FROM "person" WHERE "id_card" = 'ID-VIAJES-CAOLIN-002');

-- -------------------------------------------------------------
-- 6. Usuarios de login para roles faltantes
-- -------------------------------------------------------------
INSERT INTO "app_user" ("username", "password_hash", "person_id", "role_id")
SELECT 'rosa.recursos',
    '$2b$12$p9RxFJK2P81vrMuKPl8UZOWessPa3ovxyOTC/snmIxGCyqDHKLR8m',
    (SELECT "id" FROM "person" WHERE "id_card" = 'ID-RECURSOS-CAOLIN-001' LIMIT 1),
    (SELECT "id" FROM "role" WHERE "name" = 'GESTIÓN RECURSOS' LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM "app_user" WHERE "username" = 'rosa.recursos');

INSERT INTO "app_user" ("username", "password_hash", "person_id", "role_id")
SELECT 'miguel.viajes',
    '$2b$12$p9RxFJK2P81vrMuKPl8UZOWessPa3ovxyOTC/snmIxGCyqDHKLR8m',
    (SELECT "id" FROM "person" WHERE "id_card" = 'ID-VIAJES-CAOLIN-002' LIMIT 1),
    (SELECT "id" FROM "role" WHERE "name" = 'ENCARGADO VIAJES Y COMUNICACIÓN' LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM "app_user" WHERE "username" = 'miguel.viajes');
