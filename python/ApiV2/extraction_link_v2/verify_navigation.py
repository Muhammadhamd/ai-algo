import requests
from bs4 import BeautifulSoup
from fastapi import APIRouter, Request
from models.scrape_navigation import verify_navigation_model
from models.clean_html import clean_html
from AI_models.analize_navigation import openAiReqFindnavigation as AINavigation
from models.scrape_page import fetch_page_content
from models.scrape_selimium import scrape_first_article_from_pages

router = APIRouter()

async def main(url, headers, link_selector,clickable=False,max_attempts=3):
    current_url = url
    selector = link_selector['selectors']['navigate']
    isScrapedAgain = False
    urls = []
    attempt = 0

    while attempt < max_attempts:
        print('Fetching content...')
        soup = await fetch_page_content(current_url, headers)
        if soup:
          print('Content fetched, verifying navigation...')
          if not selector['clickable'] and selector['clickable']  != 2 :
            if (soup.body):
                print("body is availablee hhhs")
            next_page_url = verify_navigation_model(soup.body, selector)
            if next_page_url:
                print("the selector was correct")
                urls.append(next_page_url)
                current_url = next_page_url
            else:
                if attempt < max_attempts - 1:  # Allow retries with AI guidance
                    print('Navigation failed, consulting AI...')
                    print('cleaning code...')
                    cleancode = clean_html(soup.body , False,True)
                    print('cleaned...')
                    prompt = [
                        {"role": "user", "content": f"HTML: {cleancode}"},
                        {"role": "assistant", "content": f"{selector}"},
                        {"role": "user", "content": f"The provided selector did not work. Please analyze this HTML and suggest a correct selector"}
                    ]
                    ai_response = AINavigation(prompt)
                    isScrapedAgain = True
                    selector = ai_response  # Assuming AI returns this key
                    if not selector:
                        break  # If AI fails to provide a selector, stop trying
                else:
                    break  # No more retries left
          elif selector['clickable']  == 2:
              break
          else:
              extract_Articles = scrape_first_article_from_pages(link_selector)     
              urls = extract_Articles 
              break
        else:
            print('Failed to fetch content, stopping.')
            break  # Stop if unable to fetch page

        attempt += 1
    return {"theres": urls, "isScrapedAgain": isScrapedAgain, "final_selector": {"navigator":selector},"clickable":selector['clickable']}    

@router.post("/")
async def verify_navigate(request: Request):
    data = await request.json()
    url = data.get('siteURL')
    link_selector = data

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }


        # Call main function to process navigation
        
    verificationRes= await main(url, headers, link_selector)

    if verificationRes['theres']:
            print(verificationRes)
            return verificationRes
    else:
            return {"error": "No navigation found after AI consultation"}
