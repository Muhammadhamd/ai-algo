import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime
import os
import csv
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry 
import html

app = FastAPI()

# Local folders
link_files_folder = "LinkFiles"
blogs_folder = "BlogsData"

class CsvProgress(BaseModel):
    current_link: int
    total_links: int
    csv_rows_written: int

csv_progress = CsvProgress(current_link=0, total_links=0, csv_rows_written=0)








# Function to create a session with retries
def create_session():
    session = requests.Session()
    retry = Retry(
        total=5,
        read=5,
        connect=5,
        backoff_factor=0.3
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

session = create_session()

# Function to extract content from Bayut
def extract_content_bayut(url):
    response = session.get(url)
    response.encoding = 'utf-8'
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    title = soup.find('h1', class_='entry-title').text.strip() if soup.find('h1', class_='entry-title') else "no title"
    publish_date = soup.find('div', class_='publishing-date').text.strip().replace('Published: ', '') if soup.find('div', class_='publishing-date') else "no date"
    meta_description = soup.find('meta', attrs={'name': 'description'})['content'] if soup.find('meta', attrs={'name': 'description'}) else "no description"
    canonical_link = soup.find('link', rel='canonical')['href'] if soup.find('link', rel='canonical') else "no link"

    article_content = []
    for element in soup.select('article .entry-content p, article .entry-content h1, article .entry-content h2, article .entry-content h3, article .entry-content h4, article .entry-content h5, article .entry-content ul, article .entry-content ol, article .entry-content li'):
        article_content.append(element.get_text(strip=True))
    article_content = ' '.join(article_content) if article_content else "no content"

    yoast_schema_graph = soup.find('script', class_='yoast-schema-graph yoast-schema-graph--main').string if soup.find('script', class_='yoast-schema-graph yoast-schema-graph--main') else "no schema graph"

    title = html.unescape(title)
    publish_date = html.unescape(publish_date)
    meta_description = html.unescape(meta_description)
    canonical_link = html.unescape(canonical_link)
    article_content = html.unescape(article_content)
    yoast_schema_graph = html.unescape(yoast_schema_graph)

    data = {
        "Title": title,
        "Publish Date": publish_date,
        "Meta Description": meta_description,
        "Canonical Link": canonical_link,
        "Article Content": article_content,
        "Yoast Schema Graph": yoast_schema_graph
    }

    return data

# Function to extract content from Property Finder
def extract_content_property_finder(url):
    try:
        r = session.get(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')

        title_tag = soup.find("h1")
        date_tag = soup.find("p", class_="post-date")
        content_tag = soup.find(class_="entry-content")
        meta_description_tag = soup.find("meta", {"name": "description"})
        canonical_url_tag = soup.find("link", {"rel": "canonical"})
        yoast_schema_graph_tag = soup.find("script", {"class": "yoast-schema-graph", "type": "application/ld+json"})

        title = title_tag.text.strip() if title_tag else 'N/A'
        date = date_tag.text.strip() if date_tag else 'N/A'
        content = content_tag.get_text(strip=True) if content_tag else 'N/A'
        meta_description = meta_description_tag["content"] if meta_description_tag else 'N/A'
        canonical_url = canonical_url_tag["href"] if canonical_url_tag else 'N/A'
        yoast_schema_graph = yoast_schema_graph_tag.string.strip() if yoast_schema_graph_tag else 'N/A'

        data = {
            "Title": title,
            "Publish Date": date,
            "Meta Description": meta_description,
            "Canonical Link": canonical_url,
            "Article Content": content,
            "Yoast Schema Graph": yoast_schema_graph
        }
    except Exception as e:
        print(f"Error processing {url}: {e}")
        data = {
            "Title": 'N/A',
            "Publish Date": 'N/A',
            "Meta Description": 'N/A',
            "Canonical Link": 'N/A',
            "Article Content": 'N/A',
            "Yoast Schema Graph": 'N/A'
        }

    return data

# Function to generate CSV
def generate_csv(formatted_links, file, base_url, refLinkId):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    csv_file_name = f"{os.path.splitext(file)[0]}-{timestamp}.csv"
    print(f"{file},file ka naaammmmmmmm1")
    all_data = []
    total_links = len(formatted_links)
    csv_progress.total_links = total_links

    for idx, url in enumerate(formatted_links):
        try:
            if "bayut.com" in url:
                data = extract_content_bayut(url)
            elif "propertyfinder.ae" in url:
                data = extract_content_property_finder(url)
            else:
                continue
            
            # Check if required fields (Title and Meta Description) are present
            if data["Title"] != "no title" and data["Meta Description"] != "no description":
                all_data.append(data)
            else:
                print(f"Skipping {url} due to missing Title or Meta Description.")
        except Exception as e:
            print(f"Error processing {url}: {e}")

        # Update progress
        csv_progress.current_link = idx + 1
        csv_progress.csv_rows_written = len(all_data)
        print(f"Processed {csv_progress.current_link}/{csv_progress.total_links} links. Rows written: {csv_progress.csv_rows_written}")

    # Create the CSV content
    csv_file_path = os.path.join(blogs_folder, csv_file_name)
    os.makedirs(blogs_folder, exist_ok=True)
    print(f"{file},file ka naaammmmmmmmbefore2")
    linkFileName = file;
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ["Title", "Publish Date", "Meta Description", "Canonical Link", "Article Content", "Yoast Schema Graph"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_data)
    print(f"{file},file ka naaammmmmmmm2")

    # Send a webhook notification to the Node.js server
    webhook_url = "https://nodejs-server-brgrfqfra5bcf5ff.eastus-01.azurewebsites.net/api/webhook/saveCSVfile"
    payload = {
        "Message": "Data extraction and storage complete.",
        "fileName": csv_file_name,  # This is the file name, not the file object
        "refLinkId": refLinkId,
        "refFileName": linkFileName  # Use the file name instead of the file object
    }
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        print("Webhook notification sent successfully.")
    except requests.RequestException as e:
        print(f"Error sending webhook notification: {e}")
@app.get("/{file}")
async def start_csv_generation(file: str, refLinkId: str, background_tasks: BackgroundTasks):
    link_file_path = os.path.join(link_files_folder, file)
    
    if not os.path.exists(link_file_path):
        raise HTTPException(status_code=404, detail="Link file not found")

    with open(link_file_path, 'r', encoding='utf-8') as f:
        link_file_content = f.read()
    
    formatted_links = link_file_content.splitlines()
    base_url = ""  # Set base_url if necessary or remove if not needed
    
    # Start the CSV generation process in the background
    background_tasks.add_task(generate_csv, formatted_links, file, base_url, refLinkId)

    return {"status": "Task started", "message": "CSV generation process has started."}

@app.get("/csv_progress")
async def get_csv_progress():
    return csv_progress


@app.get("/progress")
async def get_progress():
    return progress
