def test_register_login_and_protected_route(client):
    register = client.post("/api/auth/register", json={"name": "Avery Stone", "email": "avery@example.com", "password": "password123"})
    assert register.status_code == 201
    assert register.json()["user"]["email"] == "avery@example.com"

    login = client.post("/api/auth/login", json={"email": "avery@example.com", "password": "password123"})
    assert login.status_code == 200

    token = login.json()["access_token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
