/*
Created: 3/1/2026
Modified: 3/22/2026
Model: PostgreSQL
Database: PostgreSQL
*/

-- Create user data types section -------------------------------------------------

CREATE TYPE "health_status_enum" AS ENUM
( 'SANO',
  'HERIDO',
  'ENFERMO',
  'MUERTO' 
);

CREATE TYPE "current_status_enum" AS ENUM
( 'TRABAJANDO',
  'EN EXPLORACIÓN',
  'TRASLADANDO RECURSOS',
  'LIBRE' 
);

CREATE TYPE "resource_category_enum" AS ENUM
( 'ALIMENTO',
  'BEBIDAS',
  'SEMILLAS',
  'MEDICINAS' 
);

CREATE TYPE "movement_type_enum" AS ENUM
( 'SALIDA',
  'INGRESO',
  'TRANSFERENCIA'
);

CREATE TYPE "request_status_enum" AS ENUM
( 'PENDIENTE',
  'APROBADO',
  'RECHAZADO' 
);

CREATE TYPE "transfer_status_enum" AS ENUM
( 'EN PREPARACIÓN',
  'DE CAMINO',
  'LLEGÓ' 
);

CREATE TYPE "exploration_status_enum" AS ENUM
( 'EN PROCESO',
  'COMPLETADA',
  'CANCELADA'
);

CREATE TYPE "ai_decision_enum" AS ENUM
( 
  'APROBADO',
  'RECHAZADO'
);

-- Create tables section -------------------------------------------------

-- Table app_user

CREATE TABLE "app_user"
(
  "id" Serial NOT NULL,
  "username" Character varying(20) NOT NULL,
  "password_hash" Character varying(255) NOT NULL,
  "created_at" Timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
  "person_id" Integer NOT NULL,
  "role_id" Integer NOT NULL
)
WITH (
  autovacuum_enabled=true)
;
COMMENT ON COLUMN "app_user"."id" IS 'Personal id for each user'
;
COMMENT ON COLUMN "app_user"."username" IS 'Unique username for each user'
;
COMMENT ON COLUMN "app_user"."password_hash" IS 'User''s password'
;
COMMENT ON COLUMN "app_user"."created_at" IS 'Timestamp when user where created in the system'
;

CREATE INDEX "IX_Relationship12" ON "app_user" ("person_id")
;

CREATE INDEX "IX_Relationship25" ON "app_user" ("role_id")
;

ALTER TABLE "app_user" ADD CONSTRAINT "PK_app_user" PRIMARY KEY ("id")
;

ALTER TABLE "app_user" ADD CONSTRAINT "username" UNIQUE ("username")
;

-- Table person

CREATE TABLE "person"
(
  "id" Serial NOT NULL,
  "name" Character varying(30) NOT NULL,
  "last_name" Character varying(50) NOT NULL,
  "age" Integer NOT NULL,
  "background_info" Text NOT NULL,
  "weight" Numeric(5,2) NOT NULL,
  "height" Numeric(5,2) NOT NULL,
  "camp_id" Integer NOT NULL,
  "current_status" "current_status_enum" NOT NULL,
  "health_status" "health_status_enum" NOT NULL,
  "camp_entry_date" Timestamp with time zone NOT NULL,
  "photo_url" Text NOT NULL,
  "is_active" Boolean NOT NULL,
  "id_card" Character varying(250) NOT NULL
)
WITH (
  autovacuum_enabled=true)
