from fastapi import APIRouter, Request
from app.api.models.response_models import HealthResponse

router = APIRouter()

@router.get("", response_model=HealthResponse)
async def check_health(request: Request):
    """
    Returns health status of the API, ChromaDB connection, and embedding model status.
    """
    db_status = "error"
    embedding_status = "error"

    try:
        # Check ChromaDB collection
        collection = request.app.state.chroma_collection
        if collection is not None:
            # Try a quick count check to ensure collection is operational
            count = collection.count()
            db_status = f"connected ({count} chunks)"
    except Exception as e:
        db_status = f"error: {str(e)}"

    try:
        # Check Embedding Model
        model = request.app.state.embedding_model
        if model is not None:
            embedding_status = "loaded"
    except Exception as e:
        embedding_status = f"error: {str(e)}"

    status = "ok" if ("error" not in db_status and "error" not in embedding_status) else "degraded"

    return HealthResponse(
        status=status,
        database=db_status,
        embedding_model=embedding_status
    )
