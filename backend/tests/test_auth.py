from uuid import uuid4


def test_register_login_and_protected_route(client):
    email = f"avery-{uuid4().hex}@example.com"
    register = client.post("/api/auth/register", json={"name": "Avery Stone", "email": email, "password": "password123"})
    assert register.status_code == 201
    assert register.json()["user"]["email"] == email

    login = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    assert login.status_code == 200

    token = login.json()["access_token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200


def test_same_user_can_use_multiple_active_tokens(client):
    email = f"sessions-{uuid4().hex}@example.com"
    client.post("/api/auth/register", json={"name": "Session User", "email": email, "password": "password123"})

    first = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    second = client.post("/api/auth/login", json={"email": email, "password": "password123"})

    assert first.status_code == 200
    assert second.status_code == 200
    first_token = first.json()["access_token"]
    second_token = second.json()["access_token"]
    assert first_token != second_token

    first_dashboard = client.get("/api/dashboard", headers={"Authorization": f"Bearer {first_token}"})
    second_dashboard = client.get("/api/dashboard", headers={"Authorization": f"Bearer {second_token}"})

    assert first_dashboard.status_code == 200
    assert second_dashboard.status_code == 200
