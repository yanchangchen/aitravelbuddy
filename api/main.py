import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI

try:
    from langchain_tavily import TavilySearch as TavilySearchResults
except ImportError:
    try:
        from langchain_community.tools.tavily_search import TavilySearchResults
    except ImportError:
        TavilySearchResults = None

from core.db import init_db
from api.routes import trips, stream, profiles, surprise, concierge

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize LLM
    gemini_key = os.getenv("GOOGLE_API_KEY")
    if not gemini_key:
        print("Warning: GOOGLE_API_KEY not set")
    
    app.state.llm = ChatGoogleGenerativeAI(
        model='gemini-3.1-flash-lite', 
        google_api_key=gemini_key
    )

    # Initialize search tool
    tavily_key = os.getenv("TAVILY_API_KEY")
    if not tavily_key:
        print("Warning: TAVILY_API_KEY not set")
    
    app.state.search_tool = TavilySearchResults(
        max_results=3, 
        tavily_api_key=tavily_key
    )

    # Initialize DB
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    if supabase_url and supabase_key:
        init_db(supabase_url, supabase_key)
    else:
        print("Warning: Supabase credentials not fully set, DB features may not work")

    yield

app = FastAPI(title="Travel Buddy API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trips.router, prefix="/api/trips", tags=["trips"])
app.include_router(stream.router, prefix="/api/ws", tags=["stream"])
app.include_router(profiles.router, prefix="/api", tags=["profiles"])
app.include_router(surprise.router, prefix="/api/surprise", tags=["surprise"])
app.include_router(concierge.router, prefix="/api/concierge", tags=["concierge"])

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
