import pathlib
import fitz  # PyMuPDF


class PDFProcessor:
    """
    Handles PDF document parsing and text extraction.
    """

    def extract_text(self, pdf_path: str) -> str:
        """
        Extracts all textual content from a PDF document.

        Args:
            pdf_path: The filesystem path to the PDF file.

        Returns:
            A clean string containing all extracted text combined.

        Raises:
            FileNotFoundError: If the PDF file does not exist.
            ValueError: If the file is not a valid PDF or is empty.
            RuntimeError: If text extraction fails.
        """
        path = pathlib.Path(pdf_path)
        if not path.is_file():
            raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

        try:
            doc = fitz.open(str(path))
        except Exception as e:
            raise ValueError(f"Failed to open PDF file: {e}")

        try:
            text_parts = []
            for page in doc:
                text_parts.append(page.get_text())

            full_text = "\n".join(text_parts).strip()

            if not full_text:
                raise ValueError("No text could be extracted from the PDF (the file may be scanned or empty).")

            return full_text
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Error extracting text from PDF: {e}")
        finally:
            doc.close()
