import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urlparse
from models.scrape_listing import scrapecontent
from models.markdown import html_filter_keep_headings_links
from models.markdown import clean_navigation

# import asyncio
# from crawl4ai import AsyncWebCrawler
from crawl4ai import AsyncWebCrawler
from fastapi import  Query
from fastapi import APIRouter
from datetime import datetime
from fastapi import APIRouter, Query
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import asyncio
from pydantic import BaseModel
router = APIRouter()
import openai

def setup_selenium():
    """Set up and return a headless Selenium WebDriver instance."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)


def openAiReq_Get_Listing(prompt=False):
  client = openai.Client(api_key='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')
  class MathReasoning(BaseModel):
    card_selector: str
  class parent(BaseModel):
    parent_selector: str
 
  current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  print(current_time)

  messages = [
   
     {
        "role": "system",
        "content": f""""
        Current attempt time: {current_time}
            You will be provided with unstractured Html blog listing page code and you have to analize the code and return css or id selector that target the article's listing container, to find the selector for articles listing container here is hint for you , there will be many articles card in listing container
        """
        
    },
          {
        "role": "user",
        "content": """
            "Important:\n"
            "- The selector should target ONLY the (articles/blogs/post) listing container."\n
            "- Recheck every time that the Selector you choose will target the listing container ."\n
            "- Do not include explanations or additional fields."\n
            "- The selector must be a valid CSS or ID."\n
            "- only return the selector that are valid and available in provided HTML DOM."\n
            "- Thoroughly analyze the HTML, but return only the JSON object with 'parent_selector'."
"""
        
    },
    {
        "role": "assistant",
        "content": (
            "I understand. Please provide the HTML and I will return the JSON object with the "
            "'parent_selector' that targets only blogs listing container"
        )
    }
    
#  
]
  if prompt:
        messages.extend(prompt)
        stream = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_schema",
        "json_schema": {
        "name": "listing_container",  # Required name for the schema
        "schema": parent.schema()  # Use the schema from the Pydantic model
    }
                         },
        messages=messages,
        
        temperature=1.0,
    )

  return json.loads(stream.choices[0].message.content)
    
def openAiReq_Get_Listing_Markdown(prompt=False):
  client = openai.Client(api_key='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')

  class parent(BaseModel):
    parent_selector: str
 
  current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  print(current_time)

  messages = [
   
     {
        "role": "system",
        "content": """"
        Current attempt time: {current_time}
            You will be provided with Markdown of blog listing page and you have to analize the Markdown and return css or id selector that target the article's listing container, to find the selector for articles listing container here is instruction related to markdown for you.\n
             1. [] this square brackets represent text inside them \n
2. # represent the heading level # for h1 , ## for h2 and as on\n
3. ()represent the link\n
4. {""} this curly brackts contain classes and ids that are applied on that element\n
4 div{} this represnt the parent container of that elements \n
              
             
        """
        
    },
          {
        "role": "user",
        "content": """
        
\"Important:\\n\"
\"- The selector should target ONLY the (articles/blogs/post) main listing container **that has the most articles or blogs**.\\n\"
\"- Recheck every time that the Selector you choose will target the correct listing container.\\n\"
\"- Do not include explanations or additional fields.\\n\"
\"- The selector must be a valid CSS or ID.\\n\"
\"- Choose the listing div that has more blogs listed always and remember the provided selector can only target the blogs listed under that div so make sure you provided the correct selector that select main listing div and ignore other listings like most popular, features, top, recommended etc.\\n\"
\"- Only return the selector that is valid and available in provided Markdown.\\n\"
\"- Thoroughly analyze the Markdown, but return only the JSON object with 'parent_selector'.\"
"""
        
    },
    {
        "role": "assistant",
        "content": (
            "I understand. Please provide the Markdown and I will return the JSON object with the "
            "'parent_selector' that targets only blogs listing container"
        )
    },
    

]
  if prompt:
        if isinstance(prompt, tuple):
          prompt = list(prompt)
        messages.extend(prompt)
        messages.extend({
           "role":"user",
           "content":"do not target featured posts",
        })
        stream = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_schema",
        "json_schema": {
        "name": "listing_container",  # Required name for the schema
        "schema": parent.schema()  # Use the schema from the Pydantic model
    }
                         },
        messages=messages,
        
        temperature=1.0,
    )

  return json.loads(stream.choices[0].message.content)
    
def openAiReq_Get_Parent(prompt=False):
  client = openai.Client(api_key='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')
  class MathReasoning(BaseModel):
    card_selector: str
 # {
    #     "role": "system",
    #     "content": """"
    #         I'm an expert HTML analyst AI. My job is to analyze any provided HTML and focus on blogs listing Container\n
    #         - After I found the container that listing all blogs I will analize common and targeted class or id using in every blog's card.\n
    #         - Next I will return the specified class or id that are used in all blogs card.\n

    #          "Example JSON response format:\n\n"
    #         {\n"
    #         "    \"parent_selector\": \"div.article-listing div.article-card\"\n"
    #         "}\n\n"
    #     """
        
    # },
        #    {
#         "role": "user",
#         "content": """
#             "Important:\n"
#             "- The selector should target ONLY the card of articles/blogs/post in a listing container."\n
#             "- Recheck every time that the Selector you choose will target the blog's card individualy."\n
#             "- Do not include explanations or additional fields."\n
#             "- The selector must be a valid CSS or ID."\n
#             "- Thoroughly analyze the HTML, but return only the JSON object with 'parent_selector'."
# """
        
#     },
#     {
#         "role": "assistant",
#         "content": (
#             "I understand. Please provide the HTML and I will return the JSON object with the "
#             "'parent_selector' that targets only the card of article, post, or blog individually."
#         )
#     }
  current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  print(current_time)

  messages = [
   
     {
        "role": "system",
        "content": f""""
        Current attempt time: {current_time}
            You will be provided with unstractured Html blogs listing Container code and you have to analize the code and return css or id selector that target every blog's card individually
        """
        
    },
    
#  
]
  if prompt:
        messages.extend(prompt)
        stream = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_schema",
        "json_schema": {
        "name": "MathReasoningSchema",  # Required name for the schema
        "schema": MathReasoning.schema()  # Use the schema from the Pydantic model
    }
                         },
        messages=messages,
        
        temperature=0.4,
    )

  return json.loads(stream.choices[0].message.content)


