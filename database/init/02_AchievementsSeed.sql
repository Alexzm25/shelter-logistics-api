INSERT INTO "achievement" ("name", "description", "condition_value", "icon_url")
SELECT 'Primeros Suministros', 'Tu campamento acumulo un total de 100 unidades de recursos en el inventario.', 100, 'primeros_suministros'
WHERE NOT EXISTS (SELECT 1 FROM "achievement" WHERE "name" = 'Primeros Suministros');

INSERT INTO "achievement" ("name", "description", "condition_value", "icon_url")
SELECT 'Despensa Llena', 'Tu campamento alcanzo 1000 unidades totales de recursos almacenados en el inventario.', 1000, 'despensa_llena'
WHERE NOT EXISTS (SELECT 1 FROM "achievement" WHERE "name" = 'Despensa Llena');

INSERT INTO "achievement" ("name", "description", "condition_value", "icon_url")
SELECT 'Exploradores Natos', 'Tu campamento completo su primera exploracion exitosamente.', 1, 'exploradores_natos'
WHERE NOT EXISTS (SELECT 1 FROM "achievement" WHERE "name" = 'Exploradores Natos');

INSERT INTO "achievement" ("name", "description", "condition_value", "icon_url")
SELECT 'Veteranos del Terreno', 'Tu campamento ha completado un total de 10 exploraciones.', 10, 'veteranos_del_terreno'
WHERE NOT EXISTS (SELECT 1 FROM "achievement" WHERE "name" = 'Veteranos del Terreno');

INSERT INTO "achievement" ("name", "description", "condition_value", "icon_url")
SELECT 'Saqueadores Expertos', 'Tu campamento recolecto en total 200 unidades de botin durante las exploraciones.', 200, 'saqueadores_expertos'
WHERE NOT EXISTS (SELECT 1 FROM "achievement" WHERE "name" = 'Saqueadores Expertos');

INSERT INTO "achievement" ("name", "description", "condition_value", "icon_url")
SELECT 'Red de Aliados', 'Tu campamento realizo su primera transferencia de recursos con otro campamento.', 1, 'red_de_aliados'
WHERE NOT EXISTS (SELECT 1 FROM "achievement" WHERE "name" = 'Red de Aliados');

INSERT INTO "achievement" ("name", "description", "condition_value", "icon_url")
SELECT 'Rutas Establecidas', 'Tu campamento completo 5 transferencias de recursos con otros campamentos.', 5, 'rutas_establecidas'
WHERE NOT EXISTS (SELECT 1 FROM "achievement" WHERE "name" = 'Rutas Establecidas');

INSERT INTO "achievement" ("name", "description", "condition_value", "icon_url")
SELECT 'Manos a la Obra', 'El campamento produjo un total acumulado de 300 unidades de recursos.', 300, 'manos_a_la_obra'
WHERE NOT EXISTS (SELECT 1 FROM "achievement" WHERE "name" = 'Manos a la Obra');

INSERT INTO "achievement" ("name", "description", "condition_value", "icon_url")
SELECT 'Comunidad Creciente', 'Tu campamento tiene 10 personas activas al mismo tiempo.', 10, 'comunidad_creciente'
WHERE NOT EXISTS (SELECT 1 FROM "achievement" WHERE "name" = 'Comunidad Creciente');

INSERT INTO "achievement" ("name", "description", "condition_value", "icon_url")
SELECT 'Nadie se Queda sin Comer', 'Tu campamento distribuyo raciones diarias en 30 ocasiones consecutivas.', 30, 'nadie_sin_comer'
WHERE NOT EXISTS (SELECT 1 FROM "achievement" WHERE "name" = 'Nadie se Queda sin Comer');

INSERT INTO "achievement" ("name", "description", "condition_value", "icon_url")
SELECT 'Campamento Saludable', 'Tu campamento tuvo 15 personas con estado de salud SANO al mismo tiempo.', 15, 'campamento_saludable'
WHERE NOT EXISTS (SELECT 1 FROM "achievement" WHERE "name" = 'Campamento Saludable');

INSERT INTO "achievement" ("name", "description", "condition_value", "icon_url")
SELECT 'Logistica Maestra', 'Tu campamento registro 100 movimientos en el inventario (ingresos, salidas o transferencias).', 100, 'logistica_maestra'
WHERE NOT EXISTS (SELECT 1 FROM "achievement" WHERE "name" = 'Logistica Maestra');
