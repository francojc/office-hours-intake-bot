from unittest.mock import patch

from app.rag import build_index, retrieve_context


def test_build_index_creates_collection(tmp_rag_corpus, tmp_chroma_path):
    """build_index loads docs and creates a non-empty collection."""
    with (
        patch("app.rag.settings") as mock_settings,
    ):
        mock_settings.rag_corpus_path = tmp_rag_corpus
        mock_settings.chroma_db_path = tmp_chroma_path
        mock_settings.rag_top_k = 3

        import app.rag as rag_module

        rag_module._index = None

        doc_count = build_index()
        assert doc_count > 0
        assert rag_module._index is not None


def test_build_index_skips_missing_corpus(tmp_path):
    """build_index returns 0 when corpus path doesn't exist."""
    with patch("app.rag.settings") as mock_settings:
        mock_settings.rag_corpus_path = tmp_path / "nonexistent"
        mock_settings.chroma_db_path = tmp_path / "chroma"

        import app.rag as rag_module

        rag_module._index = None

        doc_count = build_index()
        assert doc_count == 0
        assert rag_module._index is None


def test_retrieve_context_returns_relevant_text(
    tmp_rag_corpus, tmp_chroma_path
):
    """retrieve_context returns text related to the query."""
    with patch("app.rag.settings") as mock_settings:
        mock_settings.rag_corpus_path = tmp_rag_corpus
        mock_settings.chroma_db_path = tmp_chroma_path
        mock_settings.rag_top_k = 3

        import app.rag as rag_module

        rag_module._index = None

        build_index()
        result = retrieve_context("ser vs estar")
        assert isinstance(result, str)
        assert len(result) > 0
        assert "ser" in result.lower() or "estar" in result.lower()


def test_retrieve_context_returns_string_for_edge_query(
    tmp_rag_corpus, tmp_chroma_path
):
    """retrieve_context returns a non-empty string for any query."""
    with patch("app.rag.settings") as mock_settings:
        mock_settings.rag_corpus_path = tmp_rag_corpus
        mock_settings.chroma_db_path = tmp_chroma_path
        mock_settings.rag_top_k = 3

        import app.rag as rag_module

        rag_module._index = None

        build_index()
        result = retrieve_context("completely unrelated topic xyz")
        assert isinstance(result, str)
        assert len(result) > 0


def test_retrieve_context_empty_when_no_index():
    """retrieve_context returns empty string if index not built."""
    import app.rag as rag_module

    original = rag_module._index
    rag_module._index = None
    try:
        result = retrieve_context("anything")
        assert result == ""
    finally:
        rag_module._index = original
