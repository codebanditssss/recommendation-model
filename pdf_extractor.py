import pdfplumber
import docx
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class PDFExtractor:
    def __init__(self):
        """Initialize the PDF Extractor"""
        self.current_file = None

    def extract_text(self, file_path: str) -> Optional[str]:
        """
        Extract text from PDF or DOCX file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted text or None if extraction fails
        """
        try:
            file_path = Path(file_path)
            self.current_file = file_path
            
            # Extract based on file extension
            if file_path.suffix.lower() == '.pdf':
                return self._extract_from_pdf(file_path)
            elif file_path.suffix.lower() == '.docx':
                return self._extract_from_docx(file_path)
            else:
                logger.error(f"Unsupported file format: {file_path.suffix}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            return None

    def _extract_from_pdf(self, file_path: Path) -> Optional[str]:
        """Extract text from PDF file"""
        try:
            with pdfplumber.open(file_path) as pdf:
                text = ''
                for page in pdf.pages:
                    text += page.extract_text() or ''
                return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
            return None

    def _extract_from_docx(self, file_path: Path) -> Optional[str]:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = '\n'.join(paragraph.text for paragraph in doc.paragraphs)
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from DOCX {file_path}: {str(e)}")
            return None

    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        if not text:
            return ""
            
        # Remove multiple spaces
        text = ' '.join(text.split())
        
        # Remove multiple newlines
        text = '\n'.join(line.strip() for line in text.splitlines() if line.strip())
        
        return text.strip()

# Example usage
if __name__ == "__main__":
    # Initialize extractor
    extractor = PDFExtractor()
    
    # Example PDF extraction
    pdf_path = "data/cvs/example.pdf"
    if Path(pdf_path).exists():
        text = extractor.extract_text(pdf_path)
        if text:
            print("Successfully extracted text from PDF:")
            print(text[:500] + "..." if len(text) > 500 else text)
        else:
            print("Failed to extract text from PDF")
            
    # Example DOCX extraction
    docx_path = "data/cvs/example.docx"
    if Path(docx_path).exists():
        text = extractor.extract_text(docx_path)
        if text:
            print("\nSuccessfully extracted text from DOCX:")
            print(text[:500] + "..." if len(text) > 500 else text)
        else:
            print("\nFailed to extract text from DOCX")