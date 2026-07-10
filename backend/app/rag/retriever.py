from chromadb.api.models.Collection import Collection

from app.rag.embedding_generator import generate_embeddings


def retrieve_documents(
    collection: Collection,
    query: str,
    top_k: int = 3,
) -> dict:
    """
    Retrieve the most relevant documents from ChromaDB.

    Args:
        collection: ChromaDB collection object.
        query: User's question.
        top_k: Number of results to retrieve.

    Returns:
        Dictionary containing retrieved documents,
        metadata, IDs, and distances.
    """

    query_embedding = generate_embeddings([query])[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    return results