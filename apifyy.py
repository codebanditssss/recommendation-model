import json
import pandas as pd
from datetime import datetime
from apify_client import ApifyClient
import logging
import os
from pathlib import Path
from typing import List, Optional, Dict

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def build_search_query(keywords: List[str]) -> str:
    """Build Indeed search query from keywords"""
    # Combine keywords with OR operator
    return ' OR '.join(f'"{keyword}"' for keyword in keywords)

def scrape_indeed_jobs(skills_file: str = None, 
                      keywords: List[str] = None,
                      location: str = "Mumbai",
                      num_pages: int = 3) -> Optional[pd.DataFrame]:
    """
    Scrape Indeed jobs using Apify API and extracted skills
    
    Args:
        skills_file: Path to JSON file with extracted skills
        keywords: Direct list of keywords (alternative to skills_file)
        location: Job location to search
        num_pages: Number of pages to scrape
    """
    client = ApifyClient("apify_api_birIQxPdChTArehXsNa7IBb0N1C6r53QNeaw")
    
    try:
        # Get search keywords
        search_keywords = []
        if skills_file and Path(skills_file).exists():
            with open(skills_file, 'r') as f:
                skills_data = json.load(f)
                # Extract unique skills from all CVs
                all_skills = set()
                for cv_skills in skills_data.values():
                    for category in cv_skills.values():
                        all_skills.update(skill['skill'] for skill in category)
                search_keywords = list(all_skills)[:5]  # Limit to top 5 skills
        elif keywords:
            search_keywords = keywords
        else:
            search_keywords = ["Python Developer"]  # Default fallback
        
        # Build search query
        search_query = build_search_query(search_keywords)
        logger.info(f"Searching jobs for skills: {', '.join(search_keywords)}")
        
        run_input = {
            "country": "IN",
            "position": search_query,
            "location": location,
            "maxItems": num_pages * 15,
            "startUrls": [
                {
                    "url": f"https://in.indeed.com/jobs?q={search_query}&l={location}"
                }
            ],
            "proxyConfiguration": {
                "useApifyProxy": True
            },
            "maxConcurrency": 1
        }

        # Start the scraping run
        run = client.actor("misceres/indeed-scraper").call(run_input=run_input)
        
        if not run:
            logger.error("Failed to start the actor run")
            return None

        # Process results
        jobs_data = []
        excel_data = []
        dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        logger.info(f"Retrieved {len(dataset_items)} items from the dataset")

        output_dir = Path("scraped_data")
        output_dir.mkdir(exist_ok=True)

        # Process each job listing
        for item in dataset_items:
            try:
                # Get both relative and actual dates
                job_data = process_job_listing(item)
                if job_data:
                    jobs_data.append(job_data['json_data'])
                    excel_data.append(job_data['excel_data'])
                    logger.info(f"Successfully scraped: {job_data['json_data']['JobTitle']} at {job_data['json_data']['Company']}")
            except Exception as e:
                logger.error(f"Error processing job item: {str(e)}")
                continue

        if jobs_data:
            # Save to files
            save_job_data(jobs_data, excel_data, output_dir)
            
            # Return DataFrame for further processing
            return pd.DataFrame(excel_data)
        else:
            logger.warning("No jobs were scraped successfully")
            return None

    except Exception as e:
        logger.error(f"An error occurred during scraping: {str(e)}")
        return None

def process_job_listing(item: Dict) -> Optional[Dict]:
    """Process a single job listing"""
    try:
        # Extract job details with proper error handling
        base_data = {
            "JobTitle": extract_job_title(item),
            "Company": item.get('company', 'Not specified'),
            "Location": item.get('location', 'Not specified'),
            "Description": item.get('description', 'Not specified'),
            "Salary": extract_salary(item),
            "JobURL": item.get('url', item.get('jobUrl', 'Not specified')),
            "JobType": item.get('jobType', 'Not specified')
        }
        
        # Get dates
        json_date, excel_date = get_formatted_dates(
            item.get('postedAt', item.get('date', 'Not specified'))
        )
        
        # Create JSON specific data
        json_data = base_data.copy()
        json_data["PostedDate"] = json_date
        
        # Create Excel specific data
        excel_data = base_data.copy()
        excel_data["PostedDate"] = excel_date
        
        return {
            'json_data': json_data,
            'excel_data': excel_data
        }
    except Exception as e:
        logger.error(f"Error processing job listing: {str(e)}")
        return None

def save_job_data(jobs_data: List[Dict], 
                 excel_data: List[Dict], 
                 output_dir: Path) -> None:
    """Save job data to Excel and JSON files"""
    try:
        # Save to Excel
        excel_filename = output_dir / "indeed_jobs.xlsx"
        df_excel = pd.DataFrame(excel_data)
        df_excel.to_excel(str(excel_filename), index=False, sheet_name='Jobs')

        # Save to JSON
        json_filename = output_dir / "indeed_jobs.json"
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(jobs_data, f, ensure_ascii=False, indent=4)

        logger.info(f"\nSuccessfully scraped {len(jobs_data)} jobs")
        logger.info(f"Data saved to {excel_filename} and {json_filename}")
        
    except Exception as e:
        logger.error(f"Error saving job data: {str(e)}")

# Import existing helper functions
from apify import (
    extract_salary,
    extract_job_title,
    get_formatted_dates,
    standardize_salary
)

if __name__ == "__main__":
    # Example usage
    results = scrape_indeed_jobs(
        keywords=["Python", "Django", "React"],
        location="Mumbai",
        num_pages=3
    )
    
    if results is not None:
        print("\nScraping completed successfully!")
    else:
        print("\nScraping failed. Check the logs for details.")