from pathlib import Path
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
                "apply_chat_template": (
                    lambda self, msgs, **kw: "mock prompt"
                ),
            },
        )()
        mock_get_model.return_value = (mock_model, mock_tokenizer)

        from app.main import app

        yield TestClient(app)


@pytest.fixture
def tmp_rag_corpus(tmp_path: Path) -> Path:
    """Create a temporary RAG corpus with sample markdown files."""
    corpus_dir = tmp_path / "rag-corpus"
    spa_dir = corpus_dir / "spa212"
    spa_dir.mkdir(parents=True)

    grammar = spa_dir / "grammar_topics.md"
    grammar.write_text(
        "# Grammar Topics\n\n"
        "## Ser vs Estar\n\n"
        "Ser is used for permanent characteristics, identity, "
        "origin, and time. Estar is used for temporary states, "
        "locations, and conditions.\n\n"
        "## Preterite vs Imperfect\n\n"
        "The preterite describes completed actions in the past. "
        "The imperfect describes ongoing or habitual past actions.\n"
    )

    errors = spa_dir / "common_errors.md"
    errors.write_text(
        "# Common Errors\n\n"
        "## Ser/Estar Confusion\n\n"
        "Students often use ser when estar is required for "
        "locations: 'El libro ser en la mesa' should be "
        "'El libro esta en la mesa.'\n\n"
        "## Subjunctive Triggers\n\n"
        "Common mistake: forgetting to use subjunctive after "
        "expressions of doubt like 'dudo que' or emotion like "
        "'me alegra que.'\n"
    )

    return corpus_dir


@pytest.fixture
def tmp_chroma_path(tmp_path: Path) -> Path:
    """Return a temporary path for ChromaDB persistence."""
    chroma_dir = tmp_path / "chroma_db"
    chroma_dir.mkdir()
    return chroma_dir
