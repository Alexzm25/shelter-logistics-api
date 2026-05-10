-- Seed default professions allowed by human intake workflow

INSERT INTO profession (name, is_critical)
SELECT 'EXPLORADOR', FALSE
WHERE NOT EXISTS (
    SELECT 1 FROM profession WHERE name = 'EXPLORADOR'
);

INSERT INTO profession (name, is_critical)
SELECT 'AGRICULTOR', FALSE
WHERE NOT EXISTS (
    SELECT 1 FROM profession WHERE name = 'AGRICULTOR'
);

INSERT INTO profession (name, is_critical)
SELECT 'MEDICO', FALSE
WHERE NOT EXISTS (
    SELECT 1 FROM profession WHERE name = 'MEDICO'
);
