from langchain_core.documents import Document
from app.rag.document_loader import load_documents
from app.rag.text_chunker import split_documents
from app.rag.embedding_generator import load_embedding_model, generate_document_embeddings
from app.rag.vector_store import create_vector_store
from app.rag.retriever import retrieve_documents
from app.rag.prompt_builder import build_prompt
from app.rag.llm_client import LLMClient

def main():

    # Step 1: Load documents
    documents = load_documents()

    # Step 2: Split documents
    chunks = split_documents(documents)

    # Step 3: Generate embeddings
    model = load_embedding_model()
    embeddings = generate_document_embeddings(chunks, model)

    # Step 4: Store in ChromaDB
    collection = create_vector_store(
        documents=chunks,
        embeddings=embeddings,
    )

    print("=" * 60)
    print("Vector Store Created Successfully")
    print("=" * 60)

    # Initialize LLM Client
    llm_client = LLMClient()

    while True:

        question = input("\nAsk a question (or type 'exit'): ")

        if question.lower() == "exit":
            break

        results = retrieve_documents(
            collection=collection,
            query=question,
            model=model,
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

        # Step 5: Build prompt and generate response
        context_docs = []
        for doc_text, metadata in zip(documents, metadatas):
            context_docs.append(Document(page_content=doc_text, metadata=metadata))

        prompt = build_prompt(question, context_docs)
        
        print("=" * 60)
        print("Generating LLM Response...")
        print("=" * 60)
        
        try:
            response = llm_client.generate_response(prompt)
            print("\nLLM Response:\n")
            print(response)
        except Exception as e:
            print(f"\nError generating LLM response: {e}")
            print("Make sure you have set the GROQ_API_KEY environment variable.")
        print("=" * 60)

if __name__ == "__main__":
    main()
