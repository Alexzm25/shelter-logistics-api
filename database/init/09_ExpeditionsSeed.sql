-- =========================================================
-- EXPEDITIONS SEED
-- 18 expediciones para Campamento Caolin (8 COMPLETADA,
-- 4 CANCELADA, 3 EN PROCESO) para probar paginacion.
-- Depende de: 03_CampsSeed.sql, 08_TransfersSeed.sql
-- Idempotente: limpia datos previos del campamento antes de insertar.
-- =========================================================

-- Limpiar datos previos de expediciones de Campamento Caolin
DELETE FROM exploration_loot WHERE exploration_id IN (
  SELECT id FROM exploration WHERE camp_id = (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1)
);
DELETE FROM exploration_member WHERE exploration_id IN (
  SELECT id FROM exploration WHERE camp_id = (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1)
);
DELETE FROM exploration WHERE camp_id = (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1);

-- -------------------------------------------------------
-- EXPEDICIONES COMPLETADAS (con loot y miembros)
-- -------------------------------------------------------

-- [EXP-1] COMPLETADA | ene 2025 | 3 días | equipo de 3
INSERT INTO "exploration" ("start_date", "return_date", "exploration_status", "camp_id",
    "extra_days", "ration_per_person", "max_extra_days", "estimated_days")
VALUES (
    '2025-01-20 07:00:00+00', '2025-01-23 18:00:00+00', 'COMPLETADA',
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    0, 2, 2, 3
);