def openAiReq_Get_Parent_Markdown(prompt=False):
  client = openai.Client(api_key='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')
  class MathReasoning(BaseModel):
    card_selector: str
 # 
  current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  print(current_time)

  messages=[
    {
      "role": "system",
      "content": [
        {
          "type": "text",
          "text": "Analyze the provided structured Markdown of blog listings to identify and return a CSS or ID selector that targets each blog's card individually. The selector should be simple, correct, and focus on the listing container with the most blog cards.\n\n# Output Format\n\nThe response should be in JSON format as follows:\n```\ncard_selector: {\"e.g .blog etc\"}\n```\n\nMake sure the selector directly targets the card of the blog."
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": " <body class=\"home blog topic- body-class- text_posts_unbordered no_sitetitle_in_menu show_menu_circle_idicator sliding_sidebar_inactive\" style=\"padding-top: 0px; \npadding-bottom: 0px;\"><div class=\"site\" id=\"page\"><div class=\"site_main_container\"><header class=\"site_header\"><div class=\"header_nav_wrapper\"><div class=\"header_nav\"><div class=\"bayut_top_nav\"><div><div class=\"bayut_logo\"><a href=\"https://www.bayut.com/\" rel=\"bayut\"></a></div><div class=\"menu-bayut-property-menu-container\"><ul class=\"menu\" id=\"menu-bayut-property-menu\"><li class=\"property-dropdown menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children menu-item-747434\" id=\"menu-item-747434\"><a href=\"#\"></a><ul class=\"sub-menu\"><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-747435\" id=\"menu-item-747435\"><a href=\"https://www.bayut.com/area-guides/\"></a></li><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-747436\" id=\"menu-item-747436\"><a href=\"https://www.bayut.com/buildings/\"></a></li><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-747437\" id=\"menu-item-747437\"><a href=\"https://www.bayut.com/schools/\"></a></li></ul></li></ul></div><div class=\"brand\"><a href=\"https://www.bayut.com/mybayut/\" rel=\"home\"></a></div><div class=\"menu-bayut-product-menu-container\"><ul class=\"menu\" id=\"menu-bayut-product-menu\"><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-100424\" id=\"menu-item-100424\"><a href=\"https://www.bayut.com/floorplans/\"></a></li><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-100425\" id=\"menu-item-100425\"><a href=\"https://www.bayut.com/companies/\"></a></li><li class=\"get-in-touch-modal menu-item menu-item-type-custom menu-item-object-custom menu-item-747440\" id=\"menu-item-747440\"><a href=\"#get_in_touch_modal\" rel=\"modal:open\"></a></li><li class=\"lang-item lang-item-8187 lang-item-ar lang-item-first menu-item menu-item-type-custom menu-item-object-custom menu-item-100426-ar\" id=\"menu-item-100426-ar\"><a href=\"https://www.bayut.com/mybayut/ar/\" hreflang=\"ar\" \nlang=\"ar\"></a></li></ul></div></div></div><div><div class=\"main_menu\"><ul class=\"navbar\" id=\"top-menu\"><li class=\"tips-menu menu-item menu-item-type-custom menu-item-object-custom menu-item-11952 default_menu\" id=\"menu-item-11952\"><a href=\"/mybayut/tips/\"></a></li><li class=\"pulse-menu menu-item menu-item-type-custom menu-item-object-custom menu-item-11953 default_menu\" id=\"menu-item-11953\"><a href=\"/mybayut/pulse/\"></a></li><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-11993 default_menu\" id=\"menu-item-11993\"><a href=\"/mybayut/my-home/\"></a></li><li class=\"genz-menu menu-item menu-item-type-taxonomy menu-item-object-category menu-item-61607 default_menu\" id=\"menu-item-61607\"><a href=\"https://www.bayut.com/mybayut/gen-z/\"></a></li><li class=\"rules-menu menu-item menu-item-type-taxonomy menu-item-object-category menu-item-61606 default_menu\" id=\"menu-item-61606\"><a href=\"https://www.bayut.com/mybayut/rules-regulations/\"></a></li><li class=\"market-trends-menu menu-item menu-item-type-custom menu-item-object-custom menu-item-11954 default_menu\" id=\"menu-item-11954\"><a href=\"/mybayut/market-trends/\"></a></li><li class=\"partners-menu menu-item menu-item-type-taxonomy menu-item-object-category menu-item-61608 default_menu\" id=\"menu-item-61608\"><a href=\"https://www.bayut.com/mybayut/our-partners/\"></a></li><li class=\"bayut-after-hours-menu menu-item menu-item-type-taxonomy menu-item-object-category menu-item-12598 default_menu\" id=\"menu-item-12598\"><a href=\"https://www.bayut.com/mybayut/bayut-after-hours/\"></a></li></ul></div><div class=\"header_controls\"><a class=\"header_control_wrapper blog-link\" href=\"https://www.bayut.com/mybayut/\"></a><div class=\"header_sliding_sidebar_control header_control_wrapper\"><a class=\"sliding_sidebar_button\" href=\"#\" id=\"user_control_icon\"></a></div></div></div></div></div></header><main class=\"site-content\" id=\"content\"><section class=\"main_content_area blog_index_area gridsidebar_main_content_container\" id=\"primary\"><h4 class=\"page-title screen-reader-text entry-title\"></h4><div class=\"homepage-featured-trending-wrapper\"><div class=\"homepage-featured-posts featured-section\"><div class=\"featured-post-wrapper owl-carousel owl-theme owl-loaded owl-drag\"><div class=\"owl-stage-outer\"><div class=\"owl-stage\" style=\"transform: translate3d(-2935px, 0px, 0px); transition: 0.25s; width: 4696px;\"><div class=\"owl-item cloned\" style=\"width: 577px; margin-right: 10px;\"><div class=\"featured-post\"><a class=\"read-more\" href=\"https://www.bayut.com/mybayut/hot-property-launches-dubai-jan-2025/\" id=\"featured-post-799181\" title=\"Hot new property launches in Dubai for January 2025\"></a><div class=\"featured-post-content\"><a class=\"read-more\" href=\"https://www.bayut.com/mybayut/hot-property-launches-dubai-jan-2025/\" id=\"featured-post-title-799181\" title=\"Hot new property launches in Dubai for January 2025\"><h2 class=\"post-title\"></h2></a><div class=\"post-category-wrapper\"><div class=\"post_meta_container clearfix category-market-trends\"><div class=\"post_meta_info post_meta_row clearfix\"><span class=\"post_meta_item meta_item_category\"><a href=\"https://www.bayut.com/mybayut/market-trends/\" rel=\"category tag\"></a></span></div></div></div></div></div></div><div class=\"owl-item cloned\" style=\"width: 577px; margin-right: 10px;\"><div class=\"featured-post\"><a class=\"read-more\" href=\"https://www.bayut.com/mybayut/dubai-rental-market-report-2024/\" id=\"featured-post-796844\" title=\"Bayut’s 2024 Dubai Rental Market Report\"></a><div class=\"featured-post-content\"><a class=\"read-more\" href=\"https://www.bayut.com/mybayut/dubai-rental-market-report-2024/\" id=\"featured-post-title-796844\" title=\"Bayut’s 2024 Dubai Rental Market Report\"><h2 class=\"post-title\"></h2></a><div class=\"post-category-wrapper\"><div class=\"post_meta_container clearfix category-market-trends\"><div class=\"post_meta_info post_meta_row clearfix\"><span class=\"post_meta_item meta_item_category\"><a href=\"https://www.bayut.com/mybayut/market-trends/\" rel=\"category tag\"></a></span></div></div></div></div></div></div><div class=\"owl-item\" style=\"width: 577px; margin-right: 10px;\"><div class=\"featured-post\"><a class=\"read-more\" href=\"https://www.bayut.com/mybayut/dubai-sales-market-report-2024/\" id=\"featured-post-797238\" title=\"Bayut’s Dubai Sales Market Report for 2024\"></a><div class=\"featured-post-content\"><a class=\"read-more\" href=\"https://www.bayut.com/mybayut/dubai-sales-market-report-2024/\" id=\"featured-post-title-797238\" title=\"Bayut’s Dubai Sales Market Report for 2024\"><h2 class=\"post-title\"></h2></a><div class=\"post-category-wrapper\"><div class=\"post_meta_container clearfix category-market-trends\"><div class=\"post_meta_info post_meta_row clearfix\"><span class=\"post_meta_item meta_item_category\"><a href=\"https://www.bayut.com/mybayut/market-trends/\" rel=\"category tag\"></a></span></div></div></div></div></div></div><div class=\"owl-item\" style=\"width: 577px; margin-right: 10px;\"><div class=\"featured-post\"><a class=\"read-more\" href=\"https://www.bayut.com/mybayut/ghaf-woods-phase-2/\" id=\"featured-post-799295\" title=\"Development of the Week: Ghaf Woods Phase 2\"></a><div class=\"featured-post-content\"><a class=\"read-more\" href=\"https://www.bayut.com/mybayut/ghaf-woods-phase-2/\" id=\"featured-post-title-799295\" title=\"Development of the Week: Ghaf Woods Phase 2\"><h2 class=\"post-title\"></h2></a><div class=\"post-category-wrapper\"><div class=\"post_meta_container clearfix category-market-trends\"><div class=\"post_meta_info post_meta_row clearfix\"><span class=\"post_meta_item meta_item_category\"><a href=\"https://www.bayut.com/mybayut/market-trends/\" rel=\"category tag\"></a></span></div></div></div></div></div></div><div class=\"owl-item\" style=\"width: 577px; margin-right: 10px;\"><div class=\"featured-post\"><a class=\"read-more\" href=\"https://www.bayut.com/mybayut/hot-property-launches-dubai-jan-2025/\" id=\"featured-post-799181\" title=\"Hot new property launches in Dubai for January 2025\"></a><div class=\"featured-post-content\"><a class=\"read-more\" href=\"https://www.bayut.com/mybayut/hot-property-launches-dubai-jan-2025/\" id=\"featured-post-title-799181\" title=\"Hot new property launches in Dubai for January 2025\"><h2 class=\"post-title\"></h2></a><div class=\"post-category-wrapper\"><div class=\"post_meta_container clearfix category-market-trends\"><div class=\"post_meta_info post_meta_row clearfix\"><span class=\"post_meta_item meta_item_category\"><a href=\"https://www.bayut.com/mybayut/market-trends/\" rel=\"category tag\"></a></span></div></div></div></div></div></div><div class=\"owl-item active\" style=\"width: 577px; margin-right: 10px;\"><div class=\"featured-post\"><a class=\"read-more\" href=\"https://www.bayut.com/mybayut/dubai-rental-market-report-2024/\" id=\"featured-post-796844\" title=\"Bayut’s 2024 Dubai Rental Market Report\"></a><div class=\"featured-post-content\"><a class=\"read-more\" href=\"https://www.bayut.com/mybayut/dubai-rental-market-report-2024/\" id=\"featured-post-title-796844\" title=\"Bayut’s 2024 Dubai Rental Market Report\"><h2 class=\"post-title\"></h2></a><div class=\"post-category-wrapper\"><div class=\"post_meta_container clearfix category-market-trends\"><div class=\"post_meta_info \npost_meta_row clearfix\"><span class=\"post_meta_item meta_item_category\"><a href=\"https://www.bayut.com/mybayut/market-trends/\" rel=\"category tag\"></a></span></div></div></div></div></div></div><div class=\"owl-item cloned\" style=\"width: 577px; margin-right: 10px;\"><div class=\"featured-post\"><a class=\"read-more\" href=\"https://www.bayut.com/mybayut/dubai-sales-market-report-2024/\" id=\"featured-post-797238\" title=\"Bayut’s Dubai Sales Market Report for 2024\"></a><div class=\"featured-post-content\"><a class=\"read-more\" href=\"https://www.bayut.com/mybayut/dubai-sales-market-report-2024/\" id=\"featured-post-title-797238\" title=\"Bayut’s Dubai Sales Market Report for 2024\"><h2 class=\"post-title\"></h2></a><div class=\"post-category-wrapper\"><div class=\"post_meta_container clearfix category-market-trends\"><div class=\"post_meta_info post_meta_row clearfix\"><span class=\"post_meta_item meta_item_category\"><a href=\"https://www.bayut.com/mybayut/market-trends/\" rel=\"category tag\"></a></span></div></div></div></div></div></div><div class=\"owl-item cloned\" style=\"width: 577px; margin-right: 10px;\"><div class=\"featured-post\"><a class=\"read-more\" \nhref=\"https://www.bayut.com/mybayut/ghaf-woods-phase-2/\" id=\"featured-post-799295\" title=\"Development of the Week: Ghaf Woods Phase 2\"></a><div class=\"featured-post-content\"><a class=\"read-more\" href=\"https://www.bayut.com/mybayut/ghaf-woods-phase-2/\" id=\"featured-post-title-799295\" title=\"Development of the Week: Ghaf Woods Phase 2\"><h2 class=\"post-title\"></h2></a><div class=\"post-category-wrapper\"><div class=\"post_meta_container clearfix category-market-trends\"><div class=\"post_meta_info post_meta_row clearfix\"><span class=\"post_meta_item meta_item_category\"><a href=\"https://www.bayut.com/mybayut/market-trends/\" rel=\"category tag\"></a></span></div></div></div></div></div></div></div></div></div></div><div class=\"homepage-featured-posts trending-section\"><div class=\"featured-post-wrapper\"><div class=\"featured-post\"><a href=\"https://www.bayut.com/mybayut/smart-rental-index-dld/\" id=\"trending-post-798212\" title=\"Understanding the DLD Smart Rental Index\"></a><div class=\"featured-post-content\"><a href=\"https://www.bayut.com/mybayut/smart-rental-index-dld/\" id=\"trending-post-title-798212\" title=\"Understanding the DLD Smart Rental Index\"><h2 class=\"post-title\"></h2></a><div class=\"post-category-wrapper\"><div class=\"post_meta_container clearfix category-tips\"><div class=\"post_meta_info post_meta_row clearfix\"><span class=\"post_meta_item meta_item_category\"><a href=\"https://www.bayut.com/mybayut/tips/\" rel=\"category tag\"></a></span></div></div></div></div></div><div class=\"trending-post-sub-section\"><div class=\"featured-post\"><a href=\"https://www.bayut.com/mybayut/uae-public-holidays/\" id=\"trending-post-58482\" title=\"Vacations ahead! List of UAE public holidays for 2025\"></a><div class=\"featured-post-content\"><a href=\"https://www.bayut.com/mybayut/uae-public-holidays/\" \nid=\"trending-post-title-58482\" title=\"Vacations ahead! List of UAE public holidays for 2025\"><h2 class=\"post-title\"></h2></a><div class=\"post-category-wrapper\"><div class=\"post_meta_container clearfix category-pulse\"><div class=\"post_meta_info post_meta_row clearfix\"><span class=\"post_meta_item meta_item_category\"><a href=\"https://www.bayut.com/mybayut/pulse/\" rel=\"category tag\"></a></span></div></div></div></div></div><div class=\"featured-post\"><a href=\"https://www.bayut.com/mybayut/movies-uae-month/\" id=\"trending-post-335293\" title=\"Best movies hitting UAE cinemas in January 2025\"></a><div class=\"featured-post-content\"><a href=\"https://www.bayut.com/mybayut/movies-uae-month/\" id=\"trending-post-title-335293\" title=\"Best movies hitting UAE cinemas in January 2025\"><h2 class=\"post-title\"></h2></a><div class=\"post-category-wrapper\"><div class=\"post_meta_container clearfix category-pulse\"><div class=\"post_meta_info post_meta_row clearfix\"><span class=\"post_meta_item \nmeta_item_category\"><a href=\"https://www.bayut.com/mybayut/pulse/\" rel=\"category tag\"></a></span></div></div></div></div></div></div></div></div></div><div class=\"post_width_sidebar_row\"><div class=\"col8 sidebar_post_content_col\"><div class=\"grid_list grid_list_2_col myclass002\"><div class=\"grid_col col6\"><article class=\"blog_post_container customhentry post-689582 post type-post status-publish format-standard has-post-thumbnail hentry category-tips tag-asr-prayer-time-sharjah tag-athan-time-in-sharjah tag-azan-time-in-sharjah tag-fajr-prayer-time-in-sharjah tag-isha-prayer-time-in-sharjah tag-maghrib-prayer-time-in-sharjah tag-namaz-timings-in-sharjah tag-prayer-times-in-sharjah tag-prayer-times-in-sharjah-for-march-2024 tag-prayer-times-in-sharjah-uae tag-salah-timings-in-sharjah tag-sharjah-prayer-timing tag-tips tag-tips-sharjah bayut_topics-activity persona-locals-emiratis persona-muslims persona-sharjah\" id=\"post-689582\"><figure class=\"post_banner\"><a href=\"https://www.bayut.com/mybayut/prayer-time-sharjah/\"></a></figure><div class=\"post_body has_post_banner\"><div class=\"post_meta_info post_meta_row clearfix\"><span class=\"post_meta_item meta_item_category\"><a href=\"https://www.bayut.com/mybayut/tips/\" rel=\"category tag\"></a></span></div><div class=\"post_header\"><h3 class=\"entry-title title post_title\"><a href=\"https://www.bayut.com/mybayut/prayer-time-sharjah/\" rel=\"bookmark\"></a></h3></div></div></article></div><div class=\"grid_col col6\"><article class=\"blog_post_container customhentry post-175123 post type-post status-publish format-standard has-post-thumbnail hentry category-tips tag-abu-dhabi-muslim-prayer-times tag-abu-dhabi-prayer-time-calendar tag-abu-dhabi-prayer-time-schedule tag-asar-time-abu-dhabi tag-azan-time-abu-dhabi tag-daily-namaz-time-abu-dhabi tag-daily-namaz-times-in-abu-dhabi tag-dhuhr-namaz-time-abu-dhabi tag-dhuhr-time-abu-dhabi tag-fajr-prayer-times-abu-dhabi tag-fajr-time-abu-dhabi tag-friday-salat-time-abu-dhabi tag-how-long-is-jummah-prayer tag-isha-prayer-in-abu-dhabi tag-isha-prayer-timing-abu-dhabi tag-juma-prayer-time-in-abu-dhabi tag-latest-prayer-time-abu-dhabi tag-maghrib-prayer-timings-abu-dhabi tag-monthly-prayer-timings-in-abu-dhabi tag-namaz-time-in-abu-dhabi tag-pray-time-in-abu-dhabi tag-prayer-time-abu-dhabi tag-prayer-timings-in-abu-dhabi tag-salah-time-in-abu-dhabi tag-salat-times-abu-dhabi tag-tips tag-what-time-is-jummah-prayer-in-abu-dhabi persona-abu-dhabi persona-locals-emiratis persona-muslims\" id=\"post-175123\"><figure class=\"post_banner\"><a href=\"https://www.bayut.com/mybayut/prayer-time-abu-dhabi/\"></a></figure><div class=\"post_body has_post_banner\"><div class=\"post_meta_info post_meta_row clearfix\"><span class=\"post_meta_item meta_item_category\"><a href=\"https://www.bayut.com/mybayut/tips/\" rel=\"category tag\"></a></span></div><div class=\"post_header\"><h3 class=\"entry-title title post_title\"><a href=\"https://www.bayut.com/mybayut/prayer-time-abu-dhabi/\" rel=\"bookmark\"></a></h3></div></div></article></div><div class=\"grid_col col6\"><article class=\"blog_post_container customhentry post-109851 post type-post status-publish format-standard has-post-thumbnail hentry category-tips tag-1-liter-petrol-price-in-uae tag-change-in-uae-petrol-prices tag-crude-oil-price-in-dubai tag-current-petrol-price-in-uae tag-diesel-price-in-dubai tag-diesel-price-in-uae tag-dubai-petrol-price-per-litre-today tag-fuel-price-dubai tag-fuel-price-in-dubai tag-fuel-price-in-uae tag-fuel-prices-in-dubai tag-fuel-prices-in-the-uae tag-gas-price-in-dubai tag-gasoline-price-in-the-uae tag-gasoline-price-in-uae tag-latest-diesel-fuel-prices tag-latest-fuel-price-in-uae tag-latest-petrol-fuel-prices tag-latest-petrol-price-in-uae tag-new-petrol-price-in-uae \ntag-new-petrol-prices-in-uae tag-oil-price-in-dubai tag-one-litre-petrol-price-in-uae tag-petrol-new-price-in-the-uae tag-petrol-new-prices-in-uae tag-petrol-price-in-abu-dhabi tag-petrol-price-in-dubai tag-petrol-price-in-dubai-today tag-petrol-price-in-uae tag-petrol-price-in-uae-today tag-petrol-prices-in-dubai tag-petrol-prices-in-the-uae tag-petrol-rate-in-dubai tag-petrol-rate-in-uae tag-petrol-rates-in-uae tag-price-of-gasoline-in-uae tag-rate-of-petrol-in-uae tag-tips tag-uae-fuel-price tag-uae-fuel-prices tag-uae-petrol-price bayut_topics-travel persona-auto-market persona-motor-enthusiasts persona-uae\" id=\"post-109851\"><figure class=\"post_banner\"><a href=\"https://www.bayut.com/mybayut/petrol-prices-uae-update/\"></a></figure><div class=\"post_body has_post_banner\"><div class=\"post_meta_info post_meta_row clearfix\"><span class=\"post_meta_item meta_item_category\"><a href=\"https://www.bayut.com/mybayut/tips/\" rel=\"category tag\"></a></span></div><div class=\"post_header\"><h3 class=\"entry-title title post_title\"><a href=\"https://www.bayut.com/mybayut/petrol-prices-uae-update/\" rel=\"bookmark\"></a></h3></div></div></article></div><div class=\"grid_col col6\"><article class=\"blog_post_container customhentry post-111196 post type-post status-publish format-standard has-post-thumbnail hentry category-tips tag-5-times-prayer-time-in-dubai tag-adhan-time-in-dubai tag-asar-prayer-time-in-dubai tag-asr-prayer-time-dubai tag-current-prayer-time-in-dubai tag-dhuhr-prayer-time-in-dubai tag-dubai-prayer-times tag-fajr-prayer-in-dubai tag-friday-prayer-time-in-dubai tag-isha-prayer-time-in-dubai tag-juma-prayer-time-in-dubai tag-jumma-prayer-time-in-dubai tag-latest-prayer-timings-in-dubai tag-maghrib-prayer-in-dubai tag-maghrib-time-in-dubai tag-mosque-prayers-in-dubai tag-muslim-prayer-time-in-dubai tag-muslim-prayer-times-in-dubai tag-muslims-in-dubai tag-prayer-time-in-dubai-today tag-prayer-timings-in-dubai tag-salat-time-in-dubai \ntag-tips tag-what-is-the-prayer-time-in-dubai tag-what-time-is-isha-prayer-in-dubai tag-zuhr-prayer-time-in-dubai persona-arabs persona-dubai persona-muslims\" id=\"post-111196\"><figure class=\"post_banner\"><a href=\"https://www.bayut.com/mybayut/prayer-time-dubai/\"></a></figure><div class=\"post_body has_post_banner\"><div class=\"post_meta_info post_meta_row clearfix\"><span class=\"post_meta_item meta_item_category\"><a href=\"https://www.bayut.com/mybayut/tips/\" rel=\"category tag\"></a></span></div><div class=\"post_header\"><h3 class=\"entry-title title post_title\"><a href=\"https://www.bayut.com/mybayut/prayer-time-dubai/\" rel=\"bookmark\"></a></h3></div></div></article></div><div class=\"grid_col col6\"><article class=\"blog_post_container customhentry post-191009 post type-post status-publish format-standard has-post-thumbnail hentry category-tips tag-dubai-sunset-and-sunrise-times tag-dubai-sunset-time tag-sunrise tag-sunrise-in-dubai tag-sunrise-in-dubai-today tag-sunrise-time-in-dubai tag-sunset tag-sunset-in-dubai tag-sunset-time-in-dubai tag-what-time-is-sunrise-in-dubai tag-what-time-is-sunset-in-dubai bayut_topics-activity bayut_topics-outdoor persona-dubai persona-emiratis persona-misc\" id=\"post-191009\"><figure class=\"post_banner\"><a href=\"https://www.bayut.com/mybayut/sunrise-sunset-timings-dubai/\"></a></figure><div class=\"post_body has_post_banner\"><div class=\"post_meta_info post_meta_row clearfix\"><span class=\"post_meta_item meta_item_category\"><a href=\"https://www.bayut.com/mybayut/tips/\" rel=\"category tag\"></a></span></div><div class=\"post_header\"><h3 class=\"entry-title title post_title\"><a href=\"https://www.bayut.com/mybayut/sunrise-sunset-timings-dubai/\" rel=\"bookmark\"></a></h3></div></div></article></div><div class=\"grid_col col6\"><article class=\"blog_post_container customhentry post-689398 post type-post status-publish format-standard has-post-thumbnail hentry category-tips tag-asr-prayer-time-ras-al-khaimah tag-fajr-time-ras-al-khaimah tag-friday-prayer-time-in-ras-al-khaimah tag-isha-prayer-time-ras-al-khaimah tag-jummah-prayer-time-ras-al-khaimah tag-maghrib-time-ras-al-khaimah tag-namaz-time-in-ras-al-khaimah tag-namaz-timings-ras-al-khaimah tag-prayer-time-in-ras-al-khaimah tag-salah-time-ras-al-khaimah tag-tips bayut_topics-activity bayut_topics-things-to-do persona-ras-al-khaimah persona-uae\" id=\"post-689398\"><figure class=\"post_banner\"><a href=\"https://www.bayut.com/mybayut/prayer-times-ras-al-khaimah/\"></a></figure><div class=\"post_body has_post_banner\"><div class=\"post_meta_info post_meta_row clearfix\"><span class=\"post_meta_item meta_item_category\"><a href=\"https://www.bayut.com/mybayut/tips/\" rel=\"category tag\"></a></span></div><div class=\"post_header\"><h3 class=\"entry-title title post_title\"><a href=\"https://www.bayut.com/mybayut/prayer-times-ras-al-khaimah/\" rel=\"bookmark\"></a></h3></div></div></article></div><div class=\"dubai-transations-banner listings\"><div class=\"banner-wrapper\"><a href=\"https://www.bayut.com/property-market-analysis/sale/?utm_source=organic&amp;utm_medium=nexus&amp;utm_campaign=Bayut-Website-Banners-English\" target=\"_blank;\" title=\"Dubai Transactions\"></a></div></div><div class=\"grid_col col6\"><article class=\"blog_post_container customhentry post-690040 post type-post status-publish format-standard has-post-thumbnail hentry category-tips tag-asr-time-in-al-ain tag-azan-time-in-al-ain tag-dhuhr-time-in-al-ain tag-fajr-time-in-al-ain tag-isha-time-in-al-ain tag-maghrib-time-in-al-ain tag-namaz-timings-in-al-ain tag-prayer-time-al-ain-uae tag-prayer-time-in-al-ain tag-tips bayut_topics-activity persona-al-ain persona-arabs persona-muslims\" id=\"post-690040\"><figure class=\"post_banner\"><a href=\"https://www.bayut.com/mybayut/prayer-time-al-ain/\"></a></figure><div class=\"post_body has_post_banner\"><div class=\"post_meta_info post_meta_row clearfix\"><span class=\"post_meta_item meta_item_category\"><a href=\"https://www.bayut.com/mybayut/tips/\" rel=\"category tag\"></a></span></div><div class=\"post_header\"><h3 class=\"entry-title title post_title\"><a href=\"https://www.bayut.com/mybayut/prayer-time-al-ain/\" rel=\"bookmark\"></a></h3></div></div></article></div><div class=\"grid_col col6\"><article class=\"blog_post_container customhentry post-809752 post type-post status-publish format-standard has-post-thumbnail hentry category-market-trends tag-amazonia-residence tag-amazonia-residence-at-al-jaddaf-dubai tag-amazonia-residence-by-palladium tag-amazonia-residence-features-and-amenities tag-amazonia-residence-handover-date tag-amazonia-residence-location tag-amazonia-residence-master-plan tag-amazonia-residence-payment-plan tag-market-trends bayut_topics-buying-property bayut_topics-property bayut_topics-selling-property persona-dubai persona-market-trends persona-properties\" id=\"post-809752\"><figure class=\"post_banner\"><a href=\"https://www.bayut.com/mybayut/amazonia-residence/\"></a></figure><div class=\"post_body has_post_banner\"><div class=\"post_meta_info post_meta_row clearfix\"><span class=\"post_meta_item meta_item_category\"><a href=\"https://www.bayut.com/mybayut/market-trends/\" rel=\"category tag\"></a></span></div><div class=\"post_header\"><h3 class=\"entry-title title post_title\"><a href=\"https://www.bayut.com/mybayut/amazonia-residence/\" rel=\"bookmark\"></a></h3></div></div></article></div><div class=\"grid_col col6\"><article class=\"blog_post_container customhentry post-134724 post type-post status-publish format-standard has-post-thumbnail hentry category-tips tag-alternative-dubai-transport tag-best-way-to-get-to-the-shopping-malls-in-dubai tag-burjuman-bus-station tag-bus-stops-near-malls-in-dubai tag-cheapest-way-to-get-to-the-shopping-malls-in-dubai tag-city-centre-deira-bus-station tag-dubai-mall-shuttle tag-dubai-marina-mall-shuttle tag-dubai-outlet-mall-shuttle tag-how-to-get-to-the-dubai-mall tag-how-to-reach-malls-in-dubai tag-ibn-battuta-metro-bus-station tag-mall-of-the-emirates-bus-station tag-malls-in-dubai tag-malls-in-dubai-near-metro-stations tag-malls-in-dubai-with-bus-stops tag-malls-in-dubai-without-metro tag-reaching-al-ghurair-centre-by-bus tag-reaching-arabian-centre-by-bus tag-reaching-burjuman-mall-by-bus tag-reaching-city-centre-deira-by-bus tag-reaching-city-centre-mirdif-by-bus tag-reaching-dubai-festival-by-bus tag-reaching-dubai-mall-by-bus tag-reaching-dubai-outlet-mall-by-bus tag-reaching-ibn-battuta-mall-by-bus tag-reaching-madina-mall-by-bus tag-reaching-mall-of-the-emirates-by-bys tag-reaching-mercato-mall-by-bus tag-reaching-shopping-malls-in-dubai-via-bus tag-reaching-shopping-malls-in-dubai-via-taxi tag-reaching-shopping-malls-in-dubai-via-uber tag-reaching-wafi-mall-by-bus tag-taxi-stops-at-malls-in-dubai tag-transport-alternatives-in-dubai tag-ways-to-get-to-the-malls-in-dubai bayut_topics-mall bayut_topics-places-to-visit bayut_topics-public-transport persona-dubai persona-rta persona-shopaholics\" id=\"post-134724\"><figure class=\"post_banner\"><a href=\"https://www.bayut.com/mybayut/ways-to-get-to-dubai-malls/\"></a></figure><div class=\"post_body has_post_banner\"><div class=\"post_meta_info post_meta_row clearfix\"><span class=\"post_meta_item meta_item_category\"><a href=\"https://www.bayut.com/mybayut/tips/\" rel=\"category tag\"></a></span></div><div class=\"post_header\"><h3 class=\"entry-title title post_title\"><a href=\"https://www.bayut.com/mybayut/ways-to-get-to-dubai-malls/\" rel=\"bookmark\"></a></h3></div></div></article></div><div class=\"grid_col col6\"><article class=\"blog_post_container customhentry post-809810 post type-post status-publish format-standard has-post-thumbnail hentry category-market-trends tag-affordable-communities-to-rent-villas-in-sobha-hartland tag-buildings-to-rent-apartments-in-sobha-hartland tag-list-of-buildings-to-rent-flats-in-sobha-hartland tag-list-of-sub-communities-to-rent-houses-in-sobha-hartland tag-market-trends tag-popular-communities-to-rent-villas-in-sobha-hartland tag-rent-a-property-in-sobha-hartland tag-rent-properties-in-sobha-hartland tag-sub-communities-to-rent-villas-in-sobha-hartland bayut_topics-1-bed bayut_topics-2-bed bayut_topics-apartment bayut_topics-property bayut_topics-renting-property bayut_topics-studio bayut_topics-villa persona-dubai persona-properties persona-tenants\" id=\"post-809810\"><figure class=\"post_banner\"><a href=\"https://www.bayut.com/mybayut/rent-properties-sobha-hartland/\"></a></figure><div class=\"post_body has_post_banner\"><div class=\"post_meta_info post_meta_row clearfix\"><span class=\"post_meta_item meta_item_category\"><a href=\"https://www.bayut.com/mybayut/market-trends/\" rel=\"category tag\"></a></span></div><div class=\"post_header\"><h3 class=\"entry-title title post_title\"><a href=\"https://www.bayut.com/mybayut/rent-properties-sobha-hartland/\" rel=\"bookmark\"></a></h3></div></div></article></div></div><nav aria-label=\"Posts\" class=\"navigation pagination\" role=\"navigation\"><h2 class=\"screen-reader-text\"></h2><div class=\"nav-links\"><a class=\"page-numbers\" href=\"https://www.bayut.com/mybayut/page/2/\"></a><a class=\"page-numbers\" href=\"https://www.bayut.com/mybayut/page/3/\"></a><a class=\"page-numbers\" href=\"https://www.bayut.com/mybayut/page/605/\"></a><a class=\"next page-numbers\" href=\"https://www.bayut.com/mybayut/page/2/\"></a></div></nav></div><div class=\"default_widgets_container default_widgets_col col4\"><div class=\"widget_area\" id=\"listingpage_sidebar_widget\"><div class=\"widget_container widget_content intro_widget_content widget widget_text clearfix\" id=\"text-5\"><h4 class=\"widget_title title\"></h4><div class=\"textwidget\"><div class=\"sbi sbi_mob_col_3 sbi_tab_col_3 sbi_col_3 sbi_width_resp sbi_small\" data-cols=\"3\" data-colsmobile=\"3\" data-colstablet=\"3\" data-feedid=\"*2\" data-item-padding=\"5\" data-locatornonce=\"c07bf08696\" data-num=\"9\" data-nummobile=\"9\" data-postid=\"\" data-res=\"thumb\" data-sbi-flags=\"favorLocal\" data-sbi-index=\"1\" data-shortcode-atts='{\"feed\":\"2\"}' id=\"sb_instagram\" style=\"padding-bottom: 10px;\"><div id=\"sbi_images\" \nstyle=\"gap: 10px;\"><div class=\"sbi_item sbi_type_image sbi_had_error\" data-date=\"1738412285\" id=\"sbi_18294468835214257\"><div class=\"sbi_photo_wrap\"><a class=\"sbi_photo\" data-full-res=\"https://www.bayut.com/mybayut/wp-content/uploads/sb-instagram-feed-images/476050392_1136432301037790_3352308402899739407_nfull.jpg\" data-img-src-set='{\"d\":\"https:\\/\\/scontent-lhr6-2.cdninstagram.com\\/v\\/t51.2885-15\\/476050392_1136432301037790_3352308402899739407_n.jpg?stp=dst-jpg_e35_tt6&amp;_nc_cat=104&amp;ccb=1-7&amp;_nc_sid=18de74&amp;_nc_ohc=6ITQFvu9iNUQ7kNvgGiSPoH&amp;_nc_zt=23&amp;_nc_ht=scontent-lhr6-2.cdninstagram.com&amp;edm=ANo9K5cEAAAA&amp;oh=00_AYCns7QkML3ky5mHOfPJ4t0PuAooaUkf006hea5qYjx1EQ&amp;oe=67A45A2E\",\"150\":\"https:\\/\\/scontent-lhr6-2.cdninstagram.com\\/v\\/t51.2885-15\\/476050392_1136432301037790_3352308402899739407_n.jpg?stp=dst-jpg_e35_tt6&amp;_nc_cat=104&amp;ccb=1-7&amp;_nc_sid=18de74&amp;_nc_ohc=6ITQFvu9iNUQ7kNvgGiSPoH&amp;_nc_zt=23&amp;_nc_ht=scontent-lhr6-2.cdninstagram.com&amp;edm=ANo9K5cEAAAA&amp;oh=00_AYCns7QkML3ky5mHOfPJ4t0PuAooaUkf006hea5qYjx1EQ&amp;oe=67A45A2E\",\"320\":\"https:\\/\\/www.bayut.com\\/mybayut\\/wp-content\\/uploads\\/sb-instagram-feed-images\\/476050392_1136432301037790_3352308402899739407_nlow.jpg\",\"640\":\"https:\\/\\/www.bayut.com\\/mybayut\\/wp-content\\/uploads\\/sb-instagram-feed-images\\/476050392_1136432301037790_3352308402899739407_nfull.jpg\"}' href=\"https://www.instagram.com/p/DFh6h6bzq0c/\" rel=\"noopener nofollow noreferrer\" style=\"height: 110px; opacity: 1;\" target=\"_blank\"></a></div></div><div class=\"sbi_item sbi_type_carousel sbi_had_error\" data-date=\"1738389972\" id=\"sbi_18041506565347390\"><div class=\"sbi_photo_wrap\"><a class=\"sbi_photo\" data-full-res=\"https://www.bayut.com/mybayut/wp-content/uploads/sb-instagram-feed-images/475500766_1551948765507868_7667467467483688303_nfull.jpg\" data-img-src-set='{\"d\":\"https:\\/\\/scontent-lhr8-2.cdninstagram.com\\/v\\/t51.2885-15\\/475500766_1551948765507868_7667467467483688303_n.jpg?stp=dst-jpg_e35_tt6&amp;_nc_cat=101&amp;ccb=1-7&amp;_nc_sid=18de74&amp;_nc_ohc=6vLVpKvq1N0Q7kNvgGBURj8&amp;_nc_zt=23&amp;_nc_ht=scontent-lhr8-2.cdninstagram.com&amp;edm=ANo9K5cEAAAA&amp;oh=00_AYB4FZkCpIfU_utLYwYHGfiHTRFlVsSR4depGL0xoU3KXQ&amp;oe=67A476BA\",\"150\":\"https:\\/\\/scontent-lhr8-2.cdninstagram.com\\/v\\/t51.2885-15\\/475500766_1551948765507868_7667467467483688303_n.jpg?stp=dst-jpg_e35_tt6&amp;_nc_cat=101&amp;ccb=1-7&amp;_nc_sid=18de74&amp;_nc_ohc=6vLVpKvq1N0Q7kNvgGBURj8&amp;_nc_zt=23&amp;_nc_ht=scontent-lhr8-2.cdninstagram.com&amp;edm=ANo9K5cEAAAA&amp;oh=00_AYB4FZkCpIfU_utLYwYHGfiHTRFlVsSR4depGL0xoU3KXQ&amp;oe=67A476BA\",\"320\":\"https:\\/\\/www.bayut.com\\/mybayut\\/wp-content\\/uploads\\/sb-instagram-feed-images\\/475500766_1551948765507868_7667467467483688303_nlow.jpg\",\"640\":\"https:\\/\\/www.bayut.com\\/mybayut\\/wp-content\\/uploads\\/sb-instagram-feed-images\\/475500766_1551948765507868_7667467467483688303_nfull.jpg\"}' href=\"https://www.instagram.com/p/DFhP-Qxss9L/\" rel=\"noopener nofollow noreferrer\" style=\"height: 110px;\" target=\"_blank\"></a></div></div><div class=\"sbi_item sbi_type_image sbi_had_error\" data-date=\"1738332061\" id=\"sbi_17976200000802848\"><div class=\"sbi_photo_wrap\"><a class=\"sbi_photo\" data-full-res=\"https://www.bayut.com/mybayut/wp-content/uploads/sb-instagram-feed-images/475726986_997053188938283_1667796048753372441_nfull.jpg\" data-img-src-set='{\"d\":\"https:\\/\\/scontent-lhr6-1.cdninstagram.com\\/v\\/t51.2885-15\\/475726986_997053188938283_1667796048753372441_n.jpg?stp=dst-jpg_e35_tt6&amp;_nc_cat=109&amp;ccb=1-7&amp;_nc_sid=18de74&amp;_nc_ohc=61njSCDNYJ4Q7kNvgGENuNN&amp;_nc_zt=23&amp;_nc_ht=scontent-lhr6-1.cdninstagram.com&amp;edm=ANo9K5cEAAAA&amp;oh=00_AYAIhRrEKQIIrdptj3dyNZQQ1xElM7SiSf_gY_Gzt1AGig&amp;oe=67A44D4F\",\"150\":\"https:\\/\\/scontent-lhr6-1.cdninstagram.com\\/v\\/t51.2885-15\\/475726986_997053188938283_1667796048753372441_n.jpg?stp=dst-jpg_e35_tt6&amp;_nc_cat=109&amp;ccb=1-7&amp;_nc_sid=18de74&amp;_nc_ohc=61njSCDNYJ4Q7kNvgGENuNN&amp;_nc_zt=23&amp;_nc_ht=scontent-lhr6-1.cdninstagram.com&amp;edm=ANo9K5cEAAAA&amp;oh=00_AYAIhRrEKQIIrdptj3dyNZQQ1xElM7SiSf_gY_Gzt1AGig&amp;oe=67A44D4F\",\"320\":\"https:\\/\\/www.bayut.com\\/mybayut\\/wp-content\\/uploads\\/sb-instagram-feed-images\\/475726986_997053188938283_1667796048753372441_nlow.jpg\",\"640\":\"https:\\/\\/www.bayut.com\\/mybayut\\/wp-content\\/uploads\\/sb-instagram-feed-images\\/475726986_997053188938283_1667796048753372441_nfull.jpg\"}' href=\"https://www.instagram.com/p/DFfhhEuNVFF/\" rel=\"noopener nofollow noreferrer\" style=\"height: 110px;\" target=\"_blank\"></a></div></div><div class=\"sbi_item sbi_type_video sbi_had_error\" data-date=\"1738323651\" id=\"sbi_17865449691320626\"><div class=\"sbi_photo_wrap\"><a class=\"sbi_photo\" data-full-res=\"https://www.bayut.com/mybayut/wp-content/uploads/sb-instagram-feed-images/475481875_1335842247425427_8306176308965945275_nfull.jpg\" data-img-src-set='{\"d\":\"https:\\/\\/scontent-lhr8-2.cdninstagram.com\\/v\\/t51.29350-15\\/475481875_1335842247425427_8306176308965945275_n.jpg?stp=dst-jpg_e35_tt6&amp;_nc_cat=106&amp;ccb=1-7&amp;_nc_sid=18de74&amp;_nc_ohc=eyz15uhbnO8Q7kNvgG5op9u&amp;_nc_zt=23&amp;_nc_ht=scontent-lhr8-2.cdninstagram.com&amp;edm=ANo9K5cEAAAA&amp;_nc_gid=AgvY6R0whwmMHWd7_RPndk1&amp;oh=00_AYC95GrmTddxjKbx4_1wAGcSQUaqxJFyrbZfT_k8VacanA&amp;oe=67A47067\",\"150\":\"https:\\/\\/scontent-lhr8-2.cdninstagram.com\\/v\\/t51.29350-15\\/475481875_1335842247425427_8306176308965945275_n.jpg?stp=dst-jpg_e35_tt6&amp;_nc_cat=106&amp;ccb=1-7&amp;_nc_sid=18de74&amp;_nc_ohc=eyz15uhbnO8Q7kNvgG5op9u&amp;_nc_zt=23&amp;_nc_ht=scontent-lhr8-2.cdninstagram.com&amp;edm=ANo9K5cEAAAA&amp;_nc_gid=AgvY6R0whwmMHWd7_RPndk1&amp;oh=00_AYC95GrmTddxjKbx4_1wAGcSQUaqxJFyrbZfT_k8VacanA&amp;oe=67A47067\",\"320\":\"https:\\/\\/www.bayut.com\\/mybayut\\/wp-content\\/uploads\\/sb-instagram-feed-images\\/475481875_1335842247425427_8306176308965945275_nlow.jpg\",\"640\":\"https:\\/\\/www.bayut.com\\/mybayut\\/wp-content\\/uploads\\/sb-instagram-feed-images\\/475481875_1335842247425427_8306176308965945275_nfull.jpg\"}' href=\"https://www.instagram.com/reel/DFfQNRBPsZM/\" rel=\"noopener nofollow noreferrer\" style=\"height: 110px;\" target=\"_blank\"></a></div></div><div class=\"sbi_item sbi_type_video sbi_had_error\" data-date=\"1738299844\" id=\"sbi_18049992194129250\"><div class=\"sbi_photo_wrap\"><a class=\"sbi_photo\" data-full-res=\"https://www.bayut.com/mybayut/wp-content/uploads/sb-instagram-feed-images/475751829_1236144714114243_3060632324531955150_nfull.jpg\" data-img-src-set='{\"d\":\"https:\\/\\/scontent-lhr6-2.cdninstagram.com\\/v\\/t51.29350-15\\/475751829_1236144714114243_3060632324531955150_n.jpg?stp=dst-jpg_e35_tt6&amp;_nc_cat=100&amp;ccb=1-7&amp;_nc_sid=18de74&amp;_nc_ohc=XWx3xEJQjA0Q7kNvgF5zscA&amp;_nc_zt=23&amp;_nc_ht=scontent-lhr6-2.cdninstagram.com&amp;edm=ANo9K5cEAAAA&amp;_nc_gid=AgvY6R0whwmMHWd7_RPndk1&amp;oh=00_AYBJPolCzVoMVHd5VJcsrH1NG8mmJyTwXcN0FTb8d26OMw&amp;oe=67A4690A\",\"150\":\"https:\\/\\/scontent-lhr6-2.cdninstagram.com\\/v\\/t51.29350-15\\/475751829_1236144714114243_3060632324531955150_n.jpg?stp=dst-jpg_e35_tt6&amp;_nc_cat=100&amp;ccb=1-7&amp;_nc_sid=18de74&amp;_nc_ohc=XWx3xEJQjA0Q7kNvgF5zscA&amp;_nc_zt=23&amp;_nc_ht=scontent-lhr6-2.cdninstagram.com&amp;edm=ANo9K5cEAAAA&amp;_nc_gid=AgvY6R0whwmMHWd7_RPndk1&amp;oh=00_AYBJPolCzVoMVHd5VJcsrH1NG8mmJyTwXcN0FTb8d26OMw&amp;oe=67A4690A\",\"320\":\"https:\\/\\/www.bayut.com\\/mybayut\\/wp-content\\/uploads\\/sb-instagram-feed-images\\/475751829_1236144714114243_3060632324531955150_nlow.jpg\",\"640\":\"https:\\/\\/www.bayut.com\\/mybayut\\/wp-content\\/uploads\\/sb-instagram-feed-images\\/475751829_1236144714114243_3060632324531955150_nfull.jpg\"}' href=\"https://www.instagram.com/reel/DFejx3LpVAR/\" rel=\"noopener nofollow noreferrer\" style=\"height: 110px;\" target=\"_blank\"></a></div></div><div class=\"sbi_item sbi_type_video sbi_had_error\" data-date=\"1738241918\" id=\"sbi_17847996123397251\"><div class=\"sbi_photo_wrap\"><a class=\"sbi_photo\" data-full-res=\"https://www.bayut.com/mybayut/wp-content/uploads/sb-instagram-feed-images/475685141_991686989535378_378056489764803596_nfull.jpg\" data-img-src-set='{\"d\":\"https:\\/\\/scontent-lhr8-1.cdninstagram.com\\/v\\/t51.29350-15\\/475685141_991686989535378_378056489764803596_n.jpg?stp=dst-jpg_e35_tt6&amp;_nc_cat=111&amp;ccb=1-7&amp;_nc_sid=18de74&amp;_nc_ohc=RQK0g8W1JKUQ7kNvgGorVg7&amp;_nc_zt=23&amp;_nc_ht=scontent-lhr8-1.cdninstagram.com&amp;edm=ANo9K5cEAAAA&amp;_nc_gid=AgvY6R0whwmMHWd7_RPndk1&amp;oh=00_AYB5tKeTDK-_nqhwWW4eZhLksK_ld1VfladkRVsISvB_AQ&amp;oe=67A4713F\",\"150\":\"https:\\/\\/scontent-lhr8-1.cdninstagram.com\\/v\\/t51.29350-15\\/475685141_991686989535378_378056489764803596_n.jpg?stp=dst-jpg_e35_tt6&amp;_nc_cat=111&amp;ccb=1-7&amp;_nc_sid=18de74&amp;_nc_ohc=RQK0g8W1JKUQ7kNvgGorVg7&amp;_nc_zt=23&amp;_nc_ht=scontent-lhr8-1.cdninstagram.com&amp;edm=ANo9K5cEAAAA&amp;_nc_gid=AgvY6R0whwmMHWd7_RPndk1&amp;oh=00_AYB5tKeTDK-_nqhwWW4eZhLksK_ld1VfladkRVsISvB_AQ&amp;oe=67A4713F\",\"320\":\"https:\\/\\/www.bayut.com\\/mybayut\\/wp-content\\/uploads\\/sb-instagram-feed-images\\/475685141_991686989535378_378056489764803596_nlow.jpg\",\"640\":\"https:\\/\\/www.bayut.com\\/mybayut\\/wp-content\\/uploads\\/sb-instagram-feed-images\\/475685141_991686989535378_378056489764803596_nfull.jpg\"}' href=\"https://www.instagram.com/reel/DFc1P6Xvr4g/\" rel=\"noopener nofollow noreferrer\" style=\"height: 110px;\" target=\"_blank\"></a></div></div><div class=\"sbi_item sbi_type_carousel sbi_had_error\" data-date=\"1738241742\" id=\"sbi_18049277426232071\"><div class=\"sbi_photo_wrap\"><a class=\"sbi_photo\" data-full-res=\"https://www.bayut.com/mybayut/wp-content/uploads/sb-instagram-feed-images/474786084_18480394144052822_1820340467006203524_nfull.jpg\" data-img-src-set='{\"d\":\"https:\\/\\/scontent-lhr8-2.cdninstagram.com\\/v\\/t51.75761-15\\/474786084_18480394144052822_1820340467006203524_n.jpg?stp=dst-jpg_e35_tt6&amp;_nc_cat=103&amp;ccb=1-7&amp;_nc_sid=18de74&amp;_nc_ohc=4Q9TdFBl3moQ7kNvgGsm_Ih&amp;_nc_zt=23&amp;_nc_ht=scontent-lhr8-2.cdninstagram.com&amp;edm=ANo9K5cEAAAA&amp;_nc_gid=AgvY6R0whwmMHWd7_RPndk1&amp;oh=00_AYDYSmQLJMiZF1xYy5NlhXXIdG6juMG6GbD0ipWXNvsQ1Q&amp;oe=67A46431\",\"150\":\"https:\\/\\/scontent-lhr8-2.cdninstagram.com\\/v\\/t51.75761-15\\/474786084_18480394144052822_1820340467006203524_n.jpg?stp=dst-jpg_e35_tt6&amp;_nc_cat=103&amp;ccb=1-7&amp;_nc_sid=18de74&amp;_nc_ohc=4Q9TdFBl3moQ7kNvgGsm_Ih&amp;_nc_zt=23&amp;_nc_ht=scontent-lhr8-2.cdninstagram.com&amp;edm=ANo9K5cEAAAA&amp;_nc_gid=AgvY6R0whwmMHWd7_RPndk1&amp;oh=00_AYDYSmQLJMiZF1xYy5NlhXXIdG6juMG6GbD0ipWXNvsQ1Q&amp;oe=67A46431\",\"320\":\"https:\\/\\/www.bayut.com\\/mybayut\\/wp-content\\/uploads\\/sb-instagram-feed-images\\/474786084_18480394144052822_1820340467006203524_nlow.jpg\",\"640\":\"https:\\/\\/www.bayut.com\\/mybayut\\/wp-content\\/uploads\\/sb-instagram-feed-images\\/474786084_18480394144052822_1820340467006203524_nfull.jpg\"}' href=\"https://www.instagram.com/p/DFc1P66JGB6/\" rel=\"noopener nofollow noreferrer\" style=\"height: 110px;\" target=\"_blank\"></a></div></div><div class=\"sbi_item sbi_type_carousel sbi_had_error\" data-date=\"1738233029\" id=\"sbi_18054589088019244\"><div class=\"sbi_photo_wrap\"><a class=\"sbi_photo\" data-full-res=\"https://www.bayut.com/mybayut/wp-content/uploads/sb-instagram-feed-images/472855108_18480378619052822_3617077685331820953_nfull.jpg\" data-img-src-set='{\"d\":\"https:\\/\\/scontent-lhr8-1.cdninstagram.com\\/v\\/t51.75761-15\\/472855108_18480378619052822_3617077685331820953_n.jpg?stp=dst-jpg_e35_tt6&amp;_nc_cat=108&amp;ccb=1-7&amp;_nc_sid=18de74&amp;_nc_ohc=A6xVsYd4N2sQ7kNvgGvNCxE&amp;_nc_zt=23&amp;_nc_ht=scontent-lhr8-1.cdninstagram.com&amp;edm=ANo9K5cEAAAA&amp;_nc_gid=AgvY6R0whwmMHWd7_RPndk1&amp;oh=00_AYBf8BvPMBJzyxVdyKiVXo6Vfb7b7VC2ljGFxs362Ddtxg&amp;oe=67A4563C\",\"150\":\"https:\\/\\/scontent-lhr8-1.cdninstagram.com\\/v\\/t51.75761-15\\/472855108_18480378619052822_3617077685331820953_n.jpg?stp=dst-jpg_e35_tt6&amp;_nc_cat=108&amp;ccb=1-7&amp;_nc_sid=18de74&amp;_nc_ohc=A6xVsYd4N2sQ7kNvgGvNCxE&amp;_nc_zt=23&amp;_nc_ht=scontent-lhr8-1.cdninstagram.com&amp;edm=ANo9K5cEAAAA&amp;_nc_gid=AgvY6R0whwmMHWd7_RPndk1&amp;oh=00_AYBf8BvPMBJzyxVdyKiVXo6Vfb7b7VC2ljGFxs362Ddtxg&amp;oe=67A4563C\",\"320\":\"https:\\/\\/www.bayut.com\\/mybayut\\/wp-content\\/uploads\\/sb-instagram-feed-images\\/472855108_18480378619052822_3617077685331820953_nlow.jpg\",\"640\":\"https:\\/\\/www.bayut.com\\/mybayut\\/wp-content\\/uploads\\/sb-instagram-feed-images\\/472855108_18480378619052822_3617077685331820953_nfull.jpg\"}' href=\"https://www.instagram.com/p/DFckoTwJXYg/\" rel=\"noopener nofollow noreferrer\" style=\"height: 110px;\" target=\"_blank\"></a></div></div><div class=\"sbi_item sbi_type_carousel sbi_had_error\" data-date=\"1738160532\" id=\"sbi_18095538151519108\"><div class=\"sbi_photo_wrap\"><a class=\"sbi_photo\" data-full-res=\"https://www.bayut.com/mybayut/wp-content/uploads/sb-instagram-feed-images/475635088_9051288381591882_7766142097956397641_nfull.jpg\" data-img-src-set='{\"d\":\"https:\\/\\/scontent-lhr6-2.cdninstagram.com\\/v\\/t51.2885-15\\/475635088_9051288381591882_7766142097956397641_n.jpg?stp=dst-jpg_e35_tt6&amp;_nc_cat=104&amp;ccb=1-7&amp;_nc_sid=18de74&amp;_nc_ohc=ppbf0DrWIdYQ7kNvgFUBYZx&amp;_nc_zt=23&amp;_nc_ht=scontent-lhr6-2.cdninstagram.com&amp;edm=ANo9K5cEAAAA&amp;oh=00_AYCqe5xmEBDZf9dB_Y1iwSB10FjS4B5Qzqk0kpMPjoNDAQ&amp;oe=67A44C20\",\"150\":\"https:\\/\\/scontent-lhr6-2.cdninstagram.com\\/v\\/t51.2885-15\\/475635088_9051288381591882_7766142097956397641_n.jpg?stp=dst-jpg_e35_tt6&amp;_nc_cat=104&amp;ccb=1-7&amp;_nc_sid=18de74&amp;_nc_ohc=ppbf0DrWIdYQ7kNvgFUBYZx&amp;_nc_zt=23&amp;_nc_ht=scontent-lhr6-2.cdninstagram.com&amp;edm=ANo9K5cEAAAA&amp;oh=00_AYCqe5xmEBDZf9dB_Y1iwSB10FjS4B5Qzqk0kpMPjoNDAQ&amp;oe=67A44C20\",\"320\":\"https:\\/\\/www.bayut.com\\/mybayut\\/wp-content\\/uploads\\/sb-instagram-feed-images\\/475635088_9051288381591882_7766142097956397641_nlow.jpg\",\"640\":\"https:\\/\\/www.bayut.com\\/mybayut\\/wp-content\\/uploads\\/sb-instagram-feed-images\\/475635088_9051288381591882_7766142097956397641_nfull.jpg\"}' href=\"https://www.instagram.com/p/DFaaWNXOXQ9/\" rel=\"noopener nofollow noreferrer\" style=\"height: 110px;\" target=\"_blank\"></a></div></div></div><div id=\"sbi_load\"><span class=\"sbi_follow_btn sbi_custom\"><a href=\"https://www.instagram.com/bayutuae/\" rel=\"nofollow noopener noreferrer\" style=\"background: rgb(195,46,146);\" target=\"_blank\"></a></span></div></div></div></div></div></div><div class=\"default_widgets_container default_widgets_col col4\"><div class=\"widget_area\" id=\"default_sidebar_widget\"><div class=\"widget_container widget_content widget widget_text clearfix\" id=\"text-9\"><div class=\"textwidget\"><div class=\"mybayut-popular-posts\"><h3 class=\"section-title\"></h3><a class=\"mybayut-popular-posts-wrapper\" href=\"https://www.bayut.com/mybayut/10-things-to-do-in-the-dubai-mall/\" id=\"popular-post-50910\"><div class=\"mybayut-popular-posts-content\"><h4></h4></div></a><a class=\"mybayut-popular-posts-wrapper\" href=\"https://www.bayut.com/mybayut/food-challenges-dubai/\" id=\"popular-post-305155\"><div class=\"mybayut-popular-posts-content\"><h4></h4></div></a><a class=\"mybayut-popular-posts-wrapper\" href=\"https://www.bayut.com/mybayut/tradeling-dubai/\" id=\"popular-post-348950\"><div class=\"mybayut-popular-posts-content\"><h4></h4></div></a></div></div></div></div></div></div></section></main><footer class=\"site_footer\" id=\"colophon\" role=\"contentinfo\"><div class=\"footer_sidebars_container footers_active_1\"><div class=\"footer_sidebars_inner_wrapper\"><div class=\"footer_widgets_container footer_sidebar_1 col12\" id=\"footer_sidebar_1\"><div class=\"widget_container \nwidget_content widget widget_nav_menu clearfix\" id=\"nav_menu-7\"><div class=\"menu-bayut-footer-property-menu-container\"><ul class=\"menu\" id=\"menu-bayut-footer-property-menu\"><li class=\"property-dropdown menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children menu-item-171536\" id=\"menu-item-171536\"><a href=\"#\"></a><ul class=\"sub-menu\"><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-171538\" id=\"menu-item-171538\"><a href=\"https://www.bayut.com/for-sale/apartments/dubai/\"></a></li><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-171542\" id=\"menu-item-171542\"><a href=\"https://www.bayut.com/for-sale/apartments/abu-dhabi/\"></a></li><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-171543\" id=\"menu-item-171543\"><a href=\"https://www.bayut.com/for-sale/apartments/sharjah/\"></a></li><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-171544\" id=\"menu-item-171544\"><a href=\"https://www.bayut.com/for-sale/apartments/ajman/\"></a></li></ul></li><li class=\"property-dropdown menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children menu-item-171545\" id=\"menu-item-171545\"><a href=\"#\"></a><ul class=\"sub-menu\"><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-171546\" id=\"menu-item-171546\"><a href=\"https://www.bayut.com/for-sale/villas/dubai/\"></a></li><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-171547\" id=\"menu-item-171547\"><a href=\"https://www.bayut.com/for-sale/villas/abu-dhabi/\"></a></li><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-171549\" id=\"menu-item-171549\"><a href=\"https://www.bayut.com/for-sale/villas/sharjah/\"></a></li><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-171550\" id=\"menu-item-171550\"><a href=\"https://www.bayut.com/for-sale/villas/ajman/\"></a></li></ul></li><li class=\"property-dropdown menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children menu-item-171551\" id=\"menu-item-171551\"><a href=\"#\"></a><ul class=\"sub-menu\"><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-171552\" id=\"menu-item-171552\"><a href=\"https://www.bayut.com/to-rent/apartments/dubai/\"></a></li><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-171553\" id=\"menu-item-171553\"><a href=\"https://www.bayut.com/to-rent/apartments/abu-dhabi/\"></a></li><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-171554\" id=\"menu-item-171554\"><a href=\"https://www.bayut.com/to-rent/apartments/sharjah/\"></a></li><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-171555\" id=\"menu-item-171555\"><a href=\"https://www.bayut.com/to-rent/apartments/ajman/\"></a></li></ul></li><li class=\"property-dropdown menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children menu-item-171556\" id=\"menu-item-171556\"><a href=\"#\"></a><ul class=\"sub-menu\"><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-171557\" id=\"menu-item-171557\"><a href=\"https://www.bayut.com/to-rent/villas/dubai/\"></a></li><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-171563\" id=\"menu-item-171563\"><a href=\"https://www.bayut.com/to-rent/villas/abu-dhabi/\"></a></li><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-171564\" id=\"menu-item-171564\"><a href=\"https://www.bayut.com/to-rent/villas/sharjah/\"></a></li><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-171565\" id=\"menu-item-171565\"><a href=\"https://www.bayut.com/to-rent/villas/ajman/\"></a></li></ul></li></ul></div></div><div class=\"widget_container widget_content widget widget_nav_menu clearfix\" id=\"nav_menu-4\"><div class=\"menu-bayut-footer-container\"><ul class=\"menu\" id=\"menu-bayut-footer\"><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-12145\" id=\"menu-item-12145\"><a href=\"https://www.bayut.com/about/aboutus.html\" title=\"About Us\"></a></li><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-12144\" id=\"menu-item-12144\"><a href=\"https://www.bayut.com/contactus.html\" title=\"Contact Us\"></a></li><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-12147\" id=\"menu-item-12147\"><a href=\"https://www.bayut.com/terms.html\" title=\"Terms &amp; Privacy Policy\"></a></li></ul></div></div><div class=\"widget_container widget_content widget widget_nav_menu clearfix\" id=\"nav_menu-5\"><div class=\"menu-bayut-footer-social-container\"><ul class=\"menu\" id=\"menu-bayut-footer-social\"><li class=\"footer-facebook menu-item menu-item-type-custom menu-item-object-custom menu-item-58642\" id=\"menu-item-58642\"><a href=\"https://www.facebook.com/bayutuae\" rel=\"noopener noreferrer\" target=\"_blank\"></a></li><li class=\"footer-twitter menu-item menu-item-type-custom menu-item-object-custom menu-item-58643\" id=\"menu-item-58643\"><a href=\"https://twitter.com/bayut\" rel=\"noopener noreferrer\" target=\"_blank\"></a></li><li class=\"footer-linkedin menu-item menu-item-type-custom menu-item-object-custom menu-item-58644\" id=\"menu-item-58644\"><a href=\"https://www.linkedin.com/company/bayut-com\" rel=\"noopener noreferrer\" target=\"_blank\"></a></li><li class=\"footer-instagram menu-item menu-item-type-custom menu-item-object-custom menu-item-58646\" id=\"menu-item-58646\"><a href=\"https://www.instagram.com/bayutuae\" rel=\"noopener noreferrer\" target=\"_blank\"></a></li><li class=\"footer-appstore menu-item menu-item-type-custom menu-item-object-custom menu-item-58647\" id=\"menu-item-58647\"><a href=\"https://itunes.apple.com/app/bayut-uae-property-search/id923263211?mt=8\" rel=\"noopener noreferrer\" target=\"_blank\"></a></li><li class=\"footer-googleplay menu-item menu-item-type-custom \nmenu-item-object-custom menu-item-58648\" id=\"menu-item-58648\"><a href=\"https://play.google.com/store/apps/details?id=com.bayut.bayutapp\" rel=\"noopener noreferrer\" \ntarget=\"_blank\"></a></li></ul></div></div></div></div></div></footer></div><div class=\"bayut-property-portal-widget display-widget\"><div class=\"property-purpose\"><div class=\"bayut_logo\"><a href=\"https://www.bayut.com/\" rel=\"bayut\"></a></div></div><div class=\"property-types\"><div class=\"properties-for-sale\"><div class=\"menu-property-type-buy-container\"><ul class=\"menu\" id=\"menu-property-type-buy\"><li class=\"apartments menu-item menu-item-type-custom menu-item-object-custom menu-item-261632\" id=\"menu-item-261632\"><a href=\"https://www.bayut.com/for-sale/apartments/uae/\"></a></li><li class=\"villas menu-item menu-item-type-custom menu-item-object-custom menu-item-261633\" id=\"menu-item-261633\"><a href=\"https://www.bayut.com/for-sale/villas/uae/\"></a></li><li class=\"townhouses menu-item menu-item-type-custom menu-item-object-custom menu-item-261634\" id=\"menu-item-261634\"><a href=\"https://www.bayut.com/for-sale/townhouses/uae/\"></a></li><li class=\"residential-plots menu-item menu-item-type-custom menu-item-object-custom menu-item-261635\" id=\"menu-item-261635\"><a href=\"https://www.bayut.com/for-sale/residential-plots/uae/\"></a></li></ul></div></div><div class=\"properties-for-rent\"><div class=\"menu-property-type-rent-container\"><ul class=\"menu\" id=\"menu-property-type-rent\"><li class=\"apartments menu-item menu-item-type-custom menu-item-object-custom menu-item-261672\" id=\"menu-item-261672\"><a href=\"https://www.bayut.com/to-rent/apartments/uae/\"></a></li><li class=\"villas menu-item menu-item-type-custom menu-item-object-custom menu-item-261673\" id=\"menu-item-261673\"><a href=\"https://www.bayut.com/to-rent/villas/uae/\"></a></li><li class=\"townhouses menu-item menu-item-type-custom menu-item-object-custom menu-item-261675\" id=\"menu-item-261675\"><a href=\"https://www.bayut.com/to-rent/townhouses/uae/\"></a></li><li class=\"offices menu-item menu-item-type-custom menu-item-object-custom menu-item-261676\" id=\"menu-item-261676\"><a href=\"https://www.bayut.com/to-rent/offices/uae/\"></a></li></ul></div></div></div></div><div class=\"site_side_container\"><h3 class=\"screen-reader-text\"></h3><div class=\"info_sidebar\"><div class=\"top_header_items_holder mobile_menu_opened\"><div class=\"main_menu\"><div class=\"bayut_logo\"><a href=\"https://www.bayut.com/\" rel=\"bayut\"></a></div><ul class=\"navbar\" id=\"mobile-menu\"><li class=\"tips-menu menu-item menu-item-type-custom menu-item-object-custom menu-item-11952 default_menu\"><a href=\"/mybayut/tips/\"></a></li><li class=\"pulse-menu menu-item menu-item-type-custom menu-item-object-custom menu-item-11953 default_menu\"><a href=\"/mybayut/pulse/\"></a></li><li \nclass=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-11993 default_menu\"><a href=\"/mybayut/my-home/\"></a></li><li class=\"genz-menu menu-item menu-item-type-taxonomy menu-item-object-category menu-item-61607 default_menu\"><a href=\"https://www.bayut.com/mybayut/gen-z/\"></a></li><li class=\"rules-menu menu-item menu-item-type-taxonomy menu-item-object-category menu-item-61606 default_menu\"><a href=\"https://www.bayut.com/mybayut/rules-regulations/\"></a></li><li class=\"market-trends-menu menu-item menu-item-type-custom menu-item-object-custom menu-item-11954 default_menu\"><a href=\"/mybayut/market-trends/\"></a></li><li class=\"partners-menu menu-item menu-item-type-taxonomy menu-item-object-category menu-item-61608 default_menu\"><a href=\"https://www.bayut.com/mybayut/our-partners/\"></a></li><li class=\"bayut-after-hours-menu menu-item menu-item-type-taxonomy menu-item-object-category menu-item-12598 default_menu\"><a href=\"https://www.bayut.com/mybayut/bayut-after-hours/\"></a></li></ul><div class=\"menu-bayut-property-menu-container\"><ul class=\"menu\" id=\"menu-bayut-property-menu-1\"><li class=\"property-dropdown menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children menu-item-747434\"><a href=\"#\"></a><ul class=\"sub-menu\"><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-747435\"><a href=\"https://www.bayut.com/area-guides/\"></a></li><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-747436\"><a href=\"https://www.bayut.com/buildings/\"></a></li><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-747437\"><a href=\"https://www.bayut.com/schools/\"></a></li></ul></li></ul></div><div class=\"menu-bayut-product-menu-container\"><ul class=\"menu\" id=\"menu-bayut-product-menu-1\"><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-100424\"><a href=\"https://www.bayut.com/floorplans/\"></a></li><li class=\"menu-item menu-item-type-custom menu-item-object-custom menu-item-100425\"><a href=\"https://www.bayut.com/companies/\"></a></li><li class=\"get-in-touch-modal menu-item menu-item-type-custom menu-item-object-custom menu-item-747440\"><a href=\"#get_in_touch_modal\" rel=\"modal:open\"></a></li><li class=\"lang-item lang-item-8187 lang-item-ar \nlang-item-first menu-item menu-item-type-custom menu-item-object-custom menu-item-100426-ar\"><a href=\"https://www.bayut.com/mybayut/ar/\" hreflang=\"ar\" lang=\"ar\"></a></li></ul></div></div></div></div></div></div><div class=\"modal get-in-touch-modal\" id=\"get_in_touch_modal\"><article class=\"get-in-touch-form block-form-section\"><div class=\"info-block\" id=\"info_block_47257\"><h4 class=\"title\"></h4></div></article></div></body>"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "{\n  \"card_selector\": \".blog_post_container\"\n}"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "perfect\n"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "{\n  \"response\": \"Thank you! If you have any more questions or need further assistance, feel free to ask.\"\n}"
        }
      ]
    }
  ]
  if prompt:
        messages.extend(prompt)
        stream = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_schema",
        "json_schema": {
        "name": "MathReasoningSchema",  # Required name for the schema
        "schema": MathReasoning.schema()  # Use the schema from the Pydantic model
    }
                         },
        messages=messages,
        
        temperature=0.4,
    )

  return json.loads(stream.choices[0].message.content)

