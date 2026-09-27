-- ============================================================
--  Medicine Reminder System – Supabase SQL Schema
--  Run this in: Supabase Dashboard → SQL Editor → New Query
-- ============================================================

-- 1. Users table
CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(100) NOT NULL,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at    TIMESTAMP DEFAULT NOW()
);

-- 2. Medicines table
CREATE TABLE IF NOT EXISTS medicines (
    id             SERIAL PRIMARY KEY,
    user_id        INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name           VARCHAR(200) NOT NULL,
    dosage         VARCHAR(100) NOT NULL,
    frequency      VARCHAR(100) NOT NULL,
    reminder_time  TIME        NOT NULL,        -- e.g. 08:00
    start_date     DATE        NOT NULL,
    end_date       DATE        NOT NULL,
    instructions   TEXT        DEFAULT '',
    created_at     TIMESTAMP   DEFAULT NOW()
);

-- 3. Reminders table  (one row = one scheduled dose on a specific date)
CREATE TABLE IF NOT EXISTS reminders (
    id             SERIAL PRIMARY KEY,
    medicine_id    INTEGER NOT NULL REFERENCES medicines(id) ON DELETE CASCADE,
    user_id        INTEGER NOT NULL REFERENCES users(id)    ON DELETE CASCADE,
    scheduled_time TIME    NOT NULL,
    scheduled_date DATE    NOT NULL,
    status         VARCHAR(20) DEFAULT 'pending',  -- pending | taken | skipped
    created_at     TIMESTAMP DEFAULT NOW()
);

-- 4. Dose History table
CREATE TABLE IF NOT EXISTS dose_history (
    id             SERIAL PRIMARY KEY,
    user_id        INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reminder_id    INTEGER REFERENCES reminders(id),
    medicine_name  VARCHAR(200),
    taken_date     DATE,
    taken_time     VARCHAR(10),
    status         VARCHAR(20),     -- taken | skipped
    created_at     TIMESTAMP DEFAULT NOW()
);

-- ── Optional: Row Level Security (RLS) ─────────────────────────────────────
-- Enable so that users only see their own data (recommended for production)
-- ALTER TABLE medicines    ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE reminders    ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE dose_history ENABLE ROW LEVEL SECURITY;

-- For this prototype, disable RLS so the Python backend can read/write freely:
-- (Supabase Anon key + service_role key bypass RLS anyway at server level)
