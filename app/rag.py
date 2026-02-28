import logging

import chromadb
from llama_index.core.indices import VectorStoreIndex
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.core.storage.storage_context import StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore

from app.config import settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "intake-bot"
EMBED_MODEL = "local:sentence-transformers/all-MiniLM-L6-v2"

_index: VectorStoreIndex | None = None


def build_index() -> int:
    """Build the RAG index from the corpus directory.

    Returns the number of documents indexed. Skips re-indexing if
    the collection already has documents.
    """
    global _index

    if not settings.rag_corpus_path.exists():
        logger.warning(
            "RAG corpus path %s does not exist, skipping indexing",
            settings.rag_corpus_path,
        )
        return 0

    chroma_client = chromadb.PersistentClient(path=str(settings.chroma_db_path))
    collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    if collection.count() > 0:
        logger.info(
            "RAG collection already has %d documents, loading existing index",
            collection.count(),
        )
        _index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            embed_model=EMBED_MODEL,
        )
        return collection.count()

    reader = SimpleDirectoryReader(
        input_dir=str(settings.rag_corpus_path),
        recursive=True,
        required_exts=[".md"],
    )
    documents = reader.load_data()

    _index = VectorStoreIndex.from_documents(
        documents=documents,
        storage_context=storage_context,
        embed_model=EMBED_MODEL,
        show_progress=True,
    )

    doc_count = len(documents)
    logger.info("RAG index built: %d docs", doc_count)
    return doc_count


def retrieve_context(query: str) -> str:
    """Retrieve relevant context chunks for a query.

    Returns concatenated text from the top-k most relevant nodes,
    separated by '---'. Returns an empty string if the index is not
    built.
    """
    if _index is None:
        logger.warning("RAG index not built, returning empty context")
        return ""

    retriever = _index.as_retriever(similarity_top_k=settings.rag_top_k)
    nodes = retriever.retrieve(query)

    if not nodes:
        return ""

    return "\n---\n".join(node.get_content() for node in nodes)
