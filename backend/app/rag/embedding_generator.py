from sentence_transformers import SentenceTransformer
from langchain_core.documents import Document


def load_embedding_model(
    model_name: str = "all-MiniLM-L6-v2",
) -> SentenceTransformer:
    """
    Load and return the embedding model.
    """

    return SentenceTransformer(model_name)


def generate_document_embeddings(
    model: SentenceTransformer,
    documents,
):
    """
    Generate embeddings for a list of documents.
    """

    texts = []

    for doc in documents:
        if isinstance(doc, Document):
            texts.append(doc.page_content)
        else:
            texts.append(doc)

    embeddings = model.encode(texts)

    return embeddings


def generate_query_embedding(
    model: SentenceTransformer,
    query: str,
):
    """
    Generate an embedding for a user's query.
    """

    return model.encode([query])[0]

"""
Why not simple return model.encode(query)
Because document embeddings are generated from a list of texts, while a query is a single text. Using model.encode([query])[0] ensures the output shape is consistently a single embedding vector and avoids any ambiguity across model versions.
It isn't strictly required for many Sentence Transformers models, but it's a good habit and makes the intent explicit.
"""