def openAiReqFindLink(prompt):
  client = openai.Client(api_key='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')
  messages=[
            {
                "role":"system",
                "content": "I'm an expert web analyst. Analyze the provided HTML structure and identify the most reliable and aimed dynamic selectors that will target the article's Title and Link of any article with same stracture of code but differnt content"
            },
            
          
            {
                "role": "user",
               "content": """

Required Output Format:
You must return a JSON object with exactly two fields:
1. 'link_selector': The CSS OR Id selector  that targets article links
3. 'Title_selector': The CSS Or Id selector  that targets article Title
4. 'type':'css/id'

Guidelines for selector identification:
2. Remeber the provided article html code is the only first artile in list there are many more with different content so identify the selelctor that will work on upcoming articles with same stracture of code but different content 
3. Prefer selectors that are:
   - Stable (based on IDs, classes, or distinct structural patterns)
   - As simple as possible while still being precise
   - as more aimed as can

Example response format given:

{

    "link_selector": "a.post-link ...",
    "title_selector": "h2.post-heading ...",
    "type": "css"
}


Important:
- Do not include explanations or additional fields
- The selector must be valid CSS or id(if css not available) syntax""",


            },
       
         {
                "role":"assistant",
                "content": "I Understood provide me html of article and i will return you the fields that will target only title and Link and i will Ignore any additional content and return in expected json format"
            },
            # {
            #     "role":"user",
            #     "content": f"{data}"
            # },
        ],
  
  if prompt:
    messages.extend(prompt)
    stream = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=messages,
            temperature=0.2,
        )

  return json.loads(stream.choices[0].message.content)




