# # import json
# # import pandas as pd
# # from datetime import datetime
# # from apify_client import ApifyClient
# # import logging
# # import os

# # # Set up logging
# # logging.basicConfig(
# #     level=logging.INFO,
# #     format='%(asctime)s - %(levelname)s - %(message)s'
# # )
# # logger = logging.getLogger(__name__)

# # def scrape_indeed_jobs(search_query, location="", num_pages=3):
# #     """
# #     Scrape Indeed jobs using Apify API with misceres/indeed-scraper
    
# #     Parameters:
# #     search_query (str): The job search query
# #     location (str): Location for job search (e.g., "Mumbai, India")
# #     num_pages (int): Number of pages to scrape
# #     """
# #     # Initialize the ApifyClient with your API token
# #     client = ApifyClient("apify_api_birIQxPdChTArehXsNa7IBb0N1C6r53QNeaw")

# #     # Prepare the actor input
# #     run_input = {
# #         "country": "IN",           # Country code for India
# #         "position": search_query,   # Job title/keyword
# #         "location": location,       # Location
# #         "maxItems": num_pages * 15, # Approximate number of results
# #         "startUrls": [
# #             {
# #                 "url": f"https://in.indeed.com/jobs?q={search_query}&l={location}"
# #             }
# #         ],
# #         "proxyConfiguration": {
# #             "useApifyProxy": True
# #         },
# #         "maxConcurrency": 1
# #     }

# #     try:
# #         logger.info(f"Starting Indeed scrape for: {search_query} in {location if location else 'all locations'}")
        
# #         # Run the actor and wait for it to finish
# #         run = client.actor("misceres/indeed-scraper").call(run_input=run_input)
        
# #         if not run:
# #             logger.error("Failed to start the actor run")
# #             return

# #         # Fetch results from the actor's dataset
# #         jobs_data = []
# #         current_date = datetime.now().strftime("%Y-%m-%d")
        
# #         # Get items from the dataset
# #         dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
# #         logger.info(f"Retrieved {len(dataset_items)} items from the dataset")

# #         for item in dataset_items:
# #             try:
# #                 # Extract job details with proper error checking
# #                 title = item.get('title', item.get('jobTitle', 'Not specified'))
# #                 company = item.get('company', item.get('companyName', 'Not specified'))
# #                 location = item.get('location', item.get('jobLocation', 'Not specified'))
                
# #                 # Get description and clean it
# #                 description = item.get('description', item.get('jobDescription', ''))
# #                 if description:
# #                     # Remove extra whitespace and truncate
# #                     description = ' '.join(description.split())
# #                     if len(description) > 200:
# #                         description = description[:200] + "..."
# #                 else:
# #                     description = "Not specified"

# #                 job_data = {
# #                     "JobTitle": title,
# #                     "Company": company,
# #                     "Location": location,
# #                     "ExtractDate": current_date,
# #                     "Summary": description,
# #                     "Salary": item.get('salary', 'Not specified'),
# #                     "JobUrl": item.get('url', item.get('jobUrl', 'Not specified')),
# #                     "PostedDate": item.get('date', item.get('postDate', 'Not specified')),
# #                     "JobType": item.get('jobType', 'Not specified'),
# #                 }

# #                 # Log the raw item for debugging
# #                 logger.debug(f"Raw job data: {json.dumps(item, indent=2)}")
                
# #                 jobs_data.append(job_data)
# #                 logger.info(f"Successfully scraped: {title} at {company}")
                
# #             except Exception as e:
# #                 logger.error(f"Error processing job item: {str(e)}")
# #                 logger.debug(f"Problematic item: {json.dumps(item, indent=2)}")
# #                 continue

# #         if jobs_data:
# #             # Create output directory if it doesn't exist
# #             output_dir = "scraped_data"
# #             os.makedirs(output_dir, exist_ok=True)

# #             # Save to Excel
# #             timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
# #             excel_filename = f"{output_dir}/indeed_jobs_{timestamp}.xlsx"
# #             df = pd.DataFrame(jobs_data)
# #             df.to_excel(excel_filename, index=False, sheet_name='Jobs')

# #             # Save to JSON
# #             json_filename = f"{output_dir}/indeed_jobs_{timestamp}.json"
# #             with open(json_filename, "w", encoding="utf-8") as f:
# #                 json.dump(jobs_data, f, ensure_ascii=False, indent=4)

