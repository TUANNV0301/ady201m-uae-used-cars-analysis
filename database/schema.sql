PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS make (
    make_id INTEGER PRIMARY KEY,
    make_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS body_type (
    body_type_id INTEGER PRIMARY KEY,
    body_type_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS emirate (
    emirate_id INTEGER PRIMARY KEY,
    emirate_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS car_listing (
    listing_id INTEGER PRIMARY KEY,
    make_id INTEGER NOT NULL REFERENCES make(make_id),
    model TEXT NOT NULL,
    year INTEGER NOT NULL,
    price_aed REAL NOT NULL CHECK (price_aed > 0),
    mileage_km INTEGER NOT NULL CHECK (mileage_km >= 0),
    body_type_id INTEGER NOT NULL REFERENCES body_type(body_type_id),
    cylinders INTEGER,
    transmission TEXT,
    fuel_type TEXT,
    color TEXT,
    emirate_id INTEGER NOT NULL REFERENCES emirate(emirate_id),
    description TEXT
);

CREATE INDEX IF NOT EXISTS idx_listing_year ON car_listing(year);
CREATE INDEX IF NOT EXISTS idx_listing_price ON car_listing(price_aed);
CREATE INDEX IF NOT EXISTS idx_listing_mileage ON car_listing(mileage_km);
