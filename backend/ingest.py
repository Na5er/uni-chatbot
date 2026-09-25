import json
import os
import requests
from bs4 import BeautifulSoup
from .database import db

# Configuration
JSON_PATH = os.path.join(os.path.dirname(__file__), "knowledge.json")

def scrape_url(url: str) -> str:
    """
    Fetches the URL and extracts clean text content.
    """
    try:
        print(f"Scraping: {url} ...")
        headers = {'User-Agent': 'UniversityChatbot/1.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove scripts and styles
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()
            
        # Get text
        text = soup.get_text(separator=' ')
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        print(f"  -> Extracted {len(text)} characters.")
        return text
        
    except Exception as e:
        print(f"  -> Errors scraping {url}: {e}")
        return None

def ingest_data():
    """
    Reads data from knowledge.json.
    - If 'text' is present, uses it.
    - If 'text' is missing/empty but 'url' is present, scrapes the URL.
    - Adds to ChromaDB.
    """
    
    if not os.path.exists(JSON_PATH):
        print(f"Error: {JSON_PATH} not found.")
        return

    print("Loading data from knowledge.json...")
    
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    texts = []
    metadatas = []
    
    for item in data:
        source = item.get("source", "manual")
        content = item.get("text", "").strip()
        url = item.get("url", source if source.startswith("http") else None)
        
        # Logic: If text is empty, try to scrape
        if not content and url and url.startswith("http"):
             scraped_content = scrape_url(url)
             if scraped_content:
                 content = scraped_content
             else:
                 print(f"Skipping {url} due to scrape failure.")
                 continue
        
        if content:
            texts.append(content)
            # Use URL as the source if available, so it's clickable in the UI
            final_source = url if url else source
            metadatas.append({"source": final_source})
        else:
            print(f"Skipping item with no content: {item}")

    if texts:
        # Reset DB to avoid duplicates (Optional: logic could be smarter)
        # db.reset() 
        
        # Add to DB
        db.add_documents(texts, metadatas)
        print(f"Successfully loaded {len(texts)} items into the Knowledge Base!")
    else:
        print("No valid data found to ingest.")

if __name__ == "__main__":
    ingest_data()
