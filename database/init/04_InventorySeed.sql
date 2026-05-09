-- =========================================================
-- INVENTORY SEED
-- =========================================================

-- Recursos base
INSERT INTO "resource" ("name", "category") VALUES
('Agua Embotellada', 'BEBIDAS'),
('Latas de Frijoles', 'ALIMENTO'),
('Arroz', 'ALIMENTO'),
('Semillas de Maíz', 'SEMILLAS'),
('Semillas de Papa', 'SEMILLAS'),
('Botiquín Básico', 'MEDICINAS'),
('Antibióticos', 'MEDICINAS'),
('Vendajes', 'MEDICINAS');

-- Inventario del campamento 1
INSERT INTO "inventory" ("maximum_stock", "camp_id")
VALUES (5000, 1);

-- Recursos dentro del inventario
INSERT INTO "inventory_resource" (
    "quantity",
    "minimum_stock_level",
    "inventory_id",
    "resource_id"
)
VALUES
(
    200,
    50,
    (SELECT id FROM "inventory" WHERE "camp_id" = 1 LIMIT 1),
    (SELECT id FROM "resource" WHERE "name" = 'Agua Embotellada' LIMIT 1)
),
(
    120,
    30,
    (SELECT id FROM "inventory" WHERE "camp_id" = 1 LIMIT 1),
    (SELECT id FROM "resource" WHERE "name" = 'Latas de Frijoles' LIMIT 1)
),
(
    180,
    40,
    (SELECT id FROM "inventory" WHERE "camp_id" = 1 LIMIT 1),
    (SELECT id FROM "resource" WHERE "name" = 'Arroz' LIMIT 1)
),
(
    90,
    20,
    (SELECT id FROM "inventory" WHERE "camp_id" = 1 LIMIT 1),
    (SELECT id FROM "resource" WHERE "name" = 'Semillas de Maíz' LIMIT 1)
),
(
    70,
    20,
    (SELECT id FROM "inventory" WHERE "camp_id" = 1 LIMIT 1),
    (SELECT id FROM "resource" WHERE "name" = 'Semillas de Papa' LIMIT 1)
),
(
    40,
    10,
    (SELECT id FROM "inventory" WHERE "camp_id" = 1 LIMIT 1),
    (SELECT id FROM "resource" WHERE "name" = 'Botiquín Básico' LIMIT 1)
),
(
    35,
    10,
    (SELECT id FROM "inventory" WHERE "camp_id" = 1 LIMIT 1),
    (SELECT id FROM "resource" WHERE "name" = 'Antibióticos' LIMIT 1)
),
(
    100,
    20,
    (SELECT id FROM "inventory" WHERE "camp_id" = 1 LIMIT 1),
    (SELECT id FROM "resource" WHERE "name" = 'Vendajes' LIMIT 1)
);

-- Producción por profesión
INSERT INTO "profession_production" (
    "production_quantity",
    "resource_id",
    "profession_id"
)
VALUES
(
    25,
    (SELECT id FROM "resource" WHERE "name" = 'Latas de Frijoles' LIMIT 1),
    (SELECT id FROM "profession" WHERE "name" = 'AGRICULTOR' LIMIT 1)
),
(
    30,
    (SELECT id FROM "resource" WHERE "name" = 'Arroz' LIMIT 1),
    (SELECT id FROM "profession" WHERE "name" = 'AGRICULTOR' LIMIT 1)
),
(
    15,
    (SELECT id FROM "resource" WHERE "name" = 'Semillas de Maíz' LIMIT 1),
    (SELECT id FROM "profession" WHERE "name" = 'AGRICULTOR' LIMIT 1)
),
(
    15,
    (SELECT id FROM "resource" WHERE "name" = 'Semillas de Papa' LIMIT 1),
    (SELECT id FROM "profession" WHERE "name" = 'AGRICULTOR' LIMIT 1)
),
(
    10,
    (SELECT id FROM "resource" WHERE "name" = 'Botiquín Básico' LIMIT 1),
    (SELECT id FROM "profession" WHERE "name" = 'MEDICO' LIMIT 1)
),
(
    8,
    (SELECT id FROM "resource" WHERE "name" = 'Antibióticos' LIMIT 1),
    (SELECT id FROM "profession" WHERE "name" = 'MEDICO' LIMIT 1)
),
(
    20,
    (SELECT id FROM "resource" WHERE "name" = 'Vendajes' LIMIT 1),
    (SELECT id FROM "profession" WHERE "name" = 'MEDICO' LIMIT 1)
);