;
COMMENT ON COLUMN "person"."id" IS 'Personal id for each person'
;
COMMENT ON COLUMN "person"."name" IS 'Person''s first name'
;
COMMENT ON COLUMN "person"."last_name" IS 'Person''s last name'
;
COMMENT ON COLUMN "person"."age" IS 'Person''s age'
;
COMMENT ON COLUMN "person"."background_info" IS 'Person''s background info about its days surviving the apocalypse'
;
COMMENT ON COLUMN "person"."weight" IS 'Person''s weight'
;
COMMENT ON COLUMN "person"."height" IS 'Person''s height'
;
COMMENT ON COLUMN "person"."current_status" IS 'Current status (''TRABAJANDO'', ''EN EXPLORACIÓN'', ''TRASLADANDO RECURSOS'', ''LIBRE'')'
;
COMMENT ON COLUMN "person"."health_status" IS 'Person''s health status (''SANO'', ''HERIDO'', ''ENFERMO'', ''MUERTO'')'
;
COMMENT ON COLUMN "person"."camp_entry_date" IS 'Timestamp when the person arrived in the camp'
;
COMMENT ON COLUMN "person"."photo_url" IS 'Photo''s url where is save locally'
;
COMMENT ON COLUMN "person"."is_active" IS 'To check if person is active or not in the system'
;
COMMENT ON COLUMN "person"."id_card" IS 'Identification card for each Person'
;

CREATE INDEX "IX_Relationship13" ON "person" ("camp_id")
;

ALTER TABLE "person" ADD CONSTRAINT "PK_person" PRIMARY KEY ("id")
;

-- Table profession

CREATE TABLE "profession"
(
  "id" Serial NOT NULL,
  "is_critical" Boolean DEFAULT FALSE NOT NULL,
  "name" Character varying(50) NOT NULL
)
WITH (
  autovacuum_enabled=true)
;
COMMENT ON COLUMN "profession"."id" IS 'Profession''s id'
;
COMMENT ON COLUMN "profession"."is_critical" IS 'Attribute to check if a profession is in a critical situation or not. Basically if there is not workers available the situation is critical (true).'
;
COMMENT ON COLUMN "profession"."name" IS 'Profession''s name'
;

ALTER TABLE "profession" ADD CONSTRAINT "PK_profession" PRIMARY KEY ("id")
;

-- Table resource

CREATE TABLE "resource"
(
  "id" Serial NOT NULL,
  "name" Character varying(40) NOT NULL,
  "category" "resource_category_enum" NOT NULL
)
WITH (
  autovacuum_enabled=true)
;
COMMENT ON COLUMN "resource"."id" IS 'Resource''s id'
;
COMMENT ON COLUMN "resource"."name" IS 'Resource''s name'
;
COMMENT ON COLUMN "resource"."category" IS 'Resource''s category (''ALIMENTOS'', ''BEBIDAS'', ''SEMILLAS'',''MEDICINAS'')'
;

ALTER TABLE "resource" ADD CONSTRAINT "PK_resource" PRIMARY KEY ("id")
;

-- Table camp

CREATE TABLE "camp"
(
  "id" Serial NOT NULL,
  "name" Character varying(40) NOT NULL,
  "location" Character varying(100) NOT NULL,
  "created_at" Timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
  "session_time" Integer NOT NULL
)
WITH (
  autovacuum_enabled=true)
;
COMMENT ON COLUMN "camp"."id" IS 'Camp ID'
;
COMMENT ON COLUMN "camp"."name" IS 'Camp''s name'
;
COMMENT ON COLUMN "camp"."location" IS 'Camp''s location'
;
COMMENT ON COLUMN "camp"."created_at" IS 'Timestamp when camp was created'
;
COMMENT ON COLUMN "camp"."session_time" IS 'How mucho a session can long in minutes (its the cookies time session value) '
;

ALTER TABLE "camp" ADD CONSTRAINT "PK_camp" PRIMARY KEY ("id")
;

-- Table inventory

CREATE TABLE "inventory"
(
  "id" Serial NOT NULL,
  "maximum_stock" Integer NOT NULL,
  "camp_id" Integer NOT NULL
)
WITH (
  autovacuum_enabled=true)
;
COMMENT ON COLUMN "inventory"."id" IS 'Inventory''s id'
;
COMMENT ON COLUMN "inventory"."maximum_stock" IS 'Its the capacity of storage in the inventory'
;

