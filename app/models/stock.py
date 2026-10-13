"""Lagerbewegungen: Bestand ändern und Historie speichern."""

from app.db import get_db


class InsufficientStockError(Exception):
    """Wird ausgelöst, wenn der Bestand durch eine Entnahme negativ würde."""


def change_stock(product_id, change, reason=None):
    """Ändert den Bestand um `change` und protokolliert die Bewegung.

    Beides passiert in EINER Transaktion: entweder beides klappt oder nichts.
    """
    db = get_db()
    try:
        # Die Bedingung "quantity + ? >= 0" steht direkt im UPDATE.
        # So kann der Bestand nie negativ werden, auch nicht bei zwei gleichzeitigen Anfragen.
        cursor = db.execute(
            "UPDATE products SET quantity = quantity + ? WHERE id = ? AND quantity + ? >= 0",
            (change, product_id, change),
        )
        if cursor.rowcount == 0:
            raise InsufficientStockError()

        db.execute(
            "INSERT INTO stock_movements (product_id, change, reason) VALUES (?, ?, ?)",
            (product_id, change, reason),
        )
        db.commit()
    except Exception:
        db.rollback()  # nichts halb speichern
        raise


def get_movements(product_id):
    rows = get_db().execute(
        "SELECT id, change, reason, created_at FROM stock_movements "
        "WHERE product_id = ? ORDER BY id",
        (product_id,),
    ).fetchall()
    return [dict(r) for r in rows]
