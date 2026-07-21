import logging
from fastapi import APIRouter, Request, HTTPException
from app.api.models.chat_models import ChatRequest
from app.api.models.response_models import ChatResponse

from langchain_core.documents import Document
from app.rag.retriever import retrieve_documents
from app.rag.prompt_builder import build_prompt

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("", response_model=ChatResponse)
async def process_chat(request: Request, chat_req: ChatRequest):
    """
    Handles user chat inputs by retrieving text from ChromaDB.
    """
    query = chat_req.message.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    logger.info(f"Processing chat query: '{query}'")

    # Standard RAG pipeline
    try:
        collection = request.app.state.chroma_collection
        embedding_model = request.app.state.embedding_model

        if collection is None or embedding_model is None:
            raise RuntimeError("Database collection or embedding model is not initialized.")

        # Query Vector Database
        results = retrieve_documents(
            collection=collection,
            query=query,
            model=embedding_model,
            top_k=3
        )

        documents_ret = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        if not documents_ret:
            return ChatResponse(
                status="success",
                response="I couldn't find that information in the provided airline documents.",
                sources=[]
            )

        context_docs = []
        for doc_text, meta in zip(documents_ret, metadatas):
            context_docs.append(Document(page_content=doc_text, metadata=meta))

        sources = []
        if documents_ret:
            # Keep only the most relevant source for the user-facing response
            first_meta = metadatas[0]
            first_doc_text = documents_ret[0]
            sources = [{
                "source": first_meta.get("source", "Knowledge Base Document"),
                "distance": float(distances[0]) if distances else None,
                "preview": first_doc_text[:120] + "..." if len(first_doc_text) > 120 else first_doc_text
            }]

        # Build Prompt using matched document contexts
        prompt = build_prompt(query, context_docs)

        # Generate response using LLM Client
        response_text = request.app.state.llm_client.generate_response(prompt)

        logger.info("Response generated successfully using RAG.")
        return ChatResponse(
            status="success",
            response=response_text,
            sources=sources
        )

    except Exception as e:
        logger.error(f"RAG processing failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while generating the answer: {str(e)}"
        )
