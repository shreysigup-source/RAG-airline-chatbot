from chromadb.api.models.Collection import Collection
from sentence_transformers import SentenceTransformer

from app.rag.embedding_generator import generate_query_embedding
	
def retrieve_documents(
	collection: Collection,
	query: str,
	model: SentenceTransformer,
	top_k: int = 3,
) -> dict:
	"""
	Retrieve the most relevant documents from ChromaDB.
	
    Args:
	    collection: ChromaDB collection object.
	    query: User's question.
	    model: The loaded embedding model.
	    top_k: Number of results to retrieve.
	
	Returns:
	    Dictionary containing retrieved documents,
	    metadata, IDs, and distances.
	"""
	
	query_embedding = generate_query_embedding(query, model)
	
	results = collection.query(
	    query_embeddings=[query_embedding],
	    n_results=top_k,
	)
	
	return results
