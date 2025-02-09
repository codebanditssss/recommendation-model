import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import spacy
from skills_matcher import SkillsMatcher
from text_cleaner import TextCleaner
from pdf_extractor import PDFExtractor

logger = logging.getLogger(__name__)

class CVAnalyzer:
    def __init__(self, skills_db_path: str, output_dir: str = "processed_data"):
        """Initialize CV Analyzer with paths and components"""
        self.skills_db_path = Path(skills_db_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.pdf_extractor = PDFExtractor()
        self.text_cleaner = TextCleaner()
        self.skills_matcher = SkillsMatcher(str(skills_db_path))
        
        # Initialize skills storage
        self.extracted_skills = {}
        
    def analyze_cv(self, cv_path: str) -> Optional[Dict]:
        """Analyze a single CV and extract skills"""
        try:
            logger.info(f"Processing: {Path(cv_path).name}")
            
            # Extract text from CV
            raw_text = self.pdf_extractor.extract_text(cv_path)
            if not raw_text:
                logger.error(f"Failed to extract text from {cv_path}")
                return None
            
            logger.info(f"Successfully extracted text from {Path(cv_path).name}")
            
            # Clean text
            cleaned_text = self.text_cleaner.clean_text(raw_text)
            
            # Find skills
            skills = self.skills_matcher.find_skills(cleaned_text)
            
            # Store skills for this CV
            filename = Path(cv_path).name
            self.extracted_skills[filename] = skills
            
            # Log extracted skills
            flat_skills = [skill['skill'] for category in skills.values() for skill in category]
            logger.info(f"Extracted Skills from {filename}: {', '.join(flat_skills)}")
            
            return {
                'cv_path': cv_path,
                'filename': filename,
                'skills_found': skills
            }
            
        except Exception as e:
            logger.error(f"Error analyzing CV {cv_path}: {str(e)}")
            return None
    
    def save_extracted_skills(self) -> str:
        """Save extracted skills to JSON file"""
        try:
            skills_file = self.output_dir / 'extracted_skills.json'
            with open(skills_file, 'w', encoding='utf-8') as f:
                json.dump(self.extracted_skills, f, indent=2)
            logger.info(f"Saved extracted skills to {skills_file}")
            return str(skills_file)
        except Exception as e:
            logger.error(f"Error saving extracted skills: {str(e)}")
            return ""
    
    def get_search_keywords(self) -> List[str]:
        """Generate search keywords from extracted skills"""
        try:
            # Collect all unique skills across all CVs
            all_skills = set()
            for cv_skills in self.extracted_skills.values():
                for category in cv_skills.values():
                    all_skills.update(skill['skill'] for skill in category)
            
            # Prioritize technical and core professional skills
            priority_skills = []
            other_skills = []
            
            for skill in all_skills:
                skill_lower = skill.lower()
                if any(tech in skill_lower for tech in ['python', 'java', 'react', 'node', 'sql', 'aws']):
                    priority_skills.append(skill)
                else:
                    other_skills.append(skill)
            
            # Combine skills with priority skills first, limit to top 5
            search_keywords = priority_skills[:3] + other_skills[:2]
            
            logger.info(f"Generated search keywords: {', '.join(search_keywords)}")
            return search_keywords
            
        except Exception as e:
            logger.error(f"Error generating search keywords: {str(e)}")
            return []

def analyze_cvs(cv_dir: str, skills_db_path: str) -> Optional[str]:
    """Analyze all CVs in directory and return path to extracted skills"""
    try:
        cv_dir_path = Path(cv_dir)
        if not cv_dir_path.exists():
            logger.error(f"CV directory not found: {cv_dir}")
            return None
            
        # Initialize analyzer
        analyzer = CVAnalyzer(skills_db_path)
        
        # Get all CV files
        cv_files = []
        for ext in ['.pdf', '.PDF', '.docx', '.DOCX']:
            cv_files.extend(cv_dir_path.glob(f'*{ext}'))
        
        if not cv_files:
            logger.error("No CV files found")
            return None
            
        logger.info(f"Found {len(cv_files)} CV files to process")
        
        # Process each CV
        for cv_file in cv_files:
            analyzer.analyze_cv(str(cv_file))
        
        # Save and return path to extracted skills
        return analyzer.save_extracted_skills()
        
    except Exception as e:
        logger.error(f"Error in CV analysis: {str(e)}")
        return None

if __name__ == "__main__":
    # Example usage
    skills_file = analyze_cvs(
        cv_dir="data/cvs",
        skills_db_path="data/skills_database/professional_skills.json"
    )
    
    if skills_file:
        print(f"\nSkills extracted and saved to: {skills_file}")
    else:
        print("\nFailed to analyze CVs. Check the logs for details.")