# #             logger.info(f"\nSuccessfully scraped {len(jobs_data)} jobs")
# #             logger.info(f"Data saved to {excel_filename} and {json_filename}")
            
# #             return df

# #         else:
# #             logger.warning("No jobs were scraped successfully")
# #             return None

# #     except Exception as e:
# #         logger.error(f"An error occurred during scraping: {str(e)}")
# #         return None

# # if __name__ == "__main__":
# #     # Example usage
# #     try:
# #         results = scrape_indeed_jobs(
# #             search_query="Python Developer",    
# #             location="Mumbai, Maharashtra",     # City, State format
# #             num_pages=3
# #         )
        
# #         if results is not None:
# #             print("\nScraping completed successfully!")
# #             print("\nSample of scraped jobs:")
# #             print(results[['JobTitle', 'Company', 'Location']].head())
            
# #             # Save sample to a text file for review
# #             with open("sample_results.txt", "w", encoding="utf-8") as f:
# #                 f.write(results.to_string())
            
# #     except Exception as e:
# #         logger.error(f"Main execution error: {str(e)}")

# import json
# import pandas as pd
# from datetime import datetime
# from apify_client import ApifyClient
# import logging
# import os

# # Set up logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# def clean_date(date_str):
#     """Clean and standardize the posted date format"""
#     if not date_str or date_str == 'Not specified':
#         return 'Not specified'
#     try:
#         # Remove 'Posted' or 'posted' if present
#         date_str = date_str.lower().replace('posted', '').strip()
#         # Handle common formats
#         if 'just' in date_str or 'today' in date_str:
#             return datetime.now().strftime('%Y-%m-%d')
#         if 'yesterday' in date_str:
#             return (datetime.now() - pd.Timedelta(days=1)).strftime('%Y-%m-%d')
#         if 'ago' in date_str:
#             # Extract number and unit from strings like "30+ days ago" or "5 hours ago"
#             parts = date_str.split()
#             if len(parts) >= 3:
#                 try:
#                     num = int(parts[0].replace('+', ''))
#                     unit = parts[1].lower()
#                     if 'day' in unit:
#                         delta = pd.Timedelta(days=num)
#                     elif 'hour' in unit:
#                         delta = pd.Timedelta(hours=num)
#                     elif 'minute' in unit:
#                         delta = pd.Timedelta(minutes=num)
#                     else:
#                         return date_str
#                     return (datetime.now() - delta).strftime('%Y-%m-%d')
#                 except:
#                     return date_str
#         return date_str
#     except:
#         return 'Not specified'

# def scrape_indeed_jobs(search_query, location="", num_pages=3):
#     """
#     Scrape Indeed jobs using Apify API with misceres/indeed-scraper
    
#     Parameters:
#     search_query (str): The job search query
#     location (str): Location for job search (e.g., "Mumbai, India")
#     num_pages (int): Number of pages to scrape
#     """
#     client = ApifyClient("apify_api_birIQxPdChTArehXsNa7IBb0N1C6r53QNeaw")

#     run_input = {
#         "country": "IN",
#         "position": search_query,
#         "location": location,
#         "maxItems": num_pages * 15,
#         "startUrls": [
#             {
#                 "url": f"https://in.indeed.com/jobs?q={search_query}&l={location}"
#             }
#         ],
#         "proxyConfiguration": {
#             "useApifyProxy": True
#         },
#         "maxConcurrency": 1
#     }

#     try:
#         logger.info(f"Starting Indeed scrape for: {search_query} in {location if location else 'all locations'}")
        
#         run = client.actor("misceres/indeed-scraper").call(run_input=run_input)
        
#         if not run:
#             logger.error("Failed to start the actor run")
#             return

#         jobs_data = []
#         dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
#         logger.info(f"Retrieved {len(dataset_items)} items from the dataset")

#         for item in dataset_items:
#             try:
#                 # Enhanced title extraction
#                 title = (
#                     item.get('title') or 
#                     item.get('jobTitle') or 
#                     item.get('position') or 
#                     'Not specified'
#                 ).strip()

#                 # Enhanced company name extraction
#                 company = (
#                     item.get('company') or 
#                     item.get('companyName') or 
#                     item.get('employerName') or 
#                     'Not specified'
#                 ).strip()