def openAiReqFindLink_Markdown(prompt):
  client = openai.Client(api_key='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')
  messages=[
           {
      "role": "system",
      "content": [
        {
          "type": "text",
          "text": "Understand the HTML code provided and identify the selector for the blog's Title and Link element.\n\n# Steps\n\n1. Analyze the HTML code given to you.\n2. Locate the blog's title and link HTML structure.\n3. Determine the appropriate CSS selector that targets the blog title and link.\n4. The selector should be dynamic and work on upcoming blog cards with the same structure but different content.\n5. The selector should be as simple as possible and correct to directly target the link and title.\n\n# Output Format in JSON\n{\n\"link_selector\":\"e.g .title\",\n\"title_selector\":\"e.g .title\"\n}"
        }
      ]
    },
          
        ]
  
  if prompt:
    # Debugging: check the type of `prompt` before conversion
    
    if isinstance(prompt, tuple):
        prompt = list(prompt)  # Convert the tuple to a list
    

    # Ensure prompt is now a list before calling `extend`
    if isinstance(messages,tuple):
       messages = list(messages)
    messages.extend(prompt)

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=messages,
        temperature=0.2,
    )

  return json.loads(stream.choices[0].message.content)

def openAiReqFindnavigation(data):
  client = openai.Client(api_key='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')

  stream = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
           {
      "role": "system",
      "content": [
        {
          "type": "text",
          "text": "Analyze the provided HTML structure and identify the most reliable selectors for navigation to the Next page.\n\nYou must return a JSON object with exactly three fields:\n1. 'selector': The CSS or id that targets the navigation element for the next page.\n2. 'clickable': \n   - 0 if the navigation element uses a valid URL (e.g., <a href='https://example.com/page/2'>).\n   - 1 if the navigation element does NOT use a valid URL (e.g., <a href='{javascript-content}:...'> or <button>).\n   - 2 if the navigation is NOT available, instead of providing a useless selector, return \"2\" and stop the process.\n3. 'type': Either 'css' or 'id'.\n\n# Guidelines for Selector Identification\n- Focus only on elements that are clearly for pagination or navigation, such as:\n  - <a> tags with valid URLs for the next page (here, the 'clickable' field should be 0).\n  - <a> tags or <button> elements that use JavaScript or no valid URL (here, the 'clickable' field should be 1).\n- Navigation elements are typically located at the bottom of an article listing container.\n\n# Important\n- The selector must strictly target only the next-page navigation element.\n- The selector should be as simple as possible.\n- Do not include explanations or extra fields in your response."
        }
      ]
    },
            
          
          
             {
                "role":"user",
                "content": f"html : {data}"
            },
           
        ],
 
          max_tokens=300,
        temperature=1.0,
    )

  return json.loads(stream.choices[0].message.content)

