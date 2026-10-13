"""Datenzugriff für Produkte: hier steht das SQL, die Routen bleiben schlank."""

from decimal import Decimal

from app.db import get_db


def cents_to_euro(cents):
    """2550 -> "25.50" (Geld als Text ausgeben, ohne Rundungsfehler)."""
    return f"{Decimal(cents) / 100:.2f}"


def row_to_dict(row):
    return {
        "id": row["id"],
        "name": row["name"],
        "sku": row["sku"],
        "quantity": row["quantity"],
        "min_quantity": row["min_quantity"],
        "price": cents_to_euro(row["price_cents"]),
    }


def get_all_products():
    rows = get_db().execute("SELECT * FROM products ORDER BY id").fetchall()
    return [row_to_dict(r) for r in rows]


def get_product_by_id(product_id):
    # Das "?" ist ein Platzhalter: sqlite3 setzt den Wert sicher ein (Schutz vor SQL-Injection).
    row = get_db().execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    return row_to_dict(row) if row else None


def get_product_by_sku(sku):
    row = get_db().execute("SELECT * FROM products WHERE sku = ?", (sku,)).fetchone()
    return row_to_dict(row) if row else None


def create_product(name, sku, quantity, min_quantity, price_cents):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO products (name, sku, quantity, min_quantity, price_cents) VALUES (?, ?, ?, ?, ?)",
        (name, sku, quantity, min_quantity, price_cents),
    )
    db.commit()
    return get_product_by_id(cursor.lastrowid)


def get_low_stock_products():
    """Produkte, deren Bestand den Meldebestand erreicht oder unterschritten hat.

    Sortiert nach Dringlichkeit: das größte Defizit zuerst.
    """
    rows = get_db().execute(
        "SELECT *, (min_quantity - quantity) AS missing FROM products "
        "WHERE quantity <= min_quantity "
        "ORDER BY missing DESC, name"
    ).fetchall()
    result = []
    for row in rows:
        product = row_to_dict(row)
        product["missing"] = max(row["missing"], 0)  # wie viele Stück bis zum Meldebestand fehlen
        result.append(product)
    return result
