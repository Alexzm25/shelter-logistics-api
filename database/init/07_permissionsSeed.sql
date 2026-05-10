-- Seed permissions and role-permission associations

-- Permissions
INSERT INTO permission (name, description)
SELECT 'VER_DASHBOARD', 'Ver el tablero principal (solo admin)'
WHERE NOT EXISTS (SELECT 1 FROM permission WHERE name = 'VER_DASHBOARD');

INSERT INTO permission (name, description)
SELECT 'VER_PAGINA_TRABAJADOR', 'Ver la página de Trabajador'
WHERE NOT EXISTS (SELECT 1 FROM permission WHERE name = 'VER_PAGINA_TRABAJADOR');

INSERT INTO permission (name, description)
SELECT 'VER_PAGINA_TRANSFERENCIAS', 'Ver la página de Transferencias'
WHERE NOT EXISTS (SELECT 1 FROM permission WHERE name = 'VER_PAGINA_TRANSFERENCIAS');

INSERT INTO permission (name, description)
SELECT 'VER_PAGINA_EXPEDICIONES', 'Ver la página de Expediciones'
WHERE NOT EXISTS (SELECT 1 FROM permission WHERE name = 'VER_PAGINA_EXPEDICIONES');

INSERT INTO permission (name, description)
SELECT 'VER_INVENTARIO_COMPLETO', 'Ver el inventario completo del campamento'
WHERE NOT EXISTS (SELECT 1 FROM permission WHERE name = 'VER_INVENTARIO_COMPLETO');

INSERT INTO permission (name, description)
SELECT 'VER_LOGROS', 'Ver la vista de logros (achievements)'
WHERE NOT EXISTS (SELECT 1 FROM permission WHERE name = 'VER_LOGROS');

INSERT INTO permission (name, description)
SELECT 'GESTION_HUMANA_TOTAL', 'Control total sobre la gestión humana (ingresos de personas)'
WHERE NOT EXISTS (SELECT 1 FROM permission WHERE name = 'GESTION_HUMANA_TOTAL');

INSERT INTO permission (name, description)
SELECT 'SOLICITAR_RECURSOS', 'Permite solicitar recursos a otros campamentos'
WHERE NOT EXISTS (SELECT 1 FROM permission WHERE name = 'SOLICITAR_RECURSOS');

INSERT INTO permission (name, description)
SELECT 'SOLICITAR_PERSONAS', 'Permite solicitar personas a otros campamentos'
WHERE NOT EXISTS (SELECT 1 FROM permission WHERE name = 'SOLICITAR_PERSONAS');

INSERT INTO permission (name, description)
SELECT 'APROBAR_RECHAZAR_SOLICITUDES', 'Aprobar o rechazar solicitudes de transferencias'
WHERE NOT EXISTS (SELECT 1 FROM permission WHERE name = 'APROBAR_RECHAZAR_SOLICITUDES');

INSERT INTO permission (name, description)
SELECT 'VER_HISTORIAL_SOLICITUDES', 'Ver historial de solicitudes de transferencias'
WHERE NOT EXISTS (SELECT 1 FROM permission WHERE name = 'VER_HISTORIAL_SOLICITUDES');

INSERT INTO permission (name, description)
SELECT 'INGRESAR_RECURSOS_MANUAL', 'Realizar ingresos manuales de recursos al inventario'
WHERE NOT EXISTS (SELECT 1 FROM permission WHERE name = 'INGRESAR_RECURSOS_MANUAL');

INSERT INTO permission (name, description)
SELECT 'CREAR_EXPEDICIONES', 'Crear y gestionar expediciones'
WHERE NOT EXISTS (SELECT 1 FROM permission WHERE name = 'CREAR_EXPEDICIONES');

INSERT INTO permission (name, description)
SELECT 'REGISTRAR_PRODUCCION', 'Registrar recursos producidos (ej. agricultor)'
WHERE NOT EXISTS (SELECT 1 FROM permission WHERE name = 'REGISTRAR_PRODUCCION');

INSERT INTO permission (name, description)
SELECT 'VER_INVENTARIO_SEMILLAS', 'Ver inventario filtrado por SEMILLAS (para solicitudes de siembra)'
WHERE NOT EXISTS (SELECT 1 FROM permission WHERE name = 'VER_INVENTARIO_SEMILLAS');

INSERT INTO permission (name, description)
SELECT 'VER_INVENTARIO_MEDICINAS', 'Ver inventario filtrado por MEDICINAS (uso médico)'
WHERE NOT EXISTS (SELECT 1 FROM permission WHERE name = 'VER_INVENTARIO_MEDICINAS');

INSERT INTO permission (name, description)
SELECT 'CURAR_PERSONAS', 'Registrar curaciones y gestionar estado de salud (médico)'
WHERE NOT EXISTS (SELECT 1 FROM permission WHERE name = 'CURAR_PERSONAS');

