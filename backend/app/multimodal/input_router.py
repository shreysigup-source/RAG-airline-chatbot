import pathlib
from .pdf_processor import PDFProcessor
from .image_processor import ImageProcessor


class InputRouter:
    """
    Routes user input to the appropriate processor based on input type detection.
    """

    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.image_processor = ImageProcessor()

    def detect_input_type(self, input_path: str) -> str:
        """
        Detects input type based on the file extension.

        Args:
            input_path: The path to a file or raw string input.

        Returns:
            A string representing the detected type ("pdf", "image", or "text").
        """
        path = pathlib.Path(input_path)
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            return "pdf"
        elif suffix in {".jpg", ".jpeg", ".png", ".webp"}:
            return "image"
        elif suffix == ".txt":
            return "text"
        else:
            # Fallback to "text" if it doesn't match standard document/image extensions
            return "text"

    def route_text(self, question: str) -> dict:
        """
        Routes text inputs.

        Args:
            question: The user's text question.

        Returns:
            A structured dict containing text details.
        """
        return {
            "type": "text",
            "status": "success",
            "content": question,
        }

    def route_pdf(self, pdf_path: str) -> dict:
        """
        Routes PDF files to the PDFProcessor for extraction.

        Args:
            pdf_path: The filesystem path to the PDF file.

        Returns:
            A structured dict containing extraction results or error details.
        """
        try:
            extracted_text = self.pdf_processor.extract_text(pdf_path)
            return {
                "type": "pdf",
                "status": "success",
                "extracted_text": extracted_text,
                "file_path": pdf_path,
            }
        except Exception as e:
            return {
                "type": "pdf",
                "status": "error",
                "error": str(e),
                "file_path": pdf_path,
            }

    def route_image(self, image_path: str) -> dict:
        """
        Routes image files to the ImageProcessor for processing.

        Args:
            image_path: The filesystem path to the image file.

        Returns:
            A structured dict containing processing results or error details.
        """
        try:
            result = self.image_processor.process_image(image_path)
            return {
                "type": "image",
                "status": "success",
                "result": result,
                "file_path": image_path,
            }
        except Exception as e:
            return {
                "type": "image",
                "status": "error",
                "error": str(e),
                "file_path": image_path,
            }
