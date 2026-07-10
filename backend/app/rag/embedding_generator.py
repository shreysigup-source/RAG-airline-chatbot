from sentence_transformers import SentenceTransformer
from langchain_core.documents import Document


def generate_embeddings(
    documents,
    model_name: str = "all-MiniLM-L6-v2",
):
    """
    Generate embeddings for a list of document chunks or strings.

    Args:
        documents: List of LangChain Document objects or strings.
        model_name: Sentence Transformer model to use.

    Returns:
        tuple:
            model -> Loaded embedding model
            embeddings -> List of embedding vectors
    """

    model = SentenceTransformer(model_name)

    # Handle both Document objects and strings
    texts = []
    for doc in documents:
        if isinstance(doc, Document):
            texts.append(doc.page_content)
        else:
            texts.append(doc)

    embeddings = model.encode(texts)

    return model, embeddings