CREATE INDEX "IX_Relationship15" ON "inventory" ("camp_id")
;

ALTER TABLE "inventory" ADD CONSTRAINT "PK_inventory" PRIMARY KEY ("id")
;

-- Table transfer_request

CREATE TABLE "transfer_request"
(
  "id" Serial NOT NULL,
  "created_at" Timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
  "from_camp_id" Integer NOT NULL,
  "to_camp_id" Integer NOT NULL,
  "request_status" "request_status_enum" NOT NULL,
  "transfer_status" "transfer_status_enum",
  "arrival_date" Date,
  "departure_date" Date NOT NULL,
  "authorized_by" Character varying(80),
  "is_resource_transfer" Boolean DEFAULT TRUE NOT NULL
)
WITH (
  autovacuum_enabled=true)
;
COMMENT ON COLUMN "transfer_request"."id" IS 'Transfer request ID'
;
COMMENT ON COLUMN "transfer_request"."created_at" IS 'Date when the request was created'
;
COMMENT ON COLUMN "transfer_request"."from_camp_id" IS 'Camp ID from the request is made'
;
COMMENT ON COLUMN "transfer_request"."to_camp_id" IS 'Camp ID where the request is sent'
;
COMMENT ON COLUMN "transfer_request"."request_status" IS 'Request''s status (''PENDIENTE'', ''APROBADA'', ''RECHAZADA'')'
;
COMMENT ON COLUMN "transfer_request"."transfer_status" IS 'Transfer''s status (''EN PREPARACIÓN'', ''DE CAMINO'', ''LLEGÓ'')'
;
COMMENT ON COLUMN "transfer_request"."arrival_date" IS 'Date the requested transfer arrived at the camp'
;
COMMENT ON COLUMN "transfer_request"."departure_date" IS 'Date the requested transfer left the camp'
;

CREATE INDEX "IX_Relationship22" ON "transfer_request" ("from_camp_id")
;

CREATE INDEX "IX_Relationship23" ON "transfer_request" ("to_camp_id")
;

ALTER TABLE "transfer_request" ADD CONSTRAINT "PK_transfer_request" PRIMARY KEY ("id")
;

-- Table exploration

CREATE TABLE "exploration"
(
  "id" Serial NOT NULL,
  "start_date" Timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
  "return_date" Timestamp with time zone,
  "exploration_status" "exploration_status_enum" NOT NULL,
  "camp_id" Integer NOT NULL,
  "extra_days" Integer NOT NULL,
  "ration_per_person" Integer DEFAULT 1 NOT NULL,
  "max_extra_days" Integer DEFAULT 0 NOT NULL,
  "estimated_days" Integer DEFAULT 1 NOT NULL
)
WITH (
  autovacuum_enabled=true)
;
COMMENT ON COLUMN "exploration"."id" IS 'Exploration ID'
;
COMMENT ON COLUMN "exploration"."start_date" IS 'Timestamp when the exploration started'
;
COMMENT ON COLUMN "exploration"."return_date" IS 'Timestamp when the explorers return to the camp'
;
COMMENT ON COLUMN "exploration"."exploration_status" IS 'Exploration''s status (''EN PROCESO'', ''COMPLETADA'', ''CANCELADA'')'
;
COMMENT ON COLUMN "exploration"."extra_days" IS 'Extra days of exploration if they are needed'
;
COMMENT ON COLUMN "exploration"."ration_per_person" IS 'Ration per person per day'
;
COMMENT ON COLUMN "exploration"."max_extra_days" IS 'Number of extra days a exploration could last'
;
COMMENT ON COLUMN "exploration"."estimated_days" IS 'Number of estimated days for a exploration'
;

CREATE INDEX "IX_Relationship29" ON "exploration" ("camp_id")
;

