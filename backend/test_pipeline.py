from app.rag.document_loader import load_documents
from app.rag.text_chunker import split_documents
from app.rag.embedding_generator import (
    load_embedding_model,
    generate_document_embeddings,
)
from app.rag.vector_store import create_vector_store
from app.rag.retriever import retrieve_documents

from app.rag.prompt_builder import build_prompt
from app.rag.llm_client import LLMClient

from langchain_core.documents import Document


def main():

    # Step 1: Load documents
    documents = load_documents()

    # Step 2: Split documents
    chunks = split_documents(documents)

    # Step 3: Generate embeddings
    model = load_embedding_model()

    embeddings = generate_document_embeddings(
        model=model,
        documents=chunks,
    )

    # Step 4: Store in ChromaDB
    collection = create_vector_store(
        documents=chunks,
        embeddings=embeddings,
    )

    # Step 5: Initialize the LLM
    llm = LLMClient()

    print("=" * 60)
    print("Airline RAG Chatbot is Ready!")
    print("Type 'exit' to quit.")
    print("=" * 60)

    while True:

        question = input("\nYou: ")

        if question.lower() == "exit":
            break

        # Retrieve relevant documents
        results = retrieve_documents(
            collection=collection,
            model=model,
            query=question,
            top_k=3,
        )

        # Convert retrieved results into LangChain Document objects
        retrieved_documents = []

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]

        for document, metadata in zip(documents, metadatas):
            retrieved_documents.append(
                Document(
                    page_content=document,
                    metadata=metadata,
                )
            )

        # Build prompt
        prompt = build_prompt(
            question=question,
            context_documents=retrieved_documents,
        )

        # Generate answer using Groq
        answer = llm.generate_response(prompt)

        print("\nAssistant:\n")
        print(answer)


if __name__ == "__main__":
    main()