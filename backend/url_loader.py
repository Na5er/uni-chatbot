"""
URL Content Loader - Fetches and stores content from URLs in the knowledge base
"""
import requests
from bs4 import BeautifulSoup
from .database import db
from typing import List, Dict

def scrape_and_store_urls(urls: List[str]) -> Dict:
    """
    Scrapes multiple URLs, extracts Arabic text, and stores in vector DB.
    
    Args:
        urls: List of URLs to scrape
        
    Returns:
        Summary of what was added
    """
    results = {
        "success": 0,
        "failed": 0,
        "urls": []
    }
    
    for url in urls:
        try:
            print(f"📖 Fetching content from: {url}")
            
            # Fetch the page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.encoding = 'utf-8'  # Handle Arabic encoding
            response.raise_for_status()
            
            # Parse HTML and extract text
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'button']):
                element.decompose()
            
            # Get all text
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean up excessive whitespace
            text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
            
            if len(text) < 100:
                print(f"  ❌ Too little content extracted ({len(text)} chars)")
                results["failed"] += 1
                continue
            
            # Split into chunks (every 1500 chars roughly with 200 char overlap)
            chunk_size = 1500
            overlap = 200
            chunks = []
            for i in range(0, len(text), chunk_size - overlap):
                chunk = text[i:i+chunk_size]
                if len(chunk.strip()) > 50:  # Only add non-empty chunks
                    chunks.append(chunk)
            
            # Add to database
            texts = chunks
            metadatas = [{"source": url, "chunk_num": i+1, "total_chunks": len(chunks)} 
                         for i in range(len(chunks))]
            
            db.add_documents(texts, metadatas)
            
            print(f"  ✅ Successfully added {len(chunks)} chunks from {url}")
            results["success"] += 1
            results["urls"].append({"url": url, "chunks": len(chunks), "status": "success"})
            
        except Exception as e:
            print(f"  ❌ Error fetching {url}: {str(e)}")
            results["failed"] += 1
            results["urls"].append({"url": url, "status": "failed", "error": str(e)})
    
    return results
