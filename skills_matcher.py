import json
import os
import logging
from collections import defaultdict
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class SkillsMatcher:
    def __init__(self, path: str):
        """
        Initialize SkillsMatcher with skills database
        
        Args:
            path: Path to the skills database JSON file
        """
        self.skills_data = self.load_skills(path)

    def load_skills(self, path: str) -> Dict:
        """
        Load skills database from JSON file
        
        Args:
            path: Path to skills database file
            
        Returns:
            Dictionary containing skills data
        """
        try:
            if not os.path.exists(path):
                logger.error(f"Skills database file not found: {path}")
                return {}
                
            if os.path.getsize(path) == 0:
                logger.error("Skills database file is empty")
                return {}
                
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Error loading skills database: {str(e)}")
            return {}

    def find_skills(self, text: str) -> Dict[str, List]:
        """
        Find skills in text using the skills database
        
        Args:
            text: Text to search for skills
            
        Returns:
            Dictionary mapping skill categories to lists of found skills
        """
        try:
            found_skills = defaultdict(list)
            text = text.lower()
            
            for category, data in self.skills_data.items():
                skills = data.get('skills', [])
                priority = data.get('priority', 'Medium')
                
                for skill in skills:
                    if skill.lower() in text:
                        found_skills[category].append({
                            'skill': skill,
                            'priority': priority
                        })
            
            return dict(found_skills)
            
        except Exception as e:
            logger.error(f"Error finding skills: {str(e)}")
            return {}

    def get_skill_priority(self, skill: str) -> Optional[str]:
        """
        Get priority level for a given skill
        
        Args:
            skill: Skill name to lookup
            
        Returns:
            Priority level of the skill or None if not found
        """
        try:
            skill = skill.lower()
            for category, data in self.skills_data.items():
                if skill in [s.lower() for s in data.get('skills', [])]:
                    return data.get('priority')
            return None
            
        except Exception as e:
            logger.error(f"Error getting skill priority: {str(e)}")
            return None

    def categorize_skill(self, skill: str) -> Optional[str]:
        """
        Get category for a given skill
        
        Args:
            skill: Skill name to lookup
            
        Returns:
            Category of the skill or None if not found
        """
        try:
            skill = skill.lower()
            for category, data in self.skills_data.items():
                if skill in [s.lower() for s in data.get('skills', [])]:
                    return category
            return None
            
        except Exception as e:
            logger.error(f"Error categorizing skill: {str(e)}")
            return None

# Example usage
if __name__ == "__main__":
    # Initialize skills matcher
    matcher = SkillsMatcher("data/skills_database/professional_skills.json")
    
    # Example text
    sample_text = """
    Experienced Python developer with strong skills in Django and React.
    Proficient in SQL databases and AWS cloud services.
    Excellent problem-solving and communication skills.
    """
    
    # Find skills
    found_skills = matcher.find_skills(sample_text)
    
    # Print results
    print("\nFound Skills:")
    for category, skills in found_skills.items():
        print(f"\n{category}:")
        for skill in skills:
            print(f"- {skill['skill']} (Priority: {skill['priority']})")