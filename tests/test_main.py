from unittest.mock import AsyncMock, MagicMock, patch

import httpx
from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_ok():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("ok", "degraded")
    assert "ollama_reachable" in data
    assert "ollama_model" in data
    assert "rag_index_loaded" in data


def test_static_files_served():
    client = TestClient(app)
    response = client.get("/static/index.html")
    assert response.status_code == 200
    assert "Office Hours Intake" in response.text


@patch("app.chat.httpx.AsyncClient")
def test_chat_returns_reply(mock_client_cls):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "message": {"role": "assistant", "content": "Test reply."},
    }

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = False
    mock_client_cls.return_value = mock_client

    client = TestClient(app)
    response = client.post(
        "/chat", json={"message": "I need help with ser vs estar"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["reply"] == "Test reply."


@patch("app.chat.httpx.AsyncClient")
def test_chat_503_when_ollama_unreachable(mock_client_cls):
    mock_client = AsyncMock()
    mock_client.post.side_effect = httpx.ConnectError(
        "Connection refused"
    )
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = False
    mock_client_cls.return_value = mock_client

    client = TestClient(app)
    response = client.post("/chat", json={"message": "hello"})
    assert response.status_code == 503
