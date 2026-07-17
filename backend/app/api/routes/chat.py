import logging
from fastapi import APIRouter, Request, HTTPException
from app.api.models.chat_models import ChatRequest
from app.api.models.response_models import ChatResponse, ErrorResponse

from langchain_core.documents import Document
from app.rag.retriever import retrieve_documents
from app.rag.prompt_builder import build_prompt
from app.utils.response_router import maybe_answer_from_services
from app.api.functions.tool_calling import try_tool_calling

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("", response_model=ChatResponse)
async def process_chat(request: Request, chat_req: ChatRequest):
    """
    Handles user chat inputs by querying transactional services or retrieving text from ChromaDB.
    """
    query = chat_req.message.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    logger.info(f"Processing chat query: '{query}'")

    # Step 1: Pre-defined heuristic service lookup (direct match rules)
    try:
        direct_answer = maybe_answer_from_services(query)
        if direct_answer:
            logger.info("Answer retrieved via direct policy lookup.")
            return ChatResponse(
                status="success",
                response=direct_answer,
                sources=[{"source": "Direct Policy Lookup Table"}]
            )
    except Exception as e:
        logger.error(f"Error checking direct policy lookup: {str(e)}")

    # Step 2: LLM Tool-Calling check
    try:
        llm_client = request.app.state.llm_client
        tool_result = try_tool_calling(
            client=llm_client.client,
            model_name=llm_client.model_name,
            question=query
        )
        if tool_result:
            logger.info("Query successfully handled via tool calling.")
            return ChatResponse(
                status="success",
                response=tool_result["response"],
                sources=tool_result["sources"]
            )
    except Exception as e:
        logger.error(f"Error checking tool-calling pipeline: {str(e)}")

    # Step 3: Fallback to standard RAG pipeline
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
        sources = []
        for doc_text, meta, dist in zip(documents_ret, metadatas, distances):
            context_docs.append(Document(page_content=doc_text, metadata=meta))
            sources.append({
                "source": meta.get("source", "Knowledge Base Document"),
                "distance": float(dist),
                "preview": doc_text[:120] + "..." if len(doc_text) > 120 else doc_text
            })

        # Build Prompt using matched document contexts
        prompt = build_prompt(query, context_docs)

        # Generate response using LLM Client
        response_text = llm_client.generate_response(prompt)

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