def clean_html(body_content, remove_empty_space=False):
   
    
    from bs4 import BeautifulSoup
    import re

    soup = BeautifulSoup(body_content, 'html.parser')

    # Tags to be removed
    tags_to_remove = ["header", "footer", "iframe", "style", "script","picture","img"]

    # Remove specified tags
    for tag in tags_to_remove:
        for element in soup.find_all(tag):
            element.decompose()

    # Remove all attributes except 'class' and 'id'
    for tag in soup.find_all(True):  # Find all tags
        attributes_to_keep = {key: value for key, value in tag.attrs.items() if key in ['class', 'id','href']}
        tag.attrs = attributes_to_keep

    # Convert cleaned HTML to string
    if soup.body:

     cleaned_html = str(soup.body)
    else:
     cleaned_html = str(soup)
        

    # Remove extra gaps: replace multiple spaces, newlines, or tabs with a single space
    cleaned_html = re.sub(r'\s+', ' ', cleaned_html).strip()

    # If remove_empty_space is True, remove all spaces
    if remove_empty_space:
        cleaned_html = ''.join(cleaned_html.split())

    return cleaned_html



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

# @router.get("/")
# async def get_html_body_content(url: str = Query(..., description="The URL to fetch content from")):
#     try:
#         prompt_To_Get_Card = [] #the prompt that target the listing container o articles/blogs/posts
#         cardprompt = []  #the prompt that target the article card within listing container
#         listingContainer = ''
#         # response = requests.get(url , headers=headers)
#         print(f"get result  before{url}")

