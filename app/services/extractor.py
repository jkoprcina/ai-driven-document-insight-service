"""
Text extraction service for PDFs and images.
Supports PyMuPDF for PDFs and EasyOCR for images.
"""
import os
import fitz
import easyocr
from pathlib import Path
from typing import Tuple
import logging

logger = logging.getLogger(__name__)

class TextExtractor:
    """Extract text from PDFs and images."""
    
    def __init__(self):
        """Initialize text extractors."""
        self.reader = easyocr.Reader(['en'], gpu=False)
    
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
            results = self.reader.readtext(image_path)
            text = "\n".join([item[1] for item in results])
            return text
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            raise
    
    def extract(self, file_path: str) -> str:
        """
        Extract text from file (auto-detect format).
        
        Args:
            file_path: Path to file (PDF or image)
            
        Returns:
            Extracted text
        """
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        if suffix == ".pdf":
            return self.extract_from_pdf(file_path)
        elif suffix in [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"]:
            return self.extract_from_image(file_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
