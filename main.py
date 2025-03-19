import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from seek_scrap import scrape_jobs
from psql_connection import create_table, insert_jobs

# Load industry CSV files
industries = {
    "Banking": "data/banking.csv",
    "Financial Services": "data/Financialservices.csv",
    "Government": "data/Governmentadminstration.csv",
    "Insurance": "data/Insurance.csv",
    "Healthcare": "data/Healthcare.csv",
    "Logistics": "data/LogisticsandTrans.csv",
    "Manufacturing": "data/Manufacturing.csv",
    "Oil and Energy": "data/Oilandenergy.csv",
    "Retail": "data/Retail.csv",
    "Technology": "data/Technology.csv",
    "Utilities": "data/Utilities.csv",
}

# Function to scrape jobs for a given industry
def scrape_industry_jobs(industry_name, file_path):
    df = pd.read_csv(file_path)
    company_names = df['company_name'].tolist()

    industry_jobs = []
    for company in company_names:
        try:
            jobs = scrape_jobs(company, industry_name)
            industry_jobs.extend(jobs)
        except Exception as e:
            print(f"Error scraping {company} in {industry_name}: {e}")

    print(f"{industry_name}: {len(industry_jobs)} jobs scraped")  # Log industry-wise job count
    return industry_jobs

# Create database table
create_table()

# Multithreading to scrape jobs concurrently
all_jobs = []
with ThreadPoolExecutor(max_workers=10) as executor:
    future_to_industry = {executor.submit(scrape_industry_jobs, industry, path): industry for industry, path in industries.items()}
    
    for future in as_completed(future_to_industry):
        industry = future_to_industry[future]
        try:
            industry_jobs = future.result()
            all_jobs.extend(industry_jobs)
        except Exception as e:
            print(f"Error in scraping {industry}: {e}")

# Insert jobs into the database
insert_jobs(all_jobs)

print(f"Total jobs scraped: {len(all_jobs)}")
