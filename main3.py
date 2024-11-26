from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
from selenium.common.exceptions import StaleElementReferenceException
import datetime


# Selenium setup
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
webdriver_service = Service("chromedriver.exe")

driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

def scroll_to_bottom():
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def scrape_jobs_from_url(url):
    driver.get(url)
    time.sleep(5)

    jobs_data = []
    processed_jobs = set()
    job_titles = []  # To store job titles
    max_scroll_attempts = 10
    scroll_attempt = 0
    previous_job_count = 0

    # Collect all job titles and their clickable elements
    while scroll_attempt < max_scroll_attempts:
        scroll_to_bottom()
        
        job_blocks = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "gutter-width-y"))
        )
        
        current_job_count = len(job_blocks)
        print(f"Found {current_job_count} job blocks after scroll {scroll_attempt + 1}")
        
        if current_job_count == previous_job_count:
            scroll_attempt += 1
        else:
            scroll_attempt = 0

        previous_job_count = current_job_count

        for block in job_blocks:
            try:
                job_container = block.find_element(By.CLASS_NAME, "MuiPaper-root")
                title_element = job_container.find_element(By.CSS_SELECTOR, "p.MuiTypography-subtitle1")
                job_title = title_element.get_attribute("aria-label")
                
                company_element = job_container.find_element(By.CSS_SELECTOR, "p.MuiTypography-subtitle2.ellipsis")
                company_name = company_element.get_attribute("aria-label")
                
                job_id = f"{job_title}_{company_name}"
                if job_id in processed_jobs:
                    continue
                
                # Store job title element and its identifier
                job_titles.append((title_element, job_id))
                processed_jobs.add(job_id)
                
            except Exception as e:
                print(f"Error processing job block: {e}")
                continue
        
        if scroll_attempt >= 3:
            print("No new jobs found after multiple scrolls. Finishing collection...")
            break

        time.sleep(2)

    # Click through each job title and scrape details
    for index, (title_element, job_id) in enumerate(job_titles):
        try:
            print(f"Processing job at index {index}: {job_id}")
            
            # Scroll the element into view
            driver.execute_script("arguments[0].scrollIntoView(true);", title_element)
            time.sleep(1)
            
            # Click the element using JavaScript to avoid click interception
            driver.execute_script("arguments[0].click();", title_element)
            time.sleep(3)  # Wait for the details page to load

            # Scrape details from the new page
            job_details = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "job-details-container"))
            )
            full_description = job_details.text
            print(f"Full Job Description: {full_description}")

            # Navigate back to the main page
            driver.back()

            # Explicit wait for the original page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "gutter-width-y"))  # Adjust this selector as needed
            )

            # Store the scraped data
            jobs_data.append({
                'job_title': job_id.split("_")[0],
                'company_name': job_id.split("_")[1],
                'full_description': full_description,
            })

        except Exception as e:
            print(f"Error processing job at index {index}: {e}")
            continue
            


    return jobs_data



try:
    # Login
    driver.get("https://nirmauni.pod.ai/d/sXfPHC/opportunities/?eligibilityType=1&eligibilityType=2")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "username")))
    driver.find_element(By.NAME, "username").send_keys("write username")
    driver.find_element(By.NAME, "password").send_keys("write your pass")
    driver.find_element(
        By.CSS_SELECTOR,
        ".MuiButtonBase-root.MuiButton-root.MuiButton-contained.MuiButton-containedPrimary"
    ).click()
    time.sleep(5)
    print("Logged in")

    # Scrape data from both URLs
    urls = [
        "https://nirmauni.pod.ai/d/sXfPHC/opportunities/?eligibilityType=1&eligibilityType=2",
        "https://nirmauni.pod.ai/d/sXfPHC/applications/"
    ]
    all_jobs_data = []
    
    for url in urls:
        print(f"Scraping data from: {url}")
        jobs_data = scrape_jobs_from_url(url)
        all_jobs_data.extend(jobs_data)
        print(f"Scraped {len(jobs_data)} jobs from {url}")

    hii= []
    hii.append({
                    'job_title': 'Associate Enginner',
                    'company_name': 'Infocusp Innovations',
                    'posting_date': '29 Jul 2024',
                    'job_type': 'Internship + Job',
                    'industry': 'IT / Computers - Software',
                    'stipend': '40,000',
                    'location': 'Ahmedabad'
                })
    all_jobs_data.extend(hii)
    # Save to CSV
    if all_jobs_data:
        filename = f'all_jobs_detailed_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=[
                'job_title', 'company_name', 'posting_date', 
                'job_type', 'industry', 'stipend', 'location'
            ])
            writer.writeheader()
            writer.writerows(all_jobs_data)
            print(f"Data saved to {filename}")

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    driver.quit()
