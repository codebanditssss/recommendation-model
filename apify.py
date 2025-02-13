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

def extract_salary(item):
    """Enhanced salary extraction from both dedicated field and description"""
    # Initialize with None
    salary = None
    
    # Try getting from salary field first
    if item.get('salary'):
        salary = item['salary']
    
    # If not found, try description
    if not salary and item.get('description'):
        desc = item['description']
        # Look for various salary patterns
        patterns = [
            r'(?:salary|pay|compensation|CTC|package):\s*(₹[0-9,.]+\s*-\s*₹[0-9,.]+\s*(?:per|a|\/)\s*(?:year|month|annum))',
            r'(?:salary|pay|compensation|CTC|package):\s*(₹[0-9,.]+\s*(?:per|a|\/)\s*(?:year|month|annum))',
            r'(?:salary|pay|compensation|CTC|package):\s*([0-9,.]+\s*-\s*[0-9,.]+\s*(?:per|a|\/)\s*(?:year|month|annum))',
            r'(?:₹|Rs\.?)\s*([0-9,.]+\s*-\s*[0-9,.]+\s*(?:per|a|\/)\s*(?:year|month|annum))',
            r'([0-9,.]+\s*-\s*[0-9,.]+\s*(?:L|K|lakh|Lacs))',
            r'(₹[0-9,.]+\s*(?:L|K|lakh|Lacs))'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, desc, re.IGNORECASE)
            if match:
                salary = match.group(1)
                break
    
    if salary:
        return standardize_salary(salary)
    return 'Not specified'

def standardize_salary(salary_text):
    """Standardize salary information from different formats"""
    if not salary_text or salary_text == 'Not specified':
        return 'Not specified'
    
    try:
        # Clean the salary text
        salary_text = str(salary_text).strip()
        
        # Convert lakhs to full number
        if re.search(r'(?:L|lakh|Lacs)', salary_text, re.IGNORECASE):
            # Extract numbers before L/lakh/Lacs
            amounts = re.findall(r'([\d.]+)\s*(?:L|lakh|Lacs)', salary_text, re.IGNORECASE)
            if amounts:
                if len(amounts) == 2:
                    min_val = float(amounts[0]) * 100000
                    max_val = float(amounts[1]) * 100000
                    return f"₹{min_val:,.0f} - ₹{max_val:,.0f} per year"
                else:
                    val = float(amounts[0]) * 100000
                    return f"₹{val:,.0f} per year"
        
        # Handle monthly salaries
        if 'month' in salary_text.lower():
            amounts = re.findall(r'₹?\s*(\d+(?:,\d+)*(?:\.\d+)?)', salary_text)
            if len(amounts) == 2:
                min_salary = float(amounts[0].replace(',', '')) * 12
                max_salary = float(amounts[1].replace(',', '')) * 12
                return f"₹{min_salary:,.0f} - ₹{max_salary:,.0f} per year"
            elif len(amounts) == 1:
                yearly = float(amounts[0].replace(',', '')) * 12
                return f"₹{yearly:,.0f} per year"
        
        # Handle yearly salaries
        elif any(x in salary_text.lower() for x in ['year', 'annum', 'pa', 'per annum']):
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
    """Enhanced job title extraction"""
    if item.get('positionName'):
        return item['positionName'].strip()
    
    title_fields = ['title', 'jobTitle', 'position', 'role']
    for field in title_fields:
        if item.get(field):
            value = item[field]
            if isinstance(value, str) and value.strip():
                return value.strip()
            elif isinstance(value, list) and value:
                return value[0].strip()

    # Try extracting from description
    if item.get('description'):
        desc = item['description']
        patterns = [
            r'Title:\s*([^\n]+)',
            r'Role:\s*([^\n]+)',
            r'Position:\s*([^\n]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, desc)
            if match:
                return match.group(1).strip()

    return "Position Not Specified"

def get_formatted_dates(posted_date):
    """Returns both relative and actual dates"""
    if not posted_date or posted_date == 'Not specified':
        return 'Not specified', 'Not specified'
    
    try:
        # If it's already a relative date (e.g., "4 days ago")
        if 'ago' in posted_date.lower():
            # Keep the relative date for JSON
            json_date = posted_date
            
            # Convert to actual date for Excel
            if 'just' in posted_date.lower() or 'today' in posted_date.lower():
                excel_date = datetime.now().strftime('%Y-%m-%d')
            elif 'yesterday' in posted_date.lower():
                excel_date = (datetime.now() - pd.Timedelta(days=1)).strftime('%Y-%m-%d')
            else:
                # Extract number of days/hours
                parts = posted_date.split()
                if len(parts) >= 3:
                    try:
                        num = int(parts[0].replace('+', ''))
                        unit = parts[1].lower()
                        if 'day' in unit:
                            excel_date = (datetime.now() - pd.Timedelta(days=num)).strftime('%Y-%m-%d')
                        elif 'hour' in unit:
                            excel_date = (datetime.now() - pd.Timedelta(hours=num)).strftime('%Y-%m-%d')
                        elif 'minute' in unit:
                            excel_date = datetime.now().strftime('%Y-%m-%d')
                        else:
                            excel_date = posted_date
                    except:
                        excel_date = posted_date
                else:
                    excel_date = posted_date
        else:
            # If it's already a date format, keep it for Excel
            excel_date = posted_date
            # Convert to relative date for JSON
            try:
                post_date = datetime.strptime(posted_date, '%Y-%m-%d')
                delta = datetime.now() - post_date
                if delta.days == 0:
                    json_date = "Today"
                elif delta.days == 1:
                    json_date = "Yesterday"
                else:
                    json_date = f"{delta.days} days ago"
            except:
                json_date = posted_date
        
        return json_date, excel_date
    except:
        return posted_date, posted_date

def scrape_indeed_jobs(search_query, location="", num_pages=3):
    """Scrape Indeed jobs using Apify API"""
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
        excel_data = []
        dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        logger.info(f"Retrieved {len(dataset_items)} items from the dataset")

        for item in dataset_items:
            try:
                # Get both relative and actual dates
                json_date, excel_date = get_formatted_dates(item.get('postedAt', item.get('date', 'Not specified')))
                
                # Base job data
                base_data = {
                    "JobTitle": extract_job_title(item),
                    "Company": item.get('company', 'Not specified'),
                    "Location": item.get('location', 'Not specified'),
                    "Description": item.get('description', 'Not specified'),
                    "Salary": extract_salary(item),
                    "JobURL": item.get('url', item.get('jobUrl', 'Not specified')),
                    "JobType": item.get('jobType', 'Not specified')
                }
                
                # JSON specific data (with relative date)
                json_data = base_data.copy()
                json_data["PostedDate"] = json_date
                jobs_data.append(json_data)
                
                # Excel specific data (with actual date)
                excel_data_row = base_data.copy()
                excel_data_row["PostedDate"] = excel_date
                excel_data.append(excel_data_row)

                logger.info(f"Successfully scraped: {base_data['JobTitle']} at {base_data['Company']}")
                
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

            # Save to Excel with actual dates
            df_excel = pd.DataFrame(excel_data)
            df_excel.to_excel(excel_filename, index=False, sheet_name='Jobs')

            # Save to JSON with relative dates
            with open(json_filename, "w", encoding="utf-8") as f:
                json.dump(jobs_data, f, ensure_ascii=False, indent=4)

            logger.info(f"\nSuccessfully scraped {len(jobs_data)} jobs")
            logger.info(f"Data saved to {excel_filename} and {json_filename}")
            
            return df_excel

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
    except Exception as e:
        logger.error(f"Main execution error: {str(e)}")