#         # response = await ScrapeBody(url)
        
#         response = await fetch_full_html_with_selenium(url)
#         print(f"get result {url}")
#         # Check if the response was successful

#         # Parse the HTML content of the page with BeautifulSoup
#         print("souping")
#         soup = BeautifulSoup(response, 'html.parser')

#         print("souping..sd")

#         # Extract the body content
#         body_content = soup.body

#         if body_content:

#             print(f"Minifying HTML content... {url}")
#             minified_body = clean_html(str(body_content), remove_empty_space=False)
#             print(" " * 200)
#             print(f"Understanding article structure... {url}")
            
#             # Use AI to determine the parent selector
#             prompt_To_Get_Card = [
#                         {"role": "user", "content": f"HTML: ```html\n{minified_body}\n```"}
#                     ]
#             listing_Target = openAiReq_Get_Listing(prompt_To_Get_Card)
#             print(f"AI response for parent listing container: {listing_Target}") 
            
#             if not listing_Target['parent_selector'].strip():
#                 listingContainer = None
#             else:
#                listingContainer= body_content.select_one(listing_Target['parent_selector'])  
#             if not listingContainer:
#                 prompt_To_Get_Card = [
#                         {"role": "user", "content": f"HTML: ```html\n{minified_body}\n```"},
#                         {"role": "assistant", "content": f"{AI_res_Card_Selector}"},
#                         {"role": "user", "content": f"The provided selector did not work. Please analyze this HTML and suggest a correct selector"}
                   
