CREATE TABLE IF NOT EXISTS users (
    user_id BIGSERIAL,
    username TEXT UNIQUE NOT NULL,
    avatar_url TEXT NOT NULL
);


DO $$ BEGIN
    CREATE TYPE session_status AS ENUM ('valid', 'revoked');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS sessions (
    session_id UUID DEFAULT uuid_generate_v4() NOT NULL,
    user_id BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP + INTERVAL '1 day' NOT NULL,
    status session_status NOT NULL
);
