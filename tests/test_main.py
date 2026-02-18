from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_ok():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model_path" in data
    assert "model_loaded" in data


def test_static_files_served():
    client = TestClient(app)
    response = client.get("/static/index.html")
    assert response.status_code == 200
    assert "Office Hours Intake" in response.text


@patch("app.chat.generate", return_value="This is a test reply.")
@patch("app.chat.get_model")
def test_chat_returns_reply(mock_get_model, mock_generate):
    mock_tokenizer = type(
        "MockTokenizer",
        (),
        {
            "apply_chat_template": lambda self, msgs, **kw: "mock prompt",
        },
    )()
    mock_model = type("MockModel", (), {})()
    mock_get_model.return_value = (mock_model, mock_tokenizer)

    client = TestClient(app)
    response = client.post(
        "/chat", json={"message": "I need help with ser vs estar"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["reply"] == "This is a test reply."


@patch("app.chat.get_model", side_effect=RuntimeError("Model not found"))
def test_chat_503_when_model_missing(mock_get_model):
    client = TestClient(app)
    response = client.post("/chat", json={"message": "hello"})
    assert response.status_code == 503
