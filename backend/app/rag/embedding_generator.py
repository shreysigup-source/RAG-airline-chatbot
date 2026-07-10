from sentence_transformers import SentenceTransformer
from langchain_core.documents import Document


def generate_embeddings(
    documents: list[Document],
    model_name: str = "all-MiniLM-L6-v2",
):
    """
    Generate embeddings for a list of document chunks.

    Args:
        documents: List of LangChain Document objects.
        model_name: Sentence Transformer model to use.

    Returns:
        tuple:
            model -> Loaded embedding model
            embeddings -> List of embedding vectors
    """

    model = SentenceTransformer(model_name)

    texts = [document.page_content for document in documents]

    embeddings = model.encode(texts)

    return model, embeddings