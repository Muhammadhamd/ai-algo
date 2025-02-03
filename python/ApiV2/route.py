# extraction_link_v2/main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from extraction_link_v2"}

from fastapi import FastAPI
from .extraction_link_v2.Ai_Analize import router as extraction_link_v2_router
from .extraction_link_v2.scrape_example_links import router as scrape_example_links
from .extraction_link_v2.verify_navigation import router as verifying_navigate
from .extraction_link_v2.All_scraping import app as start_Scrap

app = FastAPI()

app.mount("/link/scrape-link-fields",extraction_link_v2_router)
app.mount("/link/scrape-example",scrape_example_links)
app.mount("/link/start",start_Scrap)
app.mount("/link/verify-navigation",verifying_navigate)