ALTER TABLE "exploration" ADD CONSTRAINT "PK_exploration" PRIMARY KEY ("id")
;

-- Table exploration_member

CREATE TABLE "exploration_member"
(
  "person_id" Integer NOT NULL,
  "exploration_id" Integer NOT NULL
)
WITH (
  autovacuum_enabled=true)
;

ALTER TABLE "exploration_member" ADD CONSTRAINT "PK_exploration_member" PRIMARY KEY ("person_id","exploration_id")
;

-- Table profession_assignment

CREATE TABLE "profession_assignment"
(
  "id" Serial NOT NULL,
  "start_date" Date NOT NULL,
  "end_date" Date,
  "reason" Character varying(100) NOT NULL,
  "is_main_profession" Boolean NOT NULL,
  "profession_id" Integer NOT NULL,
  "person_id" Integer NOT NULL,
  "is_active" Boolean NOT NULL
)
WITH (
  autovacuum_enabled=true)
;
COMMENT ON COLUMN "profession_assignment"."id" IS 'Profession assignment ID'
;
COMMENT ON COLUMN "profession_assignment"."start_date" IS 'Date when person started his profession in the camp'
;
COMMENT ON COLUMN "profession_assignment"."end_date" IS 'Date when person ended its profession (in critical cases).'
;
COMMENT ON COLUMN "profession_assignment"."reason" IS 'Reason for the assignment in the profession'
;
COMMENT ON COLUMN "profession_assignment"."is_main_profession" IS 'Boolean to check if the assignment profession is its main job or not'
;
COMMENT ON COLUMN "profession_assignment"."is_active" IS 'Boolean to check if the assignment is active or not'
;

CREATE INDEX "IX_Relationship5" ON "profession_assignment" ("profession_id")
;

CREATE INDEX "IX_Relationship6" ON "profession_assignment" ("person_id")
;

ALTER TABLE "profession_assignment" ADD CONSTRAINT "PK_profession_assignment" PRIMARY KEY ("id")
;

-- Table transfer_resource

CREATE TABLE "transfer_resource"
(
  "id" Serial NOT NULL,
  "transfer_amount" Integer NOT NULL,
  "resource_id" Integer NOT NULL,
  "request_id" Integer NOT NULL
)
WITH (
  autovacuum_enabled=true)
;
COMMENT ON COLUMN "transfer_resource"."id" IS 'Transfer resource ID'
;
COMMENT ON COLUMN "transfer_resource"."transfer_amount" IS 'Amount''s resource that will be transfer'
;

CREATE INDEX "IX_Relationship7" ON "transfer_resource" ("resource_id")
;

CREATE INDEX "IX_Relationship8" ON "transfer_resource" ("request_id")
;

ALTER TABLE "transfer_resource" ADD CONSTRAINT "PK_transfer_resource" PRIMARY KEY ("id")
;

-- Table inventory_resource

CREATE TABLE "inventory_resource"
(
  "id" Serial NOT NULL,
  "quantity" Integer NOT NULL,
  "minimum_stock_level" Integer NOT NULL,
  "inventory_id" Integer NOT NULL,
  "resource_id" Integer NOT NULL
)
WITH (
  autovacuum_enabled=true)
;
COMMENT ON COLUMN "inventory_resource"."id" IS 'Inventory Resource ID'
;
COMMENT ON COLUMN "inventory_resource"."quantity" IS 'Resource quantity that is stored in the inventory'
;
COMMENT ON COLUMN "inventory_resource"."minimum_stock_level" IS 'Its the minimum level before notify the system'
;

CREATE INDEX "IX_Relationship9" ON "inventory_resource" ("inventory_id")
;

CREATE INDEX "IX_Relationship10" ON "inventory_resource" ("resource_id")
;

ALTER TABLE "inventory_resource" ADD CONSTRAINT "PK_inventory_resource" PRIMARY KEY ("id")
;

-- Table inventory_movement

