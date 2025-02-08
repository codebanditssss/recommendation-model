# import json
# import time
# import random
# import pandas as pd
# from datetime import datetime
# import traceback
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.common.exceptions import (
#     TimeoutException, 
#     NoSuchElementException, 
#     StaleElementReferenceException,
#     WebDriverException
# )
# from webdriver_manager.chrome import ChromeDriverManager

# def auto_solve_verification(driver, timeout=10):
#     """
#     Attempt to automatically solve verification challenges
    
#     :param driver: Selenium WebDriver instance
#     :param timeout: Maximum time to wait for verification elements
#     :return: Boolean indicating if verification was handled
#     """
#     # List of potential verification challenge selectors
#     verification_selectors = [
#         # Cloudflare challenges
#         "iframe[src*='challenges.cloudflare.com']",
#         "[data-testid='cf-turnstile-container']",
        
#         # hCaptcha challenges
#         ".h-captcha",
#         "iframe[src*='hcaptcha.com']",
        
#         # reCAPTCHA challenges
#         ".g-recaptcha",
#         "iframe[src*='recaptcha']",
        
#         # Generic human verification checkboxes
#         "input[type='checkbox'][name='human']",
#         "[aria-label='Verify you are human']",
#         ".verification-checkbox",
#         ".cloudflare-challenge"
#     ]

#     # Checkbox and verification button selectors
#     checkbox_selectors = [
#         "input[type='checkbox']",
#         "[type='checkbox']",
#         ".checkbox-verify",
#         "[aria-label='I am human']",
#         "[name='verify']",
#         ".ctp-checkbox-label",
#         "#cf-hcaptcha-container"
#     ]

#     try:
#         # Check for verification challenges
#         for selector in verification_selectors:
#             try:
#                 # Wait for verification element
#                 challenge = WebDriverWait(driver, timeout).until(
#                     EC.presence_of_element_located((By.CSS_SELECTOR, selector))
#                 )
                
#                 # If iframe, try to switch to it
#                 if challenge.tag_name == 'iframe':
#                     driver.switch_to.frame(challenge)
                
#                 # Try to find and click checkbox
#                 for checkbox_selector in checkbox_selectors:
#                     try:
#                         # Wait for checkbox
#                         checkbox = WebDriverWait(driver, 5).until(
#                             EC.element_to_be_clickable((By.CSS_SELECTOR, checkbox_selector))
#                         )
                        
#                         # Use different clicking methods
#                         try:
#                             # Method 1: Direct Selenium click
#                             checkbox.click()
#                         except Exception:
#                             try:
#                                 # Method 2: JavaScript click
#                                 driver.execute_script("arguments[0].click();", checkbox)
#                             except Exception:
#                                 try:
#                                     # Method 3: Move and click
#                                     ActionChains(driver).move_to_element(checkbox).click().perform()
#                                 except Exception:
#                                     # Method 4: Scroll and click
#                                     driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
#                                     time.sleep(0.5)
#                                     driver.execute_script("arguments[0].click();", checkbox)
                        
#                         # Random delay to mimic human behavior
#                         time.sleep(random.uniform(1, 3))
                        
#                         # Switch back to default content if we switched to iframe
#                         driver.switch_to.default_content()
                        
#                         print("Verification challenge solved automatically!")
#                         return True
                    
#                     except Exception as click_error:
#                         # Continue to next selector if this one fails
#                         continue
                
#                 # If no checkbox found, switch back to default content
#                 driver.switch_to.default_content()
            
#             except TimeoutException:
#                 # No challenge found with this selector, continue
#                 continue
        
#         # No verification challenges successfully handled
#         return False
    
#     except Exception as e:
#         print(f"Error in verification handling: {e}")
#         return False

# def integrated_verification_handler(func):
#     """
#     Decorator to add automatic verification handling to scraping functions
    
#     :param func: Function to wrap with verification handling
#     :return: Wrapped function
#     """
#     def wrapper(*args, **kwargs):
#         # Get the driver from the first argument or kwargs
#         driver = None
#         if args and hasattr(args[0], 'driver'):
#             driver = args[0].driver
#         elif 'driver' in kwargs:
#             driver = kwargs['driver']
        
#         if not driver:
#             raise ValueError("No WebDriver found to handle verification")
        
#         try:
#             # Attempt to solve verification multiple times
#             for _ in range(3):  # Try up to 3 times
#                 if auto_solve_verification(driver):
#                     break
#         except Exception as e:
#             print(f"Verification handling failed: {e}")
        
#         # Execute the original function
#         return func(*args, **kwargs)
    
#     return wrapper

# class IndeedScraper:
#     def __init__(self, search_query, location='', num_pages=3):
#         """
#         Initialize the Indeed Scraper
        
#         :param search_query: Job search query string
#         :param location: Job location
#         :param num_pages: Number of pages to scrape (default is 3)
#         """
#         self.search_query = search_query
#         self.location = location
#         self.num_pages = num_pages
#         self.jobs_data = []
#         self.driver = self.setup_driver()

#     def setup_driver(self):
#         """
#         Setup Chrome WebDriver with anti-detection and performance options
#         """
#         options = webdriver.ChromeOptions()
#         options.add_argument('--start-maximized')
#         options.add_argument('--disable-notifications')
#         options.add_argument('--log-level=3')  # Suppress console logs
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
#         options.add_experimental_option('useAutomationExtension', False)
        
#         # User agent rotation to reduce detection
#         user_agents = [
#             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#             "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
#         ]
#         options.add_argument(f'user-agent={random.choice(user_agents)}')

#         service = Service(ChromeDriverManager().install())
#         driver = webdriver.Chrome(service=service, options=options)
        
#         # Additional anti-detection script
#         driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
#             "source": """
#             Object.defineProperty(navigator, 'webdriver', {
#                 get: () => undefined
#             })
#             """
#         })
        
#         return driver

#     def random_delay(self, min_time=2, max_time=5):
#         """
#         Generate random delay to mimic human behavior
#         """
#         time.sleep(random.uniform(min_time, max_time))

#     def clean_text(self, text):
#         """
#         Clean and normalize text
#         """
#         if not text:
#             return "N/A"
        
#         # Remove extra whitespaces and newlines
#         cleaned = ' '.join(text.split())
#         return cleaned if cleaned else "N/A"

#     def get_company_name(self, job):
#         """
#         Extract company name with multiple selector fallbacks
#         """
#         selectors = [
#             ".companyName", 
#             "[data-testid='company-name']", 
#             ".company_location .companyName",
#             ".jobsearch-InlineCompanyRating"
#         ]
#         for selector in selectors:
#             try:
#                 element = job.find_element(By.CSS_SELECTOR, selector)
#                 if element and element.text.strip():
#                     return self.clean_text(element.text)
#             except Exception:
#                 continue
#         return "Not specified"

#     def get_location(self, job):
#         """
#         Extract job location with multiple selector fallbacks
#         """
#         selectors = [
#             ".companyLocation", 
#             "[data-testid='text-location']", 
#             ".resultContent .location"
#         ]
#         for selector in selectors:
#             try:
#                 element = job.find_element(By.CSS_SELECTOR, selector)
#                 if element and element.text.strip():
#                     return self.clean_text(element.text)
#             except Exception:
#                 continue
#         return "Not specified"

#     def get_salary(self, job):
#         """
#         Extract salary information with multiple approaches
#         """
#         try:
#             salary_selectors = [
#                 "div.salary-snippet-container",
#                 "div.metadata",
#                 ".jobsearch-SalaryCompensationInfo-container"
#             ]
            
#             for selector in salary_selectors:
#                 try:
#                     salary_element = job.find_element(By.CSS_SELECTOR, selector)
#                     if salary_element and salary_element.text.strip():
#                         return self.clean_text(salary_element.text)
#                 except Exception:
#                     continue
#         except Exception:
#             pass
#         return "Not specified"

#     def get_job_description(self):
#         """
#         Extract job description with multiple approaches and error handling
#         """
#         try:
#             # Allow page to load
#             self.random_delay(1, 2)

#             # Close any existing popup
#             popup_close_selectors = [
#                 "[aria-label='Close']",
#                 ".popover-close-button",
#                 "#jobsearch-ViewJobButtons-closeModal"
#             ]
            
#             for selector in popup_close_selectors:
#                 try:
#                     close_button = WebDriverWait(self.driver, 3).until(
#                         EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
#                     )
#                     close_button.click()
#                     self.random_delay(0.5, 1)
#                 except Exception:
#                     continue

#             # Description selectors
#             desc_selectors = [
#                 "div#jobDescriptionText", 
#                 "div[data-testid='jobDescriptionText']", 
#                 "div.jobsearch-JobComponent-description",
#                 "#jobDescriptionText"
#             ]
            
#             for selector in desc_selectors:
#                 try:
#                     description_element = WebDriverWait(self.driver, 5).until(
#                         EC.presence_of_element_located((By.CSS_SELECTOR, selector))
#                     )
#                     description = description_element.text.strip()
                    
#                     # Truncate long descriptions
#                     return (description[:500] + "...") if len(description) > 500 else description
#                 except Exception:
#                     continue
            
#             return "Description not available"
#         except Exception as e:
#             print(f"Error extracting description: {e}")
#             return "Description not available"

#     @integrated_verification_handler
#     def scrape_jobs(self):
#         """
#         Main scraping method with integrated verification handling
#         """
#         try:
#             # Navigate to Indeed
#             self.driver.get("https://in.indeed.com/")
#             self.random_delay()

#             # Find and interact with search box
#             search_box = WebDriverWait(self.driver, 10).until(
#                 EC.presence_of_element_located((By.NAME, "q"))
#             )
#             search_box.clear()
#             search_box.send_keys(self.search_query)

#             # Add location if specified
#             if self.location:
#                 try:
#                     location_box = self.driver.find_element(By.NAME, "l")
#                     location_box.clear()
#                     location_box.send_keys(self.location)
#                 except Exception as e:
#                     print(f"Could not enter location: {e}")

#             # Submit search
#             search_box.send_keys(Keys.RETURN)
#             self.random_delay()

#             current_date = datetime.now().strftime("%Y-%m-%d")

#             # Iterate through specified number of pages
#             for page in range(self.num_pages):
#                 print(f"\nProcessing page {page + 1}")

#                 # Wait for job cards
#                 try:
#                     job_cards = WebDriverWait(self.driver, 10).until(
#                         EC.presence_of_all_elements_located((By.CLASS_NAME, "job_seen_beacon"))
#                     )
#                 except TimeoutException:
#                     print("No job listings found on this page")
#                     break
                
#                 print(f"Found {len(job_cards)} jobs on page {page + 1}")

#                 # Process each job card
#                 for index, job in enumerate(job_cards, 1):
#                     try:
#                         # Find job title
#                         title_selectors = [
#                             "h2.jobTitle a", 
#                             ".jobTitle a", 
#                             "[data-jk] a"
#                         ]
#                         title_element = None
#                         for selector in title_selectors:
#                             try:
#                                 title_element = job.find_element(By.CSS_SELECTOR, selector)
#                                 break
#                             except Exception:
#                                 continue
                        
#                         if not title_element:
#                             print(f"Could not find title for job {index}")
#                             continue

#                         # Extract details
#                         title = self.clean_text(title_element.text)
#                         company = self.get_company_name(job)
#                         location = self.get_location(job)
#                         salary = self.get_salary(job)

#                         # Click to view job details
#                         try:
#                             # Scroll to job card
#                             self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job)
#                             self.random_delay(0.5, 1)
                            
#                             # Click job title with JavaScript
#                             self.driver.execute_script("arguments[0].click();", title_element)
#                             self.random_delay(1, 2)

#                             # Extract description
#                             description = self.get_job_description()

#                             # Store job data
#                             job_data = {
#                                 "JobTitle": title,
#                                 "Company": company,
#                                 "Location": location,
#                                 "ExtractDate": current_date,
#                                 "Summary": description,
#                                 "Salary": salary,
#                                 "JobUrl": self.driver.current_url
#                             }
                            
#                             self.jobs_data.append(job_data)
#                             print(f"Successfully scraped: {title}")

#                         except Exception as e:
#                             print(f"Error clicking job title: {e}")
#                             continue

#                     except Exception as e:
#                         print(f"Error processing job: {e}")
#                         continue

#                     # Random delay between jobs
#                     self.random_delay(1, 2)

#                 # Navigate to next page
#                 if page < self.num_pages - 1:
#                     try:
#                         next_button = WebDriverWait(self.driver, 10).until(
#                             EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Next"]'))
#                         )
#                         self.driver.execute_script("arguments[0].click();", next_button)
#                         print("Navigating to next page")
#                         self.random_delay(2, 4)
#                     except Exception:
#                         print("No more pages available")
#                         break

#         except Exception as e:
#             print(f"An error occurred during scraping: {e}")
        
#         finally:
#             # Save results before closing
#             self.save_results()
#             # Close the driver
#             self.driver.quit()

#         return self.jobs_data

#     def save_results(self, excel_filename='jobs_data.xlsx', json_filename='jobs.json'):
#         """
#         Save scraped job data to Excel and JSON files
        
#         :param excel_filename: Name of Excel output file
#         :param json_filename: Name of JSON output file
#         """
#         try:
#             if not self.jobs_data:
#                 print("No jobs data to save.")
#                 return

#             # Save to Excel
#             df = pd.DataFrame(self.jobs_data)
#             df.to_excel(excel_filename, index=False, sheet_name='Jobs')

#             # Save to JSON
#             json_data = [
#                 {
#                     "title": job["JobTitle"], 
#                     "company": job["Company"], 
#                     "location": job["Location"],
#                     "salary": job["Salary"]
#                 } for job in self.jobs_data
#             ]
#             with open(json_filename, "w", encoding="utf-8") as f:
#                 json.dump(json_data, f, ensure_ascii=False, indent=4)

#             print(f"\nSuccessfully saved {len(self.jobs_data)} jobs")
#             print(f"Data saved to {excel_filename} and {json_filename}")
        
#         except Exception as e:
#             print(f"Error saving results: {e}")

# def main():
#     """
#     Main function to run the Indeed job scraper
#     """
#     try:
#         # Configure scraper
#         search_query = input("Enter job search query (e.g., 'Software Engineer'): ").strip() or "Software Engineer"
#         location = input("Enter location (press Enter for default): ").strip() or "India"
        
#         # Get number of pages to scrape
#         while True:
#             try:
#                 num_pages = int(input("Enter number of pages to scrape (1-10): ").strip() or 3)
#                 if 1 <= num_pages <= 10:
#                     break
#                 else:
#                     print("Please enter a number between 1 and 10.")
#             except ValueError:
#                 print("Invalid input. Please enter a number.")

#         # Create scraper instance
#         scraper = IndeedScraper(search_query, location, num_pages)
        
#         # Start timing
#         start_time = time.time()
        
#         # Scrape jobs
#         scraper.scrape_jobs()
        
#         # Calculate and display scraping time
#         end_time = time.time()
#         print(f"\nScraping completed in {end_time - start_time:.2f} seconds")

#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#         traceback.print_exc()
    
# if __name__ == "__main__":
#     main()

import json
import time
import random
import pandas as pd
import requests
from datetime import datetime
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import *
from webdriver_manager.chrome import ChromeDriverManager

def check_site_accessibility(url, timeout=10):
    """
    Check if the site is accessible before starting the scraper
    """
    try:
        response = requests.head(url, timeout=timeout)
        return response.status_code == 200
    except requests.RequestException:
        return False

def setup_driver_with_proxy(proxy=None):
    """
    Setup Chrome WebDriver with optional proxy support
    """
    options = webdriver.ChromeOptions()
    
    # Basic anti-detection settings
    options.add_argument('--start-maximized')
    options.add_argument('--disable-notifications')
    options.add_argument('--log-level=3')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Add proxy if specified
    if proxy:
        options.add_argument(f'--proxy-server={proxy}')
    
    # Additional anti-bot measures
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    
    # Rotate user agents
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15"
    ]
    options.add_argument(f'user-agent={random.choice(user_agents)}')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Additional anti-detection scripts
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        """
    })
    
    return driver

class IndeedScraper:
    def __init__(self, search_query, location='', num_pages=3, proxy=None):
        """
        Initialize the Indeed Scraper with proxy support
        """
        self.search_query = search_query
        self.location = location
        self.num_pages = num_pages
        self.proxy = proxy
        self.jobs_data = []
        self.base_url = "https://in.indeed.com"
        
        # Check site accessibility before starting
        if not check_site_accessibility(self.base_url):
            print(f"Warning: {self.base_url} seems to be inaccessible. Trying with proxy if provided...")
        
        self.driver = setup_driver_with_proxy(self.proxy)

    def random_delay(self, min_time=2, max_time=5):
        """
        Generate random delay to mimic human behavior
        """
        time.sleep(random.uniform(min_time, max_time))

    def navigate_with_retry(self, url, max_retries=3):
        """
        Attempt to navigate to URL with retries
        """
        for attempt in range(max_retries):
            try:
                self.driver.get(url)
                WebDriverWait(self.driver, 10).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                return True
            except Exception as e:
                print(f"Navigation attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    print("All navigation attempts failed")
                    return False
                time.sleep(random.uniform(2, 5))
        return False

    def clean_text(self, text):
        """
        Clean and normalize text
        """
        if not text:
            return "N/A"
        return ' '.join(text.split()).strip() or "N/A"

    def get_company_name(self, job):
        """
        Extract company name with multiple selector fallbacks
        """
        selectors = [
            ".companyName", 
            "[data-testid='company-name']", 
            ".company_location .companyName",
            ".jobsearch-InlineCompanyRating"
        ]
        for selector in selectors:
            try:
                element = job.find_element(By.CSS_SELECTOR, selector)
                if element and element.text.strip():
                    return self.clean_text(element.text)
            except Exception:
                continue
        return "Not specified"

    def get_location(self, job):
        """
        Extract job location with multiple selector fallbacks
        """
        selectors = [
            ".companyLocation", 
            "[data-testid='text-location']", 
            ".resultContent .location"
        ]
        for selector in selectors:
            try:
                element = job.find_element(By.CSS_SELECTOR, selector)
                if element and element.text.strip():
                    return self.clean_text(element.text)
            except Exception:
                continue
        return "Not specified"

    def get_salary(self, job):
        """
        Extract salary information with multiple approaches
        """
        salary_selectors = [
            "div.salary-snippet-container",
            "div.metadata",
            ".jobsearch-SalaryCompensationInfo-container"
        ]
        
        for selector in salary_selectors:
            try:
                salary_element = job.find_element(By.CSS_SELECTOR, selector)
                if salary_element and salary_element.text.strip():
                    return self.clean_text(salary_element.text)
            except Exception:
                continue
        return "Not specified"

    def scrape_jobs(self):
        """
        Enhanced main scraping method with better error handling
        """
        try:
            # Initial navigation with retry
            if not self.navigate_with_retry(self.base_url):
                print("Could not access Indeed. Please check your internet connection or try using a proxy.")
                return []

            print(f"Successfully navigated to {self.base_url}")
            self.random_delay()

            # Enhanced search box interaction
            try:
                search_box = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "q"))
                )
                search_box.clear()
                # Type like a human
                for char in self.search_query:
                    search_box.send_keys(char)
                    time.sleep(random.uniform(0.1, 0.3))

                if self.location:
                    try:
                        location_box = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.NAME, "l"))
                        )
                        location_box.clear()
                        for char in self.location:
                            location_box.send_keys(char)
                            time.sleep(random.uniform(0.1, 0.3))
                    except Exception as e:
                        print(f"Location input error: {e}")

                # Submit search with delay
                time.sleep(random.uniform(0.5, 1.5))
                search_box.send_keys(Keys.RETURN)
                print("Search submitted successfully")

                # Process search results
                current_date = datetime.now().strftime("%Y-%m-%d")
                
                for page in range(self.num_pages):
                    print(f"\nProcessing page {page + 1}")
                    
                    # Wait for job cards
                    try:
                        job_cards = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_all_elements_located((By.CLASS_NAME, "job_seen_beacon"))
                        )
                        print(f"Found {len(job_cards)} jobs on page {page + 1}")

                        # Process each job
                        for job in job_cards:
                            try:
                                # Extract basic job info
                                title_element = job.find_element(By.CSS_SELECTOR, "h2.jobTitle a")
                                title = self.clean_text(title_element.text)
                                company = self.get_company_name(job)
                                location = self.get_location(job)
                                salary = self.get_salary(job)

                                job_data = {
                                    "JobTitle": title,
                                    "Company": company,
                                    "Location": location,
                                    "Salary": salary,
                                    "ExtractDate": current_date,
                                }
                                
                                self.jobs_data.append(job_data)
                                print(f"Successfully scraped: {title} at {company}")
                                
                                self.random_delay(1, 2)
                                
                            except Exception as e:
                                print(f"Error processing job: {e}")
                                continue

                        # Navigate to next page if not on last page
                        if page < self.num_pages - 1:
                            try:
                                # Try multiple selectors for the next button
                                next_button_selectors = [
                                    '[aria-label="Next"]',
                                    'a[data-testid="pagination-page-next"]',
                                    '.np[aria-label="Next"]',
                                    '.pagination-list li:last-child a',
                                    'a[data-testid="pagination-nav-next"]'
                                ]
                                
                                next_button = None
                                for selector in next_button_selectors:
                                    try:
                                        next_button = WebDriverWait(self.driver, 5).until(
                                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                                        )
                                        break
                                    except:
                                        continue
                                
                                if next_button:
                                    # Scroll into view
                                    self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                                    time.sleep(1)
                                    
                                    # Try multiple click methods
                                    try:
                                        next_button.click()
                                    except:
                                        try:
                                            self.driver.execute_script("arguments[0].click();", next_button)
                                        except:
                                            # If clicking fails, try constructing URL for next page
                                            current_url = self.driver.current_url
                                            if 'start=' in current_url:
                                                next_start = int(current_url.split('start=')[1].split('&')[0]) + 10
                                                next_url = current_url.replace(f'start={next_start-10}', f'start={next_start}')
                                            else:
                                                next_url = current_url + ('&' if '?' in current_url else '?') + 'start=10'
                                            self.driver.get(next_url)
                                    
                                    # Wait for page load
                                    WebDriverWait(self.driver, 10).until(
                                        lambda driver: driver.execute_script("return document.readyState") == "complete"
                                    )
                                    self.random_delay(2, 4)
                                else:
                                    print("Next button not found - end of available pages")
                            except Exception as e:
                                print(f"Could not navigate to next page: {e}")
                                break
                                
                    except Exception as e:
                        print(f"Error processing page {page + 1}: {e}")
                        break

            except Exception as e:
                print(f"Error during search: {e}")
                return []

        except Exception as e:
            print(f"Critical error during scraping: {e}")
            traceback.print_exc()
        finally:
            if self.jobs_data:
                self.save_results()
            self.driver.quit()
            return self.jobs_data

    def save_results(self, excel_filename='jobs_data.xlsx', json_filename='jobs.json'):
        """
        Save scraped job data to Excel and JSON files
        """
        try:
            if not self.jobs_data:
                print("No jobs data to save.")
                return

            # Save to Excel
            df = pd.DataFrame(self.jobs_data)
            df.to_excel(excel_filename, index=False, sheet_name='Jobs')

            # Save to JSON
            with open(json_filename, "w", encoding="utf-8") as f:
                json.dump(self.jobs_data, f, ensure_ascii=False, indent=4)

            print(f"\nSuccessfully saved {len(self.jobs_data)} jobs")
            print(f"Data saved to {excel_filename} and {json_filename}")
        
        except Exception as e:
            print(f"Error saving results: {e}")

def main():
    """
    Enhanced main function with proxy support
    """
    try:
        search_query = input("Enter job search query: ").strip() or "Software Engineer"
        location = input("Enter location (press Enter for default): ").strip() or "India"
        num_pages = int(input("Enter number of pages to scrape (1-10): ").strip() or 3)
        
        # Optional proxy input
        use_proxy = input("Do you want to use a proxy? (y/n): ").lower().strip() == 'y'
        proxy = None
        if use_proxy:
            proxy = input("Enter proxy address (e.g., http://proxy:port): ").strip()
        
        start_time = time.time()
        scraper = IndeedScraper(search_query, location, num_pages, proxy)
        results = scraper.scrape_jobs()
        
        print(f"\nScraping completed in {time.time() - start_time:.2f} seconds")
        return results

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()