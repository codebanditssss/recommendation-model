import pdfplumber
import logging

logger = logging.getLogger(__name__)

class PDFExtractor:
    def __init__(self):
        self.current_file = None

    def extract_text(self, pdf_path):
        """Extract text from PDF file"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                self.current_file = pdf_path
                text = ''
                for page in pdf.pages:
                    text += page.extract_text() or ''
                return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            return None