import json
import os
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class SkillsMatcher:
    def __init__(self, path):
        self.skills_data = self.load_skills(path)

    def load_skills(self, path):
        """Load skills database from JSON file"""
        try:
            if os.path.getsize(path) == 0:
                raise ValueError("Skills database file is empty")
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading skills database: {str(e)}")
            return {}

    def find_skills(self, text):
        """Find skills in text"""
        found_skills = defaultdict(list)
        
        for category, data in self.skills_data.items():
            for skill in data['skills']:
                if skill.lower() in text.lower():
                    found_skills[category].append({
                        'skill': skill,
                        'priority': data['priority']
                    })
        
        return dict(found_skills)