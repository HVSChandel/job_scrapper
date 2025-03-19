from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
from datetime import datetime, timedelta
import re

def convert_relative_time(relative_time):
    current_date = datetime.now()
    
    # Extract the numerical value and unit using regex
    match = re.match(r"(\d+)([hdwmy]) ago", relative_time)
    
    if not match:
        return "Invalid format"

    value, unit = int(match.group(1)), match.group(2)

    if unit == 'h':
        actual_date = current_date - timedelta(hours=value)
    elif unit == 'd':
        actual_date = current_date - timedelta(days=value)
    elif unit == 'w':
        actual_date = current_date - timedelta(weeks=value)
    elif unit == 'm':
        actual_date = current_date - timedelta(days=value * 30)  # Approximate
    elif unit == 'y':
        actual_date = current_date - timedelta(days=value * 365)  # Approximate
    else:
        return "Invalid format"
    
    return actual_date.strftime('%Y-%m-%d')

def scrape_jobs(company_name,industry):
    # Set up Selenium WebDriver
    options = Options()
    options.add_argument("--headless") 
    # options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    # Initialize WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(180)  # 3 minutes timeout
    
    job_data = []
    page = 1
    formatted_company_name = "-".join(company_name.split())

    while True:
        # Construct URL
        URL = f"https://www.seek.com.au/{formatted_company_name}-jobs?page={page}"
        print(f"Scraping page {page}: {URL}")
        
        try:
            driver.get(URL)
        except Exception as e:
            print("Page load timeout error:", e)
            break
        
        time.sleep(3)  # Wait for page elements to load
        
        # Check if the page loaded
        print("Page loaded successfully!")
        

        # Locate the main container
        try:
            job_container = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[6]/div/section/div[2]/div/div/div[1]/div/div/div/div/div[1]/div/div[1]/div[2]/div[2]")
            job_divs = job_container.find_elements(By.XPATH, "./div")
            if not job_divs:
                print("No more job listings found. Stopping.")
                break 
        except Exception as e:
            print("Error locating job container, stopping:", e)
            break

        

        for job in job_divs:
            try:
                title = job.find_element(By.XPATH, ".//h3/div/a").text if job.find_elements(By.XPATH, ".//h3/div/a") else None
                posting_date = job.find_element(By.XPATH, "/html/body/div[1]/div/div[6]/div/section/div[2]/div/div/div[1]/div/div/div/div/div[1]/div/div[1]/div[2]/div[2]/div[1]/article/div[4]/div[4]/span").text if job.find_elements(By.XPATH, "/html/body/div[1]/div/div[6]/div/section/div[2]/div/div/div[1]/div/div/div/div/div[1]/div/div[1]/div[2]/div[2]/div[1]/article/div[4]/div[4]/span") else None
                if posting_date is not None:
                    posting_date = convert_relative_time(posting_date)
                link = job.find_element(By.XPATH, "/html/body/div[1]/div/div[6]/div/section/div[2]/div/div/div[1]/div/div/div/div/div[1]/div/div[1]/div[2]/div[2]/div[1]/article/div[1]/a").get_attribute("href") if job.find_elements(By.XPATH, "/html/body/div[1]/div/div[6]/div/section/div[2]/div/div/div[1]/div/div/div/div/div[1]/div/div[1]/div[2]/div[2]/div[1]/article/div[1]/a") else None
                jd_1 = job.find_element(By.XPATH, "/html/body/div[1]/div/div[6]/div/section/div[2]/div/div/div[1]/div/div/div/div/div[1]/div/div[1]/div[2]/div[2]/div[1]/article/div[4]/div[3]").text if job.find_elements(By.XPATH, "/html/body/div[1]/div/div[6]/div/section/div[2]/div/div/div[1]/div/div/div/div/div[1]/div/div[1]/div[2]/div[2]/div[1]/article/div[4]/div[3]") else None
                jd_2 = job.find_element(By.XPATH, "/html/body/div[1]/div/div[6]/div/section/div[2]/div/div/div[1]/div/div/div/div/div[1]/div/div[1]/div[2]/div[2]/div[1]/article/div[4]/ul").text if job.find_elements(By.XPATH, "/html/body/div[1]/div/div[6]/div/section/div[2]/div/div/div[1]/div/div/div/div/div[1]/div/div[1]/div[2]/div[2]/div[1]/article/div[4]/ul") else None
                jd_3 = job.find_element(By.XPATH, "/html/body/div[1]/div/div[6]/div/section/div[2]/div/div/div[1]/div/div/div/div/div[1]/div/div[1]/div[2]/div[2]/div[1]/article/div[4]/span").text if job.find_elements(By.XPATH, "/html/body/div[1]/div/div[6]/div/section/div[2]/div/div/div[1]/div/div/div/div/div[1]/div/div[1]/div[2]/div[2]/div[1]/article/div[4]/span") else None

                job_desc = " ".join(filter(None, [jd_1, jd_2, jd_3]))

                job_data.append({
                    "Title": title,
                    "company_name": company_name,
                    "industry": industry,
                    "Posting_Date": posting_date,
                    "Link": link,
                    "Job_Description": job_desc
                })
            except Exception as e:
                print("Error extracting job:", e)
        page += 1

    
    driver.quit()
    return job_data

# # Example usage
# company_name = "Bendigo and Adelaide Bank"
# industry = "Banking"
# jobs = scrape_jobs(company_name,industry)
# # Export the job data to a JSON file
# output_file = "jobs.json"
# with open(output_file, "w", encoding="utf-8") as f:
#     json.dump(jobs, f, ensure_ascii=False, indent=4)
# print(f"Job data exported to {output_file}")
