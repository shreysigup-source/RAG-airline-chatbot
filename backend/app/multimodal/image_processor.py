import pathlib


class ImageProcessor:
    """
    Placeholder service for processing images, preparing the abstraction
    for a future vision model integration.
    """

    def __init__(self):
        self.supported_extensions = {".jpg", ".jpeg", ".png", ".webp"}

    def validate_image(self, image_path: str) -> None:
        """
        Validates whether the file exists and is of a supported format.

        Args:
            image_path: The filesystem path to the image file.

        Raises:
            FileNotFoundError: If the image file does not exist.
            ValueError: If the file extension is not supported.
        """
        path = pathlib.Path(image_path)
        if not path.is_file():
            raise FileNotFoundError(f"Image file not found at: {image_path}")

        ext = path.suffix.lower()
        if ext not in self.supported_extensions:
            raise ValueError(
                f"Unsupported image format '{ext}'. Supported formats: {', '.join(self.supported_extensions)}"
            )

    def process_image(self, image_path: str) -> dict:
        """
        Processes the image and returns status information.
        Currently a placeholder for future Vision API integration.

        Args:
            image_path: The filesystem path to the image file.

        Returns:
            A structured dict detailing the status of image processing.
        """
        self.validate_image(image_path)
        return {
            "status": "not_implemented",
            "message": "Vision model integration will be added in a future version.",
        }
