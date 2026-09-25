# University Chatbot (RAG Architecture)

This project implements a Retrieval-Augmented Generation (RAG) chatbot for a university website.

## Architecture Overview

The system consists of four main components:

1.  **Frontend (`/frontend`)**: A standalone widget (HTML/JS/CSS) embedded on the university website. It handles user interaction and displays responses.
2.  **Scraper (`/scraper`)**: A data ingestion module that crawls the university website and extracts text content with source URLs.
3.  **Vector DB (`/vector_db`)**: A storage layer using a vector database (e.g., ChromaDB, Pinecone) to store text embeddings for semantic search.
4.  **Backend (`/backend`)**: The core logic that receives queries, searches the Vector DB, retrieves relevant context, and generates answers using an LLM (e.g., GPT-4, Gemini) with citations.

## Directory Structure

- `frontend/`: Chatbot widget code.
- `scraper/`: Web scraping scripts and data processing.
- `vector_db/`: Database configuration and storage scripts.
- `backend/`: API server and AI logic.
