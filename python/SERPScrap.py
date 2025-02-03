# import requests

# def google_global_search(api_key, query):
#     # Construct the API URL for a global search
#     search_url = "https://www.googleapis.com/customsearch/v1"
    
#     # Set up the parameters for the API request
#     params = {
#         'key': api_key,
#         'q': 'Guide to sewa',
#         'cx': '77407f8e68f2642cc',
#         'num': 10,                 # Number of results to return
#         'gl': 'AE',                # Set geolocation to UAE
#         'hl': 'en'   # Example CSE ID that searches the entire web
#         # Note: Replace with your own CSE ID that searches the web if you want.
#     }
    
#     # Send a GET request to the Google Custom Search API
#     response = requests.get(search_url, params=params)
#     print("response")
#     print(response.json())
#     # Check if the request was successful
#     if response.status_code == 200:
#         results = response.json().get('items', [])
        
#         # List to hold the scraped results
#         scraped_data = []

#         for item in results:
#             title = item.get('title', 'No title')
#             link = item.get('link', 'No link')
#             snippet = item.get('snippet', 'No snippet')
            
#             # Append the title, link, and snippet to the scraped data
#             scraped_data.append({
#                 'title': title,
#                 'link': link,
#                 'snippet': snippet
#             })

#         return scraped_data
#     else:
#         print("Failed to retrieve the webpage:", response.status_code)
#         return None

# # Example usage
#     # Your API Key
# api_key = "AIzaSyC6t6hRSKppW7b2BN74NSC2StoV5T3gY2U"  # Replace with your actual API key
# query = "Guide to SEWA"  

# results = google_global_search(api_key, query)
# print(results)
# if results:
#         for idx, result in enumerate(results, start=1):
#             print(f"{idx}. Title: {result['title']}\n   Link: {result['link']}\n   Snippet: {result['snippet']}\n")

from urllib.parse import urlparse, parse_qs
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, BackgroundTasks,Request
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import random
import asyncio
app = FastAPI()
def extract_base_url(full_url):
    parsed_url = urlparse(full_url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return base_url

def google_search_scraper(query , gl='AE' , range = 10):
    # Replace spaces in the query with '+'
    query = query.replace(' ', '+')
    url = f"https://www.google.com/search?q={query}&gl={gl}"  # Set language to English and location to UAE

    # User-agent to mimic a browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Make a request to Google
    response = requests.get(url, headers=headers)
    print(response)
    # Check for successful response
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find search result elements
        results = []
        rank = 1

        for g in soup.select('div.g'):
            # Check for "People also ask" and skip it
            people_ask_span = g.find('span', text="People also ask")
            if people_ask_span:
                print("skiped")
                continue  # Skip this result and move to the next one

            # Extract title and link
            title = g.find('h3')
            link_tag = g.find('a', href=True)
            print( title , link_tag)
            if title and link_tag:
                # Extract the actual URL from Google's redirect URL
                raw_link = link_tag['href']
                parsed_link = urlparse(raw_link)
                if 'url' in parse_qs(parsed_link.query):
                    actual_link = parse_qs(parsed_link.query)['url'][0]
                else:
                    actual_link = raw_link

                # Compare base URLs
                print({
                    'title': title.text,
                    'rank': rank,
                    'link': actual_link
                })
                if extract_base_url(actual_link) == "https://www.propertyfinder.ae":
                    results.append({
                        'title': title.text,
                        'rank': rank,
                        'link': actual_link
                    })
                rank += 1

        return results
    else:
        print("Error fetching results:", response.status_code)
        return []

# Usage example


# Print the results

async def random_delay():
    delay = random.randint(10, 40)
    await asyncio.sleep(delay)
    return delay  # optional: return the delay if you want to log it or for debugging



@app.post("/")
async def search(request: Request):
    # Parse the JSON body
    data = await request.json()
    keywords = data.get("keywords")
    print(keywords)
    gl = data.get("gl")
    range_value = data.get("range_value")
    
    results = []
    # Loop through each keyword dictionary and execute the search
    for item in keywords:
        keyword_id = item["_id"]
        keyword_text = item["keyword"]
        search_result = google_search_scraper(keyword_text, gl, range_value)
        
        # Append the result in the specified structure
        results.append({
            "id": keyword_id,
            "result": search_result
        })

        await random_delay()
    
    return JSONResponse(content=results)