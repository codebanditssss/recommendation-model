import json
import pandas as pd
from datetime import datetime
from apify_client import ApifyClient
import logging
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def scrape_indeed_jobs(search_query, location="", num_pages=3):
    """
    Scrape Indeed jobs using Apify API with misceres/indeed-scraper
    
    Parameters:
    search_query (str): The job search query
    location (str): Location for job search (e.g., "Mumbai, India")
    num_pages (int): Number of pages to scrape
    """
    # Initialize the ApifyClient with your API token
    client = ApifyClient("apify_api_birIQxPdChTArehXsNa7IBb0N1C6r53QNeaw")

    # Prepare the actor input
    run_input = {
        "country": "IN",           # Country code for India
        "position": search_query,   # Job title/keyword
        "location": location,       # Location
        "maxItems": num_pages * 15, # Approximate number of results
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
        
        # Run the actor and wait for it to finish
        run = client.actor("misceres/indeed-scraper").call(run_input=run_input)
        
        if not run:
            logger.error("Failed to start the actor run")
            return

        # Fetch results from the actor's dataset
        jobs_data = []
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Get items from the dataset
        dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        logger.info(f"Retrieved {len(dataset_items)} items from the dataset")

        for item in dataset_items:
            try:
                # Extract job details with proper error checking
                title = item.get('title', item.get('jobTitle', 'Not specified'))
                company = item.get('company', item.get('companyName', 'Not specified'))
                location = item.get('location', item.get('jobLocation', 'Not specified'))
                
                # Get description and clean it
                description = item.get('description', item.get('jobDescription', ''))
                if description:
                    # Remove extra whitespace and truncate
                    description = ' '.join(description.split())
                    if len(description) > 200:
                        description = description[:200] + "..."
                else:
                    description = "Not specified"

                job_data = {
                    "JobTitle": title,
                    "Company": company,
                    "Location": location,
                    "ExtractDate": current_date,
                    "Summary": description,
                    "Salary": item.get('salary', 'Not specified'),
                    "JobUrl": item.get('url', item.get('jobUrl', 'Not specified')),
                    "PostedDate": item.get('date', item.get('postDate', 'Not specified')),
                    "JobType": item.get('jobType', 'Not specified'),
                }

                # Log the raw item for debugging
                logger.debug(f"Raw job data: {json.dumps(item, indent=2)}")
                
                jobs_data.append(job_data)
                logger.info(f"Successfully scraped: {title} at {company}")
                
            except Exception as e:
                logger.error(f"Error processing job item: {str(e)}")
                logger.debug(f"Problematic item: {json.dumps(item, indent=2)}")
                continue

        if jobs_data:
            # Create output directory if it doesn't exist
            output_dir = "scraped_data"
            os.makedirs(output_dir, exist_ok=True)

            # Save to Excel
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            excel_filename = f"{output_dir}/indeed_jobs_{timestamp}.xlsx"
            df = pd.DataFrame(jobs_data)
            df.to_excel(excel_filename, index=False, sheet_name='Jobs')

            # Save to JSON
            json_filename = f"{output_dir}/indeed_jobs_{timestamp}.json"
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
    # Example usage
    try:
        results = scrape_indeed_jobs(
            search_query="Python Developer",    
            location="Mumbai, Maharashtra",     # City, State format
            num_pages=3
        )
        
        if results is not None:
            print("\nScraping completed successfully!")
            print("\nSample of scraped jobs:")
            print(results[['JobTitle', 'Company', 'Location']].head())
            
            # Save sample to a text file for review
            with open("sample_results.txt", "w", encoding="utf-8") as f:
                f.write(results.to_string())
            
    except Exception as e:
        logger.error(f"Main execution error: {str(e)}")