def seed(client, headers):
    customer = client.post("/api/customers", headers=headers, json={"name": "Northwind", "email": "ops@northwind.example.com"}).json()
    product = client.post("/api/products", headers=headers, json={"name": "Scanner", "sku": "SCN-1", "unit_price": "25.00", "quantity": 5, "low_stock_threshold": 2}).json()
    return customer, product


def test_order_creation_decrements_inventory(client, auth_headers):
    customer, product = seed(client, auth_headers)
    response = client.post("/api/orders", headers={**auth_headers, "Idempotency-Key": "order-1"}, json={"customer_id": customer["id"], "items": [{"product_id": product["id"], "quantity": 2}]})
    assert response.status_code == 201
    assert response.json()["total_amount"] == "50.00"
    updated = client.get(f"/api/products/{product['id']}", headers=auth_headers).json()
    assert updated["quantity"] == 3


def test_insufficient_stock_rolls_back(client, auth_headers):
    customer, product = seed(client, auth_headers)
    response = client.post("/api/orders", headers=auth_headers, json={"customer_id": customer["id"], "items": [{"product_id": product["id"], "quantity": 9}]})
    assert response.status_code == 409
    updated = client.get(f"/api/products/{product['id']}", headers=auth_headers).json()
    assert updated["quantity"] == 5


def test_idempotency_returns_original_order(client, auth_headers):
    customer, product = seed(client, auth_headers)
    payload = {"customer_id": customer["id"], "items": [{"product_id": product["id"], "quantity": 1}]}
    first = client.post("/api/orders", headers={**auth_headers, "Idempotency-Key": "retry-key"}, json=payload)
    second = client.post("/api/orders", headers={**auth_headers, "Idempotency-Key": "retry-key"}, json=payload)
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] == second.json()["id"]
    orders = client.get("/api/orders", headers=auth_headers).json()
    assert orders["total"] == 1
