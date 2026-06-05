-- =========================================================
-- INVENTORY SEED
-- =========================================================

-- Recursos base
INSERT INTO "resource" ("name", "category")
SELECT 'Agua Embotellada', 'BEBIDAS'
WHERE NOT EXISTS (SELECT 1 FROM "resource" WHERE "name" = 'Agua Embotellada');

INSERT INTO "resource" ("name", "category")
SELECT 'Latas de Frijoles', 'ALIMENTO'
WHERE NOT EXISTS (SELECT 1 FROM "resource" WHERE "name" = 'Latas de Frijoles');

INSERT INTO "resource" ("name", "category")
SELECT 'Arroz', 'ALIMENTO'
WHERE NOT EXISTS (SELECT 1 FROM "resource" WHERE "name" = 'Arroz');

INSERT INTO "resource" ("name", "category")
SELECT 'Semillas de Maíz', 'SEMILLAS'
WHERE NOT EXISTS (SELECT 1 FROM "resource" WHERE "name" = 'Semillas de Maíz');

INSERT INTO "resource" ("name", "category")
SELECT 'Semillas de Papa', 'SEMILLAS'
WHERE NOT EXISTS (SELECT 1 FROM "resource" WHERE "name" = 'Semillas de Papa');

INSERT INTO "resource" ("name", "category")
SELECT 'Botiquín Básico', 'MEDICINAS'
WHERE NOT EXISTS (SELECT 1 FROM "resource" WHERE "name" = 'Botiquín Básico');

INSERT INTO "resource" ("name", "category")
SELECT 'Antibióticos', 'MEDICINAS'
WHERE NOT EXISTS (SELECT 1 FROM "resource" WHERE "name" = 'Antibióticos');

INSERT INTO "resource" ("name", "category")
SELECT 'Vendajes', 'MEDICINAS'
WHERE NOT EXISTS (SELECT 1 FROM "resource" WHERE "name" = 'Vendajes');

-- Inventario del campamento base
INSERT INTO "inventory" ("maximum_stock", "camp_id")
SELECT 1000, c."id"
FROM "camp" c
WHERE c."name" = 'Campamento Caolin'
AND NOT EXISTS (
    SELECT 1 FROM "inventory" i WHERE i.camp_id = c."id"
)
LIMIT 1;

-- Recursos dentro del inventario
INSERT INTO "inventory_resource" ("quantity", "minimum_stock_level", "inventory_id", "resource_id")
SELECT 200, 50, inv.id, r.id
FROM "resource" r, "inventory" inv
JOIN "camp" c ON c.id = inv.camp_id
WHERE c."name" = 'Campamento Caolin' AND r."name" = 'Agua Embotellada'
AND NOT EXISTS (
    SELECT 1 FROM "inventory_resource" ir WHERE ir.inventory_id = inv.id AND ir.resource_id = r.id
);

INSERT INTO "inventory_resource" ("quantity", "minimum_stock_level", "inventory_id", "resource_id")
SELECT 120, 30, inv.id, r.id
FROM "resource" r, "inventory" inv
JOIN "camp" c ON c.id = inv.camp_id
WHERE c."name" = 'Campamento Caolin' AND r."name" = 'Latas de Frijoles'
AND NOT EXISTS (
    SELECT 1 FROM "inventory_resource" ir WHERE ir.inventory_id = inv.id AND ir.resource_id = r.id
);

INSERT INTO "inventory_resource" ("quantity", "minimum_stock_level", "inventory_id", "resource_id")
SELECT 180, 40, inv.id, r.id
FROM "resource" r, "inventory" inv
JOIN "camp" c ON c.id = inv.camp_id
WHERE c."name" = 'Campamento Caolin' AND r."name" = 'Arroz'
AND NOT EXISTS (
    SELECT 1 FROM "inventory_resource" ir WHERE ir.inventory_id = inv.id AND ir.resource_id = r.id
);

INSERT INTO "inventory_resource" ("quantity", "minimum_stock_level", "inventory_id", "resource_id")
SELECT 90, 20, inv.id, r.id
FROM "resource" r, "inventory" inv
JOIN "camp" c ON c.id = inv.camp_id
WHERE c."name" = 'Campamento Caolin' AND r."name" = 'Semillas de Maíz'
AND NOT EXISTS (
    SELECT 1 FROM "inventory_resource" ir WHERE ir.inventory_id = inv.id AND ir.resource_id = r.id
);