#                 # Enhanced location extraction
#                 location = (
#                     item.get('location') or 
#                     item.get('jobLocation') or 
#                     item.get('place') or 
#                     'Not specified'
#                 ).strip()

#                 # Get and clean description
#                 description = item.get('description') or item.get('jobDescription', '')
#                 if description:
#                     description = ' '.join(description.split())
#                     if len(description) > 200:
#                         description = description[:200] + "..."
#                 else:
#                     description = "Not specified"

#                 # Enhanced posted date extraction
#                 posted_date = (
#                     item.get('date') or 
#                     item.get('postDate') or 
#                     item.get('postedAt') or 
#                     item.get('datePosted') or 
#                     'Not specified'
#                 )
#                 posted_date = clean_date(posted_date)

#                 # Create simplified job data dictionary
#                 job_data = {
#                     "JobTitle": title,
#                     "Company": company,
#                     "Location": location,
#                     "Summary": description,
#                     "PostedDate": posted_date
#                 }

#                 jobs_data.append(job_data)
#                 logger.info(f"Successfully scraped: {title} at {company}")
                
#             except Exception as e:
#                 logger.error(f"Error processing job item: {str(e)}")
#                 continue

#         if jobs_data:
#             # Create output directory
#             output_dir = "scraped_data"
#             os.makedirs(output_dir, exist_ok=True)

#             # Create timestamp for filenames
#             timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

#             # Save to Excel
#             excel_filename = f"{output_dir}/indeed_jobs_{timestamp}.xlsx"
#             df = pd.DataFrame(jobs_data)
#             df.to_excel(excel_filename, index=False, sheet_name='Jobs')

#             # Save simplified data to JSON
#             json_filename = f"{output_dir}/indeed_jobs_simplified_{timestamp}.json"
#             with open(json_filename, "w", encoding="utf-8") as f:
#                 json.dump(jobs_data, f, ensure_ascii=False, indent=4)

#             logger.info(f"\nSuccessfully scraped {len(jobs_data)} jobs")
#             logger.info(f"Data saved to {excel_filename} and {json_filename}")
            
#             return df

#         else:
#             logger.warning("No jobs were scraped successfully")
#             return None

#     except Exception as e:
#         logger.error(f"An error occurred during scraping: {str(e)}")
#         return None

# if __name__ == "__main__":
#     try:
#         results = scrape_indeed_jobs(
#             search_query="Python Developer",    
#             location="Mumbai, Maharashtra",
#             num_pages=3
#         )
        
#         if results is not None:
#             print("\nScraping completed successfully!")
#             print("\nSample of scraped jobs:")
#             print(results[['JobTitle', 'Company', 'Location', 'PostedDate']].head())
#     except Exception as e:
#         logger.error(f"Main execution error: {str(e)}")

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

def extract_job_title(item):
    """Enhanced job title extraction with better field handling"""
    # First try positionName as it's the most reliable
    if item.get('positionName'):
        return item['positionName'].strip()
    
    # Try to extract title from HTML content if available
    if item.get('descriptionHTML'):
        try:
            if '<h1' in item['descriptionHTML'] and 'Title:' in item['descriptionHTML']:
                import re
                title_match = re.search(r'<h1[^>]*>.*?Title:\s*([^<]+)', item['descriptionHTML'])
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

    # If no title found, log the issue
    logger.warning(f"Could not find title in item: {json.dumps(item, indent=2)}")
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
                # Enhanced data extraction
                job_data = {
                    "JobTitle": extract_job_title(item),
                    "Company": item.get('company', 'Not specified'),
                    "Location": item.get('location', 'Not specified'),
                    "Description": item.get('description', 'Not specified'),
                    "Salary": item.get('salary', 'Not specified'),
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

            # Create timestamp for filenames
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            # Save to Excel
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
    try:
        results = scrape_indeed_jobs(
            search_query="Python Developer",    
            location="Mumbai, Maharashtra",
            num_pages=3
        )
        
        if results is not None:
            print("\nScraping completed successfully!")
            print("\nSample of scraped jobs:")
            print(results[['JobTitle', 'Company', 'Location', 'PostedDate', 'JobType', 'Salary']].head())
    except Exception as e:
        logger.error(f"Main execution error: {str(e)}")