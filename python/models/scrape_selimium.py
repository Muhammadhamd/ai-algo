from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
import time


def scrape_fam_properties_blog(selectors):
    site_url = selectors["siteURL"]
    parent_selector = selectors["selectors"]["parent"]
    link_selector = selectors["selectors"]["target"]["link_selector"]
    title_selector = selectors["selectors"]["target"]["title_selector"]
    next_page_selector = selectors["selectors"]["navigate"]["selector"]

    # Headless Chrome setup
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(options=chrome_options)

    all_articles = []

    try:
        driver.get(site_url)

        # Optionally close any cookie banners / overlays here:
        # try:
        #     close_button = driver.find_element(By.CSS_SELECTOR, ".cookie-close-selector")
        #     close_button.click()
        # except NoSuchElementException:
        #     pass

        while True:
            # Wait for page content to load
            time.sleep(2)

            # 1) Find all parent elements
            parents = driver.find_elements(By.CSS_SELECTOR, parent_selector)
            if not parents:
                print("No parent elements found; stopping.")
                break

            # 2) For each parent, extract link and title
            for parent in parents:
                try:
                    link_element = parent.find_element(By.CSS_SELECTOR, link_selector)
                    title_element = parent.find_element(By.CSS_SELECTOR, title_selector)

                    article_link = link_element.get_attribute("href")
                    article_title = title_element.get_attribute("title")

                    # Store or print the extracted info
                    print(article_title)
                    all_articles.append((article_title, article_link))
                except NoSuchElementException:
                    pass

            # 3) Try to find and click the "Next" pagination link
            try:
                # Wait explicitly for the next button to be clickable
                wait = WebDriverWait(driver, 10)
                next_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, next_page_selector))
                )

                # Scroll into view
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(1)

                # Use JavaScript click to avoid potential overlay interception
                driver.execute_script("arguments[0].click();", next_button)
                print("Next page button clicked.")
            except (NoSuchElementException, TimeoutException):
                # No more next button or timed out waiting for it
                print("No next page button found; finished pagination.")
                break
            except ElementClickInterceptedException as e:
                print(f"Click was intercepted: {e}")
                break

        # Print all collected articles
        for title, link in all_articles:
            print(f"Title: {title}\nLink: {link}\n---")

    finally:
        driver.quit()


def scrape_first_article_from_pages( selectors,page_limit=3):
    site_url = selectors["siteURL"]
    parent_selector = selectors["selectors"]["parent"]
    link_selector = selectors["selectors"]["target"]["link_selector"]
    title_selector = selectors["selectors"]["target"]["title_selector"]
    next_page_selector = selectors["selectors"]["navigate"]["selector"]

    # Headless Chrome setup
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(options=chrome_options)

    scraped_articles = []

    try:
        driver.get(site_url)
        current_page = 1

        while current_page <= page_limit:
            print(f"Scraping page {current_page}...")

            # Wait for the page content to load
            time.sleep(2)

            # Find the first parent element
            try:
                first_parent = driver.find_element(By.CSS_SELECTOR, parent_selector)

                # Extract the first article's link and title
                link_element = first_parent.find_element(By.CSS_SELECTOR, link_selector)
                title_element = first_parent.find_element(By.CSS_SELECTOR, title_selector)

                article_link = link_element.get_attribute("href")
                article_title = title_element.text

                scraped_articles.append((article_title, article_link))
                print(f"Page {current_page} - Title: {article_title}, Link: {article_link}")

            except NoSuchElementException:
                print(f"Could not find article on page {current_page}")
                break

            # Navigate to the next page
            try:
                wait = WebDriverWait(driver, 10)
                next_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, next_page_selector))
                )

                # Scroll into view and click the next button
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", next_button)
                print(f"Navigated to page {current_page + 1}")
            except (NoSuchElementException, TimeoutException):
                print("No next page button found; stopping.")
                break
            except ElementClickInterceptedException as e:
                print(f"Click intercepted: {e}")
                break

            # Increment the page count
            current_page += 1

        # Print all collected articles
        print("\nCollected Articles:")
        return scraped_articles

    finally:
        driver.quit()