CREATE TABLE "inventory_movement"
(
  "id" Serial NOT NULL,
  "created_at" Timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
  "quantity" Integer NOT NULL,
  "inventory_resource_id" Integer NOT NULL,
  "movement_type" "movement_type_enum" NOT NULL,
  "transfer_request_id" Integer
)
WITH (
  autovacuum_enabled=true)
;
COMMENT ON COLUMN "inventory_movement"."id" IS 'Inventory Movement ID'
;
COMMENT ON COLUMN "inventory_movement"."created_at" IS 'Date when movement in inventory was made'
;
COMMENT ON COLUMN "inventory_movement"."quantity" IS 'Quantity of the resource being move'
;
COMMENT ON COLUMN "inventory_movement"."movement_type" IS 'Movement type (''SALIDA'', ''INGRESO'', ''TRANSFERENCIA'').'
;

CREATE INDEX "IX_Relationship14" ON "inventory_movement" ("inventory_resource_id")
;

ALTER TABLE "inventory_movement" ADD CONSTRAINT "PK_inventory_movement" PRIMARY KEY ("id")
;

-- Table exploration_loot

CREATE TABLE "exploration_loot"
(
  "id" Serial NOT NULL,
  "quantity" Integer NOT NULL,
  "resource_id" Integer NOT NULL,
  "exploration_id" Integer NOT NULL,
  "is_added_to_inventory" Boolean DEFAULT FALSE NOT NULL
)
WITH (
  autovacuum_enabled=true)
;
COMMENT ON COLUMN "exploration_loot"."id" IS 'Exploration loot ID'
;
COMMENT ON COLUMN "exploration_loot"."quantity" IS 'Quantity of loot collected in the exploration'
;
COMMENT ON COLUMN "exploration_loot"."is_added_to_inventory" IS 'To check if the exploration loot have been added to the inventory or not'
;

CREATE INDEX "IX_Relationship16" ON "exploration_loot" ("resource_id")
;

CREATE INDEX "IX_Relationship17" ON "exploration_loot" ("exploration_id")
;

ALTER TABLE "exploration_loot" ADD CONSTRAINT "PK_exploration_loot" PRIMARY KEY ("id")
;

-- Table profession_production

CREATE TABLE "profession_production"
(
  "id" Serial NOT NULL,
  "production_quantity" Integer NOT NULL,
  "resource_id" Integer NOT NULL,
  "profession_id" Integer NOT NULL
)
WITH (
  autovacuum_enabled=true)
;
COMMENT ON COLUMN "profession_production"."id" IS 'Profession production ID'
;
COMMENT ON COLUMN "profession_production"."production_quantity" IS 'Quantity of resources obtained in production'
;

CREATE INDEX "IX_Relationship18" ON "profession_production" ("resource_id")
;

CREATE INDEX "IX_Relationship19" ON "profession_production" ("profession_id")
;

ALTER TABLE "profession_production" ADD CONSTRAINT "PK_profession_production" PRIMARY KEY ("id")
;

-- Table ai_log

CREATE TABLE "ai_log"
(
  "id" Serial NOT NULL,
  "decision_reason" Text NOT NULL,
  "created_at" Timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
  "ai_decision" "ai_decision_enum" NOT NULL,
  "evaluation_context" Jsonb NOT NULL,
  "camp_id" Integer,
  "person_id" Integer,
  "final_user_decision" Boolean NOT NULL
)
WITH (
  autovacuum_enabled=true)
;
COMMENT ON COLUMN "ai_log"."id" IS 'AI log ID'
;
COMMENT ON COLUMN "ai_log"."decision_reason" IS 'Reason for the system''s AI decision'
;
COMMENT ON COLUMN "ai_log"."created_at" IS 'Timestamp when AI log was made'
;
COMMENT ON COLUMN "ai_log"."ai_decision" IS 'Decision made by the sistem''s AI'
;
COMMENT ON COLUMN "ai_log"."evaluation_context" IS 'JSON with information needed for the system''s AI'
;
COMMENT ON COLUMN "ai_log"."final_user_decision" IS 'True = approved, False = disapproved'
;

