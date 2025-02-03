import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime
import os
import csv

app = FastAPI()

class Progress(BaseModel):
    current_page: int
    links_extracted: int
    total_links: int

progress = Progress(current_page=0, links_extracted=0, total_links=0)

def extract_links_bayut(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()  # Raise an error for bad status codes
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return [], None

    soup = BeautifulSoup(r.text, 'html.parser')

    # Find all <h3> tags with the specified class and extract links
    anchor_tags = soup.find_all('h2', class_='entry-title title post_title')
    links = [anchor_tag.find('a').get('href') for anchor_tag in anchor_tags]

    # Find the "next page" link
    next_page = soup.find('a', class_='next page-numbers')
    next_page_url = next_page.get('href') if next_page else None

    # Handle the specific case for page 468
    if url == "https://www.bayut.com/mybayut/page/468/":
        next_page_url = "https://www.bayut.com/mybayut/page/469/"
    elif url == "https://www.bayut.com/mybayut/page/472/":
        next_page_url = "https://www.bayut.com/mybayut/page/473/"
    elif url == "https://www.bayut.com/mybayut/page/474/":
        next_page_url = "https://www.bayut.com/mybayut/page/475/"

    return links, next_page_url

def extract_links_propertyfinder(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()  # Raise an error for bad status codes
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return [], None

    soup = BeautifulSoup(r.text, 'html.parser')

    # Find all <div> tags with the class 'col post-item' and extract links
    post_items = soup.find_all('div', class_='col post-item')
    links = [post_item.find('a').get('href') for post_item in post_items]

    # Find the "next page" link
    next_page = soup.find('a', class_='next page-number')
    next_page_url = next_page.get('href') if next_page else None

    return links, next_page_url

def send_webhook_notification(status_code, message, base_url, file_name=None):
    webhook_url = "http://4.213.60.40:4000/api/webhook/getextractLink"
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

def scrape_all_pages(starting_url, base_url):
    if not starting_url:
        print("URL not found")
        send_webhook_notification(500, "URL not found", base_url)
        return None

    all_links = set()
    url = starting_url

    if "bayut.com" in starting_url:
        extract_links = extract_links_bayut
    elif "propertyfinder.ae" in starting_url:
        extract_links = extract_links_propertyfinder
    else:
        print("Unsupported URL")
        send_webhook_notification(500, "Unsupported URL", base_url)
        return None

    try:
        page_count = int(starting_url.split('/')[-2])
    except ValueError:
        page_count = 1

    if not os.path.exists("LinkFiles"):
        os.makedirs("LinkFiles")

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"link-{timestamp}.txt"
    file_content = []

    while url:
        print(f"Processing page {page_count} ({url})...")
        try:
            links, next_page_url = extract_links(url)
            if not links:
                print(f"No links found on {url}")
                send_webhook_notification(500, f"No links found on {url}", base_url)
                break

            new_links = set(links) - all_links

            progress.current_page = page_count
            progress.links_extracted = len(new_links)
            progress.total_links = len(all_links) + len(new_links)

            for link in new_links:
                file_content.append([link])

            all_links.update(new_links)

            print(f"Done with {url}. Links extracted: {progress.links_extracted}. Total links: {progress.total_links}")
            if next_page_url is None:
                break
            url = next_page_url
            page_count += 1

        except Exception as e:
            print(f"Error while processing {url}: {e}")
            send_webhook_notification(500, f"Error processing {url}: {e}", base_url)
            break

    with open(f"LinkFiles/{file_name}", mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Links"])
        writer.writerows(file_content)

    send_webhook_notification(200, "Successfully saved links.", base_url, file_name)
@app.get("/{encoded_url:path}")
async def start_scraping(encoded_url: str, background_tasks: BackgroundTasks):
    print(encoded_url, "this is base url +++++++++++++==")
    UpdURL = "https://" + encoded_url
    base_url = unquote(UpdURL)
    if not base_url:
        raise HTTPException(status_code=404, detail="URL not found")

    print(base_url, "this is base url encoded +++++++++++++==")

    # Validate if the URL is supported
    if "bayut.com" in base_url:
            background_tasks.add_task(scrape_all_pages, base_url, base_url)

    elif "propertyfinder.ae" in base_url:
            background_tasks.add_task(scrape_all_pages, base_url, base_url)

    else:
        raise HTTPException(status_code=400, detail="Unsupported URL")

    # Start the scraping process in the background

    return {"status": "Task started", "message": "Scraping process has started."}
@app.get("/progress")
async def get_progress():
    return progress