#                     ]
#                 listing_Target = openAiReq_Get_Listing(prompt_To_Get_Card)
#                 print(f"retry AI response for parent listing container: {listing_Target}") 
#                 if not listing_Target['parent_selector'].strip():
#                    return {"error":"cant undertand the website stracture"}
#                 else:
#                   listingContainer= body_content.select_one(listing_Target['parent_selector'])  
#                   if not listingContainer:
#                       return {"error":"cant undertand the website stracture"}
#             listingContainer = clean_html(str(listingContainer), remove_empty_space=False)      
#             cardprompt = [
#                         {"role": "user", "content": f"HTML: ```html\n{listingContainer}\n```"}
#                     ]   
#             AI_res_Card_Selector = openAiReq_Get_Parent(cardprompt)
#             print(f"AI response for card container: {AI_res_Card_Selector}")
#             print(" " * 200)

#             blogContainer = None
#             if not AI_res_Card_Selector['card_selector'].strip():

#               blogContainer = []
#             else:
#                blogContainer= body_content.select(AI_res_Card_Selector['card_selector'])  
#             # Check if the blogContainer is empty
#             if not blogContainer or blogContainer == '':  # If blogContainer is an empty array
#                 print(f"Blog container is empty for {url}. Retrying with updated parent selector...")
#                 cardprompt = [
#                         {"role": "user", "content": f"HTML:```html\n{minified_body}\n```"},
#                         {"role": "assistant", "content": f"{AI_res_Card_Selector}"},
#                         {"role": "user", "content": f"The provided selector did not work. Please analyze this HTML and suggest a correct selector"}
#                     ]
#                 # Retry fetching the parent selector with AI or provide a fallback
#                 retry_container_selector = openAiReq_Get_Parent(cardprompt)
#                 print(f"Retry AI response: {retry_container_selector}")
                
