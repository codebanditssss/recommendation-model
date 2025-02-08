import json
import time
import random
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    StaleElementReferenceException
)

def setup_driver():
    """
    Setup Chrome WebDriver with anti-detection and performance options
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-notifications')
    options.add_argument('--log-level=3')  # Suppress console logs
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # User agent rotation to reduce detection
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
    ]
    options.add_argument(f'user-agent={random.choice(user_agents)}')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Additional anti-detection script
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
        """
    })
    
    return driver

def random_delay(min_time=2, max_time=5):
    """
    Generate random delay to mimic human behavior
    """
    time.sleep(random.uniform(min_time, max_time))

def handle_verification_challenge(driver):
    """
    Handle Indeed's verification challenges
    """
    try:
        # Check for different types of verification challenges
        challenge_selectors = [
            "iframe[src*='challenges.cloudflare.com']",  # Cloudflare
            "[data-testid='cf-turnstile-container']",  # Cloudflare Turnstile
            "#px-captcha",  # Imperva/Incapsula
            ".g-recaptcha"  # reCAPTCHA
        ]
        
        for selector in challenge_selectors:
            try:
                challenge = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                print("Verification challenge detected!")
                input("Please solve the verification challenge manually, then press Enter to continue...")
                return True
            except TimeoutException:
                continue
        
        return False
    except Exception as e:
        print(f"Error handling verification challenge: {e}")
        return False

def wait_and_find_element(driver, by, value, timeout=10):
    """
    Wait and find an element with error handling
    """
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    except TimeoutException:
        print(f"Timeout waiting for element: {value}")
        return None

def get_company_name(job):
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
                return element.text.strip()
        except Exception:
            continue
    return "Not specified"

def get_location(job):
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
                return element.text.strip()
        except Exception:
            continue
    return "Not specified"

def get_salary(job):
    """
    Extract salary information with multiple approaches
    """
    try:
        salary_selectors = [
            "div.salary-snippet-container",
            "div.metadata",
            ".jobsearch-SalaryCompensationInfo-container"
        ]
        
        for selector in salary_selectors:
            try:
                salary_element = job.find_element(By.CSS_SELECTOR, selector)
                if salary_element and salary_element.text.strip():
                    return salary_element.text.strip()
            except Exception:
                continue
    except Exception:
        pass
    return "Not specified"

def get_job_description(driver):
    """
    Extract job description with multiple approaches and error handling
    """
    try:
        # Allow page to load
        random_delay(1, 2)

        # Close any existing popup
        popup_close_selectors = [
            "[aria-label='Close']",
            ".popover-close-button",
            "#jobsearch-ViewJobButtons-closeModal"
        ]
        
        for selector in popup_close_selectors:
            try:
                close_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                close_button.click()
                random_delay(0.5, 1)
            except Exception:
                continue

        # Description selectors
        desc_selectors = [
            "div#jobDescriptionText", 
            "div[data-testid='jobDescriptionText']", 
            "div.jobsearch-JobComponent-description",
            "#jobDescriptionText"
        ]
        
        for selector in desc_selectors:
            try:
                description_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                description = description_element.text.strip()
                
                # Truncate long descriptions
                return (description[:500] + "...") if len(description) > 500 else description
            except Exception:
                continue
        
        return "Description not available"
    except Exception as e:
        print(f"Error extracting description: {e}")
        return "Description not available"

def scrape_indeed_jobs(search_query, num_pages=3):
    """
    Main scraping function with enhanced error handling and anti-detection
    """
    driver = setup_driver()
    jobs_data = []
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        # Navigate to Indeed with random delay
        driver.get("https://in.indeed.com/")
        random_delay()

        # Handle potential verification challenge
        if handle_verification_challenge(driver):
            random_delay(2, 4)

        # Find and interact with search box
        search_box = wait_and_find_element(driver, By.NAME, "q")
        if not search_box:
            print("Could not find search box")
            return
            
        search_box.clear()
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)
        random_delay()

        for page in range(num_pages):
            print(f"\nProcessing page {page + 1}")
            
            # Handle potential verification challenge
            if handle_verification_challenge(driver):
                random_delay(2, 4)

            # Wait and find job cards
            try:
                job_cards = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "job_seen_beacon"))
                )
            except TimeoutException:
                print("No job listings found on this page")
                break
                
            print(f"Found {len(job_cards)} jobs on page {page + 1}")

            for index, job in enumerate(job_cards, 1):
                try:
                    # Find job title with multiple approaches
                    title_selectors = [
                        "h2.jobTitle a", 
                        ".jobTitle a", 
                        "[data-jk] a"
                    ]
                    title_element = None
                    for selector in title_selectors:
                        try:
                            title_element = job.find_element(By.CSS_SELECTOR, selector)
                            break
                        except Exception:
                            continue
                    
                    if not title_element:
                        print(f"Could not find title for job {index}")
                        continue

                    title = title_element.text.strip()
                    company = get_company_name(job)
                    location = get_location(job)
                    salary = get_salary(job)

                    # Click and get description
                    try:
                        # Scroll to job card
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job)
                        random_delay(0.5, 1)
                        
                        # Click job title with JavaScript to avoid potential interception
                        driver.execute_script("arguments[0].click();", title_element)
                        random_delay(1, 2)

                        # Extract description
                        description = get_job_description(driver)

                        job_data = {
                            "JobTitle": title,
                            "Company": company,
                            "Location": location,
                            "ExtractDate": current_date,
                            "Summary": description,
                            "Salary": salary,
                            "JobUrl": driver.current_url
                        }
                        
                        jobs_data.append(job_data)
                        print(f"Successfully scraped: {title}")

                    except Exception as e:
                        print(f"Error processing job {title}: {str(e)}")
                        continue

                except Exception as e:
                    print(f"Error with job card {index}: {str(e)}")
                    continue

                # Random delay between job processing
                random_delay(1, 2)

            # Navigate to next page
            if page < num_pages - 1:
                try:
                    next_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Next"]'))
                    )
                    driver.execute_script("arguments[0].click();", next_button)
                    print("Navigating to next page")
                    random_delay(2, 4)
                except Exception:
                    print("No more pages available")
                    break

        # Save results
        if jobs_data:
            # Excel output
            df = pd.DataFrame(jobs_data)
            df.to_excel("jobs_data.xlsx", index=False, sheet_name='Jobs')

            # JSON output
            json_data = [
                {
                    "title": job["JobTitle"], 
                    "company": job["Company"], 
                    "location": job["Location"]
                } for job in jobs_data
            ]
            with open("jobs.json", "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)

            print(f"\nSuccessfully scraped {len(jobs_data)} jobs")
            print("Data saved to jobs_data.xlsx and jobs.json")
        else:
            print("No jobs were scraped successfully")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        driver.quit()

if __name__ == "__main__":
    # Customize search query and number of pages
    scrape_indeed_jobs("Software Engineer", num_pages=3)