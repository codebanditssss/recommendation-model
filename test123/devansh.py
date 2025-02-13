from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import time
import json

class IndeedJobScraper:
    def _init_(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--start-maximized')
        self.options.add_argument('--disable-notifications')
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.jobs_data = []

    def wait_for_element(self, by, value, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def get_text_safe(self, element, selector, method=By.CSS_SELECTOR):
        try:
            return element.find_element(method, selector).text.strip()
        except:
            return "Not specified"

    def extract_job_details(self, job_card):
        job_data = {}
        
        # Extract job title
        try:
            job_data['title'] = job_card.find_element(By.CSS_SELECTOR, "h2.jobTitle").text.strip()
        except:
            job_data['title'] = "Not specified"

        # Extract company name
        try:
            job_data['company'] = job_card.find_element(By.CSS_SELECTOR, "[data-testid='company-name']").text.strip()
        except:
            job_data['company'] = "Not specified"

        # Extract location
        try:
            job_data['location'] = job_card.find_element(By.CSS_SELECTOR, "[data-testid='text-location']").text.strip()
        except:
            job_data['location'] = "Not specified"

        # Extract salary if available
        try:
            job_data['salary'] = job_card.find_element(By.CSS_SELECTOR, "[class*='salary-snippet']").text.strip()
        except:
            job_data['salary'] = "Not specified"

        # Extract job description snippet
        try:
            job_data['description'] = job_card.find_element(By.CSS_SELECTOR, ".job-snippet").text.strip()
        except:
            job_data['description'] = "Not specified"

        # Extract job type (if available)
        try:
            job_data['job_type'] = job_card.find_element(By.CSS_SELECTOR, "[class*='metadata'] [class*='attribute_snippet']").text.strip()
        except:
            job_data['job_type'] = "Not specified"

        # Extract posting date
        try:
            job_data['posted_date'] = job_card.find_element(By.CSS_SELECTOR, ".date").text.strip()
        except:
            job_data['posted_date'] = "Not specified"

        return job_data

    def scrape_jobs(self, search_query, location="", num_pages=1):
        try:
            # Navigate to Indeed
            self.driver.get("https://in.indeed.com/")
            time.sleep(3)

            # Input search query
            search_box = self.wait_for_element(By.NAME, "q")
            search_box.clear()
            search_box.send_keys(search_query)

            # Input location if provided
            if location:
                location_box = self.wait_for_element(By.NAME, "l")
                location_box.clear()
                location_box.send_keys(location)

            search_box.send_keys(Keys.RETURN)
            time.sleep(5)

            # Process specified number of pages
            for page in range(num_pages):
                print(f"\nProcessing page {page + 1}")
                
                # Wait for job cards to load
                self.wait_for_element(By.CLASS_NAME, "job_seen_beacon")
                time.sleep(2)

                # Get all job cards
                job_cards = self.driver.find_elements(By.CLASS_NAME, "job_seen_beacon")
                print(f"Found {len(job_cards)} jobs on page {page + 1}")

                # Process each job card
                for i, job_card in enumerate(job_cards, 1):
                    try:
                        print(f"Processing job {i} on page {page + 1}")
                        job_data = self.extract_job_details(job_card)
                        self.jobs_data.append(job_data)
                    except Exception as e:
                        print(f"Error processing job {i} on page {page + 1}: {str(e)}")
                        continue

                # Try to go to next page if not on last page
                if page < num_pages - 1:
                    try:
                        next_button = self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Next Page']")
                        next_button.click()
                        time.sleep(3)
                    except:
                        print("No more pages available")
                        break

            return self.save_results()

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return self.save_results()

        finally:
            self.driver.quit()

    def save_results(self):
        # Save to CSV
        df = pd.DataFrame(self.jobs_data)
        csv_filename = "job_listings.csv"
        df.to_csv(csv_filename, index=False)
        
        # Save to JSON
        json_filename = "job_listings.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.jobs_data, f, indent=2, ensure_ascii=False)
        
        return df, self.jobs_data

# Usage example
if __name__ == "_main_":
    scraper = IndeedJobScraper()
    # You can specify search query, location, and number of pages to scrape
    df, jobs = scraper.scrape_jobs(
        search_query="Data Scientist",
        location="Bangalore",
        num_pages=2
    )
    
    print("\nScraping completed!")
    print(f"Total jobs collected: {len(jobs)}")
    print("Results saved to job_listings.csv and job_listings.json")