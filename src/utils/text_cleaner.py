import re
import spacy
import logging

logger = logging.getLogger(__name__)

class TextCleaner:
    def __init__(self, spacy_model='en_core_web_sm'):
        self.nlp = spacy.load(spacy_model)
    
    def clean_text(self, text):
        """Clean and preprocess text"""
        if text is None:
            return ''
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and extra whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Use spaCy for lemmatization
        doc = self.nlp(text)
        text = ' '.join([token.lemma_ for token in doc])
        
        return text.strip()