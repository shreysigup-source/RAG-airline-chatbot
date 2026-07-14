from sentence_transformers import SentenceTransformer
from langchain_core.documents import Document


def load_embedding_model(model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    """
    Load the sentence transformer model.
    """
    return SentenceTransformer(model_name)


def generate_document_embeddings(
    documents: list[Document],
    model: SentenceTransformer,
) -> list:
    """
    Generate embeddings for document chunks using the provided model.
    """
    texts = [doc.page_content for doc in documents]
    return model.encode(texts)


def generate_query_embedding(
    query: str,
    model: SentenceTransformer,
) -> list:
    """
    Generate embedding for a single query using the provided model.
    """
    return model.encode([query])[0]
