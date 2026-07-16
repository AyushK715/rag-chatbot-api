DOC = {"title": "FAQ", "content": "Our support team is available 24/7 via email at help@example.com."}


def test_chat_without_documents(client, auth_headers):
    r = client.post("/chat", json={"question": "What is the refund window?"}, headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert "don't know" in body["answer"].lower()
    assert body["sources"] == []


def test_chat_with_documents_returns_sources(client, auth_headers):
    client.post("/documents", json=DOC, headers=auth_headers)
    r = client.post("/chat", json={"question": "How do I contact support?"}, headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["answer"] == "Mocked grounded answer."
    assert len(body["sources"]) >= 1
    assert body["sources"][0]["title"] == "FAQ"


def test_chat_requires_auth(client):
    r = client.post("/chat", json={"question": "hello"})
    assert r.status_code == 401
