import psycopg2
from psycopg2 import sql

# PostgreSQL database credentials
DB_CONFIG = {
    "dbname": "job_trends",
    "user": "myuser",
    "password": "password",
    "host": "localhost",  # Change if using a remote database
    "port": "5432"        # Default PostgreSQL port
}



# Connect to PostgreSQL
def connect_db():
    return psycopg2.connect(**DB_CONFIG)

# Create the jobs table if it doesn't exist
def create_table():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id SERIAL PRIMARY KEY,
            title TEXT,
            company_name TEXT NOT NULL,
            industry TEXT NOT NULL,
            posting_date DATE,
            link TEXT ,
            job_description TEXT 
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# Insert multiple job entries into the table
def insert_jobs(jobs):
    conn = connect_db()
    cur = conn.cursor()
    
    insert_query = """
        INSERT INTO jobs (title, company_name, industry, posting_date, link, job_description) 
        VALUES (%s, %s, %s, %s, %s, %s);
    """

    # Prepare data for bulk insert
    job_values = [
        (
            job["Title"],
            job["company_name"],
            job["industry"],
            None if job["Posting_Data"] == "N/A" else job["Posting_Data"],  # Convert "N/A" to NULL
            job["Link"],
            job["Job_Description"]
        )
        for job in jobs
    ]

    # Execute batch insertion
    cur.executemany(insert_query, job_values)

    conn.commit()
    cur.close()
    conn.close()


# Run the script
# create_table()  

