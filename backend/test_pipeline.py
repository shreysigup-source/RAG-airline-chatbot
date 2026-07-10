from app.rag.document_loader import load_documents
from app.rag.text_chunker import split_documents
from app.rag.embedding_generator import generate_embeddings
from app.rag.vector_store import create_vector_store


def main():
    # Step 1: Load documents
    documents = load_documents()

    print("=" * 60)
    print(f"Documents Loaded: {len(documents)}")

    # Step 2: Split into chunks
    chunks = split_documents(documents)

    print(f"Total Chunks Created: {len(chunks)}")

    # Step 3: Generate embeddings
    model, embeddings = generate_embeddings(chunks)

    print(f"Total Embeddings: {len(embeddings)}")
    print(f"Embedding Dimension: {len(embeddings[0])}")

    # Step 4: Store embeddings in ChromaDB
    collection = create_vector_store(
        documents=chunks,
        embeddings=embeddings,
    )

    print(f"Vector Database Collection: {collection.name}")

    print("=" * 60)

    # Step 5: Display the first 3 chunks
    if chunks:
        for i, chunk in enumerate(chunks[:3], start=1):
            print("=" * 60)
            print(f"Chunk {i}")
            print("=" * 60)

            print(chunk.page_content)

            print("\nMetadata:")
            print(chunk.metadata)

            print(f"\nLength: {len(chunk.page_content)} characters\n")

    print("=" * 60)
    print("First 10 values of the first embedding:")
    print(embeddings[0][:10])

    print("=" * 60)
    print("Vector database created successfully!")


if __name__ == "__main__":
    main()