#                 if retry_container_selector and retry_container_selector['card_selector'].strip():  # Retry succeeded
#                     blogContainer = body_content.select(retry_container_selector['card_selector'])
#                     if not blogContainer or blogContainer == '':  # Still empty after retry
#                         return {
#                             "error": f"Unable to extract blog container using the AI-suggested parent selector {retry_container_selector['card_selector']} for {url}."
#                         }
#                     AI_res_Card_Selector = retry_container_selector
#                 else:
#                     return {
#                         "error": f"Failed to fetch a valid parent selector for {url}."
#                     }

#             print(f"Extracting title and link fields... {url}")
            
#             # Use AI to find the link and title selectors within the container
#             # print(str(blogContainer[0]))
#             blogContainer = clean_html(str(blogContainer[0]))
#             print(f"Link extraction result: {blogContainer}")
#             ai_Link_prompt =[ 
#                     {
#                 "role":"user",
#                 "content": f"{blogContainer}"
#             }]
#             ailinkres = openAiReqFindLink(ai_Link_prompt)
#             print(f"Link extraction result: {ailinkres}")
#             if not ailinkres['type'] or not ailinkres['title_selector'] or not ailinkres['link_selector']:
#                  ai_Link_prompt =[ 
#                 {"role":"user", "content": f"{blogContainer}" },
#                 {"role": "assistant", "content": f"{ailinkres}"},
#                 {"role": "user", "content": f"you missed the parameters. Please analyze this HTML and suggest a correct selector"}
#                  ]
#                  ailinkres = openAiReqFindLink(ai_Link_prompt)
#             if not ailinkres['type'] or not ailinkres['title_selector'] or not ailinkres['link_selector']:
#                 return {"error":"cannot find html parameters"}

#             print(f"AI parent container extraction done for {url}")
#             print("_" * 100)
#             print(f"Working on pagination for {url}")
            
#             # Use AI to find the navigation elements
#             ainavigationres = openAiReqFindnavigation(minified_body)
#             print(f"AI navigation result: {ainavigationres}")
            
#             # Extract content using the determined selectors
#             print(f"Extracting content... {url}")

#             max_retries = 5  # Prevent infinite loops
#             retry_count = 0
#             prompt_history = []  # Stores conversation history with AI
#             original_ailinkres = ailinkres.copy()  # Preserve original selectors
#             while retry_count < max_retries:
#                 fetchContent = scrapecontent(body_content, AI_res_Card_Selector['card_selector'], ailinkres)
                 
#                 if fetchContent['status'] == 200: 
#                     return {
#                         'parent': AI_res_Card_Selector['card_selector'],
#                         'target': ailinkres,
#                         'navigate': ainavigationres,
#                         'extracted': fetchContent
#                     }
#                 error_context = {
#                 "error_code": fetchContent['code'],
#                 "error_message": fetchContent['message'],
#                 "used_selectors": {
#                     "parent": AI_res_Card_Selector['card_selector'],
#                     "link": ailinkres.get('link_selector'),
#                     "title": ailinkres.get('title_selector')
#                 },
#                 "html_snippet": clean_html(str(body_content), remove_empty_space=False)
#                 }
                            
                
#                 if fetchContent['status'] == 400:
#                     body_content = BeautifulSoup(body_content,'html.parser')
#                     fetchContent = scrapecontent(body_content, AI_res_Card_Selector['card_selector'], ailinkres)
#                 elif fetchContent['status'] == 404:
#                        print("notfound")
#                 elif fetchContent['status'] == 500:
#                     print(fetchContent['message'])
                

#         else:
#             return "No body tag found in the HTML."
#     except requests.RequestException as e:
#         return f"An error occurred: {str(e)}"


@router.get("/")
async def get_html_body_content(url: str = Query(..., description="The URL to fetch content from")):
    try:
        prompt_To_Get_Card= [] #the prompt that target the listing container o articles/blogs/posts
        listingContainer = ''
        # response = requests.get(url , headers=headers)
        print(f"get result  before{url}")

        # response = await ScrapeBody(url)
        
        response = await fetch_full_html_with_selenium(url)
        print(f"get result {url}")
        # Check if the response was successful

        # Parse the HTML content of the page with BeautifulSoup
        print("souping")
        soup = BeautifulSoup(response, 'html.parser')

        print("souping..sd")

        # Extract the body content
        body_content = soup.body
        print(soup.body)
        body_content_for_extraction= soup.body
        if body_content:

            print(f"Minifying HTML content... {url}")
        
            minified_body =  html_filter_keep_headings_links(body_content)
            body_for_navigation = clean_navigation(str(body_content))
           
            # return
            print(" " * 200)
            print(f"Understanding article structure... {url}")
            
            # Use AI to determine the parent selector
            prompt_To_Get_Card = [
                        {"role": "user", "content": f"{minified_body}"}
                    ]
            listing_Target = openAiReq_Get_Parent_Markdown(prompt_To_Get_Card)
            print(f"AI response for parent listing container: {listing_Target}") 
            
            if not listing_Target['card_selector'].strip():
                listingContainer = None
            else:
               listingContainer= body_content.select_one(listing_Target['card_selector'])  
            if not listingContainer:
                prompt_To_Get_Card = [
                        {"role": "user", "content": f"{minified_body}"},
                        {"role": "assistant", "content": f"{listing_Target}"},
                        {"role": "user", "content": f"The provided selector did not work. Please analyze this HTML and suggest a correct selector that select blog's card"}
                   
                    ]
                listing_Target = openAiReq_Get_Parent_Markdown(prompt_To_Get_Card)
                print(f"retry AI response for parent listing container: {listing_Target}") 
                if not listing_Target['card_selector'].strip():
                   return {"error":"cant undertand the website stracture"}
                else:
                  listingContainer= body_content.select_one(listing_Target['card_selector'])  
                  if not listingContainer:
                      return {"error":"cant undertand the website stracture"}
            ai_Link_prompt =[ 
                    {
                "role":"user",
                "content": f"{listingContainer}"
            },]

          
            
            ailinkres = openAiReqFindLink_Markdown(ai_Link_prompt)
            print(f"Link extraction result: {ailinkres}")
            if not ailinkres['title_selector'] or not ailinkres['link_selector']:
                 ai_Link_prompt =[ 
                {"role":"user", "content": f"{minified_body}" },
                {"role": "assistant", "content": f"{ailinkres}"},
                {"role": "user", "content": f"you missed the parameters. Please analyze this html and suggest a correct selector"}
                 ]
                 ailinkres = openAiReqFindLink(ai_Link_prompt)
            if not ailinkres['title_selector'] or not ailinkres['link_selector']:
                return {"error":"cannot find Markdown parameters"}

            print(f"AI parent container extraction done for {url}")
            print("_" * 100)
            print(f"Working on pagination for {url}")
            
            # Use AI to find the navigation elements
            ainavigationres = openAiReqFindnavigation(body_for_navigation)
            print(f"AI navigation result: {ainavigationres}")
            
            # Extract content using the determined selectors
            print(f"Extracting content... {url}")

            fetchContent = scrapecontent(str(body_content_for_extraction),listing_Target['card_selector'], ailinkres)
            print(fetchContent)
            if fetchContent['code'] == 200: 
                    return {
                        'parent': listing_Target['card_selector'],
                        'target': ailinkres,
                        'navigate': ainavigationres,
                        'extracted': fetchContent
                    }
            error_context = {
                "error_code": fetchContent['code'],
                "error_message": fetchContent['message'],
                "used_selectors": {
                    "parent": listing_Target['card_selector'],
                    "link": ailinkres.get('link_selector'),
                    "title": ailinkres.get('title_selector')
                },
                "html_snippet": clean_html(str(body_content_for_extraction), remove_empty_space=False)
                }
                            
                
            # print(error_context)
            return(error_context)
                

        else:
            return "No body tag found in the HTML."
    except requests.RequestException as e:
        return f"An error occurred: {str(e)}"

