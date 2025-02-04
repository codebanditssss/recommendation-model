import os
import logging
from datetime import datetime

# Project paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
CV_DIR = os.path.join(DATA_DIR, 'cvs')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')
REPORTS_DIR = os.path.join(OUTPUT_DIR, 'reports')
LOGS_DIR = os.path.join(OUTPUT_DIR, 'logs')

# Create directories if they don't exist
for dir_path in [DATA_DIR, CV_DIR, OUTPUT_DIR, REPORTS_DIR, LOGS_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Spacy model configuration
SPACY_MODEL = 'en_core_web_sm'

# Skills database file
SKILLS_DB = os.path.join(DATA_DIR, 'skills_database', 'professional_skills.json')

# Logging configuration
LOG_FILE = os.path.join(LOGS_DIR, f'cv_analysis_{datetime.now().strftime("%Y%m%d")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# File extensions to process
VALID_EXTENSIONS = ['.pdf', '.PDF', '.docx', '.DOCX']

# Analysis configurations
MIN_CONFIDENCE_SCORE = 0.7
MAX_SKILLS_PER_CATEGORY = 10