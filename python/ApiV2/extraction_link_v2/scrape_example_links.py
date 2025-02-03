from fastapi import Query, Request, APIRouter
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from models.scrape_listing import scrapecontent
from models.clean_html import clean_html
import time
import requests
router = APIRouter()
def setup_selenium():
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    
    driver = webdriver.Chrome(options=options)
    return driver


async def fetch_full_html_with_selenium(url):
    """Fetch fully rendered HTML using Selenium."""
    driver = setup_selenium()
    try:
        driver.get(url)
        print(f"Fetching content from: {url}")
        # Wait for the body tag to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        return driver.page_source  # Return fully rendered HTML
    except Exception as e:
        print(f"Error fetching HTML with Selenium: {e}")
        return None
    finally:
        driver.quit()
@router.post("/")
async def get_html_body_content(request: Request):
    driver = setup_selenium()
    try:
        # Parse JSON from request body
        data = await request.json()
        url = data.get('siteURL')
        
        # response = requests.get(url , headers=headers)
        print(f"get result  before{url}")

        # response = await ScrapeBody(url)
        headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
         }
        response = await fetch_full_html_with_selenium(url)
        # response = asyncio.run(ScrapeBody())
        print(f"get result {url}")
        # Check if the response was successful

        # Parse the HTML content of the page with BeautifulSoup
        print("souping")
        soup = BeautifulSoup(response, 'html.parser')
        print("souping..sd")

        # Extract the body content
        body_content = soup.body

        if body_content:
            

            
             
            fetchContent = scrapecontent(str(body_content),data['selectors']['parent'],data['selectors']['target'])
            print(fetchContent)
            return { 'parent':data['selectors']['parent'] ,'target': data['selectors']['target'], 'navigate': data['selectors']['navigate'] , 'extracted': fetchContent}
        else:
            return "No body tag found in the HTML."
    except requests.RequestException as e:
        return f"An error occurred: {str(e)}"


# # Example usage
# if __name__ == '__main__':
#     # url = 'https://propertyfinder.ae/blog/all-posts'
#     # url = 'https://bayut.com/mybayut'
#     # url = 'https://blog.olx.com.pk/category/real-estate/'
#     # url = 'https://propsearch.ae/blog'
#     # url = 'https://www.squareyards.ae/blog/real-estate-news'
#     url = 'https://emirates.estate/articles-search/'
     
     

#     result = get_html_body_content(url)
#     parsed_url = urlparse(url)
#     domain_name = parsed_url.netloc.replace("www.", "")  # Remove 'www.' if present
#     filename = f"{domain_name}.json"
    
#     if isinstance(result, dict):  # Check if result is a dictionary
#         with open(f"{filename}", 'w') as json_file:
#             json.dump({"url": url, "content": result}, json_file, indent=4)
#     else:
#         print(result)