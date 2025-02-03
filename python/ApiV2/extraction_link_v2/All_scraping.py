from fastapi import FastAPI, HTTPException, Request ,BackgroundTasks
import requests
from bs4 import BeautifulSoup
import csv
from typing import List, Dict
from models.scrape_page import fetch_page_content
from models.scrape_listing import scrapecontent
from models.scrape_navigation import verify_navigation_model
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import asyncio
from urllib.parse import urlparse
import os
app = FastAPI()


def write_to_csv(data: List[Dict], filename: str):
    with open(filename, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for item in data:
            writer.writerow([item['title'], item['url']])

async def scrape_with_selenium(url, selectors, csv_filename):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    import asyncio

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        results = []

        while True:
            print(f"Scraping page: {url}")

            # Extract articles on the page
            try:
                parent_elements = driver.find_elements(By.CSS_SELECTOR, selectors["parent"])
                for parent in parent_elements:
                    try:
                        link_element = parent.find_element(By.CSS_SELECTOR, selectors["target"]["link_selector"])
                        title_element = parent.find_element(By.CSS_SELECTOR, selectors["target"]["title_selector"])
                        article_link = link_element.get_attribute("href")
                        article_title = title_element.text
                        results.append({"title": article_title, "url": article_link})
                    except Exception as e:
                        print(f"Error extracting article: {e}")
            except Exception as e:
                print(f"Error finding parent elements: {e}")

            # Write results to CSV
            write_to_csv(results, csv_filename)

            # Find and navigate to the next page
            if selectors["navigate"]['clickable'] == 2:
                print("Navigation type 2 detected. Exiting...")
                break

            if selectors["navigate"]['clickable'] == 1:
                try:
                    next_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selectors["navigate"]["selector"]))
                    )
                    next_button.click()
                    await asyncio.sleep(2)  # Wait for page load
                except Exception:
                    print("No next button found or unable to navigate further.")
                    break

            elif selectors["navigate"]['clickable'] == 0:
                print("Navigation type 0 detected. Fetching next page by href...")
                try:
                    next_url_element = driver.find_element(By.CSS_SELECTOR, selectors["navigate"]["selector"])
                    next_url = next_url_element.get_attribute("href")
                    if next_url and next_url != url:
                        driver.get(next_url)
                        print(next_url)
                        await asyncio.sleep(2)
                    else:
                        print("No valid next URL found or already on the last page.")
                        break
                except Exception:
                    print("No next URL or navigation selector found.")
                    break
            else:
                print("Unsupported navigation type.")
                break

        return results
    finally:
        driver.quit()




def send_webhook_notification(status_code, message, base_url, file_name=None):
    webhook_url = "http://localhost:4000/api/webhook/getextractLink"
    payload = {
        "message": message,
        "statusCode": status_code,
        "respon": {
            "fileName": file_name,
            "site_link": base_url
        }
    }
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        print("Webhook notification sent successfully.")
    except requests.RequestException as e:
        print(f"Error sending webhook notification: {e}")

async def scrape_task(url, selectors, csv_filename):
    navigation_selector = selectors["navigate"]
    results = []

    if navigation_selector["clickable"]:  # Use Selenium for JS-based navigation
        print("Using Selenium for JS-based navigation...")
    results = await scrape_with_selenium(url, selectors, csv_filename)

    # Send webhook notification upon task completion
    send_webhook_notification(200, "Scraping process completed.",url, csv_filename)

@app.post("/")
async def scrape_endpoint(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    url = data["siteURL"]
    selectors = data["selectors"]
    navigation_selector = selectors["navigate"]
    directory = "./database/BlogsData/"
    os.makedirs(directory, exist_ok=True)

    # Construct the CSV file path
    csv_filename = os.path.join(directory, f"{urlparse(url).netloc.replace('.', '_')}_scraped_data.csv")

    # Initialize CSV file with headers if it doesn't exist
    with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'url'])  # Write headers

    # Schedule the scraping task in the background
    background_tasks.add_task(scrape_task, url, selectors, csv_filename)

    return {"status": "Task started", "message": "Scraping process has started."}