INSERT INTO "inventory_resource" ("quantity", "minimum_stock_level", "inventory_id", "resource_id")
SELECT 70, 20, inv.id, r.id
FROM "resource" r, "inventory" inv
JOIN "camp" c ON c.id = inv.camp_id
WHERE c."name" = 'Campamento Caolin' AND r."name" = 'Semillas de Papa'
AND NOT EXISTS (
    SELECT 1 FROM "inventory_resource" ir WHERE ir.inventory_id = inv.id AND ir.resource_id = r.id
);

INSERT INTO "inventory_resource" ("quantity", "minimum_stock_level", "inventory_id", "resource_id")
SELECT 40, 10, inv.id, r.id
FROM "resource" r, "inventory" inv
JOIN "camp" c ON c.id = inv.camp_id
WHERE c."name" = 'Campamento Caolin' AND r."name" = 'Botiquín Básico'
AND NOT EXISTS (
    SELECT 1 FROM "inventory_resource" ir WHERE ir.inventory_id = inv.id AND ir.resource_id = r.id
);

INSERT INTO "inventory_resource" ("quantity", "minimum_stock_level", "inventory_id", "resource_id")
SELECT 35, 10, inv.id, r.id
FROM "resource" r, "inventory" inv
JOIN "camp" c ON c.id = inv.camp_id
WHERE c."name" = 'Campamento Caolin' AND r."name" = 'Antibióticos'
AND NOT EXISTS (
    SELECT 1 FROM "inventory_resource" ir WHERE ir.inventory_id = inv.id AND ir.resource_id = r.id
);

INSERT INTO "inventory_resource" ("quantity", "minimum_stock_level", "inventory_id", "resource_id")
SELECT 100, 20, inv.id, r.id
FROM "resource" r, "inventory" inv
JOIN "camp" c ON c.id = inv.camp_id
WHERE c."name" = 'Campamento Caolin' AND r."name" = 'Vendajes'
AND NOT EXISTS (
    SELECT 1 FROM "inventory_resource" ir WHERE ir.inventory_id = inv.id AND ir.resource_id = r.id
);

-- Producción por profesión
INSERT INTO "profession_production" ("production_quantity", "resource_id", "profession_id")
SELECT 25, r.id, p.id
FROM "resource" r, "profession" p
WHERE r."name" = 'Latas de Frijoles' AND p."name" = 'AGRICULTOR'
AND NOT EXISTS (
    SELECT 1 FROM "profession_production" pp WHERE pp.resource_id = r.id AND pp.profession_id = p.id
);

INSERT INTO "profession_production" ("production_quantity", "resource_id", "profession_id")
SELECT 30, r.id, p.id
FROM "resource" r, "profession" p
WHERE r."name" = 'Arroz' AND p."name" = 'AGRICULTOR'
AND NOT EXISTS (
    SELECT 1 FROM "profession_production" pp WHERE pp.resource_id = r.id AND pp.profession_id = p.id
);

INSERT INTO "profession_production" ("production_quantity", "resource_id", "profession_id")
SELECT 15, r.id, p.id
FROM "resource" r, "profession" p
WHERE r."name" = 'Semillas de Maíz' AND p."name" = 'AGRICULTOR'
AND NOT EXISTS (
    SELECT 1 FROM "profession_production" pp WHERE pp.resource_id = r.id AND pp.profession_id = p.id
);

INSERT INTO "profession_production" ("production_quantity", "resource_id", "profession_id")
SELECT 15, r.id, p.id
FROM "resource" r, "profession" p
WHERE r."name" = 'Semillas de Papa' AND p."name" = 'AGRICULTOR'
AND NOT EXISTS (
    SELECT 1 FROM "profession_production" pp WHERE pp.resource_id = r.id AND pp.profession_id = p.id
);

INSERT INTO "profession_production" ("production_quantity", "resource_id", "profession_id")
SELECT 10, r.id, p.id
FROM "resource" r, "profession" p
WHERE r."name" = 'Botiquín Básico' AND p."name" = 'MEDICO'
AND NOT EXISTS (
    SELECT 1 FROM "profession_production" pp WHERE pp.resource_id = r.id AND pp.profession_id = p.id
);

