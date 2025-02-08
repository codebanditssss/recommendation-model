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
        Extract salary information with multiple selector fallbacks
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

    def get_job_description(self, job):
        """
        Extract short job description with updated selector fallbacks
        """
        description_selectors = [
            ".job-snippet ul li",  # For bullet points
            ".job-snippet",  # Standard snippet
            "[data-testid='job-snippet']",  # Data attribute
            ".job-snippet-container",  # Container
            ".jobCardShelfContainer div",  # General container
            ".job-desc",  # Generic description
            ".jobDescriptionText"  # Full description
        ]
        
        for selector in description_selectors:
            try:
                # Try to find multiple elements first (for bullet points)
                desc_elements = job.find_elements(By.CSS_SELECTOR, selector)
                if desc_elements:
                    # Combine multiple elements if found
                    description = " ".join([elem.text.strip() for elem in desc_elements if elem.text.strip()])
                    if description:
                        description = self.clean_text(description)
                        if len(description) > 200:
                            description = description[:197] + "..."
                        return description
                
                # If no elements found, try single element
                desc_element = job.find_element(By.CSS_SELECTOR, selector)
                if desc_element and desc_element.text.strip():
                    description = self.clean_text(desc_element.text)
                    if len(description) > 200:
                        description = description[:197] + "..."
                    return description
            except Exception:
                continue
        return "Description not available"

    def scrape_jobs(self):
        """
        Enhanced main scraping method with job description extraction
        """
        try:
            if not self.navigate_with_retry(self.base_url):
                print("Could not access Indeed. Please check your internet connection or try using a proxy.")
                return []

            print(f"Successfully navigated to {self.base_url}")
            self.random_delay()

            try:
                search_box = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "q"))
                )
                search_box.clear()
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

                time.sleep(random.uniform(0.5, 1.5))
                search_box.send_keys(Keys.RETURN)
                print("Search submitted successfully")

                current_date = datetime.now().strftime("%Y-%m-%d")
                
                for page in range(self.num_pages):
                    print(f"\nProcessing page {page + 1}")
                    
                    try:
                        job_cards = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_all_elements_located((By.CLASS_NAME, "job_seen_beacon"))
                        )
                        print(f"Found {len(job_cards)} jobs on page {page + 1}")

                        for job in job_cards:
                            try:
                                title_element = job.find_element(By.CSS_SELECTOR, "h2.jobTitle a")
                                title = self.clean_text(title_element.text)
                                company = self.get_company_name(job)
                                location = self.get_location(job)
                                salary = self.get_salary(job)
                                description = self.get_job_description(job)

                                job_data = {
                                    "JobTitle": title,
                                    "Company": company,
                                    "Location": location,
                                    "Salary": salary,
                                    "Description": description,
                                    "ExtractDate": current_date,
                                }
                                
                                self.jobs_data.append(job_data)
                                print(f"Successfully scraped: {title} at {company}")
                                
                                self.random_delay(1, 2)
                                
                            except Exception as e:
                                print(f"Error processing job: {e}")
                                continue

                        if page < self.num_pages - 1:
                            try:
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
                                    self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                                    time.sleep(1)
                                    
                                    try:
                                        next_button.click()
                                    except:
                                        try:
                                            self.driver.execute_script("arguments[0].click();", next_button)
                                        except:
                                            current_url = self.driver.current_url
                                            if 'start=' in current_url:
                                                next_start = int(current_url.split('start=')[1].split('&')[0]) + 10
                                                next_url = current_url.replace(f'start={next_start-10}', f'start={next_start}')
                                            else:
                                                next_url = current_url + ('&' if '?' in current_url else '?') + 'start=10'
                                            self.driver.get(next_url)
                                    
                                    WebDriverWait(self.driver, 10).until(
                                        lambda driver: driver.execute_script("return document.readyState") == "complete"
                                    )
                                    self.random_delay(2, 4)
                                else:
                                    print("Next button not found - end of available pages")
                                    break
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
    Main function with proxy support
    """
    try:
        search_query = input("Enter job search query: ").strip() or "Software Engineer"
        location = input("Enter location (press Enter for default): ").strip() or "India"
        num_pages = int(input("Enter number of pages to scrape (1-10): ").strip() or 3)
        
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