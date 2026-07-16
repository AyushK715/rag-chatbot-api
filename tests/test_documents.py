DOC = {"title": "Refund Policy", "content": "Customers may return items within 30 days of purchase for a full refund."}


def test_create_document(client, auth_headers):
    r = client.post("/documents", json=DOC, headers=auth_headers)
    assert r.status_code == 201
    body = r.json()
    assert body["title"] == "Refund Policy"
    assert body["chunk_count"] >= 1
    assert body["deduplicated"] is False


def test_idempotent_ingestion(client, auth_headers):
    first = client.post("/documents", json=DOC, headers=auth_headers).json()
    second = client.post("/documents", json=DOC, headers=auth_headers).json()
    assert second["deduplicated"] is True
    assert second["id"] == first["id"]


def test_list_and_delete_document(client, auth_headers):
    doc_id = client.post("/documents", json=DOC, headers=auth_headers).json()["id"]

    listed = client.get("/documents", headers=auth_headers).json()
    assert any(d["id"] == doc_id for d in listed)

    r = client.delete(f"/documents/{doc_id}", headers=auth_headers)
    assert r.status_code == 204

    listed = client.get("/documents", headers=auth_headers).json()
    assert not any(d["id"] == doc_id for d in listed)


def test_delete_other_users_document_404(client, auth_headers):
    doc_id = client.post("/documents", json=DOC, headers=auth_headers).json()["id"]

    client.post("/auth/register", json={"email": "other@x.com", "password": "password1"})
    token = client.post(
        "/auth/login", json={"email": "other@x.com", "password": "password1"}
    ).json()["access_token"]

    r = client.delete(f"/documents/{doc_id}", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 404
