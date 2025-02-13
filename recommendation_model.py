import json
import pandas as pd
from datetime import datetime
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# Import from local modules
from cv_analyzer2 import analyze_cvs
from apifyy import scrape_indeed_jobs
from text_cleaner import TextCleaner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('recommendation_model.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class JobRecommender:
    def __init__(self, base_dir: str = "."):
        """
        Initialize the job recommender
        
        Args:
            base_dir: Base directory for the project
        """
        self.base_dir = Path(base_dir)
        self.cv_dir = self.base_dir / "data" / "cvs"
        self.skills_db = self.base_dir / "data" / "skills_database" / "professional_skills.json"
        self.output_dir = self.base_dir / "recommendations"
        
        # Create necessary directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.text_cleaner = TextCleaner()
        
    def calculate_match_score(self, 
                            cv_skills: Dict[str, List], 
                            job_skills: List[str]) -> Tuple[float, List[str], List[str]]:
        """
        Calculate match score between CV skills and job requirements
        
        Returns:
            Tuple containing:
            - Match score (0-100)
            - Matching skills
            - Missing skills
        """
        try:
            # Flatten CV skills from all categories
            cv_skill_set = set()
            for category, skills in cv_skills.items():
                cv_skill_set.update([skill['skill'].lower() for skill in skills])
            
            # Convert job skills to set for comparison
            job_skill_set = set(skill.lower() for skill in job_skills)
            
            # Find matching and missing skills
            matching_skills = cv_skill_set.intersection(job_skill_set)
            missing_skills = job_skill_set - cv_skill_set
            
            # Calculate match score
            if not job_skill_set:
                match_score = 0
            else:
                match_score = (len(matching_skills) / len(job_skill_set)) * 100
                
            return match_score, list(matching_skills), list(missing_skills)
            
        except Exception as e:
            logger.error(f"Error calculating match score: {str(e)}")
            return 0.0, [], []
    
    def extract_job_skills(self, job_description: str) -> List[str]:
        """Extract skills from job description"""
        try:
            # Clean the job description
            cleaned_text = self.text_cleaner.clean_text(job_description)
            
            # Load skills database
            with open(self.skills_db, 'r') as f:
                skills_data = json.load(f)
            
            # Look for skills in the job description
            found_skills = set()
            for category in skills_data.values():
                for skill in category['skills']:
                    if skill.lower() in cleaned_text.lower():
                        found_skills.add(skill)
            
            return list(found_skills)
            
        except Exception as e:
            logger.error(f"Error extracting job skills: {str(e)}")
            return []
    
    def generate_recommendations(self, 
                               location: str = "Mumbai", 
                               min_match_score: float = 50) -> Optional[pd.DataFrame]:
        """
        Generate job recommendations for all CVs
        
        Args:
            location: Location for job search
            min_match_score: Minimum match score to include in recommendations
        """
        try:
            # Step 1: Analyze CVs
            logger.info("Starting CV analysis...")
            skills_file = analyze_cvs(str(self.cv_dir), str(self.skills_db))
            
            if not skills_file:
                logger.error("Failed to analyze CVs")
                return None
            
            # Load extracted skills
            with open(skills_file, 'r') as f:
                cv_skills_data = json.load(f)
            
            # Step 2: Get search keywords from CV skills
            all_skills = set()
            for cv_data in cv_skills_data.values():
                for category in cv_data.values():
                    all_skills.update(skill['skill'] for skill in category)
            search_keywords = list(all_skills)[:5]  # Use top 5 skills
            
            # Step 3: Scrape job listings
            logger.info(f"Scraping jobs with keywords: {', '.join(search_keywords)}")
            jobs_df = scrape_indeed_jobs(keywords=search_keywords, location=location)
            
            if jobs_df is None or jobs_df.empty:
                logger.error("No jobs found")
                return None
            
            # Step 4: Generate recommendations
            recommendations = []
            
            for cv_filename, cv_skills in cv_skills_data.items():
                logger.info(f"Generating recommendations for {cv_filename}")
                
                for _, job in jobs_df.iterrows():
                    # Extract skills from job description
                    job_skills = self.extract_job_skills(job['Description'])
                    
                    # Calculate match score
                    match_score, matching_skills, missing_skills = self.calculate_match_score(
                        cv_skills, job_skills
                    )
                    
                    if match_score >= min_match_score:
                        recommendations.append({
                            'CV_Filename': cv_filename,
                            'Job_Title': job['JobTitle'],
                            'Company': job['Company'],
                            'Location': job['Location'],
                            'Match_Score': round(match_score, 2),
                            'Matching_Skills': ', '.join(matching_skills),
                            'Missing_Skills': ', '.join(missing_skills),
                            'Job_URL': job['JobURL'],
                            'Posted_Date': job['PostedDate'],
                            'Salary': job['Salary']
                        })
            
            if not recommendations:
                logger.warning("No recommendations met the minimum match score")
                return None
            
            # Create recommendations DataFrame
            recommendations_df = pd.DataFrame(recommendations)
            
            # Sort by match score
            recommendations_df = recommendations_df.sort_values(
                ['CV_Filename', 'Match_Score'], 
                ascending=[True, False]
            )
            
            # Save recommendations
            self.save_recommendations(recommendations_df)
            
            return recommendations_df
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return None
    
    def save_recommendations(self, df: pd.DataFrame) -> None:
        """Save recommendations to Excel file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            excel_path = self.output_dir / f'job_recommendations_{timestamp}.xlsx'
            
            # Create Excel writer
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                # Write main recommendations
                df.to_excel(writer, sheet_name='Recommendations', index=False)
                
                # Add summary sheet
                summary_data = []
                for cv_name in df['CV_Filename'].unique():
                    cv_df = df[df['CV_Filename'] == cv_name]
                    summary_data.append({
                        'CV_Filename': cv_name,
                        'Total_Matches': len(cv_df),
                        'Average_Match_Score': cv_df['Match_Score'].mean(),
                        'Top_Matching_Job': cv_df.iloc[0]['Job_Title'],
                        'Top_Match_Score': cv_df.iloc[0]['Match_Score']
                    })
                
                pd.DataFrame(summary_data).to_excel(
                    writer, 
                    sheet_name='Summary', 
                    index=False
                )
            
            logger.info(f"Recommendations saved to {excel_path}")
            
        except Exception as e:
            logger.error(f"Error saving recommendations: {str(e)}")

def main():
    """Main execution function"""
    try:
        # Initialize recommender
        recommender = JobRecommender()
        
        # Generate recommendations
        recommendations = recommender.generate_recommendations(
            location="Mumbai",
            min_match_score=50
        )
        
        if recommendations is not None:
            # Print summary
            print("\nRecommendation Summary:")
            print(f"Total recommendations generated: {len(recommendations)}")
            
            # Group by CV and show top matches
            for cv_name in recommendations['CV_Filename'].unique():
                cv_recommendations = recommendations[
                    recommendations['CV_Filename'] == cv_name
                ].head(3)
                
                print(f"\nTop 3 matches for {cv_name}:")
                for _, rec in cv_recommendations.iterrows():
                    print(f"- {rec['Job_Title']} at {rec['Company']}")
                    print(f"  Match Score: {rec['Match_Score']}%")
                    print(f"  Key Matching Skills: {rec['Matching_Skills']}")
        else:
            print("\nNo recommendations generated. Please check the following:")
            print("1. Ensure you have CV files in the data/cvs directory")
            print("2. Check that your CVs are in PDF or DOCX format")
            print("3. Verify the skills database file exists")
            print("4. Check the logs for more detailed error messages")
                    
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()