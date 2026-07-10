from app.rag.document_loader import load_documents
from app.rag.text_chunker import split_documents
from app.rag.embedding_generator import generate_embeddings
from app.rag.vector_store import create_vector_store
from app.rag.retriever import retrieve_documents


def main():

    # Step 1: Load documents
    documents = load_documents()

    # Step 2: Split documents
    chunks = split_documents(documents)

    # Step 3: Generate embeddings
    model, embeddings = generate_embeddings(chunks)

    # Step 4: Store in ChromaDB
    collection = create_vector_store(
        documents=chunks,
        embeddings=embeddings,
    )

    print("=" * 60)
    print("Vector Store Created Successfully")
    print("=" * 60)

    while True:

        question = input("\nAsk a question (or type 'exit'): ")

        if question.lower() == "exit":
            break

        results = retrieve_documents(
            collection=collection,
            query=question,
            top_k=3,
        )

        print("\nRetrieved Documents:\n")

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for i, (document, metadata, distance) in enumerate(
            zip(documents, metadatas, distances),
            start=1,
        ):
            print("-" * 60)
            print(f"Result {i}")
            print(f"Source   : {metadata['source']}")
            print(f"Distance : {distance:.4f}")
            print()
            print(document)
            print()


if __name__ == "__main__":
    main()
