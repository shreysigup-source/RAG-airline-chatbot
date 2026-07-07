from app.rag.document_loader import load_documents
from app.rag.text_chunker import split_documents


def main():
    # Step 1: Load documents
    documents = load_documents()

    print("=" * 60)
    print(f"Documents Loaded: {len(documents)}")

    # Step 2: Split into chunks
    chunks = split_documents(documents)

    print(f"Total Chunks Created: {len(chunks)}")
    print("=" * 60)

    # Step 3: Display the first 3 chunks
    if chunks:
        for i, chunk in enumerate(chunks[:3], start=1):
            print("=" * 60)
            print(f"Chunk {i}")
            print("=" * 60)

            print(chunk.page_content)

            print("\nMetadata:")
            print(chunk.metadata)

            print(f"\nLength: {len(chunk.page_content)} characters\n")


if __name__ == "__main__":
    main()