from __future__ import annotations

from decimal import Decimal

from app.models import AuditLog, Customer, Order, Product


def create_customer(client, headers, email="ops@northwind.example.com"):
    response = client.post(
        "/api/customers",
        headers=headers,
        json={"name": "Northwind Logistics", "email": email, "company": "Northwind Logistics", "phone": "+1-212-555-0101"},
    )
    assert response.status_code == 201
    return response.json()


def create_product(client, headers, sku="SCN-1001", quantity=12, price="125.00"):
    response = client.post(
        "/api/products",
        headers=headers,
        json={
            "name": "Relay Barcode Scanner",
            "sku": sku,
            "description": "Handheld scanner for receiving and shipping",
            "unit_price": price,
            "quantity": quantity,
            "low_stock_threshold": 4,
        },
    )
    assert response.status_code == 201
    return response.json()


def create_order(client, headers, customer_id, product_id, quantity=2, idem_key="order-key"):
    response = client.post(
        "/api/orders",
        headers={**headers, "Idempotency-Key": idem_key},
        json={"customer_id": customer_id, "items": [{"product_id": product_id, "quantity": quantity}]},
    )
    assert response.status_code == 201
    return response.json()


def test_health_endpoints(client):
    assert client.get("/health").status_code == 200
    assert client.get("/health/database").status_code == 200


def test_unique_constraints_and_crud_flow(client, auth_headers):
    product = create_product(client, auth_headers, sku="UNIQUE-1")
    duplicate_product = client.post(
        "/api/products",
        headers=auth_headers,
        json={
            "name": "Relay Barcode Scanner",
            "sku": "UNIQUE-1",
            "description": "Duplicate SKU should fail",
            "unit_price": "125.00",
            "quantity": 12,
            "low_stock_threshold": 4,
        },
    )
    assert duplicate_product.status_code == 409

    customer = create_customer(client, auth_headers, email="ops-unique@example.com")
    duplicate_customer = client.post(
        "/api/customers",
        headers=auth_headers,
        json={"name": "Northwind Logistics", "email": "ops-unique@example.com", "company": "Northwind Logistics"},
    )
    assert duplicate_customer.status_code == 409

    fetched_product = client.get(f"/api/products/{product['id']}", headers=auth_headers)
    assert fetched_product.status_code == 200
    assert fetched_product.json()["sku"] == "UNIQUE-1"

    fetched_customer = client.get(f"/api/customers/{customer['id']}", headers=auth_headers)
    assert fetched_customer.status_code == 200
    assert fetched_customer.json()["email"] == "ops-unique@example.com"


def test_assessment_route_aliases_and_put_update(client, auth_headers):
    product = create_product(client, auth_headers, sku="PUT-1", quantity=9, price="18.00")
    updated = client.put(
        f"/products/{product['id']}",
        headers=auth_headers,
        json={
            "name": "Relay Barcode Scanner Plus",
            "sku": "PUT-1A",
            "description": "Updated scanner",
            "unit_price": "22.50",
            "quantity": 7,
            "low_stock_threshold": 3,
        },
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Relay Barcode Scanner Plus"
    assert updated.json()["sku"] == "PUT-1A"
    assert updated.json()["quantity"] == 7

    products = client.get("/products", headers=auth_headers)
    assert products.status_code == 200
    assert products.json()["total"] == 1


def test_order_transaction_idempotency_and_audit(client, auth_headers, db_session):
    customer = create_customer(client, auth_headers, email="fulfillment@example.com")
    product = create_product(client, auth_headers, sku="ORDER-1", quantity=14, price="39.50")

    first = create_order(client, auth_headers, customer["id"], product["id"], quantity=3, idem_key="idem-1")
    second = client.post(
        "/api/orders",
        headers={**auth_headers, "Idempotency-Key": "idem-1"},
        json={"customer_id": customer["id"], "items": [{"product_id": product["id"], "quantity": 3}]},
    )
    assert second.status_code == 201
    assert second.json()["id"] == first["id"]

    updated_product = client.get(f"/api/products/{product['id']}", headers=auth_headers).json()
    assert updated_product["quantity"] == 11
    assert Decimal(updated_product["unit_price"]) == Decimal("39.50")

    audit_rows = db_session.query(AuditLog).filter(AuditLog.entity_type == "order", AuditLog.entity_id == first["id"]).all()
    assert len(audit_rows) == 1
    assert audit_rows[0].action == "created"

    conflicting = client.post(
        "/api/orders",
        headers={**auth_headers, "Idempotency-Key": "idem-1"},
        json={"customer_id": customer["id"], "items": [{"product_id": product["id"], "quantity": 1}]},
    )
    assert conflicting.status_code == 409


def test_order_cancellation_restocks_and_soft_deletes(client, auth_headers, db_session):
    customer = create_customer(client, auth_headers, email="returns@example.com")
    product = create_product(client, auth_headers, sku="CANCEL-1", quantity=8, price="20.00")
    order = create_order(client, auth_headers, customer["id"], product["id"], quantity=2, idem_key="cancel-1")

    cancel = client.delete(f"/api/orders/{order['id']}", headers=auth_headers)
    assert cancel.status_code == 204

    order_lookup = client.get(f"/api/orders/{order['id']}", headers=auth_headers)
    assert order_lookup.status_code == 404

    restored_product = client.get(f"/api/products/{product['id']}", headers=auth_headers).json()
    assert restored_product["quantity"] == 8

    db_order = db_session.query(Order).filter(Order.id == order["id"]).one()
    assert db_order.status == "cancelled"
    assert db_order.deleted_at is not None

    cancel_logs = db_session.query(AuditLog).filter(AuditLog.entity_type == "order", AuditLog.entity_id == order["id"], AuditLog.action == "cancelled").all()
    assert len(cancel_logs) == 1


def test_dashboard_reflects_operational_state(client, auth_headers):
    customer = create_customer(client, auth_headers, email="dashboard@example.com")
    product = create_product(client, auth_headers, sku="DASH-1", quantity=5, price="120.00")
    create_order(client, auth_headers, customer["id"], product["id"], quantity=4, idem_key="dash-1")

    dashboard = client.get("/api/dashboard", headers=auth_headers)
    assert dashboard.status_code == 200
    body = dashboard.json()
    assert body["total_products"] >= 1
    assert body["total_customers"] >= 1
    assert body["total_orders"] >= 1
    assert len(body["recent_orders"]) >= 1
    assert len(body["low_stock_products"]) >= 1