-- Role -> Permission associations
-- ADMINISTRADOR SISTEMA: puede ver todas las páginas y tiene control total en gestión humana
INSERT INTO role_permission (role_id, permission_id)
SELECT (SELECT id FROM role WHERE name = 'ADMINISTRADOR SISTEMA'), (SELECT id FROM permission WHERE name = 'VER_DASHBOARD')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permission rp WHERE rp.role_id = (SELECT id FROM role WHERE name = 'ADMINISTRADOR SISTEMA')
    AND rp.permission_id = (SELECT id FROM permission WHERE name = 'VER_DASHBOARD')
);

INSERT INTO role_permission (role_id, permission_id)
SELECT (SELECT id FROM role WHERE name = 'ADMINISTRADOR SISTEMA'), (SELECT id FROM permission WHERE name = 'VER_PAGINA_TRABAJADOR')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permission rp WHERE rp.role_id = (SELECT id FROM role WHERE name = 'ADMINISTRADOR SISTEMA')
    AND rp.permission_id = (SELECT id FROM permission WHERE name = 'VER_PAGINA_TRABAJADOR')
);

INSERT INTO role_permission (role_id, permission_id)
SELECT (SELECT id FROM role WHERE name = 'ADMINISTRADOR SISTEMA'), (SELECT id FROM permission WHERE name = 'VER_PAGINA_TRANSFERENCIAS')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permission rp WHERE rp.role_id = (SELECT id FROM role WHERE name = 'ADMINISTRADOR SISTEMA')
    AND rp.permission_id = (SELECT id FROM permission WHERE name = 'VER_PAGINA_TRANSFERENCIAS')
);

INSERT INTO role_permission (role_id, permission_id)
SELECT (SELECT id FROM role WHERE name = 'ADMINISTRADOR SISTEMA'), (SELECT id FROM permission WHERE name = 'VER_PAGINA_EXPEDICIONES')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permission rp WHERE rp.role_id = (SELECT id FROM role WHERE name = 'ADMINISTRADOR SISTEMA')
    AND rp.permission_id = (SELECT id FROM permission WHERE name = 'VER_PAGINA_EXPEDICIONES')
);

INSERT INTO role_permission (role_id, permission_id)
SELECT (SELECT id FROM role WHERE name = 'ADMINISTRADOR SISTEMA'), (SELECT id FROM permission WHERE name = 'VER_INVENTARIO_COMPLETO')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permission rp WHERE rp.role_id = (SELECT id FROM role WHERE name = 'ADMINISTRADOR SISTEMA')
    AND rp.permission_id = (SELECT id FROM permission WHERE name = 'VER_INVENTARIO_COMPLETO')
);

INSERT INTO role_permission (role_id, permission_id)
SELECT (SELECT id FROM role WHERE name = 'ADMINISTRADOR SISTEMA'), (SELECT id FROM permission WHERE name = 'VER_LOGROS')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permission rp WHERE rp.role_id = (SELECT id FROM role WHERE name = 'ADMINISTRADOR SISTEMA')
    AND rp.permission_id = (SELECT id FROM permission WHERE name = 'VER_LOGROS')
);

INSERT INTO role_permission (role_id, permission_id)
SELECT (SELECT id FROM role WHERE name = 'ADMINISTRADOR SISTEMA'), (SELECT id FROM permission WHERE name = 'VER_HISTORIAL_SOLICITUDES')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permission rp WHERE rp.role_id = (SELECT id FROM role WHERE name = 'ADMINISTRADOR SISTEMA')
    AND rp.permission_id = (SELECT id FROM permission WHERE name = 'VER_HISTORIAL_SOLICITUDES')
);

INSERT INTO role_permission (role_id, permission_id)
SELECT (SELECT id FROM role WHERE name = 'ADMINISTRADOR SISTEMA'), (SELECT id FROM permission WHERE name = 'GESTION_HUMANA_TOTAL')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permission rp WHERE rp.role_id = (SELECT id FROM role WHERE name = 'ADMINISTRADOR SISTEMA')
    AND rp.permission_id = (SELECT id FROM permission WHERE name = 'GESTION_HUMANA_TOTAL')
);

-- TRABAJADOR: verá la página de trabajador, podrá solicitar recursos y ver logros
INSERT INTO role_permission (role_id, permission_id)
SELECT (SELECT id FROM role WHERE name = 'TRABAJADOR'), (SELECT id FROM permission WHERE name = 'VER_PAGINA_TRABAJADOR')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permission rp WHERE rp.role_id = (SELECT id FROM role WHERE name = 'TRABAJADOR')
    AND rp.permission_id = (SELECT id FROM permission WHERE name = 'VER_PAGINA_TRABAJADOR')
);

