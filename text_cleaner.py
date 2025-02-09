import re
import string
import logging
from typing import Optional
import spacy
from spacy.language import Language

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TextCleaner:
    """
    A class to clean and preprocess text data for skill matching.
    """
    
    def __init__(self, spacy_model: str = 'en_core_web_sm'):
        """
        Initialize the TextCleaner with specified spaCy model.
        
        Args:
            spacy_model: Name of the spaCy model to use (default: 'en_core_web_sm')
        """
        try:
            self.nlp = spacy.load(spacy_model)
            # Add custom components to the pipeline
            self.nlp.add_pipe('custom_preprocessor', before='parser')
            logger.info(f"Initialized TextCleaner with {spacy_model} model")
        except Exception as e:
            logger.error(f"Error loading spaCy model: {str(e)}")
            raise

    @staticmethod
    @Language.component("custom_preprocessor")
    def custom_preprocessor(doc):
        """Custom preprocessing component for spaCy pipeline"""
        return doc

    def remove_special_characters(self, text: str) -> str:
        """
        Remove special characters while preserving important punctuation.
        
        Args:
            text: Input text string
            
        Returns:
            Cleaned text string
        """
        # Keep hyphens for compound words, periods for abbreviations
        text = re.sub(r'[^\w\s\-\.]', ' ', text)
        # Remove standalone hyphens and periods
        text = re.sub(r'\s+[-\.]\s+', ' ', text)
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace in text.
        
        Args:
            text: Input text string
            
        Returns:
            Text with normalized whitespace
        """
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        return text.strip()

    def normalize_technical_terms(self, text: str) -> str:
        """
        Normalize common technical terms and abbreviations.
        
        Args:
            text: Input text string
            
        Returns:
            Text with normalized technical terms
        """
        # Define common variations and their normalized forms
        normalizations = {
            r'java\s*script': 'javascript',
            r'type\s*script': 'typescript',
            r'react\.?\s*js': 'react',
            r'node\.?\s*js': 'nodejs',
            r'vue\.?\s*js': 'vue',
            r'next\.?\s*js': 'nextjs',
            r'mongo\s*db': 'mongodb',
            r'ms[- ]sql': 'mssql',
            r'my[- ]sql': 'mysql',
            r'postgres\s*sql': 'postgresql',
            r'aws\s+cloud': 'aws',
            r'azure\s+cloud': 'azure',
            r'gcp\s+cloud': 'gcp',
            r'dot\s*net': '.net',
            r'c\s*#': 'csharp',
            r'c\s*\+\+': 'cpp'
        }
        
        # Apply normalizations
        for pattern, replacement in normalizations.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text

    def clean_text(self, text: Optional[str], remove_stopwords: bool = True) -> str:
        """
        Clean and preprocess text data.
        
        Args:
            text: Input text string
            remove_stopwords: Whether to remove stopwords (default: True)
            
        Returns:
            Cleaned and preprocessed text
        """
        if text is None:
            logger.warning("Received None as input text")
            return ""
            
        try:
            # Convert to string if not already
            text = str(text)
            
            # Convert to lowercase
            text = text.lower()
            
            # Remove URLs
            text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
            
            # Remove email addresses
            text = re.sub(r'\S+@\S+', '', text)
            
            # Normalize technical terms
            text = self.normalize_technical_terms(text)
            
            # Remove special characters
            text = self.remove_special_characters(text)
            
            # Process with spaCy
            doc = self.nlp(text)
            
            # Tokenize and clean
            tokens = []
            for token in doc:
                # Skip if it's a stopword and remove_stopwords is True
                if remove_stopwords and token.is_stop:
                    continue
                    
                # Skip if it's punctuation or whitespace
                if token.is_punct or token.is_space:
                    continue
                    
                # Add token's lemma
                tokens.append(token.lemma_)
            
            # Join tokens back into text
            text = ' '.join(tokens)
            
            # Normalize whitespace
            text = self.normalize_whitespace(text)
            
            return text
            
        except Exception as e:
            logger.error(f"Error cleaning text: {str(e)}")
            # Return empty string on error
            return ""

    def extract_technical_terms(self, text: str) -> list:
        """
        Extract technical terms and skills from text.
        
        Args:
            text: Input text string
            
        Returns:
            List of extracted technical terms
        """
        try:
            # Clean the text first
            cleaned_text = self.clean_text(text)
            
            # Process with spaCy
            doc = self.nlp(cleaned_text)
            
            # Extract noun phrases and technical terms
            technical_terms = []
            for chunk in doc.noun_chunks:
                # Add noun phrases that might be technical terms
                technical_terms.append(chunk.text)
            
            # Add single token technical terms
            for token in doc:
                if (token.pos_ in ['NOUN', 'PROPN'] and 
                    token.text not in [term.split()[-1] for term in technical_terms]):
                    technical_terms.append(token.text)
            
            return list(set(technical_terms))
            
        except Exception as e:
            logger.error(f"Error extracting technical terms: {str(e)}")
            return []

# Example usage
if __name__ == "__main__":
    # Initialize the cleaner
    cleaner = TextCleaner()
    
    # Example text
    sample_text = """
    Senior Python Developer needed!
    
    Required Skills:
    - Python, Django, Flask
    - JavaScript/React.js
    - MongoDB, PostgreSQL
    - AWS Cloud experience
    - Strong problem-solving skills
    """
    
    # Clean the text
    cleaned_text = cleaner.clean_text(sample_text)
    print("Cleaned text:")
    print(cleaned_text)
    
    # Extract technical terms
    terms = cleaner.extract_technical_terms(sample_text)
    print("\nExtracted technical terms:")
    print(terms)