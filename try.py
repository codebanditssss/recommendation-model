# import time
# import random
# import warnings
# import os
# import csv
# import re
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# # Suppress warnings
# warnings.filterwarnings("ignore", category=ResourceWarning)

# class IndeedScraper:
#     def __init__(self, search_query, num_pages=1):
#         """
#         Initialize the Indeed Scraper
        
#         :param search_query: Job search query string
#         :param num_pages: Number of pages to scrape (default is 1)
#         """
#         self.search_query = search_query
#         self.num_pages = num_pages
#         self.jobs_data = []
#         self.driver = None

#     def setup_driver(self):
#         """
#         Sets up and returns a Chrome driver with optimized settings
        
#         :return: Configured Selenium WebDriver
#         """
#         # Chrome options for better stability and performance
#         chrome_options = Options()
#         chrome_options.add_argument("--no-sandbox")
#         chrome_options.add_argument("--disable-dev-shm-usage")
#         chrome_options.add_argument("--start-maximized")
#         chrome_options.add_argument("--disable-extensions")
#         chrome_options.add_argument("--disable-gpu")
#         chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#         chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         chrome_options.add_experimental_option('useAutomationExtension', False)
        
#         # Optional: Run in headless mode
#         # chrome_options.add_argument("--headless")

#         # Use WebDriver Manager to handle driver installation
#         service = Service(ChromeDriverManager().install())
        
#         # Initialize the WebDriver
#         self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
#         # Additional anti-detection measures
#         self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
#             "source": """
#             Object.defineProperty(navigator, 'webdriver', {
#                 get: () => undefined
#             })
#             """
#         })
        
#         return self.driver

#     def random_delay(self, min_time=2, max_time=5):
#         """
#         Generate a random delay to mimic human browsing behavior
        
#         :param min_time: Minimum delay time
#         :param max_time: Maximum delay time
#         """
#         time.sleep(random.uniform(min_time, max_time))

#     def clean_text(self, text):
#         """
#         Clean and normalize text
        
#         :param text: Input text to clean
#         :return: Cleaned text
#         """
#         if not text:
#             return "N/A"
        
#         # Remove extra whitespaces and newlines
#         cleaned = re.sub(r'\s+', ' ', text).strip()
#         return cleaned

#     def extract_job_details(self, job_card):
#         """
#         Extract job details from a single job card
        
#         :param job_card: Selenium WebElement representing a job card
#         :return: Dictionary of job details
#         """
#         def safe_find_element(element, by, selector):
#             """
#             Safely find an element with error handling
            
#             :param element: Parent WebElement
#             :param by: Selenium By locator
#             :param selector: CSS selector or XPath
#             :return: Element text or 'N/A'
#             """
#             try:
#                 return self.clean_text(element.find_element(by, selector).text)
#             except (NoSuchElementException, StaleElementReferenceException):
#                 return "N/A"

#         try:
#             # More robust element finding with multiple selectors
#             job_title_selectors = [
#                 "h2 a",
#                 ".jobTitle > a",
#                 "div[class*='title'] a"
#             ]
            
#             company_selectors = [
#                 ".companyName",
#                 "span[class*='company']",
#                 "div[class*='company']"
#             ]
            
#             location_selectors = [
#                 ".companyLocation",
#                 "div[class*='location']",
#                 "span[class*='location']"
#             ]

#             # Try multiple selectors for each detail
#             job_title = "N/A"
#             for selector in job_title_selectors:
#                 try:
#                     job_title = self.clean_text(job_card.find_element(By.CSS_SELECTOR, selector).text)
#                     if job_title and job_title != "N/A":
#                         break
#                 except Exception:
#                     continue

#             company = "N/A"
#             location = "N/A"
#             additional_info = "N/A"

#             # Try multiple selectors for company and location
#             text_content = job_card.text
#             lines = [line.strip() for line in text_content.split('\n') if line.strip()]

