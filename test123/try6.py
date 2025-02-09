import json
import pandas as pd
from datetime import datetime
from apify_client import ApifyClient
import logging
import os
import re

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def standardize_salary(salary_text):
    """
    Standardize salary information from different formats
    Returns: A standardized string format of the salary
    """
    if not salary_text or salary_text == 'Not specified':
        return 'Not specified'
    
    try:
        # Clean the salary text
        salary_text = str(salary_text).strip()
        
        # Handle monthly salaries
        if 'month' in salary_text.lower():
            # Extract amounts
            amounts = re.findall(r'₹?\s*(\d+(?:,\d+)*(?:\.\d+)?)', salary_text)
            if len(amounts) == 2:
                # Convert to yearly and format as range
                min_salary = float(amounts[0].replace(',', '')) * 12
                max_salary = float(amounts[1].replace(',', '')) * 12
                return f"₹{min_salary:,.0f} - ₹{max_salary:,.0f} per year"
            elif len(amounts) == 1:
                # Single monthly amount
                yearly = float(amounts[0].replace(',', '')) * 12
                return f"₹{yearly:,.0f} per year"
        
        # Handle yearly salaries
        elif 'year' in salary_text.lower():
            # Extract amounts
            amounts = re.findall(r'₹?\s*(\d+(?:,\d+)*(?:\.\d+)?)', salary_text)
            if len(amounts) == 2:
                min_salary = float(amounts[0].replace(',', ''))
                max_salary = float(amounts[1].replace(',', ''))
                return f"₹{min_salary:,.0f} - ₹{max_salary:,.0f} per year"
            elif len(amounts) == 1:
                salary = float(amounts[0].replace(',', ''))
                return f"₹{salary:,.0f} per year"
        
        # If no month/year specified but has numbers
        amounts = re.findall(r'₹?\s*(\d+(?:,\d+)*(?:\.\d+)?)', salary_text)
        if amounts:
            if len(amounts) == 2:
                min_salary = float(amounts[0].replace(',', ''))
                max_salary = float(amounts[1].replace(',', ''))
                return f"₹{min_salary:,.0f} - ₹{max_salary:,.0f}"
            elif len(amounts) == 1:
                salary = float(amounts[0].replace(',', ''))
                return f"₹{salary:,.0f}"
        
        return salary_text
    except Exception as e:
        logger.error(f"Error standardizing salary: {str(e)} for text: {salary_text}")
        return salary_text

def extract_job_title(item):
    """Enhanced job title extraction with better field handling"""
    # First try positionName as it's the most reliable
    if item.get('positionName'):
        return item['positionName'].strip()
    
    # Try to extract title from HTML content if available
    if item.get('descriptionHTML'):
        try:
            if '<h1' in item['descriptionHTML'] and 'Title:' in item['descriptionHTML']:
                title_match = re.search(r'<h1[^>]*>.*?Title:\s*([^<]+)', item['descriptionHTML'])
                if title_match:
                    return title_match.group(1).strip()
        except:
            pass

    # Check description for salary information
    if item.get('description'):
        try:
            title_match = re.search(r'Title:\s*([^\n]+)', item['description'])
            if title_match:
                return title_match.group(1).strip()
        except:
            pass

    # Check other possible title fields
    title_fields = ['title', 'jobTitle', 'position', 'role']
    for field in title_fields:
        if item.get(field):
            value = item[field]
            if isinstance(value, str) and value.strip():
                return value.strip()
            elif isinstance(value, list) and value:
                return value[0].strip()

    return "Position Not Specified"

def extract_job_type(item):
    """Enhanced job type extraction"""
    if isinstance(item.get('jobType'), list):
        return ', '.join(item['jobType'])
    elif isinstance(item.get('jobType'), str):
        return item['jobType']
    return item.get('employmentType', 'Not specified')