INSERT INTO role_permission (role_id, permission_id)
SELECT (SELECT id FROM role WHERE name = 'TRABAJADOR'), (SELECT id FROM permission WHERE name = 'SOLICITAR_RECURSOS')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permission rp WHERE rp.role_id = (SELECT id FROM role WHERE name = 'TRABAJADOR')
    AND rp.permission_id = (SELECT id FROM permission WHERE name = 'SOLICITAR_RECURSOS')
);

INSERT INTO role_permission (role_id, permission_id)
SELECT (SELECT id FROM role WHERE name = 'TRABAJADOR'), (SELECT id FROM permission WHERE name = 'VER_LOGROS')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permission rp WHERE rp.role_id = (SELECT id FROM role WHERE name = 'TRABAJADOR')
    AND rp.permission_id = (SELECT id FROM permission WHERE name = 'VER_LOGROS')
);

INSERT INTO role_permission (role_id, permission_id)
SELECT (SELECT id FROM role WHERE name = 'TRABAJADOR'), (SELECT id FROM permission WHERE name = 'REGISTRAR_PRODUCCION')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permission rp WHERE rp.role_id = (SELECT id FROM role WHERE name = 'TRABAJADOR')
    AND rp.permission_id = (SELECT id FROM permission WHERE name = 'REGISTRAR_PRODUCCION')
);

INSERT INTO role_permission (role_id, permission_id)
SELECT (SELECT id FROM role WHERE name = 'TRABAJADOR'), (SELECT id FROM permission WHERE name = 'VER_INVENTARIO_SEMILLAS')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permission rp WHERE rp.role_id = (SELECT id FROM role WHERE name = 'TRABAJADOR')
    AND rp.permission_id = (SELECT id FROM permission WHERE name = 'VER_INVENTARIO_SEMILLAS')
);

INSERT INTO role_permission (role_id, permission_id)
SELECT (SELECT id FROM role WHERE name = 'TRABAJADOR'), (SELECT id FROM permission WHERE name = 'VER_INVENTARIO_MEDICINAS')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permission rp WHERE rp.role_id = (SELECT id FROM role WHERE name = 'TRABAJADOR')
    AND rp.permission_id = (SELECT id FROM permission WHERE name = 'VER_INVENTARIO_MEDICINAS')
);

INSERT INTO role_permission (role_id, permission_id)
SELECT (SELECT id FROM role WHERE name = 'TRABAJADOR'), (SELECT id FROM permission WHERE name = 'CURAR_PERSONAS')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permission rp WHERE rp.role_id = (SELECT id FROM role WHERE name = 'TRABAJADOR')
    AND rp.permission_id = (SELECT id FROM permission WHERE name = 'CURAR_PERSONAS')
);

-- GESTIÓN RECURSOS: gestión de transferencias, aprobación y manejo de inventario
INSERT INTO role_permission (role_id, permission_id)
SELECT (SELECT id FROM role WHERE name = 'GESTIÓN RECURSOS'), (SELECT id FROM permission WHERE name = 'VER_PAGINA_TRANSFERENCIAS')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permission rp WHERE rp.role_id = (SELECT id FROM role WHERE name = 'GESTIÓN RECURSOS')
    AND rp.permission_id = (SELECT id FROM permission WHERE name = 'VER_PAGINA_TRANSFERENCIAS')
);

INSERT INTO role_permission (role_id, permission_id)
SELECT (SELECT id FROM role WHERE name = 'GESTIÓN RECURSOS'), (SELECT id FROM permission WHERE name = 'SOLICITAR_RECURSOS')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permission rp WHERE rp.role_id = (SELECT id FROM role WHERE name = 'GESTIÓN RECURSOS')
    AND rp.permission_id = (SELECT id FROM permission WHERE name = 'SOLICITAR_RECURSOS')
);

INSERT INTO role_permission (role_id, permission_id)
SELECT (SELECT id FROM role WHERE name = 'GESTIÓN RECURSOS'), (SELECT id FROM permission WHERE name = 'SOLICITAR_PERSONAS')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permission rp WHERE rp.role_id = (SELECT id FROM role WHERE name = 'GESTIÓN RECURSOS')
    AND rp.permission_id = (SELECT id FROM permission WHERE name = 'SOLICITAR_PERSONAS')
);

INSERT INTO role_permission (role_id, permission_id)
SELECT (SELECT id FROM role WHERE name = 'GESTIÓN RECURSOS'), (SELECT id FROM permission WHERE name = 'APROBAR_RECHAZAR_SOLICITUDES')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permission rp WHERE rp.role_id = (SELECT id FROM role WHERE name = 'GESTIÓN RECURSOS')
    AND rp.permission_id = (SELECT id FROM permission WHERE name = 'APROBAR_RECHAZAR_SOLICITUDES')
);

