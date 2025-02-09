# # import json
# # import time
# # from selenium import webdriver
# # from selenium.webdriver.common.by import By
# # from selenium.webdriver.common.keys import Keys
# # from selenium.webdriver.chrome.service import Service
# # from webdriver_manager.chrome import ChromeDriverManager
# # from selenium.webdriver.support.ui import WebDriverWait
# # from selenium.webdriver.support import expected_conditions as EC
# # from selenium.common.exceptions import TimeoutException, NoSuchElementException

# # def setup_driver():
# #     options = webdriver.ChromeOptions()
# #     options.add_argument('--start-maximized')
# #     options.add_argument('--disable-notifications')
# #     service = Service(ChromeDriverManager().install())
# #     return webdriver.Chrome(service=service, options=options)

# # def wait_and_find_element(driver, by, value, timeout=10):
# #     try:
# #         element = WebDriverWait(driver, timeout).until(
# #             EC.presence_of_element_located((by, value))
# #         )
# #         return element
# #     except TimeoutException:
# #         print(f"Timeout waiting for element: {value}")
# #         return None

# # def get_company_name(job):
# #     """Try multiple selectors to find company name"""
# #     selectors = [
# #         ".companyName",
# #         "[data-testid='company-name']",
# #         ".company_location .companyName",
# #         ".company_location span",
# #         ".resultContent .company"
# #     ]
    
# #     for selector in selectors:
# #         try:
# #             element = job.find_element(By.CSS_SELECTOR, selector)
# #             if element:
# #                 return element.text.strip()
# #         except:
# #             continue
# #     return "Company name not available"

# # def get_location(job):
# #     """Try multiple selectors to find location"""
# #     selectors = [
# #         ".companyLocation",
# #         "[data-testid='text-location']",
# #         ".company_location .companyLocation",
# #         ".resultContent .location"
# #     ]
    
# #     for selector in selectors:
# #         try:
# #             element = job.find_element(By.CSS_SELECTOR, selector)
# #             if element:
# #                 return element.text.strip()
# #         except:
# #             continue
# #     return "Location not available"

# # def get_job_description(driver):
# #     """Get job description with better waiting and verification"""
# #     try:
# #         # Wait for the job description iframe to load (if it exists)
# #         try:
# #             iframe = WebDriverWait(driver, 5).until(
# #                 EC.presence_of_element_located((By.CSS_SELECTOR, "#vjs-container-iframe"))
# #             )
# #             driver.switch_to.frame(iframe)
# #         except:
# #             pass  # No iframe found, continue with main content

# #         # Wait for description to load with multiple selector attempts
# #         description_selectors = [
# #             "#jobDescriptionText",
# #             ".jobsearch-jobDescriptionText",
# #             "[data-testid='jobDescriptionText']",
# #             ".job-description"
# #         ]

# #         for selector in description_selectors:
# #             try:
# #                 description_element = WebDriverWait(driver, 5).until(
# #                     EC.presence_of_element_located((By.CSS_SELECTOR, selector))
# #                 )
# #                 description = description_element.text.strip()
                
# #                 # Verify we got actual content
# #                 if description and len(description) > 20:  # Arbitrary minimum length
# #                     return description
# #             except:
# #                 continue

# #         # Switch back to default content if we switched to iframe
# #         try:
# #             driver.switch_to.default_content()
# #         except:
# #             pass

# #         return "Description not available"
# #     except Exception as e:
# #         print(f"Error getting description: {str(e)}")
# #         return "Error retrieving description"

# # def scrape_indeed_jobs(search_query, num_pages=3):
# #     driver = setup_driver()
# #     jobs_data = []
    
# #     try:
# #         # Navigate to Indeed
# #         driver.get("https://in.indeed.com/")
# #         print("Navigated to Indeed.com")
        
# #         # Handle cookie consent if it appears
# #         try:
# #             cookie_button = wait_and_find_element(driver, By.CSS_SELECTOR, "[data-cookie-notice-accept-btn]", timeout=5)
# #             if cookie_button:
# #                 cookie_button.click()
# #                 print("Handled cookie notice")
# #         except:
# #             print("No cookie notice found or already accepted")

# #         # Find and fill search box
# #         search_box = wait_and_find_element(driver, By.NAME, "q")
# #         if not search_box:
# #             print("Could not find search box")
# #             return
            
# #         search_box.clear()
# #         search_box.send_keys(search_query)
# #         search_box.send_keys(Keys.RETURN)
# #         print(f"Searching for: {search_query}")

# #         # Iterate through pages
# #         for page in range(num_pages):
# #             print(f"\nScraping page {page + 1}")
# #             time.sleep(5)  # Wait for page load
            
