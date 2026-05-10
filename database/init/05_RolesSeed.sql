-- Seed default roles of the application
 
INSERT INTO role (name, description)
SELECT 'ADMINISTRADOR SISTEMA', 'Acceso general al sistema, gestiona únicamente el ingreso de personas al campamento.'
WHERE NOT EXISTS (
    SELECT 1 FROM role WHERE name = 'ADMINISTRADOR SISTEMA'
);
 
INSERT INTO role (name, description)
SELECT 'TRABAJADOR', 'Puede realizar cambios en el inventario, sujetos a autorización del gestor de recursos.'
WHERE NOT EXISTS (
    SELECT 1 FROM role WHERE name = 'TRABAJADOR'
);
 
INSERT INTO role (name, description)
SELECT 'GESTIÓN RECURSOS', 'Encargado de autorizar movimientos de inventario, traslados y envíos de recursos entre campamentos.'
WHERE NOT EXISTS (
    SELECT 1 FROM role WHERE name = 'GESTIÓN RECURSOS'
);
 
INSERT INTO role (name, description)
SELECT 'ENCARGADO VIAJES Y COMUNICACIÓN', 'Responsable de organizar expediciones y gestionar negociaciones con otros campamentos.'
WHERE NOT EXISTS (
    SELECT 1 FROM role WHERE name = 'ENCARGADO VIAJES Y COMUNICACIÓN'
);