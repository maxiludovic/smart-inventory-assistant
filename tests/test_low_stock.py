def add(client, sku, quantity, min_quantity):
    client.post("/products", json={"name": sku, "sku": sku, "quantity": quantity, "min_quantity": min_quantity})


def test_low_stock_lists_only_products_at_or_below_minimum(client):
    add(client, "OK", quantity=20, min_quantity=5)
    add(client, "GRENZE", quantity=5, min_quantity=5)
    add(client, "KNAPP", quantity=1, min_quantity=10)

    low = client.get("/products/low-stock").get_json()
    assert [p["sku"] for p in low] == ["KNAPP", "GRENZE"]  # größtes Defizit zuerst
    assert low[0]["missing"] == 9


def test_product_appears_after_sale(client):
    add(client, "MILCH", quantity=6, min_quantity=5)
    assert client.get("/products/low-stock").get_json() == []

    client.post("/products/1/stock", json={"change": -2, "reason": "Verkauf"})
    low = client.get("/products/low-stock").get_json()
    assert [p["sku"] for p in low] == ["MILCH"]