INSERT INTO "profession_production" ("production_quantity", "resource_id", "profession_id")
SELECT 8, r.id, p.id
FROM "resource" r, "profession" p
WHERE r."name" = 'Antibióticos' AND p."name" = 'MEDICO'
AND NOT EXISTS (
    SELECT 1 FROM "profession_production" pp WHERE pp.resource_id = r.id AND pp.profession_id = p.id
);

INSERT INTO "profession_production" ("production_quantity", "resource_id", "profession_id")
SELECT 20, r.id, p.id
FROM "resource" r, "profession" p
WHERE r."name" = 'Vendajes' AND p."name" = 'MEDICO'
AND NOT EXISTS (
    SELECT 1 FROM "profession_production" pp WHERE pp.resource_id = r.id AND pp.profession_id = p.id
);

-- Inventario del campamento Azulejo
INSERT INTO "inventory" ("maximum_stock", "camp_id")
SELECT 1000, c."id"
FROM "camp" c
WHERE c."name" = 'Campamento Azulejo'
AND NOT EXISTS (
    SELECT 1 FROM "inventory" i WHERE i.camp_id = c."id"
)
LIMIT 1;

INSERT INTO "inventory_resource" ("quantity", "minimum_stock_level", "inventory_id", "resource_id")
SELECT 100, 30, inv.id, r.id
FROM "resource" r, "inventory" inv
JOIN "camp" c ON c.id = inv.camp_id
WHERE c."name" = 'Campamento Azulejo' AND r."name" = 'Agua Embotellada'
AND NOT EXISTS (
    SELECT 1 FROM "inventory_resource" ir WHERE ir.inventory_id = inv.id AND ir.resource_id = r.id
);

INSERT INTO "inventory_resource" ("quantity", "minimum_stock_level", "inventory_id", "resource_id")
SELECT 60, 20, inv.id, r.id
FROM "resource" r, "inventory" inv
JOIN "camp" c ON c.id = inv.camp_id
WHERE c."name" = 'Campamento Azulejo' AND r."name" = 'Arroz'
AND NOT EXISTS (
    SELECT 1 FROM "inventory_resource" ir WHERE ir.inventory_id = inv.id AND ir.resource_id = r.id
);

INSERT INTO "inventory_resource" ("quantity", "minimum_stock_level", "inventory_id", "resource_id")
SELECT 50, 15, inv.id, r.id
FROM "resource" r, "inventory" inv
JOIN "camp" c ON c.id = inv.camp_id
WHERE c."name" = 'Campamento Azulejo' AND r."name" = 'Latas de Frijoles'
AND NOT EXISTS (
    SELECT 1 FROM "inventory_resource" ir WHERE ir.inventory_id = inv.id AND ir.resource_id = r.id
);

INSERT INTO "inventory_resource" ("quantity", "minimum_stock_level", "inventory_id", "resource_id")
SELECT 120, 30, inv.id, r.id
FROM "resource" r, "inventory" inv
JOIN "camp" c ON c.id = inv.camp_id
WHERE c."name" = 'Campamento Azulejo' AND r."name" = 'Semillas de Maíz'
AND NOT EXISTS (
    SELECT 1 FROM "inventory_resource" ir WHERE ir.inventory_id = inv.id AND ir.resource_id = r.id
);

INSERT INTO "inventory_resource" ("quantity", "minimum_stock_level", "inventory_id", "resource_id")
SELECT 80, 20, inv.id, r.id
FROM "resource" r, "inventory" inv
JOIN "camp" c ON c.id = inv.camp_id
WHERE c."name" = 'Campamento Azulejo' AND r."name" = 'Semillas de Papa'
AND NOT EXISTS (
    SELECT 1 FROM "inventory_resource" ir WHERE ir.inventory_id = inv.id AND ir.resource_id = r.id
);

INSERT INTO "inventory_resource" ("quantity", "minimum_stock_level", "inventory_id", "resource_id")
SELECT 25, 10, inv.id, r.id
FROM "resource" r, "inventory" inv
JOIN "camp" c ON c.id = inv.camp_id
WHERE c."name" = 'Campamento Azulejo' AND r."name" = 'Vendajes'
AND NOT EXISTS (
    SELECT 1 FROM "inventory_resource" ir WHERE ir.inventory_id = inv.id AND ir.resource_id = r.id
);

-- Inventario del campamento Fayenza
INSERT INTO "inventory" ("maximum_stock", "camp_id")
SELECT 1000, c."id"
FROM "camp" c
WHERE c."name" = 'Campamento Fayenza'
AND NOT EXISTS (
    SELECT 1 FROM "inventory" i WHERE i.camp_id = c."id"
)
LIMIT 1;

