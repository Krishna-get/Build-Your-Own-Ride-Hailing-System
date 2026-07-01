-- starter/schema.sql
-- PostgreSQL schema for the Week 5 deliverable.
-- Run this against your database before starting the FastAPI implementation.
--
-- Usage:
--   psql -U postgres -d ridehailing -f schema.sql
--
-- This covers the 5 core tables needed for Weeks 5-8.
-- You will likely ALTER these as dispatch/pricing logic lands in later weeks
-- — that's expected, schemas evolve.

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ── Users (riders and drivers share this table, distinguished by `role`) ──────

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,   -- store bcrypt hash, never plaintext
    role VARCHAR(10) NOT NULL CHECK (role IN ('rider', 'driver')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ── Drivers (extends users with driver-specific fields) ───────────────────────

CREATE TABLE drivers (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    vehicle_make VARCHAR(50),
    vehicle_model VARCHAR(50),
    license_plate VARCHAR(20),
    status VARCHAR(20) NOT NULL DEFAULT 'OFFLINE'
        CHECK (status IN ('OFFLINE', 'ONLINE', 'EN_ROUTE', 'ON_TRIP')),
    rating NUMERIC(3,2) DEFAULT 5.00
);

-- ── Driver locations (latest known position — overwritten frequently) ─────────

CREATE TABLE driver_locations (
    driver_id UUID PRIMARY KEY REFERENCES drivers(user_id) ON DELETE CASCADE,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index for fast lookups when scanning all online drivers
CREATE INDEX idx_driver_locations_updated_at ON driver_locations(updated_at);

-- ── Trips ──────────────────────────────────────────────────────────────────────

CREATE TABLE trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rider_id UUID NOT NULL REFERENCES users(id),
    driver_id UUID REFERENCES drivers(user_id),  -- NULL until matched

    pickup_lat DOUBLE PRECISION NOT NULL,
    pickup_lng DOUBLE PRECISION NOT NULL,
    dropoff_lat DOUBLE PRECISION NOT NULL,
    dropoff_lng DOUBLE PRECISION NOT NULL,

    status VARCHAR(20) NOT NULL DEFAULT 'REQUESTED'
        CHECK (status IN (
            'REQUESTED', 'MATCHING', 'PENDING_ACCEPT', 'ACCEPTED',
            'EN_ROUTE', 'IN_TRIP', 'COMPLETED', 'RATED', 'CANCELLED'
        )),

    fare_total NUMERIC(10,2),       -- filled in once Pricing Service runs (Week 8)
    surge_multiplier NUMERIC(3,2) DEFAULT 1.00,

    idempotency_key VARCHAR(100) UNIQUE,  -- prevents duplicate ride requests

    requested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_trips_rider_id ON trips(rider_id);
CREATE INDEX idx_trips_driver_id ON trips(driver_id);
CREATE INDEX idx_trips_status ON trips(status);

-- ── Payments ───────────────────────────────────────────────────────────────────

CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    amount NUMERIC(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'COMPLETED', 'FAILED', 'REFUNDED')),
    paid_at TIMESTAMPTZ
);

-- ── Seed data for local testing ────────────────────────────────────────────────

INSERT INTO users (username, password_hash, role) VALUES
    ('rider1', '$2b$12$placeholder_hash_replace_with_real_bcrypt', 'rider'),
    ('driver1', '$2b$12$placeholder_hash_replace_with_real_bcrypt', 'driver');

-- Note: generate real bcrypt hashes using passlib in your seed script,
-- don't hardcode plaintext-derived hashes in production schemas like this.
