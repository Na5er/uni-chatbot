import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from .database import db
from .utils import normalize_arabic
from dotenv import load_dotenv

# LangChain Imports
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from fastapi.staticfiles import StaticFiles
from .url_loader import scrape_and_store_urls

load_dotenv()

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend directory
app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")

class ChatRequest(BaseModel):
    message: str

class LearnRequest(BaseModel):
    content: str
    source: str = "manual_entry"

# --- RAG Setup ---
openai_key = os.getenv("OPENAI_API_KEY")
google_key = os.getenv("GOOGLE_API_KEY")

if google_key and google_key != "your-google-api-key-here":
    print("Using Gemini LLM.")
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=google_key)
elif openai_key and openai_key != "your-openai-api-key-here":
    print("Using OpenAI LLM.")
    llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=openai_key)
else:
    print("Using mock LLM for free operation.")
    llm = None

# Strict System Prompt
SYSTEM_PROMPT = """Role: You are the official, helpful support chatbot for the university website. Your primary goal is to assist students, faculty, and visitors by providing highly accurate information.

Context:
{context}

Instructions:

You must answer the user's question based ONLY on the information provided in the "Context" block above.

It is strictly forbidden to make up any information, guess, or use your general outside training knowledge.

If the answer to the user's question is not explicitly and clearly found within the "Context", you must reply with exactly this phrase: "عذراً، هذه المعلومة غير متوفرة لدي حالياً. يرجى التواصل مع إدارة الجامعة أو مراجعة الموقع الرسمي."

All of your responses must be in clear, professional, and concise Modern Standard Arabic, even if the user asks their question in a local dialect.
يجب عليك دائماً كتابة رابط المصدر (Source URL) في نهاية إجابتك.
"""

prompt_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("user", "{question}")
])

@app.on_event("startup")
async def startup_event():
    # Optional: Load mock data on startup if DB is empty
    # from .mock_data import load_mock_data
    # load_mock_data()
    pass

@app.get("/")
def read_root():
    return {"status": "University Chatbot Backend (RAG Enabled) Running"}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    user_message = request.message
    
    # 1. Retrieve relevant docs from Chroma (increased k for better context)
    docs = db.search(user_message, k=5)
    
    # Filter out low-relevance results (score threshold)
    # database.py returns a normalized combined score (0 to 1). Lowered to > 0.25 due to FakeEmbeddings.
    high_relevance_docs = [d for d in docs if d.get("score", 0) > 0.25]
    
    # Prepare context text with source information
    context_text = "\n\n".join([
        f"[Source: {d['source']} - Chunk {d.get('chunk_num', '?')}]\n{d['content']}"
        for d in high_relevance_docs
    ])
    
    # 2. Generate Answer (RAG)
    if llm:
        # Real RAG with LangChain
        chain = prompt_template | llm | StrOutputParser()
        answer = chain.invoke({"context": context_text, "question": user_message})
    else:
        # Fallback Mock Logic (if no API Key)
        if high_relevance_docs:
            top_doc = high_relevance_docs[0]
            # Since no LLM is configured, just return the exact matched text and append the source link
            answer = f"{top_doc['content']}\n\nرابط المصدر: {top_doc['source']}"
        else:
            answer = "عذراً، هذه المعلومة غير متوفرة لدي حالياً. يرجى التواصل مع إدارة الجامعة أو مراجعة الموقع الرسمي."

    # 3. Extract best source (take highest relevance)
    best_source = high_relevance_docs[0]["source"] if high_relevance_docs else ""
    
    return {"answer": answer, "source": best_source}

@app.post("/api/learn")
async def learn(request: LearnRequest):
    """Add new knowledge manually."""
    db.add_documents([request.content], [{"source": request.source}])
    return {"message": "Knowledge added to Vector DB!", "content": request.content}

@app.post("/api/load-urls")
async def load_urls(urls: dict):
    """
    Load content from multiple URLs and add to knowledge base.
    
    Example:
    {
        "urls": [
            "https://www.sgu.edu.om/admissions-ar/Undergraduate-Admissions",
            "https://example.com/page"
        ]
    }
    """
    if not urls.get("urls") or not isinstance(urls["urls"], list):
        raise HTTPException(status_code=400, detail="Please provide 'urls' as a list")
    
    result = scrape_and_store_urls(urls["urls"])
    
    if result["failed"] > 0:
        status = f"⚠️  Partial Success: {result['success']} succeeded, {result['failed']} failed"
    else:
        status = f"✅ Success: All {result['success']} URLs loaded!"
    
    return {
        "status": status,
        "summary": result
    }

@app.get("/api/knowledge-sources")
async def get_sources():
    """Get list of all sources in the knowledge base."""
    try:
        all_data = db.vector_db.get(include=['metadatas'])
        
        sources = {}
        for metadata in all_data.get('metadatas', []):
            source = metadata.get('source', 'unknown')
            if source not in sources:
                sources[source] = 0
            sources[source] += 1
        
        return {
            "total_chunks": len(all_data.get('ids', [])),
            "sources": sources,
            "message": "Knowledge base contains these sources"
        }
    except Exception as e:
        return {
            "total_chunks": 0,
            "sources": {},
            "message": f"Knowledge base is empty or error: {str(e)}"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
