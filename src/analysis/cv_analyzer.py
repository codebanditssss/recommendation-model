import logging
from ..utils.pdf_extractor import PDFExtractor
from ..utils.text_cleaner import TextCleaner
from ..utils.skills_matcher import SkillsMatcher

logger = logging.getLogger(__name__)

class CVAnalyzer:
    def __init__(self, skills_db_path, spacy_model='en_core_web_sm'):
        self.pdf_extractor = PDFExtractor()
        self.text_cleaner = TextCleaner(spacy_model)
        self.skills_matcher = SkillsMatcher(skills_db_path)
    
    def analyze_cv(self, cv_path):
        """Analyze a single CV"""
        try:
            # Extract text from CV
            raw_text = self.pdf_extractor.extract_text(cv_path)
            if not raw_text:
                return None
            
            # Clean text
            cleaned_text = self.text_cleaner.clean_text(raw_text)
            
            # Find skills
            skills = self.skills_matcher.find_skills(cleaned_text)
            
            return {
                'cv_path': cv_path,
                'skills_found': skills
            }
            
        except Exception as e:
            logger.error(f"Error analyzing CV {cv_path}: {str(e)}")
            return None