from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request

from app import models

products_bp = Blueprint("products", __name__, url_prefix="/products")


def is_non_negative_int(value):
    # bool ist in Python auch ein int (True == 1), deshalb extra ausschließen
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def parse_price_to_cents(value):
    """ "7.99" -> 799. Gibt None zurück, wenn der Preis ungültig ist."""
    try:
        price = Decimal(str(value))
    except InvalidOperation:
        return None
    if price < 0 or price != price.quantize(Decimal("0.01")):
        return None  # negativ oder mehr als 2 Nachkommastellen
    return int(price * 100)


def validate_product(data):
    """Prüft die Eingabe und gibt eine Liste von Fehlermeldungen zurück."""
    errors = []
    if not str(data.get("name", "")).strip():
        errors.append("name ist erforderlich")
    if not str(data.get("sku", "")).strip():
        errors.append("sku ist erforderlich")
    for field in ("quantity", "min_quantity"):
        if not is_non_negative_int(data.get(field, 0)):
            errors.append(f"{field} muss eine ganze Zahl >= 0 sein")
    if parse_price_to_cents(data.get("price", "0")) is None:
        errors.append("price muss eine Zahl >= 0 mit höchstens 2 Nachkommastellen sein")
    return errors


@products_bp.get("")
def list_products():
    return jsonify(models.get_all_products())


@products_bp.get("/low-stock")
def list_low_stock():
    """Alle Produkte, die nachbestellt werden sollten."""
    return jsonify(models.get_low_stock_products())


@products_bp.get("/<int:product_id>")
def get_product(product_id):
    product = models.get_product_by_id(product_id)
    if product is None:
        return jsonify({"error": "Produkt nicht gefunden"}), 404
    return jsonify(product)


@products_bp.post("")
def create_product():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "JSON-Body erwartet"}), 400

    errors = validate_product(data)
    if errors:
        return jsonify({"errors": errors}), 400

    sku = data["sku"].strip()
    if models.get_product_by_sku(sku):
        return jsonify({"error": "Diese SKU existiert bereits"}), 409

    product = models.create_product(
        name=data["name"].strip(),
        sku=sku,
        quantity=data.get("quantity", 0),
        min_quantity=data.get("min_quantity", 0),
        price_cents=parse_price_to_cents(data.get("price", "0")),
    )
    return jsonify(product), 201


@products_bp.post("/<int:product_id>/stock")
def change_stock(product_id):
    """Wareneingang ({"change": 10}) oder Entnahme ({"change": -3})."""
    if models.get_product_by_id(product_id) is None:
        return jsonify({"error": "Produkt nicht gefunden"}), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "JSON-Body erwartet"}), 400

    change = data.get("change")
    if not isinstance(change, int) or isinstance(change, bool) or change == 0:
        return jsonify({"error": "change muss eine ganze Zahl ungleich 0 sein"}), 400

    try:
        models.change_stock(product_id, change, data.get("reason"))
    except models.InsufficientStockError:
        return jsonify({"error": "Nicht genug Bestand für diese Entnahme"}), 400

    return jsonify(models.get_product_by_id(product_id))


@products_bp.get("/<int:product_id>/movements")
def list_movements(product_id):
    if models.get_product_by_id(product_id) is None:
        return jsonify({"error": "Produkt nicht gefunden"}), 404
    return jsonify(models.get_movements(product_id))