CREATE INDEX "IX_Relationship28" ON "ai_log" ("camp_id")
;

CREATE INDEX "IX_Relationship32" ON "ai_log" ("person_id")
;

ALTER TABLE "ai_log" ADD CONSTRAINT "PK_ai_log" PRIMARY KEY ("id")
;

-- Table role

CREATE TABLE "role"
(
  "id" Serial NOT NULL,
  "name" Character varying(40) NOT NULL,
  "description" Character varying(100) NOT NULL
)
WITH (
  autovacuum_enabled=true)
;
COMMENT ON COLUMN "role"."id" IS 'Role ID'
;
COMMENT ON COLUMN "role"."name" IS 'Role''s name'
;
COMMENT ON COLUMN "role"."description" IS 'Short description about the role'
;

ALTER TABLE "role" ADD CONSTRAINT "PK_role" PRIMARY KEY ("id")
;

-- Table permission

CREATE TABLE "permission"
(
  "id" Serial NOT NULL,
  "name" Character varying(40) NOT NULL,
  "description" Character varying(100) NOT NULL
)
WITH (
  autovacuum_enabled=true)
;
COMMENT ON COLUMN "permission"."id" IS 'Permission ID'
;
COMMENT ON COLUMN "permission"."name" IS 'Permission''s name'
;
COMMENT ON COLUMN "permission"."description" IS 'Permission''s description about what it can do.'
;

ALTER TABLE "permission" ADD CONSTRAINT "PK_permission" PRIMARY KEY ("id")
;

-- Table role_permission

CREATE TABLE "role_permission"
(
  "role_id" Integer NOT NULL,
  "permission_id" Integer NOT NULL
)
WITH (
  autovacuum_enabled=true)
;

ALTER TABLE "role_permission" ADD CONSTRAINT "PK_role_permission" PRIMARY KEY ("role_id","permission_id")
;

-- Table achievement

CREATE TABLE "achievement"
(
  "id" Serial NOT NULL,
  "name" Character varying(50) NOT NULL,
  "description" Character varying(200) NOT NULL,
  "condition_value" Integer NOT NULL,
  "icon_url" Character varying(255) NOT NULL
)
WITH (
  autovacuum_enabled=true)
;
COMMENT ON COLUMN "achievement"."id" IS 'Achievement ID'
;
COMMENT ON COLUMN "achievement"."name" IS 'Achievement''s name'
;
COMMENT ON COLUMN "achievement"."description" IS 'Achievement''s description'
;
COMMENT ON COLUMN "achievement"."condition_value" IS 'It is the condition to unlock the achievement'
;
COMMENT ON COLUMN "achievement"."icon_url" IS 'Icon''s URL of local files'
;

ALTER TABLE "achievement" ADD CONSTRAINT "PK_achievement" PRIMARY KEY ("id")
;

ALTER TABLE "achievement" ADD CONSTRAINT "name" UNIQUE ("name")
;

-- Table user_achievement

CREATE TABLE "user_achievement"
(
  "user_id" Integer NOT NULL,
  "achievement_id" Integer NOT NULL,
  "is_unlocked" Boolean NOT NULL,
  "unlocked_at" Timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
)
WITH (
  autovacuum_enabled=true)
;
COMMENT ON COLUMN "user_achievement"."is_unlocked" IS 'Boolean to check if the achievement is unlocked'
;
COMMENT ON COLUMN "user_achievement"."unlocked_at" IS 'Timestamp when achievement was unlocked'
;

ALTER TABLE "user_achievement" ADD CONSTRAINT "PK_user_achievement" PRIMARY KEY ("user_id","achievement_id")
;

-- Table daily_ration_log

