-- =============================================================
-- SEED: Usuarios y personas (un usuario por rol)
-- Campamento: Campamento Azulejo
-- =============================================================

-- -------------------------------------------------------------
-- 1. Administrador
-- -------------------------------------------------------------
INSERT INTO "person" (
    "name", "last_name", "birth_date", "background_info", "weight", "height",
    "camp_id", "current_status", "health_status", "camp_entry_date",
    "photo_url", "is_active", "id_card"
)
SELECT 'Sofia', 'Vargas', '1988-03-14',
    'Administradora del campamento desde su fundacion. Ex coordinadora de emergencias civiles.',
    65.00, 1.68,
    (SELECT "id" FROM "camp" WHERE "name" = 'Campamento Azulejo' LIMIT 1),
    'TRABAJANDO', 'SANO', NOW(),
    'uploads/default_admin.jpg', TRUE, 'ADMIN-AZU-001'
WHERE NOT EXISTS (SELECT 1 FROM "person" WHERE "id_card" = 'ADMIN-AZU-001');

INSERT INTO "app_user" ("username", "password_hash", "person_id", "role_id")
SELECT 'adminAzulejo',
    '$2b$12$6vt60gbOIeCBSjt2V/FA9.EJe8Zfc7KZD8QMSFzPEO.GKd1SfhMxC',
    (SELECT "id" FROM "person" WHERE "id_card" = 'ADMIN-AZU-001' LIMIT 1),
    (SELECT "id" FROM "role" WHERE "name" = 'ADMINISTRADOR SISTEMA' LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM "app_user" WHERE "username" = 'adminAzulejo');

-- -------------------------------------------------------------
-- 2. Trabajador (profesion: MEDICO)
-- -------------------------------------------------------------
INSERT INTO "person" (
    "name", "last_name", "birth_date", "background_info", "weight", "height",
    "camp_id", "current_status", "health_status", "camp_entry_date",
    "photo_url", "is_active", "id_card"
)
SELECT 'Diego', 'Mora', '1994-09-22',
    'Medico de urgencias que llego al campamento tras cruzar la zona norte infectada.',
    78.00, 1.80,
    (SELECT "id" FROM "camp" WHERE "name" = 'Campamento Azulejo' LIMIT 1),
    'TRABAJANDO', 'SANO', NOW(),
    'uploads/default_worker.jpg', TRUE, 'ID-MEDICO-AZU-001'
WHERE NOT EXISTS (SELECT 1 FROM "person" WHERE "id_card" = 'ID-MEDICO-AZU-001');

INSERT INTO "app_user" ("username", "password_hash", "person_id", "role_id")
SELECT 'medico.azulejo',
    '$2b$12$6vt60gbOIeCBSjt2V/FA9.EJe8Zfc7KZD8QMSFzPEO.GKd1SfhMxC',
    (SELECT "id" FROM "person" WHERE "id_card" = 'ID-MEDICO-AZU-001' LIMIT 1),
    (SELECT "id" FROM "role" WHERE "name" = 'TRABAJADOR' LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM "app_user" WHERE "username" = 'medico.azulejo');

INSERT INTO "profession_assignment" (
    "start_date", "end_date", "reason",
    "is_main_profession", "profession_id", "person_id", "is_active"
)
SELECT CURRENT_DATE, NULL,
    'Asignado como medico principal del campamento.',
    TRUE,
    (SELECT "id" FROM "profession" WHERE "name" = 'MEDICO' LIMIT 1),
    (SELECT "id" FROM "person" WHERE "id_card" = 'ID-MEDICO-AZU-001' LIMIT 1),
    TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM "profession_assignment"
    WHERE person_id = (SELECT "id" FROM "person" WHERE "id_card" = 'ID-MEDICO-AZU-001' LIMIT 1)
    AND is_active = TRUE
);

