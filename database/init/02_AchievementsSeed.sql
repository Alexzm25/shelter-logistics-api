
INSERT INTO "achievement" (
    "name",
    "description",
    "condition_value",
    "icon_url"
) VALUES

-- 1. Recursos acumulados en inventario
(
    'Primeros Suministros',
    'Tu campamento acumuló un total de 100 unidades de recursos en el inventario.',
    100,
    'primeros_suministros'
),

-- 2. Recursos acumulados — nivel avanzado
(
    'Despensa Llena',
    'Tu campamento alcanzó 1000 unidades totales de recursos almacenados en el inventario.',
    1000,
    'despensa_llena'
),

-- 3. Primera exploración completada
(
    'Exploradores Natos',
    'Tu campamento completó su primera exploración exitosamente.',
    1,
    'exploradores_natos'
),

-- 4. Diez exploraciones completadas
(
    'Veteranos del Terreno',
    'Tu campamento ha completado un total de 10 exploraciones.',
    10,
    'veteranos_del_terreno'
),

-- 5. Botín total recolectado en exploraciones
(
    'Saqueadores Expertos',
    'Tu campamento recolectó en total 200 unidades de botín durante las exploraciones.',
    200,
    'saqueadores_expertos'
),

-- 6. Primera transferencia enviada o recibida
(
    'Red de Aliados',
    'Tu campamento realizó su primera transferencia de recursos con otro campamento.',
    1,
    'red_de_aliados'
),

-- 7. Cinco transferencias completadas
(
    'Rutas Establecidas',
    'Tu campamento completó 5 transferencias de recursos con otros campamentos.',
    5,
    'rutas_establecidas'
),

-- 8. Producción total del campamento
(
    'Manos a la Obra',
    'El campamento produjo un total acumulado de 300 unidades de recursos.',
    300,
    'manos_a_la_obra'
),

-- 9. Personas activas en el campamento
(
    'Comunidad Creciente',
    'Tu campamento tiene 10 personas activas al mismo tiempo.',
    10,
    'comunidad_creciente'
),

-- 10. Raciones diarias distribuidas
(
    'Nadie se Queda sin Comer',
    'Tu campamento distribuyó raciones diarias en 30 ocasiones consecutivas.',
    30,
    'nadie_sin_comer'
),

-- 11. Personas sanas en el campamento
(
    'Campamento Saludable',
    'Tu campamento tuvo 15 personas con estado de salud SANO al mismo tiempo.',
    15,
    'campamento_saludable'
),

-- 12. Movimientos de inventario realizados
(
    'Logística Maestra',
    'Tu campamento registró 100 movimientos en el inventario (ingresos, salidas o transferencias).',
    100,
    'logistica_maestra'
);