CREATE TABLE "daily_ration_log"
(
  "id" Serial NOT NULL,
  "persons_fed" Integer NOT NULL,
  "executed_at" Timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
  "camp_id" Integer
)
WITH (
  autovacuum_enabled=true)
;
COMMENT ON COLUMN "daily_ration_log"."id" IS 'ID for each daily ration log'
;
COMMENT ON COLUMN "daily_ration_log"."persons_fed" IS 'Number of persons who have been fed'
;
COMMENT ON COLUMN "daily_ration_log"."executed_at" IS 'Timestamp when daily ration were executed in the system (once per day)'
;

CREATE INDEX "IX_Relationship31" ON "daily_ration_log" ("camp_id")
;

ALTER TABLE "daily_ration_log" ADD CONSTRAINT "PK_daily_ration_log" PRIMARY KEY ("id")
;

-- Table production_log

CREATE TABLE "production_log"
(
  "id" Serial NOT NULL,
  "actual_quantity" Integer NOT NULL,
  "expected_quantity" Integer NOT NULL,
  "camp_id" Integer NOT NULL,
  "person_id" Integer NOT NULL,
  "resource_id" Integer NOT NULL,
  "profession_id" Integer NOT NULL
)
WITH (
  autovacuum_enabled=true)
;
COMMENT ON COLUMN "production_log"."id" IS 'ID for each production log'
;
COMMENT ON COLUMN "production_log"."actual_quantity" IS 'Actual quantity produced'
;
COMMENT ON COLUMN "production_log"."expected_quantity" IS 'This is the expected quantity based on entity profession_production'
;

CREATE INDEX "IX_Relationship34" ON "production_log" ("camp_id")
;

CREATE INDEX "IX_Relationship35" ON "production_log" ("person_id")
;

CREATE INDEX "IX_Relationship36" ON "production_log" ("resource_id")
;

CREATE INDEX "IX_Relationship37" ON "production_log" ("profession_id")
;

ALTER TABLE "production_log" ADD CONSTRAINT "PK_production_log" PRIMARY KEY ("id")
;

-- Table transfer_participants

CREATE TABLE "transfer_participants"
(
  "person_id" Integer NOT NULL,
  "request_id" Integer NOT NULL,
  "is_transfer_active" Boolean NOT NULL
)
WITH (
  autovacuum_enabled=true)
;
COMMENT ON COLUMN "transfer_participants"."is_transfer_active" IS 'Attribute to check if the participant is in an active transfer
'
;

ALTER TABLE "transfer_participants" ADD CONSTRAINT "PK_transfer_participants" PRIMARY KEY ("person_id","request_id")
;

-- Create foreign keys (relationships) section -------------------------------------------------

