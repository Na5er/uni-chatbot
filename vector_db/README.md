# Vector Database Module

## Purpose
This module allows the chatbot to understand the **meaning** of user queries rather than just matching keywords. It stores the "embeddings" (numerical representations) of the scraped text.

## Tools
- **ChromaDB**: Open-source embedding database.
- **Pinecone**: Managed vector database service.
- **OpenAI Embeddings / HuggingFace**: Models to convert text to vectors.

## Workflow
1.  Receive text chunks from the Scraper.
2.  Generate embeddings for each chunk.
3.  Store embeddings + metadata (text, URL) in the database.
4.  Provide a search interface: `query -> embedding -> nearest neighbors`.
