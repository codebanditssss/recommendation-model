import time
import random
import warnings
import os
import csv
import re
import sys
import traceback
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
warnings.filterwarnings("ignore", category=DeprecationWarning)

class IndeedScraper:
    def __init__(self, search_query, location='', num_pages=3):
        """
        Initialize the Indeed Scraper
        
        :param search_query: Job search query string
        :param location: Job location
        :param num_pages: Number of pages to scrape (default is 3)
        """
        self.search_query = search_query
        self.location = location
        self.num_pages = num_pages
        self.jobs_data = []
        self.driver = None

    def setup_driver(self):
        """
        Sets up and returns a Chrome driver with anti-detection measures
        
        :return: Configured Selenium WebDriver
        """
        try:
            # Chrome options for stealth and performance
            options = Options()
            
            # Anti-detection arguments
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # User agent spoofing
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
            
            # Optional: Run in headless mode (uncomment if needed)
            # options.add_argument("--headless")

            # Initialize Chrome driver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            # Additional stealth measures
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
            traceback.print_exc()
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
        cleaned = re.sub(r'\s+', ' ', str(text)).strip()
        return cleaned if cleaned else "N/A"

    def extract_job_details(self, job_card):
        """
        Comprehensive method to extract job details with multiple fallback strategies
        
        :param job_card: WebElement representing the job card
        :return: Dictionary of job details
        """
        # Detailed job detail extraction with multiple selectors
        job_detail_selectors = {
            'title': [
                ".jobTitle > a",
                "h2 a",
                "[data-jk] a",
                ".title a"
            ],
            'company': [
                ".companyName",
                "[data-company-name]",
                ".company",
                ".companyInfo"
            ],
            'location': [
                ".companyLocation",
                ".location",
                "[data-location]"
            ]
        }

        job_details = {
            'JobTitle': 'N/A',
            'Company': 'N/A',
            'Location': 'N/A',
            'JobDescription': 'N/A'
        }

        # Try multiple selectors for each detail
        for detail_type, selectors in job_detail_selectors.items():
            for selector in selectors:
                try:
                    element = job_card.find_element(By.CSS_SELECTOR, selector)
                    cleaned_text = self.clean_text(element.text)
                    if cleaned_text and cleaned_text != 'N/A':
                        job_details[detail_type.capitalize()] = cleaned_text
                        break
                except Exception:
                    continue

        # Extract description (requires opening job details)
        try:
            # Click on job to open detailed view
            job_card.click()
            self.random_delay(1, 2)

            # Description selectors
            desc_selectors = [
                "#jobDescriptionText",
                ".jobsearch-JobComponent-description",
                "[id*='jobDescriptionText']",
                ".job-description"
            ]
            
            for selector in desc_selectors:
                try:
                    desc_element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    job_description = self.clean_text(desc_element.text)
                    if job_description and job_description != "N/A":
                        job_details['JobDescription'] = job_description
                        break
                except Exception:
                    continue

        except Exception as e:
            print(f"Error extracting job description: {e}")

        return job_details

    def scrape_jobs(self):
        """
        Main method to scrape job listings from Indeed
        
        :return: List of scraped job details
        """
        # Setup the WebDriver
        try:
            self.driver = self.setup_driver()
        except Exception as e:
            print(f"Failed to setup WebDriver: {e}")
            return []

        try:
            # Navigate to Indeed
            self.driver.get("https://www.indeed.com/")
            self.random_delay()

            # Find and interact with the search bar
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            search_box.clear()
            search_box.send_keys(self.search_query)

            # Add location if specified
            if self.location:
                try:
                    location_box = self.driver.find_element(By.NAME, "l")
                    location_box.clear()
                    location_box.send_keys(self.location)
                except Exception as e:
                    print(f"Could not enter location: {e}")

            # Submit search
            search_box.send_keys(Keys.RETURN)
            self.random_delay()

            # Iterate through specified number of pages
            for page in range(self.num_pages):
                print(f"\nScraping Page {page + 1}")

                try:
                    # Wait for job cards to load
                    job_cards = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".job_seen_beacon, [data-jk]"))
                    )
                except TimeoutException:
                    print(f"No job cards found on page {page + 1}")
                    break

                # Extract details from each job card
                for job_card in job_cards:
                    try:
                        # Use comprehensive extraction method
                        job_details = self.extract_job_details(job_card)
                        
                        # Only add if job title is meaningful
                        if job_details['JobTitle'] and job_details['JobTitle'] != 'N/A':
                            self.jobs_data.append(job_details)
                            print(f"Scraped: {job_details['JobTitle']} at {job_details['Company']}")
                    except Exception as e:
                        print(f"Error processing job card: {e}")

                self.random_delay(2, 4)

                # Navigate to next page
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, '[aria-label="Next"]')
                    next_button.click()
                    self.random_delay(2, 4)
                except NoSuchElementException:
                    print("No more pages to scrape")
                    break

        except Exception as e:
            print(f"An error occurred during scraping: {e}")
            traceback.print_exc()

        finally:
            # Ensure driver is closed
            self.safe_quit_driver()

        return self.jobs_data

    def safe_quit_driver(self):
        """
        Safely close the WebDriver and clean up resources
        """
        try:
            if self.driver:
                # Attempt to close browser windows
                self.driver.quit()
        except Exception as e:
            print(f"Error during driver cleanup: {e}")
        
        try:
            # Alternative process termination
            import subprocess
            subprocess.run("taskkill /F /IM chromedriver.exe /T", shell=True, capture_output=True)
            subprocess.run("taskkill /F /IM chrome.exe /T", shell=True, capture_output=True)
        except Exception as e:
            print(f"Error killing Chrome processes: {e}")

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
            traceback.print_exc()

def main():
    """
    Main function to run the Indeed job scraper
    """
    try:
        # Configure scraper
        search_query = "Software Engineer"
        location = "India"  # Optional: specify location
        num_pages = 3  # Number of pages to scrape

        # Create scraper instance
        scraper = IndeedScraper(search_query, location, num_pages)
        
        # Scrape jobs
        scraper.scrape_jobs()

        # Save to CSV
        scraper.save_to_csv()

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        traceback.print_exc()
    
if __name__ == "__main__":
    main()