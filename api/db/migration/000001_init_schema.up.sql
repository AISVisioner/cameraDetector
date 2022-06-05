CREATE TABLE "admins" (
  "admin_name" varchar PRIMARY KEY,
  "hashed_password" varchar NOT NULL,
  "full_name" varchar NOT NULL,
  "email" varchar UNIQUE NOT NULL,
  "password_changed_at" timestamptz NOT NULL DEFAULT '0001-01-01',
  "created_at" timestamptz NOT NULL DEFAULT (now()),
  "changed_user_id" uuid DEFAULT null,
  "deleted_user_id" uuid DEFAULT null
);

CREATE TABLE "visitors" (
  "visitor_id" uuid PRIMARY KEY,
  "visitor_name" varchar NOT NULL,
  "encoding" _float8 NOT NULL,
  "image" varchar NOT NULL,
  "visits_count" integer NOT NULL DEFAULT 1,
  "recent_access_at" timestamptz NOT NULL DEFAULT (now()),
  "created_at" timestamptz NOT NULL DEFAULT (now()),
  "updated_at" timestamptz NOT NULL DEFAULT (now())
);

CREATE TABLE "sessions" (
  "session_id" uuid PRIMARY KEY,
  "username" varchar NOT NULL,
  "refresh_token" varchar NOT NULL,
  "user_agent" varchar NOT NULL,
  "client_ip" varchar NOT NULL,
  "is_blocked" boolean NOT NULL DEFAULT false,
  "expires_at" timestamptz NOT NULL,
  "created_at" timestamptz NOT NULL DEFAULT (now())
);

ALTER TABLE "admins" ADD FOREIGN KEY ("changed_user_id") REFERENCES "visitors" ("visitor_id");

ALTER TABLE "admins" ADD FOREIGN KEY ("deleted_user_id") REFERENCES "visitors" ("visitor_id");

ALTER TABLE "sessions" ADD FOREIGN KEY ("username") REFERENCES "admins" ("admin_name");
