-- Datenbankschema für Smart Inventory Assistant

CREATE TABLE IF NOT EXISTS products (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT    NOT NULL,
    sku          TEXT    NOT NULL UNIQUE,           -- Artikelnummer
    quantity     INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    min_quantity INTEGER NOT NULL DEFAULT 0 CHECK (min_quantity >= 0),  -- Meldebestand
    price_cents  INTEGER NOT NULL DEFAULT 0 CHECK (price_cents >= 0)    -- Preis in Cent
);

-- Historique: jede Lagerbewegung wird protokolliert (wer nachrechnen will, kann es)
CREATE TABLE IF NOT EXISTS stock_movements (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id  INTEGER NOT NULL REFERENCES products(id),
    change      INTEGER NOT NULL CHECK (change <> 0),   -- +10 = Wareneingang, -3 = Verkauf
    reason      TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);