INSERT INTO "inventory_resource" ("quantity", "minimum_stock_level", "inventory_id", "resource_id")
SELECT 150, 40, inv.id, r.id
FROM "resource" r, "inventory" inv
JOIN "camp" c ON c.id = inv.camp_id
WHERE c."name" = 'Campamento Fayenza' AND r."name" = 'Agua Embotellada'
AND NOT EXISTS (
    SELECT 1 FROM "inventory_resource" ir WHERE ir.inventory_id = inv.id AND ir.resource_id = r.id
);

INSERT INTO "inventory_resource" ("quantity", "minimum_stock_level", "inventory_id", "resource_id")
SELECT 80, 20, inv.id, r.id
FROM "resource" r, "inventory" inv
JOIN "camp" c ON c.id = inv.camp_id
WHERE c."name" = 'Campamento Fayenza' AND r."name" = 'Latas de Frijoles'
AND NOT EXISTS (
    SELECT 1 FROM "inventory_resource" ir WHERE ir.inventory_id = inv.id AND ir.resource_id = r.id
);

INSERT INTO "inventory_resource" ("quantity", "minimum_stock_level", "inventory_id", "resource_id")
SELECT 200, 50, inv.id, r.id
FROM "resource" r, "inventory" inv
JOIN "camp" c ON c.id = inv.camp_id
WHERE c."name" = 'Campamento Fayenza' AND r."name" = 'Arroz'
AND NOT EXISTS (
    SELECT 1 FROM "inventory_resource" ir WHERE ir.inventory_id = inv.id AND ir.resource_id = r.id
);

INSERT INTO "inventory_resource" ("quantity", "minimum_stock_level", "inventory_id", "resource_id")
SELECT 60, 15, inv.id, r.id
FROM "resource" r, "inventory" inv
JOIN "camp" c ON c.id = inv.camp_id
WHERE c."name" = 'Campamento Fayenza' AND r."name" = 'Semillas de Maíz'
AND NOT EXISTS (
    SELECT 1 FROM "inventory_resource" ir WHERE ir.inventory_id = inv.id AND ir.resource_id = r.id
);

INSERT INTO "inventory_resource" ("quantity", "minimum_stock_level", "inventory_id", "resource_id")
SELECT 45, 15, inv.id, r.id
FROM "resource" r, "inventory" inv
JOIN "camp" c ON c.id = inv.camp_id
WHERE c."name" = 'Campamento Fayenza' AND r."name" = 'Semillas de Papa'
AND NOT EXISTS (
    SELECT 1 FROM "inventory_resource" ir WHERE ir.inventory_id = inv.id AND ir.resource_id = r.id
);

INSERT INTO "inventory_resource" ("quantity", "minimum_stock_level", "inventory_id", "resource_id")
SELECT 20, 8, inv.id, r.id
FROM "resource" r, "inventory" inv
JOIN "camp" c ON c.id = inv.camp_id
WHERE c."name" = 'Campamento Fayenza' AND r."name" = 'Botiquín Básico'
AND NOT EXISTS (
    SELECT 1 FROM "inventory_resource" ir WHERE ir.inventory_id = inv.id AND ir.resource_id = r.id
);

INSERT INTO "inventory_resource" ("quantity", "minimum_stock_level", "inventory_id", "resource_id")
SELECT 12, 5, inv.id, r.id
FROM "resource" r, "inventory" inv
JOIN "camp" c ON c.id = inv.camp_id
WHERE c."name" = 'Campamento Fayenza' AND r."name" = 'Antibióticos'
AND NOT EXISTS (
    SELECT 1 FROM "inventory_resource" ir WHERE ir.inventory_id = inv.id AND ir.resource_id = r.id
);

INSERT INTO "inventory_resource" ("quantity", "minimum_stock_level", "inventory_id", "resource_id")
SELECT 65, 15, inv.id, r.id
FROM "resource" r, "inventory" inv
JOIN "camp" c ON c.id = inv.camp_id
WHERE c."name" = 'Campamento Fayenza' AND r."name" = 'Vendajes'
AND NOT EXISTS (
    SELECT 1 FROM "inventory_resource" ir WHERE ir.inventory_id = inv.id AND ir.resource_id = r.id
);