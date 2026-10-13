import sqlite3
from pathlib import Path

from flask import current_app, g


def get_db():
    """Gibt die Datenbankverbindung für die aktuelle Anfrage zurück (eine pro Anfrage)."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row  # Zeilen wie Dictionaries lesen: row["name"]
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(exception=None):
    """Schließt die Verbindung am Ende jeder Anfrage."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Erstellt die Tabellen aus schema.sql (falls sie noch nicht existieren)."""
    schema = (Path(__file__).parent / "schema.sql").read_text(encoding="utf-8")
    get_db().executescript(schema)


def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
