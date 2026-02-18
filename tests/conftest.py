from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    with patch("app.chat.get_model") as mock_get_model:
        mock_model = type("MockModel", (), {})()
        mock_tokenizer = type(
            "MockTokenizer",
            (),
            {
                "apply_chat_template": lambda self, msgs, **kw: "mock prompt",
            },
        )()
        mock_get_model.return_value = (mock_model, mock_tokenizer)

        from app.main import app

        yield TestClient(app)