#             # Attempt to separate company, location, and additional info
#             if lines:
#                 # First line is usually the job title (which we've already extracted)
#                 # Look for company in subsequent lines
#                 for line in lines[1:]:
#                     # Check if line contains a location indicator
#                     if any(loc in line.lower() for loc in ['remote', 'pune', 'delhi', 'mumbai', 'bangalore', 'hyderabad', 'chennai', 'noida', 'gurgaon']):
#                         location = line
#                         # Find company before the location
#                         company_candidates = lines[1:lines.index(line)]
#                         if company_candidates:
#                             company = company_candidates[0]
#                         break
#                     elif not company:
#                         # If no location found yet, assume first line is company
#                         company = line

#             # Clean up company and location
#             company = self.clean_text(company)
#             location = self.clean_text(location)

#             return {
#                 "JobTitle": job_title,
#                 "Company": company,
#                 "Location": location,
#             }
#         except Exception as e:
#             print(f"Error extracting job details: {e}")
#             return {
#                 "JobTitle": "N/A",
#                 "Company": "N/A",
#                 "Location": "N/A",
#             }

#     def scrape_jobs(self):
#         """
#         Main method to scrape job listings from Indeed
        
#         :return: List of scraped job details
#         """
#         # Setup the WebDriver
#         driver = self.setup_driver()

#         try:
#             # Navigate to Indeed
#             driver.get("https://www.indeed.com/")
#             self.random_delay()

#             # Find and interact with the search bar
#             search_box = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.NAME, "q"))
#             )
#             search_box.clear()
#             search_box.send_keys(self.search_query)
#             search_box.send_keys(Keys.RETURN)
#             self.random_delay()

#             # Iterate through specified number of pages
#             for page in range(self.num_pages):
#                 print(f"\nScraping Page {page + 1}")

#                 try:
#                     # Wait for job cards to load
#                     job_cards = WebDriverWait(driver, 10).until(
#                         EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".job_seen_beacon, [data-jk]"))
#                     )
#                 except TimeoutException:
#                     print(f"No job cards found on page {page + 1}")
#                     break

#                 # Extract details from each job card
#                 for job_card in job_cards:
#                     try:
#                         job_details = self.extract_job_details(job_card)
                        
#                         # Only add if job title is not empty or 'N/A'
#                         if job_details['JobTitle'] and job_details['JobTitle'] != "N/A":
#                             self.jobs_data.append(job_details)
#                             print(f"Scraped: {job_details['JobTitle']} at {job_details['Company']}")
#                     except Exception as e:
#                         print(f"Error processing job card: {e}")

#                 self.random_delay(2, 4)

#                 # Navigate to next page
#                 try:
#                     next_button = driver.find_element(By.CSS_SELECTOR, '[aria-label="Next"]')
#                     next_button.click()
#                     self.random_delay(2, 4)
#                 except NoSuchElementException:
#                     print("No more pages to scrape")
#                     break

#         except Exception as e:
#             print(f"An error occurred during scraping: {e}")

#         finally:
#             # Ensure driver is closed
#             self.quit_driver()

#         return self.jobs_data

#     def quit_driver(self):
#         """
#         Safely close the WebDriver and clean up resources
#         """
#         try:
#             if self.driver:
#                 # Close the browser
#                 self.driver.quit()
                
#                 # Additional cleanup for Chrome processes (Windows-specific)
#                 os.system("taskkill /F /IM chrome.exe /T")
#         except Exception as e:
#             print(f"Error during driver cleanup: {e}")
#         finally:
#             # Ensure driver is set to None
#             self.driver = None

#     def save_to_csv(self, filename='indeed_jobs.csv'):
#         """
#         Save scraped job data to a CSV file
        
#         :param filename: Name of the output CSV file
#         """
#         try:
#             with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
#                 fieldnames = ['JobTitle', 'Company', 'Location']
#                 writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
#                 writer.writeheader()
#                 for job in self.jobs_data:
#                     writer.writerow(job)
            
