# Scraper Module

## Purpose
This module handles the **Data Ingestion** phase. It is responsible for crawling the university website to build the knowledge base.

## Tools
- **Python**: The primary language for scripting.
- **BeautifulSoup / Scrapy**: For HTML parsing and crawling.
- **Firecrawl** (Optional): For ready-made crawling solutions.

## Functionality
1.  Navigate through university pages.
2.  Extract text content from each page.
3.  Chunk the text into manageable pieces.
4.  **Meta-data**: Store the source URL for every chunk to enable citation in the final response.

## Output Structure
JSON or similar format:
```json
[
  {
    "text": "The semester starts on September 1st...",
    "url": "https://univ.edu/calendar",
    "title": "Academic Calendar"
  }
]
```
