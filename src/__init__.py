# src/__init__.py
from .extractor import process_pdfs  # Expose main function
from .heading_classifier import PDFOutlineExtractor

__all__ = ['process_pdfs', 'PDFOutlineExtractor']