INSERT INTO "exploration_member" ("person_id", "exploration_id")
VALUES
((SELECT id FROM person WHERE id_card = 'TEST-SEED-001' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-01-20 07:00:00+00' LIMIT 1)),
((SELECT id FROM person WHERE id_card = 'TEST-SEED-004' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-01-20 07:00:00+00' LIMIT 1)),
((SELECT id FROM person WHERE id_card = 'TEST-SEED-005' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-01-20 07:00:00+00' LIMIT 1));

INSERT INTO "exploration_loot" ("quantity", "resource_id", "exploration_id", "is_added_to_inventory")
VALUES
(35, (SELECT id FROM resource WHERE name = 'Agua Embotellada' LIMIT 1),
     (SELECT id FROM exploration WHERE start_date = '2025-01-20 07:00:00+00' LIMIT 1), TRUE),
(20, (SELECT id FROM resource WHERE name = 'Latas de Frijoles' LIMIT 1),
     (SELECT id FROM exploration WHERE start_date = '2025-01-20 07:00:00+00' LIMIT 1), TRUE);

-- [EXP-2] COMPLETADA | feb 2025 | 5 días | equipo de 2
INSERT INTO "exploration" ("start_date", "return_date", "exploration_status", "camp_id",
    "extra_days", "ration_per_person", "max_extra_days", "estimated_days")
VALUES (
    '2025-02-03 06:30:00+00', '2025-02-08 17:00:00+00', 'COMPLETADA',
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    0, 2, 3, 5
);

INSERT INTO "exploration_member" ("person_id", "exploration_id")
VALUES
((SELECT id FROM person WHERE id_card = 'TEST-SEED-001' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-02-03 06:30:00+00' LIMIT 1)),
((SELECT id FROM person WHERE id_card = 'TEST-SEED-005' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-02-03 06:30:00+00' LIMIT 1));

INSERT INTO "exploration_loot" ("quantity", "resource_id", "exploration_id", "is_added_to_inventory")
VALUES
(12, (SELECT id FROM resource WHERE name = 'Botiquín Básico' LIMIT 1),
     (SELECT id FROM exploration WHERE start_date = '2025-02-03 06:30:00+00' LIMIT 1), TRUE),
(8,  (SELECT id FROM resource WHERE name = 'Antibióticos' LIMIT 1),
     (SELECT id FROM exploration WHERE start_date = '2025-02-03 06:30:00+00' LIMIT 1), TRUE),
(15, (SELECT id FROM resource WHERE name = 'Vendajes' LIMIT 1),
     (SELECT id FROM exploration WHERE start_date = '2025-02-03 06:30:00+00' LIMIT 1), TRUE);

-- [EXP-3] COMPLETADA | feb 2025 | 4 días | 1 día extra | equipo de 3
INSERT INTO "exploration" ("start_date", "return_date", "exploration_status", "camp_id",
    "extra_days", "ration_per_person", "max_extra_days", "estimated_days")
VALUES (
    '2025-02-15 08:00:00+00', '2025-02-20 16:00:00+00', 'COMPLETADA',
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    1, 2, 2, 4
);

INSERT INTO "exploration_member" ("person_id", "exploration_id")
VALUES
((SELECT id FROM person WHERE id_card = 'TEST-SEED-001' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-02-15 08:00:00+00' LIMIT 1)),
((SELECT id FROM person WHERE id_card = 'TEST-SEED-004' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-02-15 08:00:00+00' LIMIT 1)),
((SELECT id FROM person WHERE id_card = 'TEST-SEED-005' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-02-15 08:00:00+00' LIMIT 1));

INSERT INTO "exploration_loot" ("quantity", "resource_id", "exploration_id", "is_added_to_inventory")
VALUES
(60, (SELECT id FROM resource WHERE name = 'Agua Embotellada' LIMIT 1),
     (SELECT id FROM exploration WHERE start_date = '2025-02-15 08:00:00+00' LIMIT 1), TRUE),
(25, (SELECT id FROM resource WHERE name = 'Arroz' LIMIT 1),
     (SELECT id FROM exploration WHERE start_date = '2025-02-15 08:00:00+00' LIMIT 1), TRUE);

-- [EXP-4] COMPLETADA | mar 2025 | 6 días | equipo de 2
INSERT INTO "exploration" ("start_date", "return_date", "exploration_status", "camp_id",
    "extra_days", "ration_per_person", "max_extra_days", "estimated_days")
VALUES (
    '2025-03-02 07:00:00+00', '2025-03-08 19:00:00+00', 'COMPLETADA',
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    0, 3, 2, 6
);

INSERT INTO "exploration_member" ("person_id", "exploration_id")
VALUES
((SELECT id FROM person WHERE id_card = 'TEST-SEED-004' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-03-02 07:00:00+00' LIMIT 1)),
((SELECT id FROM person WHERE id_card = 'TEST-SEED-005' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-03-02 07:00:00+00' LIMIT 1));

INSERT INTO "exploration_loot" ("quantity", "resource_id", "exploration_id", "is_added_to_inventory")
VALUES
(40, (SELECT id FROM resource WHERE name = 'Latas de Frijoles' LIMIT 1),
     (SELECT id FROM exploration WHERE start_date = '2025-03-02 07:00:00+00' LIMIT 1), TRUE),
(20, (SELECT id FROM resource WHERE name = 'Semillas de Maíz' LIMIT 1),
     (SELECT id FROM exploration WHERE start_date = '2025-03-02 07:00:00+00' LIMIT 1), TRUE);

-- [EXP-5] COMPLETADA | mar 2025 | 3 días | equipo de 3
INSERT INTO "exploration" ("start_date", "return_date", "exploration_status", "camp_id",
    "extra_days", "ration_per_person", "max_extra_days", "estimated_days")
VALUES (
    '2025-03-18 06:00:00+00', '2025-03-21 20:00:00+00', 'COMPLETADA',
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    0, 2, 1, 3
);

INSERT INTO "exploration_member" ("person_id", "exploration_id")
VALUES
((SELECT id FROM person WHERE id_card = 'TEST-SEED-001' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-03-18 06:00:00+00' LIMIT 1)),
((SELECT id FROM person WHERE id_card = 'TEST-SEED-004' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-03-18 06:00:00+00' LIMIT 1)),
((SELECT id FROM person WHERE id_card = 'TEST-SEED-005' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-03-18 06:00:00+00' LIMIT 1));

INSERT INTO "exploration_loot" ("quantity", "resource_id", "exploration_id", "is_added_to_inventory")
VALUES
(50, (SELECT id FROM resource WHERE name = 'Agua Embotellada' LIMIT 1),
     (SELECT id FROM exploration WHERE start_date = '2025-03-18 06:00:00+00' LIMIT 1), TRUE),
(10, (SELECT id FROM resource WHERE name = 'Antibióticos' LIMIT 1),
     (SELECT id FROM exploration WHERE start_date = '2025-03-18 06:00:00+00' LIMIT 1), TRUE);

-- [EXP-6] COMPLETADA | abr 2025 | 7 días | 2 días extra | equipo de 2
INSERT INTO "exploration" ("start_date", "return_date", "exploration_status", "camp_id",
    "extra_days", "ration_per_person", "max_extra_days", "estimated_days")
VALUES (
    '2025-04-01 07:30:00+00', '2025-04-10 14:00:00+00', 'COMPLETADA',
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    2, 2, 3, 7
);

INSERT INTO "exploration_member" ("person_id", "exploration_id")
VALUES
((SELECT id FROM person WHERE id_card = 'TEST-SEED-001' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-04-01 07:30:00+00' LIMIT 1)),
((SELECT id FROM person WHERE id_card = 'TEST-SEED-005' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-04-01 07:30:00+00' LIMIT 1));

INSERT INTO "exploration_loot" ("quantity", "resource_id", "exploration_id", "is_added_to_inventory")
VALUES
(30, (SELECT id FROM resource WHERE name = 'Semillas de Papa' LIMIT 1),
     (SELECT id FROM exploration WHERE start_date = '2025-04-01 07:30:00+00' LIMIT 1), TRUE),
(45, (SELECT id FROM resource WHERE name = 'Arroz' LIMIT 1),
     (SELECT id FROM exploration WHERE start_date = '2025-04-01 07:30:00+00' LIMIT 1), TRUE),
(18, (SELECT id FROM resource WHERE name = 'Vendajes' LIMIT 1),
     (SELECT id FROM exploration WHERE start_date = '2025-04-01 07:30:00+00' LIMIT 1), TRUE);

-- [EXP-7] COMPLETADA | abr 2025 | 4 días | equipo de 3
INSERT INTO "exploration" ("start_date", "return_date", "exploration_status", "camp_id",
    "extra_days", "ration_per_person", "max_extra_days", "estimated_days")
VALUES (
    '2025-04-14 08:00:00+00', '2025-04-18 17:00:00+00', 'COMPLETADA',
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    0, 2, 2, 4
);

INSERT INTO "exploration_member" ("person_id", "exploration_id")
VALUES
((SELECT id FROM person WHERE id_card = 'TEST-SEED-001' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-04-14 08:00:00+00' LIMIT 1)),
((SELECT id FROM person WHERE id_card = 'TEST-SEED-004' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-04-14 08:00:00+00' LIMIT 1)),
((SELECT id FROM person WHERE id_card = 'TEST-SEED-005' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-04-14 08:00:00+00' LIMIT 1));

INSERT INTO "exploration_loot" ("quantity", "resource_id", "exploration_id", "is_added_to_inventory")
VALUES
(70, (SELECT id FROM resource WHERE name = 'Agua Embotellada' LIMIT 1),
     (SELECT id FROM exploration WHERE start_date = '2025-04-14 08:00:00+00' LIMIT 1), TRUE),
(35, (SELECT id FROM resource WHERE name = 'Latas de Frijoles' LIMIT 1),
     (SELECT id FROM exploration WHERE start_date = '2025-04-14 08:00:00+00' LIMIT 1), TRUE);

-- [EXP-8] COMPLETADA | may 2025 | 5 días | equipo de 2
INSERT INTO "exploration" ("start_date", "return_date", "exploration_status", "camp_id",
    "extra_days", "ration_per_person", "max_extra_days", "estimated_days")
VALUES (
    '2025-05-02 06:00:00+00', '2025-05-07 16:00:00+00', 'COMPLETADA',
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    0, 3, 2, 5
);

INSERT INTO "exploration_member" ("person_id", "exploration_id")
VALUES
((SELECT id FROM person WHERE id_card = 'TEST-SEED-004' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-05-02 06:00:00+00' LIMIT 1)),
((SELECT id FROM person WHERE id_card = 'TEST-SEED-005' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-05-02 06:00:00+00' LIMIT 1));

INSERT INTO "exploration_loot" ("quantity", "resource_id", "exploration_id", "is_added_to_inventory")
VALUES
(55, (SELECT id FROM resource WHERE name = 'Arroz' LIMIT 1),
     (SELECT id FROM exploration WHERE start_date = '2025-05-02 06:00:00+00' LIMIT 1), TRUE),
(14, (SELECT id FROM resource WHERE name = 'Botiquín Básico' LIMIT 1),
     (SELECT id FROM exploration WHERE start_date = '2025-05-02 06:00:00+00' LIMIT 1), TRUE);

-- -------------------------------------------------------
-- EXPEDICIONES CANCELADAS
-- -------------------------------------------------------

-- [EXP-9] CANCELADA | feb 2025 | equipo de 2 (clima adverso)
INSERT INTO "exploration" ("start_date", "return_date", "exploration_status", "camp_id",
    "extra_days", "ration_per_person", "max_extra_days", "estimated_days")
VALUES (
    '2025-02-10 09:00:00+00', '2025-02-11 12:00:00+00', 'CANCELADA',
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    0, 2, 1, 4
);

INSERT INTO "exploration_member" ("person_id", "exploration_id")
VALUES
((SELECT id FROM person WHERE id_card = 'TEST-SEED-001' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-02-10 09:00:00+00' LIMIT 1)),
((SELECT id FROM person WHERE id_card = 'TEST-SEED-004' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-02-10 09:00:00+00' LIMIT 1));

-- [EXP-10] CANCELADA | mar 2025 | equipo de 3 (miembro herido)
INSERT INTO "exploration" ("start_date", "return_date", "exploration_status", "camp_id",
    "extra_days", "ration_per_person", "max_extra_days", "estimated_days")
VALUES (
    '2025-03-12 07:00:00+00', '2025-03-13 08:00:00+00', 'CANCELADA',
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    0, 2, 2, 5
);

INSERT INTO "exploration_member" ("person_id", "exploration_id")
VALUES
((SELECT id FROM person WHERE id_card = 'TEST-SEED-001' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-03-12 07:00:00+00' LIMIT 1)),
((SELECT id FROM person WHERE id_card = 'TEST-SEED-004' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-03-12 07:00:00+00' LIMIT 1)),
((SELECT id FROM person WHERE id_card = 'TEST-SEED-005' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-03-12 07:00:00+00' LIMIT 1));

-- [EXP-11] CANCELADA | abr 2025 | equipo de 2 (zona peligrosa)
INSERT INTO "exploration" ("start_date", "return_date", "exploration_status", "camp_id",
    "extra_days", "ration_per_person", "max_extra_days", "estimated_days")
VALUES (
    '2025-04-22 08:30:00+00', '2025-04-22 19:00:00+00', 'CANCELADA',
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    0, 2, 1, 3
);

INSERT INTO "exploration_member" ("person_id", "exploration_id")
VALUES
((SELECT id FROM person WHERE id_card = 'TEST-SEED-004' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-04-22 08:30:00+00' LIMIT 1)),
((SELECT id FROM person WHERE id_card = 'TEST-SEED-005' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-04-22 08:30:00+00' LIMIT 1));

-- [EXP-12] CANCELADA | may 2025 | equipo de 2 (suministros insuficientes)
INSERT INTO "exploration" ("start_date", "return_date", "exploration_status", "camp_id",
    "extra_days", "ration_per_person", "max_extra_days", "estimated_days")
VALUES (
    '2025-05-10 07:00:00+00', '2025-05-10 15:00:00+00', 'CANCELADA',
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    0, 3, 2, 6
);

INSERT INTO "exploration_member" ("person_id", "exploration_id")
VALUES
((SELECT id FROM person WHERE id_card = 'TEST-SEED-001' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-05-10 07:00:00+00' LIMIT 1)),
((SELECT id FROM person WHERE id_card = 'TEST-SEED-005' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-05-10 07:00:00+00' LIMIT 1));

-- -------------------------------------------------------
-- EXPEDICIONES EN PROCESO
-- -------------------------------------------------------

-- [EXP-13] EN PROCESO | reciente | equipo de 3
INSERT INTO "exploration" ("start_date", "exploration_status", "camp_id",
    "extra_days", "ration_per_person", "max_extra_days", "estimated_days")
VALUES (
    '2025-05-20 07:00:00+00', 'EN PROCESO',
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    0, 2, 3, 7
);

INSERT INTO "exploration_member" ("person_id", "exploration_id")
VALUES
((SELECT id FROM person WHERE id_card = 'TEST-SEED-001' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-05-20 07:00:00+00' LIMIT 1)),
((SELECT id FROM person WHERE id_card = 'TEST-SEED-004' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-05-20 07:00:00+00' LIMIT 1)),
((SELECT id FROM person WHERE id_card = 'TEST-SEED-005' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-05-20 07:00:00+00' LIMIT 1));

-- [EXP-14] EN PROCESO | reciente | equipo de 2
INSERT INTO "exploration" ("start_date", "exploration_status", "camp_id",
    "extra_days", "ration_per_person", "max_extra_days", "estimated_days")
VALUES (
    '2025-05-22 08:00:00+00', 'EN PROCESO',
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    0, 2, 2, 5
);

INSERT INTO "exploration_member" ("person_id", "exploration_id")
VALUES
((SELECT id FROM person WHERE id_card = 'TEST-SEED-004' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-05-22 08:00:00+00' LIMIT 1)),
((SELECT id FROM person WHERE id_card = 'TEST-SEED-005' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-05-22 08:00:00+00' LIMIT 1));

-- [EXP-15] EN PROCESO | reciente | equipo de 2
INSERT INTO "exploration" ("start_date", "exploration_status", "camp_id",
    "extra_days", "ration_per_person", "max_extra_days", "estimated_days")
VALUES (
    '2025-05-24 06:30:00+00', 'EN PROCESO',
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    0, 3, 1, 4
);

INSERT INTO "exploration_member" ("person_id", "exploration_id")
VALUES
((SELECT id FROM person WHERE id_card = 'TEST-SEED-001' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-05-24 06:30:00+00' LIMIT 1)),
((SELECT id FROM person WHERE id_card = 'TEST-SEED-005' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-05-24 06:30:00+00' LIMIT 1));

-- -------------------------------------------------------
-- EXPEDICIONES EXTRAS (para tener 18 en total y dar más
-- margen a la paginación)
-- -------------------------------------------------------

-- [EXP-16] COMPLETADA | ene 2025 | 2 días | equipo de 2
INSERT INTO "exploration" ("start_date", "return_date", "exploration_status", "camp_id",
    "extra_days", "ration_per_person", "max_extra_days", "estimated_days")
VALUES (
    '2025-01-08 07:00:00+00', '2025-01-10 17:00:00+00', 'COMPLETADA',
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    0, 1, 1, 2
);

INSERT INTO "exploration_member" ("person_id", "exploration_id")
VALUES
((SELECT id FROM person WHERE id_card = 'TEST-SEED-004' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-01-08 07:00:00+00' LIMIT 1)),
((SELECT id FROM person WHERE id_card = 'TEST-SEED-005' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-01-08 07:00:00+00' LIMIT 1));

INSERT INTO "exploration_loot" ("quantity", "resource_id", "exploration_id", "is_added_to_inventory")
VALUES
(20, (SELECT id FROM resource WHERE name = 'Agua Embotellada' LIMIT 1),
     (SELECT id FROM exploration WHERE start_date = '2025-01-08 07:00:00+00' LIMIT 1), TRUE),
(10, (SELECT id FROM resource WHERE name = 'Vendajes' LIMIT 1),
     (SELECT id FROM exploration WHERE start_date = '2025-01-08 07:00:00+00' LIMIT 1), TRUE);

-- [EXP-17] COMPLETADA | ene 2025 | 4 días | equipo de 3
INSERT INTO "exploration" ("start_date", "return_date", "exploration_status", "camp_id",
    "extra_days", "ration_per_person", "max_extra_days", "estimated_days")
VALUES (
    '2025-01-28 08:00:00+00', '2025-02-01 16:00:00+00', 'COMPLETADA',
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    0, 2, 2, 4
);

INSERT INTO "exploration_member" ("person_id", "exploration_id")
VALUES
((SELECT id FROM person WHERE id_card = 'TEST-SEED-001' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-01-28 08:00:00+00' LIMIT 1)),
((SELECT id FROM person WHERE id_card = 'TEST-SEED-004' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-01-28 08:00:00+00' LIMIT 1)),
((SELECT id FROM person WHERE id_card = 'TEST-SEED-005' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-01-28 08:00:00+00' LIMIT 1));

INSERT INTO "exploration_loot" ("quantity", "resource_id", "exploration_id", "is_added_to_inventory")
VALUES
(25, (SELECT id FROM resource WHERE name = 'Latas de Frijoles' LIMIT 1),
     (SELECT id FROM exploration WHERE start_date = '2025-01-28 08:00:00+00' LIMIT 1), TRUE),
(30, (SELECT id FROM resource WHERE name = 'Arroz' LIMIT 1),
     (SELECT id FROM exploration WHERE start_date = '2025-01-28 08:00:00+00' LIMIT 1), TRUE);

-- [EXP-18] CANCELADA | may 2025 | equipo de 3
INSERT INTO "exploration" ("start_date", "return_date", "exploration_status", "camp_id",
    "extra_days", "ration_per_person", "max_extra_days", "estimated_days")
VALUES (
    '2025-05-16 09:00:00+00', '2025-05-16 18:30:00+00', 'CANCELADA',
    (SELECT id FROM camp WHERE name = 'Campamento Caolin' LIMIT 1),
    0, 2, 2, 5
);

INSERT INTO "exploration_member" ("person_id", "exploration_id")
VALUES
((SELECT id FROM person WHERE id_card = 'TEST-SEED-001' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-05-16 09:00:00+00' LIMIT 1)),
((SELECT id FROM person WHERE id_card = 'TEST-SEED-004' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-05-16 09:00:00+00' LIMIT 1)),
((SELECT id FROM person WHERE id_card = 'TEST-SEED-005' LIMIT 1),
 (SELECT id FROM exploration WHERE start_date = '2025-05-16 09:00:00+00' LIMIT 1));