ALTER TABLE "exploration_member"
  ADD CONSTRAINT "Relationship3"
    FOREIGN KEY ("person_id")
    REFERENCES "person" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "exploration_member"
  ADD CONSTRAINT "Relationship4"
    FOREIGN KEY ("exploration_id")
    REFERENCES "exploration" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "profession_assignment"
  ADD CONSTRAINT "Relationship5"
    FOREIGN KEY ("profession_id")
    REFERENCES "profession" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "profession_assignment"
  ADD CONSTRAINT "Relationship6"
    FOREIGN KEY ("person_id")
    REFERENCES "person" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "transfer_resource"
  ADD CONSTRAINT "Relationship7"
    FOREIGN KEY ("resource_id")
    REFERENCES "resource" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "transfer_resource"
  ADD CONSTRAINT "Relationship8"
    FOREIGN KEY ("request_id")
    REFERENCES "transfer_request" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "inventory_resource"
  ADD CONSTRAINT "Relationship9"
    FOREIGN KEY ("inventory_id")
    REFERENCES "inventory" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "inventory_resource"
  ADD CONSTRAINT "Relationship10"
    FOREIGN KEY ("resource_id")
    REFERENCES "resource" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "inventory_movement"
  ADD CONSTRAINT "Relationship38"
    FOREIGN KEY ("transfer_request_id")
    REFERENCES "transfer_request" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "app_user"
  ADD CONSTRAINT "Relationship12"
    FOREIGN KEY ("person_id")
    REFERENCES "person" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "person"
  ADD CONSTRAINT "Relationship13"
    FOREIGN KEY ("camp_id")
    REFERENCES "camp" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "inventory_movement"
  ADD CONSTRAINT "Relationship14"
    FOREIGN KEY ("inventory_resource_id")
    REFERENCES "inventory_resource" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "inventory"
  ADD CONSTRAINT "Relationship15"
    FOREIGN KEY ("camp_id")
    REFERENCES "camp" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "exploration_loot"
  ADD CONSTRAINT "Relationship16"
    FOREIGN KEY ("resource_id")
    REFERENCES "resource" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "exploration_loot"
  ADD CONSTRAINT "Relationship17"
    FOREIGN KEY ("exploration_id")
    REFERENCES "exploration" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "profession_production"
  ADD CONSTRAINT "Relationship18"
    FOREIGN KEY ("resource_id")
    REFERENCES "resource" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "profession_production"
  ADD CONSTRAINT "Relationship19"
    FOREIGN KEY ("profession_id")
    REFERENCES "profession" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "role_permission"
  ADD CONSTRAINT "Relationship20"
    FOREIGN KEY ("role_id")
    REFERENCES "role" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "role_permission"
  ADD CONSTRAINT "Relationship21"
    FOREIGN KEY ("permission_id")
    REFERENCES "permission" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "transfer_request"
  ADD CONSTRAINT "Relationship22"
    FOREIGN KEY ("from_camp_id")
    REFERENCES "camp" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "transfer_request"
  ADD CONSTRAINT "Relationship23"
    FOREIGN KEY ("to_camp_id")
    REFERENCES "camp" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "app_user"
  ADD CONSTRAINT "Relationship25"
    FOREIGN KEY ("role_id")
    REFERENCES "role" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "user_achievement"
  ADD CONSTRAINT "Relationship26"
    FOREIGN KEY ("user_id")
    REFERENCES "app_user" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "user_achievement"
  ADD CONSTRAINT "Relationship27"
    FOREIGN KEY ("achievement_id")
    REFERENCES "achievement" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "ai_log"
  ADD CONSTRAINT "Relationship28"
    FOREIGN KEY ("camp_id")
    REFERENCES "camp" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "exploration"
  ADD CONSTRAINT "Relationship29"
    FOREIGN KEY ("camp_id")
    REFERENCES "camp" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "daily_ration_log"
  ADD CONSTRAINT "Relationship31"
    FOREIGN KEY ("camp_id")
    REFERENCES "camp" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "ai_log"
  ADD CONSTRAINT "Relationship32"
    FOREIGN KEY ("person_id")
    REFERENCES "person" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "production_log"
  ADD CONSTRAINT "Relationship34"
    FOREIGN KEY ("camp_id")
    REFERENCES "camp" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "production_log"
  ADD CONSTRAINT "Relationship35"
    FOREIGN KEY ("person_id")
    REFERENCES "person" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "production_log"
  ADD CONSTRAINT "Relationship36"
    FOREIGN KEY ("resource_id")
    REFERENCES "resource" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "production_log"
  ADD CONSTRAINT "Relationship37"
    FOREIGN KEY ("profession_id")
    REFERENCES "profession" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "transfer_participants"
  ADD CONSTRAINT "Relationship38"
    FOREIGN KEY ("person_id")
    REFERENCES "person" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

ALTER TABLE "transfer_participants"
  ADD CONSTRAINT "Relationship39"
    FOREIGN KEY ("request_id")
    REFERENCES "transfer_request" ("id")
      ON DELETE NO ACTION
      ON UPDATE NO ACTION
;

