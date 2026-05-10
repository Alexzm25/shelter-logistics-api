-- Seed default camps

INSERT INTO "camp" ("name", "location", "session_time")
SELECT 'Campamento Caolin', 'Valle Caolin', 60
WHERE NOT EXISTS (
    SELECT 1 FROM "camp" WHERE "name" = 'Campamento Caolin'
);

INSERT INTO "camp" ("name", "location", "session_time")
SELECT 'Campamento Fayenza', 'Afueras de la ciudad', 60
WHERE NOT EXISTS (
    SELECT 1 FROM "camp" WHERE "name" = 'Campamento Fayenza'
);

INSERT INTO "camp" ("name", "location", "session_time")
SELECT 'Campamento Azulejo', 'Bosque Azulejo', 60
WHERE NOT EXISTS (
    SELECT 1 FROM "camp" WHERE "name" = 'Campamento Azulejo'
);

