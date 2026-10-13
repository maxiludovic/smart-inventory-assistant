import os

from flask import Flask, jsonify

from app import db


def create_app(test_config=None):
    """Application Factory: erstellt und konfiguriert die Flask-App."""
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)

    # Standard: SQLite-Datei im Ordner instance/
    app.config["DATABASE"] = os.path.join(app.instance_path, "inventory.db")

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    from app.routes.products import products_bp
    app.register_blueprint(products_bp)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    return app
