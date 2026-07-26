def test_create_document_invalid_payload(client):
    """Test creating a document with missing fields."""
    response = client.post("/documents/", json={"title": "Test Doc"})
    assert response.status_code == 422  # Unprocessable Entity (FastAPI validation)

def test_chat_endpoint_validation(client):
    """Test chat endpoint fails gracefully on invalid payload."""
    response = client.post("/chat/", json={"invalid": "payload"})
    assert response.status_code == 422
