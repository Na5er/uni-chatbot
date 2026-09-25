import os
import shutil
from typing import List, Dict
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import FakeEmbeddings 
from langchain_core.documents import Document
from .utils import normalize_arabic
from dotenv import load_dotenv

load_dotenv()

# Use FakeEmbeddings for free operation (no API costs)
print("Using FakeEmbeddings for free local embeddings.")
embeddings = FakeEmbeddings(size=1536)

DB_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")

class Database:
    def __init__(self):
        self.vector_db = Chroma(
            persist_directory=DB_DIR, 
            embedding_function=embeddings
        )

    def add_documents(self, texts: List[str], metadatas: List[Dict] = None):
        """
        Normalizes Arabic text and adds it to ChromaDB.
        """
        if metadatas is None:
            metadatas = [{} for _ in texts]
            
        docs = []
        for text, meta in zip(texts, metadatas):
            # 1. Normalize Text
            clean_text = normalize_arabic(text)
            # Store original text in metadata to show to user, but embed normalized text
            meta["original_text"] = text 
            
            docs.append(Document(page_content=clean_text, metadata=meta))
            
        self.vector_db.add_documents(docs)
        print(f"Added {len(docs)} documents to ChromaDB.")

    def search(self, query: str, k: int = 5) -> List[Dict]:
        """
        Normalizes query and searches Vector DB with keyword fallback.
        When results are poor, uses keyword matching to find relevant documents.
        """
        clean_query = normalize_arabic(query)
        print(f"Searching for: {clean_query}")
        
        # Use similarity_search_with_score to get results
        results = self.vector_db.similarity_search_with_score(clean_query, k=k)
        
        # If results are available, enhance them with keyword matching
        enhanced_results = []
        for doc, score in results:
            content = doc.metadata.get("original_text", doc.page_content)
            clean_content = normalize_arabic(content)
            # Keyword boost: check how many query words appear in the normalized content
            query_words = clean_query.split()
            keyword_matches = sum(1 for word in query_words if word in clean_content)
            keyword_score = keyword_matches / len(query_words) if query_words else 0
            
            # Inverse distance to get similarity (higher is better)
            similarity = 1 / (1 + score)
            
            # Combine scores: give more weight to keyword matching
            combined_score = (similarity * 0.3) + (keyword_score * 0.7)
            
            enhanced_results.append({
                "content": content,
                "source": doc.metadata.get("source", "Unknown"),
                "score": combined_score,
                "chunk_num": doc.metadata.get("chunk_num", 0)
            })
        
        # Sort by combined score (higher = better match)
        enhanced_results.sort(key=lambda x: x["score"], reverse=True)
        
        return enhanced_results[:k]
    
    def reset(self):
        """Clears the database."""
        if os.path.exists(DB_DIR):
            shutil.rmtree(DB_DIR)
            print("Database reset.")
        self.vector_db = Chroma(
            persist_directory=DB_DIR, 
            embedding_function=embeddings
        )

db = Database()