# #             # Wait for job cards to be visible
# #             try:
# #                 WebDriverWait(driver, 10).until(
# #                     EC.presence_of_all_elements_located((By.CLASS_NAME, "job_seen_beacon"))
# #                 )
# #             except TimeoutException:
# #                 print("Timeout waiting for job cards")
# #                 continue

# #             # Find all job cards
# #             job_cards = driver.find_elements(By.CLASS_NAME, "job_seen_beacon")
# #             if not job_cards:
# #                 print("No job cards found on this page")
# #                 break
                
# #             print(f"Found {len(job_cards)} job cards")
            
# #             for index, job in enumerate(job_cards, 1):
# #                 try:
# #                     # Extract job title
# #                     title_element = job.find_element(By.CSS_SELECTOR, "h2.jobTitle")
# #                     title = title_element.text.strip()
                    
# #                     # Get company name and location
# #                     company = get_company_name(job)
# #                     location = get_location(job)
                    
# #                     # Click job to load description
# #                     try:
# #                         # Scroll element into view
# #                         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job)
# #                         time.sleep(1)
                        
# #                         # Click using JavaScript
# #                         driver.execute_script("arguments[0].click();", title_element)
# #                         time.sleep(2)  # Wait for description to load
                        
# #                         # Get description using improved function
# #                         description = get_job_description(driver)
                        
# #                         if description == "Description not available":
# #                             print(f"Warning: Could not get description for job {index}")
# #                             continue

# #                     except Exception as e:
# #                         print(f"Error clicking job {index}: {str(e)}")
# #                         continue

# #                     job_data = {
# #                         "title": title,
# #                         "company": company,
# #                         "location": location,
# #                         "description": description
# #                     }
                    
# #                     jobs_data.append(job_data)
# #                     print(f"Successfully scraped: {title} at {company}")

# #                 except Exception as e:
# #                     print(f"Error scraping job {index} on page {page + 1}: {str(e)}")
# #                     continue

# #             # Try to go to next page if not on last page
# #             if page < num_pages - 1:
# #                 try:
# #                     next_button = driver.find_element(By.CSS_SELECTOR, '[aria-label="Next"]')
# #                     driver.execute_script("arguments[0].click();", next_button)
# #                     print("Navigating to next page")
# #                     time.sleep(3)
# #                 except:
# #                     print("No more pages available")
# #                     break

# #         # Save the data
# #         with open("jobs.json", "w", encoding="utf-8") as f:
# #             json.dump(jobs_data, f, ensure_ascii=False, indent=4)
        
# #         print(f"\nSuccessfully scraped {len(jobs_data)} jobs and saved to jobs.json")
        
# #     except Exception as e:
# #         print(f"An error occurred: {str(e)}")
    
# #     finally:
# #         driver.quit()

# # if __name__ == "_main_":
# #     scrape_indeed_jobs("Management Jobs", num_pages=3)

# import json
# import time
# import pandas as pd
# from datetime import datetime
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException

# def setup_driver():
#     options = webdriver.ChromeOptions()
#     options.add_argument('--start-maximized')
#     options.add_argument('--disable-notifications')
#     options.add_argument('--log-level=3')  # Suppress console logs
#     options.add_experimental_option('excludeSwitches', ['enable-logging'])
#     service = Service(ChromeDriverManager().install())
#     return webdriver.Chrome(service=service, options=options)

# def wait_and_find_element(driver, by, value, timeout=10):
#     try:
#         element = WebDriverWait(driver, timeout).until(
#             EC.presence_of_element_located((by, value))
#         )
#         return element
#     except TimeoutException:
#         print(f"Timeout waiting for element: {value}")
#         return None

# def get_company_name(job):
#     selectors = [".companyName", "[data-testid='company-name']", ".company_location .companyName"]
#     for selector in selectors:
#         try:
#             element = job.find_element(By.CSS_SELECTOR, selector)
#             if element:
#                 return element.text.strip()
#         except:
#             continue
#     return "Not specified"

# def get_location(job):
#     selectors = [".companyLocation", "[data-testid='text-location']", ".resultContent .location"]
#     for selector in selectors:
#         try:
#             element = job.find_element(By.CSS_SELECTOR, selector)
#             if element:
#                 return element.text.strip()
#         except:
#             continue
#     return "Not specified"

# def get_salary(job):
#     try:
#         # Try the primary salary element
#         salary_element = job.find_element(By.CSS_SELECTOR, "div.salary-snippet-container")
#         if salary_element:
#             return salary_element.text.strip()
#     except:
#         try:
#             # Try alternative salary element
#             metadata = job.find_element(By.CSS_SELECTOR, "div.metadata")
#             if "₹" in metadata.text:
#                 return metadata.text.strip()
#         except:
#             pass
#     return "Not specified"