INSERT INTO role_permission (role_id, permission_id)
SELECT (SELECT id FROM role WHERE name = 'GESTIÓN RECURSOS'), (SELECT id FROM permission WHERE name = 'VER_HISTORIAL_SOLICITUDES')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permission rp WHERE rp.role_id = (SELECT id FROM role WHERE name = 'GESTIÓN RECURSOS')
    AND rp.permission_id = (SELECT id FROM permission WHERE name = 'VER_HISTORIAL_SOLICITUDES')
);

INSERT INTO role_permission (role_id, permission_id)
SELECT (SELECT id FROM role WHERE name = 'GESTIÓN RECURSOS'), (SELECT id FROM permission WHERE name = 'VER_INVENTARIO_COMPLETO')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permission rp WHERE rp.role_id = (SELECT id FROM role WHERE name = 'GESTIÓN RECURSOS')
    AND rp.permission_id = (SELECT id FROM permission WHERE name = 'VER_INVENTARIO_COMPLETO')
);

INSERT INTO role_permission (role_id, permission_id)
SELECT (SELECT id FROM role WHERE name = 'GESTIÓN RECURSOS'), (SELECT id FROM permission WHERE name = 'INGRESAR_RECURSOS_MANUAL')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permission rp WHERE rp.role_id = (SELECT id FROM role WHERE name = 'GESTIÓN RECURSOS')
    AND rp.permission_id = (SELECT id FROM permission WHERE name = 'INGRESAR_RECURSOS_MANUAL')
);

INSERT INTO role_permission (role_id, permission_id)
SELECT (SELECT id FROM role WHERE name = 'GESTIÓN RECURSOS'), (SELECT id FROM permission WHERE name = 'VER_LOGROS')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permission rp WHERE rp.role_id = (SELECT id FROM role WHERE name = 'GESTIÓN RECURSOS')
    AND rp.permission_id = (SELECT id FROM permission WHERE name = 'VER_LOGROS')
);

-- ENCARGADO VIAJES Y COMUNICACIÓN: expediciones y solicitudes externas
INSERT INTO role_permission (role_id, permission_id)
SELECT (SELECT id FROM role WHERE name = 'ENCARGADO VIAJES Y COMUNICACIÓN'), (SELECT id FROM permission WHERE name = 'VER_PAGINA_EXPEDICIONES')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permission rp WHERE rp.role_id = (SELECT id FROM role WHERE name = 'ENCARGADO VIAJES Y COMUNICACIÓN')
    AND rp.permission_id = (SELECT id FROM permission WHERE name = 'VER_PAGINA_EXPEDICIONES')
);

INSERT INTO role_permission (role_id, permission_id)
SELECT (SELECT id FROM role WHERE name = 'ENCARGADO VIAJES Y COMUNICACIÓN'), (SELECT id FROM permission WHERE name = 'CREAR_EXPEDICIONES')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permission rp WHERE rp.role_id = (SELECT id FROM role WHERE name = 'ENCARGADO VIAJES Y COMUNICACIÓN')
    AND rp.permission_id = (SELECT id FROM permission WHERE name = 'CREAR_EXPEDICIONES')
);

INSERT INTO role_permission (role_id, permission_id)
SELECT (SELECT id FROM role WHERE name = 'ENCARGADO VIAJES Y COMUNICACIÓN'), (SELECT id FROM permission WHERE name = 'SOLICITAR_RECURSOS')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permission rp WHERE rp.role_id = (SELECT id FROM role WHERE name = 'ENCARGADO VIAJES Y COMUNICACIÓN')
    AND rp.permission_id = (SELECT id FROM permission WHERE name = 'SOLICITAR_RECURSOS')
);

INSERT INTO role_permission (role_id, permission_id)
SELECT (SELECT id FROM role WHERE name = 'ENCARGADO VIAJES Y COMUNICACIÓN'), (SELECT id FROM permission WHERE name = 'SOLICITAR_PERSONAS')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permission rp WHERE rp.role_id = (SELECT id FROM role WHERE name = 'ENCARGADO VIAJES Y COMUNICACIÓN')
    AND rp.permission_id = (SELECT id FROM permission WHERE name = 'SOLICITAR_PERSONAS')
);

INSERT INTO role_permission (role_id, permission_id)
SELECT (SELECT id FROM role WHERE name = 'ENCARGADO VIAJES Y COMUNICACIÓN'), (SELECT id FROM permission WHERE name = 'VER_LOGROS')
WHERE NOT EXISTS (
    SELECT 1 FROM role_permission rp WHERE rp.role_id = (SELECT id FROM role WHERE name = 'ENCARGADO VIAJES Y COMUNICACIÓN')
    AND rp.permission_id = (SELECT id FROM permission WHERE name = 'VER_LOGROS')
);