import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.api.models.response_models import UploadResponse
from app.multimodal.pdf_processor import PDFProcessor
from app.multimodal.image_processor import ImageProcessor

router = APIRouter()

# Setup temporary upload directory inside backend/app
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMP_DIR = os.path.join(BASE_DIR, "temp_uploads")
os.makedirs(TEMP_DIR, exist_ok=True)

pdf_processor = PDFProcessor()
image_processor = ImageProcessor()

@router.post("/pdf", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Accepts a PDF file, extracts text using PDFProcessor, and returns the result.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    temp_file_path = os.path.join(TEMP_DIR, file.filename)
    try:
        # Save uploaded file chunk by chunk
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        extracted_text = pdf_processor.extract_text(temp_file_path)
        
        return UploadResponse(
            status="success",
            message="PDF text extracted successfully.",
            extracted_text=extracted_text,
            file_path=file.filename
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF extraction failed: {str(e)}")
    finally:
        # Guarantee removal of the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@router.post("/image", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """
    Accepts an image file, runs it through ImageProcessor, and returns the result.
    """
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise HTTPException(status_code=400, detail=f"Unsupported format '{ext}'. Supported formats: .jpg, .jpeg, .png, .webp")

    temp_file_path = os.path.join(TEMP_DIR, file.filename)
    try:
        # Save uploaded file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        result = image_processor.process_image(temp_file_path)
        
        return UploadResponse(
            status="success",
            message="Image processed successfully.",
            result=result,
            file_path=file.filename
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")
    finally:
        # Guarantee removal of the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
