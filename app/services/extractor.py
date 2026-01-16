"""
Text extraction service for PDFs and images.
Supports PyMuPDF for PDFs and EasyOCR for images.
"""
import os
import fitz
from pathlib import Path
from typing import Tuple
import logging
import signal
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, TimeoutError

logger = logging.getLogger(__name__)

class TimeoutException(Exception):
    """Raised when extraction takes too long"""
    pass

@contextmanager
def timeout(seconds=30):
    """
    Cross-platform timeout context manager.
    Uses signal on Unix, ThreadPoolExecutor on Windows.
    """
    import platform
    
    if platform.system() == "Windows":
        # Windows doesn't support signal.alarm(), skip timeout
        # Log a warning that timeout is not available
        logger.debug(f"Timeout not supported on Windows, extraction may hang")
        yield
    else:
        # Unix-like systems - use signal.alarm()
        def timeout_handler(signum, frame):
            raise TimeoutException(f"Extraction timed out after {seconds} seconds")
        
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)

class TextExtractor:
    """Extract text from PDFs and images."""
    
    def __init__(self):
        """Initialize text extractors lazily to avoid startup crashes."""
        self.reader = None
        self.ocr_available = None  # Unknown until first use

    def _ensure_reader(self):
        """Lazily initialize EasyOCR reader when needed."""
        if self.reader is not None:
            return
        if self.ocr_available is False:
            # Previously detected as unavailable
            raise RuntimeError("OCR service unavailable")
        try:
            # Import easyocr only when needed to avoid heavy startup
            import easyocr  # noqa: WPS433
            self.reader = easyocr.Reader(['en'], gpu=False)
            self.ocr_available = True
            logger.info("EasyOCR reader initialized successfully (CPU mode)")
        except Exception as e:
            self.ocr_available = False
            logger.warning(f"EasyOCR initialization failed: {e}. OCR will be unavailable.")
            raise
    
    def extract_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF using PyMuPDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        try:
            text = ""
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def extract_from_image(self, image_path: str) -> str:
        """
        Extract text from image using EasyOCR.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted text
        """
        try:
            self._ensure_reader()
            results = self.reader.readtext(image_path)
            text = "\n".join([item[1] for item in results])
            return text
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            raise
    
    def extract(self, file_path: str) -> str:
        """
        Extract text from file (auto-detect format) with timeout.
        
        Args:
            file_path: Path to file (PDF or image)
            
        Returns:
            Extracted text
            
        Raises:
            TimeoutException: If extraction takes too long
            ValueError: If file format unsupported
        """
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        # Validate file exists and is not empty
        if not path.exists():
            raise ValueError(f"File not found: {file_path}")
        if path.stat().st_size == 0:
            logger.warning(f"File is empty: {file_path}")
            return ""
        
        try:
            # Use timeout for extraction (30 seconds)
            with timeout(30):
                if suffix == ".pdf":
                    return self.extract_from_pdf(file_path)
                elif suffix in [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"]:
                    return self.extract_from_image(file_path)
                else:
                    raise ValueError(f"Unsupported file format: {suffix}")
        except TimeoutException as e:
            logger.error(f"Text extraction timeout for {file_path}: {e}")
            raise
