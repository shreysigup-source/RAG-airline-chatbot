from chromadb.api.models.Collection import Collection
from sentence_transformers import SentenceTransformer

from app.rag.embedding_generator import generate_query_embedding


def retrieve_documents(
    collection: Collection,
    model: SentenceTransformer,
    query: str,
    top_k: int = 3,
) -> dict:
    """
    Retrieve the most relevant documents from ChromaDB.
    """

    query_embedding = generate_query_embedding(
        model=model,
        query=query,
    )

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    return results