-- -------------------------------------------------------------
-- 3. Gestion de Recursos
-- -------------------------------------------------------------
INSERT INTO "person" (
    "name", "last_name", "birth_date", "background_info", "weight", "height",
    "camp_id", "current_status", "health_status", "camp_entry_date",
    "photo_url", "is_active", "id_card"
)
SELECT 'Elena', 'Quesada', '1990-07-05',
    'Logistica y almacen. Mantuvo el inventario del campamento durante los primeros meses del apocalipsis.',
    60.50, 1.63,
    (SELECT "id" FROM "camp" WHERE "name" = 'Campamento Azulejo' LIMIT 1),
    'TRABAJANDO', 'SANO', NOW(),
    'uploads/default_worker.jpg', TRUE, 'ID-RECURSOS-AZU-001'
WHERE NOT EXISTS (SELECT 1 FROM "person" WHERE "id_card" = 'ID-RECURSOS-AZU-001');

INSERT INTO "app_user" ("username", "password_hash", "person_id", "role_id")
SELECT 'recursos.azulejo',
    '$2b$12$6vt60gbOIeCBSjt2V/FA9.EJe8Zfc7KZD8QMSFzPEO.GKd1SfhMxC',
    (SELECT "id" FROM "person" WHERE "id_card" = 'ID-RECURSOS-AZU-001' LIMIT 1),
    (SELECT "id" FROM "role" WHERE "name" = 'GESTIÓN RECURSOS' LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM "app_user" WHERE "username" = 'recursos.azulejo');

-- -------------------------------------------------------------
-- 4. Encargado Viajes y Comunicacion
-- -------------------------------------------------------------
INSERT INTO "person" (
    "name", "last_name", "birth_date", "background_info", "weight", "height",
    "camp_id", "current_status", "health_status", "camp_entry_date",
    "photo_url", "is_active", "id_card"
)
SELECT 'Tomas', 'Alvarado', '1986-11-30',
    'Explorador veterano y negociador entre campamentos. Conoce las rutas seguras del bosque Azulejo.',
    82.00, 1.83,
    (SELECT "id" FROM "camp" WHERE "name" = 'Campamento Azulejo' LIMIT 1),
    'TRABAJANDO', 'SANO', NOW(),
    'uploads/default_worker.jpg', TRUE, 'ID-VIAJES-AZU-001'
WHERE NOT EXISTS (SELECT 1 FROM "person" WHERE "id_card" = 'ID-VIAJES-AZU-001');

INSERT INTO "app_user" ("username", "password_hash", "person_id", "role_id")
SELECT 'viajes.azulejo',
    '$2b$12$6vt60gbOIeCBSjt2V/FA9.EJe8Zfc7KZD8QMSFzPEO.GKd1SfhMxC',
    (SELECT "id" FROM "person" WHERE "id_card" = 'ID-VIAJES-AZU-001' LIMIT 1),
    (SELECT "id" FROM "role" WHERE "name" = 'ENCARGADO VIAJES Y COMUNICACIÓN' LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM "app_user" WHERE "username" = 'viajes.azulejo');

-- -------------------------------------------------------------
-- 5. Inventario: recursos faltantes en Campamento Azulejo
--    (Agua, Arroz, Frijoles, Semillas ya existen en 06_InventorySeed.sql)
-- -------------------------------------------------------------
INSERT INTO "inventory_resource" ("quantity", "minimum_stock_level", "inventory_id", "resource_id")
SELECT 30, 10, inv.id, r.id
FROM "resource" r, "inventory" inv
JOIN "camp" c ON c.id = inv.camp_id
WHERE c."name" = 'Campamento Azulejo' AND r."name" = 'Botiquín Básico'
AND NOT EXISTS (
    SELECT 1 FROM "inventory_resource" ir WHERE ir.inventory_id = inv.id AND ir.resource_id = r.id
);

INSERT INTO "inventory_resource" ("quantity", "minimum_stock_level", "inventory_id", "resource_id")
SELECT 20, 8, inv.id, r.id
FROM "resource" r, "inventory" inv
JOIN "camp" c ON c.id = inv.camp_id
WHERE c."name" = 'Campamento Azulejo' AND r."name" = 'Antibióticos'
AND NOT EXISTS (
    SELECT 1 FROM "inventory_resource" ir WHERE ir.inventory_id = inv.id AND ir.resource_id = r.id
);