# def get_post_date(job):
#     try:
#         date_element = job.find_element(By.CSS_SELECTOR, "span.date")
#         if date_element:
#             return date_element.text.strip()
#     except:
#         pass
#     return "Not specified"

# def get_job_description(driver):
#     description = None
#     try:
#         # First close any existing popup
#         try:
#             close_button = WebDriverWait(driver, 5).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label='Close']"))
#             )
#             if close_button and close_button.is_displayed():
#                 close_button.click()
#                 time.sleep(1)
#         except:
#             pass

#         # Wait for the new job to be clickable and loaded
#         time.sleep(2)

#         # Try different description selectors
#         selectors = [
#             "div#jobDescriptionText", 
#             "div[data-testid='jobDescriptionText']", 
#             "div.jobsearch-JobComponent-description"
#         ]
        
#         for selector in selectors:
#             try:
#                 description_element = WebDriverWait(driver, 5).until(
#                     EC.presence_of_element_located((By.CSS_SELECTOR, selector))
#                 )
#                 if description_element:
#                     description = description_element.text.strip()
#                     if len(description) > 50:  # Make sure we got real content
#                         break
#             except:
#                 continue

#         if description:
#             # Extract first meaningful paragraph
#             paragraphs = [p.strip() for p in description.split('\n') if len(p.strip()) > 50]
#             if paragraphs:
#                 return paragraphs[0][:200] + "..." if len(paragraphs[0]) > 200 else paragraphs[0]
        
#         return "Description not available"
#     except:
#         return "Description not available"

# def scrape_indeed_jobs(search_query, num_pages=3):
#     driver = setup_driver()
#     jobs_data = []
#     current_date = datetime.now().strftime("%Y-%m-%d")
    
#     try:
#         driver.get("https://in.indeed.com/")
#         print("Navigated to Indeed.com")

#         search_box = wait_and_find_element(driver, By.NAME, "q")
#         if not search_box:
#             print("Could not find search box")
#             return
            
#         search_box.clear()
#         search_box.send_keys(search_query)
#         search_box.send_keys(Keys.RETURN)
#         print(f"Searching for: {search_query}")

#         for page in range(num_pages):
#             print(f"\nProcessing page {page + 1}")
#             time.sleep(5)

#             job_cards = driver.find_elements(By.CLASS_NAME, "job_seen_beacon")
#             if not job_cards:
#                 print("No job listings found on this page")
#                 break
                
#             print(f"Found {len(job_cards)} jobs on page {page + 1}")

#             for index, job in enumerate(job_cards, 1):
#                 try:
#                     title_element = job.find_element(By.CSS_SELECTOR, "h2.jobTitle")
#                     title = title_element.text.strip()
#                     company = get_company_name(job)
#                     location = get_location(job)
#                     post_date = get_post_date(job)
#                     salary = get_salary(job)

#                     # Click and get description
#                     try:
#                         # Close any existing popup first
#                         close_buttons = driver.find_elements(By.CSS_SELECTOR, "[aria-label='Close']")
#                         for button in close_buttons:
#                             if button.is_displayed():
#                                 button.click()
#                                 time.sleep(1)

#                         # Now click the new job
#                         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job)
#                         time.sleep(1)
#                         driver.execute_script("arguments[0].click();", title_element)
#                         time.sleep(2)

#                         description = get_job_description(driver)

#                         job_data = {
#                             "JobTitle": title,
#                             "Company": company,
#                             "Location": location,
#                             "PostDate": post_date,
#                             "ExtractDate": current_date,
#                             "Summary": description,
#                             "Salary": salary,
#                             "JobUrl": driver.current_url
#                         }
                        
#                         jobs_data.append(job_data)
#                         print(f"Successfully scraped: {title}")

#                     except Exception as e:
#                         print(f"Error processing job {title}: {str(e)}")
#                         continue

#                 except Exception as e:
#                     print(f"Error with job card {index}: {str(e)}")
#                     continue

#                 time.sleep(1)

#             if page < num_pages - 1:
#                 try:
#                     next_button = driver.find_element(By.CSS_SELECTOR, '[aria-label="Next"]')
#                     driver.execute_script("arguments[0].click();", next_button)
#                     print("Navigating to next page")
#                     time.sleep(3)
#                 except:
#                     print("No more pages available")
#                     break

#         if jobs_data:
#             # Create DataFrame
#             df = pd.DataFrame(jobs_data)
#             columns = ['JobTitle', 'Company', 'Location', 'PostDate', 'ExtractDate', 'Summary', 'Salary', 'JobUrl']
#             df = df[columns]
            