def clean_date(date_str):
    """Clean and standardize the posted date format"""
    if not date_str or date_str == 'Not specified':
        return 'Not specified'
    try:
        # Remove 'Posted' or 'posted' if present
        date_str = date_str.lower().replace('posted', '').strip()
        # Handle common formats
        if 'just' in date_str or 'today' in date_str:
            return datetime.now().strftime('%Y-%m-%d')
        if 'yesterday' in date_str:
            return (datetime.now() - pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        if 'ago' in date_str:
            parts = date_str.split()
            if len(parts) >= 3:
                try:
                    num = int(parts[0].replace('+', ''))
                    unit = parts[1].lower()
                    if 'day' in unit:
                        delta = pd.Timedelta(days=num)
                    elif 'hour' in unit:
                        delta = pd.Timedelta(hours=num)
                    elif 'minute' in unit:
                        delta = pd.Timedelta(minutes=num)
                    else:
                        return date_str
                    return (datetime.now() - delta).strftime('%Y-%m-%d')
                except:
                    return date_str
        return date_str
    except:
        return 'Not specified'

def scrape_indeed_jobs(search_query, location="", num_pages=3):
    """
    Scrape Indeed jobs using Apify API with misceres/indeed-scraper
    """
    client = ApifyClient("apify_api_birIQxPdChTArehXsNa7IBb0N1C6r53QNeaw")

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

    try:
        logger.info(f"Starting Indeed scrape for: {search_query} in {location if location else 'all locations'}")
        
        run = client.actor("misceres/indeed-scraper").call(run_input=run_input)
        
        if not run:
            logger.error("Failed to start the actor run")
            return

        jobs_data = []
        dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        logger.info(f"Retrieved {len(dataset_items)} items from the dataset")

        for item in dataset_items:
            try:
                # Extract salary from multiple possible sources
                salary = item.get('salary')
                if not salary:
                    # Try to find salary in description
                    desc = item.get('description', '')
                    salary_match = re.search(r'(?:salary|pay|compensation):\s*(₹[\d,.]+ *-? *₹?[\d,.]+ *(?:per|a|\/)\s*(?:year|month|annum))', 
                                          desc, re.IGNORECASE)
                    if salary_match:
                        salary = salary_match.group(1)

                job_data = {
                    "JobTitle": extract_job_title(item),
                    "Company": item.get('company', 'Not specified'),
                    "Location": item.get('location', 'Not specified'),
                    "Description": item.get('description', 'Not specified'),
                    "Salary": standardize_salary(salary),
                    "JobURL": item.get('url', item.get('jobUrl', 'Not specified')),
                    "PostedDate": clean_date(item.get('postedAt', item.get('date', 'Not specified'))),
                    "JobType": extract_job_type(item)
                }

                jobs_data.append(job_data)
                logger.info(f"Successfully scraped: {job_data['JobTitle']} at {job_data['Company']}")
                
            except Exception as e:
                logger.error(f"Error processing job item: {str(e)}")
                continue

        if jobs_data:
            # Create output directory
            output_dir = "scraped_data"
            os.makedirs(output_dir, exist_ok=True)

            # Fixed filenames (will overwrite existing files)
            excel_filename = f"{output_dir}/indeed_jobs.xlsx"
            json_filename = f"{output_dir}/indeed_jobs.json"

            # Save to Excel
            df = pd.DataFrame(jobs_data)
            df.to_excel(excel_filename, index=False, sheet_name='Jobs')

            # Save to JSON
            with open(json_filename, "w", encoding="utf-8") as f:
                json.dump(jobs_data, f, ensure_ascii=False, indent=4)

            logger.info(f"\nSuccessfully scraped {len(jobs_data)} jobs")
            logger.info(f"Data saved to {excel_filename} and {json_filename}")
            
            return df

        else:
            logger.warning("No jobs were scraped successfully")
            return None

    except Exception as e:
        logger.error(f"An error occurred during scraping: {str(e)}")
        return None

if __name__ == "__main__":
    try:
        results = scrape_indeed_jobs(
            search_query="Python Developer",    
            location="Mumbai, Maharashtra",
            num_pages=3
        )
        
        if results is not None:
            print("\nScraping completed successfully!")
            print("\nSample of scraped jobs:")
            print(results[['JobTitle', 'Company', 'Location', 'Salary']].head())
    except Exception as e:
        logger.error(f"Main execution error: {str(e)}")