#             print(f"\nJob data saved to {filename}")
#         except Exception as e:
#             print(f"Error saving to CSV: {e}")

# def main():
#     """
#     Main function to run the Indeed job scraper
#     """
#     try:
#         # Configure scraper
#         search_query = "Software Engineer"
#         num_pages = 3  # Number of pages to scrape

#         # Create scraper instance
#         scraper = IndeedScraper(search_query, num_pages)
        
#         # Scrape jobs
#         job_results = scraper.scrape_jobs()

#         # Print results
#         print("\nScraped Job Data:")
#         for job in job_results:
#             print(job)

#         # Save to CSV
#         scraper.save_to_csv()

#     except Exception as e:
#         print(f"An error occurred: {e}")
    
# if __name__ == "__main__":
#     main()

import time
import random
import warnings
import os
import csv
import re
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, WebDriverException

# Suppress warnings
warnings.filterwarnings("ignore", category=ResourceWarning)

class IndeedScraper:
    def __init__(self, search_query, num_pages=1):
        """
        Initialize the Indeed Scraper
        
        :param search_query: Job search query string
        :param num_pages: Number of pages to scrape (default is 1)
        """
        self.search_query = search_query
        self.num_pages = num_pages
        self.jobs_data = []
        self.driver = None

    def setup_driver(self):
        """
        Sets up and returns a Chrome driver with optimized settings
        
        :return: Configured Selenium WebDriver
        """
        # Chrome options for better stability and performance
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Optional: Run in headless mode (uncomment if needed)
        # chrome_options.add_argument("--headless")

        try:
            # Use WebDriver Manager to handle driver installation
            service = Service(ChromeDriverManager().install())
            
            # Initialize the WebDriver
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Additional anti-detection measures
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
                """
            })
            
            return driver
        except Exception as e:
            print(f"Error setting up WebDriver: {e}")
            sys.exit(1)

    def random_delay(self, min_time=2, max_time=5):
        """
        Generate a random delay to mimic human browsing behavior
        
        :param min_time: Minimum delay time
        :param max_time: Maximum delay time
        """
        time.sleep(random.uniform(min_time, max_time))

    def clean_text(self, text):
        """
        Clean and normalize text
        
        :param text: Input text to clean
        :return: Cleaned text
        """
        if not text:
            return "N/A"
        
        # Remove extra whitespaces and newlines
        cleaned = re.sub(r'\s+', ' ', text).strip()
        return cleaned if cleaned else "N/A"

    def extract_job_details(self, job_card):
        """
        Extract job details from a single job card
        
        :param job_card: Selenium WebElement representing a job card
        :return: Dictionary of job details
        """
        try:
            # Extract Job Title
            job_title_selectors = [
                "h2 a",
                ".jobTitle > a",
                "div[class*='title'] a"
            ]
            job_title = "N/A"
            for selector in job_title_selectors:
                try:
                    job_title = self.clean_text(job_card.find_element(By.CSS_SELECTOR, selector).text)
                    if job_title and job_title != "N/A":
                        break
                except Exception:
                    continue

            # Extract full text content
            full_text = job_card.text
            lines = [line.strip() for line in full_text.split('\n') if line.strip()]

            # Extract Company
            company = "N/A"
            # Company might be the first non-title line
            if len(lines) > 1:
                company = self.clean_text(lines[1])

            # Extract Location
            location = "N/A"
            # Look for location in remaining lines
            location_keywords = ['remote', 'hybrid', 'onsite'] + [
                'pune', 'mumbai', 'bangalore', 'bengaluru', 'hyderabad', 
                'chennai', 'delhi', 'gurgaon', 'noida', 'mumbai', 'kolkata'
            ]
            
            for line in lines[2:]:
                if any(keyword in line.lower() for keyword in location_keywords):
                    location = self.clean_text(line)
                    break

            # Extract Job Description
            job_description = "N/A"
            try:
                # Click on job to open detailed view
                job_card.click()
                self.random_delay(1, 2)

                # Wait for description to load
                desc_selectors = [
                    "#jobDescriptionText",
                    ".jobsearch-JobComponent-description",
                    "[id*='jobDescriptionText']"
                ]
                
                for selector in desc_selectors:
                    try:
                        desc_element = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        job_description = self.clean_text(desc_element.text)
                        if job_description and job_description != "N/A":
                            break
                    except Exception:
                        continue
            except Exception as e:
                print(f"Error extracting job description: {e}")

            return {
                "JobTitle": job_title,
                "Company": company,
                "Location": location,
                "JobDescription": job_description
            }
        except Exception as e:
            print(f"Error extracting job details: {e}")
            return {
                "JobTitle": "N/A",
                "Company": "N/A",
                "Location": "N/A",
                "JobDescription": "N/A"
            }

    def scrape_jobs(self):
        """
        Main method to scrape job listings from Indeed
        
        :return: List of scraped job details
        """
        # Setup the WebDriver
        try:
            driver = self.setup_driver()
            self.driver = driver
        except Exception as e:
            print(f"Failed to setup WebDriver: {e}")
            return []

        try:
            # Navigate to Indeed
            driver.get("https://www.indeed.com/")
            self.random_delay()

            # Find and interact with the search bar
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            search_box.clear()
            search_box.send_keys(self.search_query)
            search_box.send_keys(Keys.RETURN)
            self.random_delay()

            # Iterate through specified number of pages
            for page in range(self.num_pages):
                try:
                    # Wait for job cards to load
                    job_cards = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".job_seen_beacon, [data-jk]"))
                    )
                except TimeoutException:
                    print(f"No job cards found on page {page + 1}")
                    break

                # Extract details from each job card
                for job_card in job_cards:
                    try:
                        job_details = self.extract_job_details(job_card)
                        
                        # Only add if job title is not empty or 'N/A'
                        if job_details['JobTitle'] and job_details['JobTitle'] != "N/A":
                            self.jobs_data.append(job_details)
                    except Exception as e:
                        print(f"Error processing job card: {e}")

                self.random_delay(2, 4)

                # Navigate to next page
                try:
                    next_button = driver.find_element(By.CSS_SELECTOR, '[aria-label="Next"]')
                    next_button.click()
                    self.random_delay(2, 4)
                except NoSuchElementException:
                    break

        except WebDriverException as e:
            print(f"WebDriver error: {e}")
        except Exception as e:
            print(f"An error occurred during scraping: {e}")

        finally:
            # Ensure driver is closed
            self.quit_driver()

        return self.jobs_data

    def quit_driver(self):
        """
        Safely close the WebDriver and clean up resources
        """
        try:
            if self.driver:
                # Close the browser
                self.driver.quit()
                
                # Additional cleanup for Chrome processes (Windows-specific)
                os.system("taskkill /F /IM chrome.exe /T")
        except Exception as e:
            print(f"Error during driver cleanup: {e}")
        finally:
            # Ensure driver is set to None
            self.driver = None

    def save_to_csv(self, filename='indeed_jobs.csv'):
        """
        Save scraped job data to a CSV file
        
        :param filename: Name of the output CSV file
        """
        try:
            # Ensure the file is writable
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['JobTitle', 'Company', 'Location', 'JobDescription']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for job in self.jobs_data:
                    writer.writerow(job)
            
            print(f"Successfully saved {len(self.jobs_data)} jobs to {filename}")
        except PermissionError:
            print(f"Permission denied. Please close any applications using {filename} and try again.")
        except Exception as e:
            print(f"Error saving to CSV: {e}")

def main():
    """
    Main function to run the Indeed job scraper
    """
    try:
        # Configure scraper
        search_query = "Software Engineer"
        num_pages = 3  # Number of pages to scrape

        # Create scraper instance
        scraper = IndeedScraper(search_query, num_pages)
        
        # Scrape jobs
        scraper.scrape_jobs()

        # Save to CSV
        scraper.save_to_csv()

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
if __name__ == "__main__":
    main()