#             # Save to Excel
#             df.to_excel("jobs_data.xlsx", index=False, sheet_name='Jobs')

#             # Save JSON
#             json_data = [{
#                 "title": job["JobTitle"],
#                 "company": job["Company"],
#                 "location": job["Location"]
#             } for job in jobs_data]
            
#             with open("jobs.json", "w", encoding="utf-8") as f:
#                 json.dump(json_data, f, ensure_ascii=False, indent=4)

#             print(f"\nSuccessfully scraped {len(jobs_data)} jobs")
#             print("Data saved to jobs_data.xlsx and jobs.json")
#         else:
#             print("No jobs were scraped successfully")

#     except Exception as e:
#         print(f"An error occurred: {str(e)}")

#     finally:
#         driver.quit()

# if __name__ == "__main__":
#     scrape_indeed_jobs("Management Jobs", num_pages=3)

import json
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-notifications')
    options.add_argument('--log-level=3')  # Suppress console logs
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def wait_and_find_element(driver, by, value, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
    except TimeoutException:
        print(f"Timeout waiting for element: {value}")
        return None

def get_company_name(job):
    selectors = [".companyName", "[data-testid='company-name']", ".company_location .companyName"]
    for selector in selectors:
        try:
            element = job.find_element(By.CSS_SELECTOR, selector)
            if element:
                return element.text.strip()
        except:
            continue
    return "Not specified"

def get_location(job):
    selectors = [".companyLocation", "[data-testid='text-location']", ".resultContent .location"]
    for selector in selectors:
        try:
            element = job.find_element(By.CSS_SELECTOR, selector)
            if element:
                return element.text.strip()
        except:
            continue
    return "Not specified"

def get_salary(job):
    try:
        salary_element = job.find_element(By.CSS_SELECTOR, "div.salary-snippet-container")
        if salary_element:
            return salary_element.text.strip()
    except:
        try:
            metadata = job.find_element(By.CSS_SELECTOR, "div.metadata")
            if "₹" in metadata.text:
                return metadata.text.strip()
        except:
            pass
    return "Not specified"

def get_job_description(driver):
    """Extracts the correct job description after clicking on a job."""
    try:
        time.sleep(2)  # Allow page to load

        # Close any existing popup
        try:
            close_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label='Close']"))
            )
            if close_button and close_button.is_displayed():
                close_button.click()
                time.sleep(1)
        except:
            pass  # No popup means no issue

        # Try extracting the job description from different elements
        selectors = ["div#jobDescriptionText", "div[data-testid='jobDescriptionText']", "div.jobsearch-JobComponent-description"]
        
        for selector in selectors:
            try:
                description_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if description_element:
                    description = description_element.text.strip()
                    if len(description) > 50:  # Ensure it's meaningful
                        return description[:200] + "..." if len(description) > 200 else description
            except:
                continue
        
        return "Description not available"
    except:
        return "Description not available"

def scrape_indeed_jobs(search_query, num_pages=3):
    driver = setup_driver()
    jobs_data = []
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        driver.get("https://in.indeed.com/")
        print("Navigated to Indeed.com")

        search_box = wait_and_find_element(driver, By.NAME, "q")
        if not search_box:
            print("Could not find search box")
            return
            
        search_box.clear()
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)
        print(f"Searching for: {search_query}")

        for page in range(num_pages):
            print(f"\nProcessing page {page + 1}")
            time.sleep(5)

            job_cards = driver.find_elements(By.CLASS_NAME, "job_seen_beacon")
            if not job_cards:
                print("No job listings found on this page")
                break
                
            print(f"Found {len(job_cards)} jobs on page {page + 1}")

            for index, job in enumerate(job_cards, 1):
                try:
                    title_element = job.find_element(By.CSS_SELECTOR, "h2.jobTitle")
                    title = title_element.text.strip()
                    company = get_company_name(job)
                    location = get_location(job)
                    salary = get_salary(job)

                    # Click and get description
                    try:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job)
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", title_element)
                        time.sleep(2)

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

                time.sleep(1)

            if page < num_pages - 1:
                try:
                    next_button = driver.find_element(By.CSS_SELECTOR, '[aria-label="Next"]')
                    driver.execute_script("arguments[0].click();", next_button)
                    print("Navigating to next page")
                    time.sleep(3)
                except:
                    print("No more pages available")
                    break

        if jobs_data:
            df = pd.DataFrame(jobs_data)
            df.to_excel("jobs_data.xlsx", index=False, sheet_name='Jobs')

            json_data = [{"title": job["JobTitle"], "company": job["Company"], "location": job["Location"]} for job in jobs_data]
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
    scrape_indeed_jobs("Management Jobs", num_pages=3)
