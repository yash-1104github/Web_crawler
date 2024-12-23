import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import csv
from fake_useragent import UserAgent


ua = UserAgent()
options = webdriver.ChromeOptions()
options.add_argument(f"user-agent={ua.random}")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

def extract_profile_data(url):
    driver.get(url)
    
    name_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.text-heading-xlarge")))
    summary_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "section.public-profile-edit__summary-section")))
    
   
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    name = name_element.text.strip()
    summary = summary_element.find('div', class_='text-body-medium').text.strip() if summary_element else ""
    
    return {
        "name": name,
        "job_title": soup.find('div', class_='text-body-medium').text.strip() if soup.find('div', class_='text-body-medium') else "",
        "location": soup.find('span', class_='text-body-small').text.strip() if soup.find('span', class_='text-body-small') else "",
        "summary": summary
    }

def extract_company_data(url):
    driver.get(url)
    
    company_name_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.company-name")))
    overview_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "section.public-profile-edit__summary-section")))
    

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    company_name = company_name_element.text.strip()
    overview = overview_element.find('div', class_='text-body-medium').text.strip() if overview_element else ""
    
    return {
        "company_name": company_name,
        "industry": soup.find('span', class_='company-industry').text.strip() if soup.find('span', class_='company-industry') else "",
        "location": soup.find('span', class_='company-location').text.strip() if soup.find('span', class_='company-location') else "",
        "overview": overview
    }

def handle_pagination(base_url, max_pages=5):
    all_data = []
    for page in range(max_pages):
        url = f"{base_url}&page={page}"
        print(f"Processing URL: {url}")
        
       
        data = extract_data(url)
        
        all_data.append(data)
        
       
        time.sleep(2)
    
    return all_data

def extract_data(url):
    
    if "in" in url:
        return extract_profile_data(url)
    else:
        return extract_company_data(url)

base_url_profiles = "https://www.linkedin.com/in/karan-singh-saluja-773908a9/"
base_url_companies = "https://www.linkedin.com/search/results/all/?fetchDeterministicClustersOnly=true&heroEntityKey=urn%3Ali%3Aorganization%3A422813&keywords=zomato&origin=RICH_QUERY_SUGGESTION&position=0&searchId=84059e4c-5c32-4b7d-9bb7-9fcb8fa94895&sid=iPB&spellCorrectionEnabled=false"

profiles_data = handle_pagination(base_url_profiles)
companies_data = handle_pagination(base_url_companies)

with open('profiles.csv', 'w', newline='') as csvfile:
    fieldnames = ['name', 'job_title', 'location', 'summary']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for data in profiles_data:
        writer.writerow(data)

with open('companies.csv', 'w', newline='') as csvfile:
    fieldnames = ['company_name', 'industry', 'location', 'overview']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for data in companies_data:
        writer.writerow(data)

print("Scraping completed successfully!")