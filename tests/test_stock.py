def create(client, quantity=10):
    response = client.post("/products", json={"name": "Reis 1kg", "sku": "REIS-1", "quantity": quantity})
    return response.get_json()["id"]


def test_stock_in_and_out(client):
    pid = create(client, quantity=10)

    r = client.post(f"/products/{pid}/stock", json={"change": 5, "reason": "Lieferung"})
    assert r.status_code == 200
    assert r.get_json()["quantity"] == 15

    r = client.post(f"/products/{pid}/stock", json={"change": -4, "reason": "Verkauf"})
    assert r.get_json()["quantity"] == 11


def test_stock_cannot_go_negative(client):
    pid = create(client, quantity=2)

    r = client.post(f"/products/{pid}/stock", json={"change": -3})
    assert r.status_code == 400

    # Bestand ist unverändert und es wurde keine Bewegung gespeichert
    assert client.get(f"/products/{pid}").get_json()["quantity"] == 2
    assert client.get(f"/products/{pid}/movements").get_json() == []


def test_movements_are_recorded(client):
    pid = create(client)
    client.post(f"/products/{pid}/stock", json={"change": 5, "reason": "Lieferung"})
    client.post(f"/products/{pid}/stock", json={"change": -2, "reason": "Verkauf"})

    movements = client.get(f"/products/{pid}/movements").get_json()
    assert [m["change"] for m in movements] == [5, -2]
    assert movements[0]["reason"] == "Lieferung"


def test_invalid_change_is_rejected(client):
    pid = create(client)
    for bad in (0, "5", 2.5, True, None):
        r = client.post(f"/products/{pid}/stock", json={"change": bad})
        assert r.status_code == 400, bad


def test_stock_for_unknown_product_returns_404(client):
    assert client.post("/products/999/stock", json={"change": 1}).status_code == 404
