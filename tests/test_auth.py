def test_register_and_login(client):
    r = client.post("/auth/register", json={"email": "a@b.com", "password": "password1"})
    assert r.status_code == 201

    r = client.post("/auth/login", json={"email": "a@b.com", "password": "password1"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_register_duplicate_email(client):
    client.post("/auth/register", json={"email": "dup@b.com", "password": "password1"})
    r = client.post("/auth/register", json={"email": "dup@b.com", "password": "password1"})
    assert r.status_code == 409


def test_login_wrong_password(client):
    client.post("/auth/register", json={"email": "c@b.com", "password": "password1"})
    r = client.post("/auth/login", json={"email": "c@b.com", "password": "wrongpass1"})
    assert r.status_code == 401


def test_protected_route_requires_token(client):
    r = client.get("/documents")
    assert r.status_code == 401
