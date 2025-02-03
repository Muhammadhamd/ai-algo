from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
async def fetch_page_content(url, headers):
    try:
        # Set up Selenium with headless Chrome and headers
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        chrome_options.add_argument("--no-sandbox")

        
        driver = webdriver.Chrome(options=chrome_options)

        # Fetch the page
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Get page source
        page_source = driver.page_source

        # Parse with BeautifulSoup
        
        soap = BeautifulSoup(page_source, 'html.parser')

        return soap
    except Exception as e:
        print(f"Error fetching page content: {e}")
        return None
    finally:
        driver.quit()
