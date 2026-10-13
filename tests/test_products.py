def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_create_and_list_product(client):
    response = client.post("/products", json={
        "name": "Kaffee 500g", "sku": "KAF-500", "quantity": 20, "min_quantity": 5, "price": "7.99"
    })
    assert response.status_code == 201
    assert response.get_json()["price"] == "7.99"

    products = client.get("/products").get_json()
    assert len(products) == 1
    assert products[0]["sku"] == "KAF-500"


def test_create_product_rejects_invalid_data(client):
    response = client.post("/products", json={"name": "", "sku": "X", "quantity": -3})
    assert response.status_code == 400
    assert "name ist erforderlich" in response.get_json()["errors"]


def test_duplicate_sku_is_rejected(client):
    product = {"name": "Tee", "sku": "TEE-1", "price": "3.50"}
    assert client.post("/products", json=product).status_code == 201
    assert client.post("/products", json=product).status_code == 409


def test_unknown_product_returns_404(client):
    assert client.get("/products/999").status_code == 404


def test_price_with_too_many_decimals_is_rejected(client):
    response = client.post("/products", json={"name": "Milch", "sku": "MIL-1", "price": "1.999"})
    assert response.status_code == 400
