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
from core.logger import get_logger
from api.routes import trips, stream, profiles, surprise, concierge

load_dotenv()
logger = get_logger("api_main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Travel Buddy FastAPI Backend Service...")
    
    # Initialize LLM
    gemini_key = os.getenv("GOOGLE_API_KEY")
    if not gemini_key:
        logger.warning("⚠️ GOOGLE_API_KEY environment variable is not set!")
    else:
        logger.info("✅ Google Gemini LLM key configured successfully.")
    
    app.state.llm = ChatGoogleGenerativeAI(
        model='gemini-3.1-flash-lite', 
        google_api_key=gemini_key or "dummy_key_for_init"
    )

    # Initialize search tool
    tavily_key = os.getenv("TAVILY_API_KEY")
    if not tavily_key:
        logger.warning("⚠️ TAVILY_API_KEY environment variable is not set!")
    else:
        logger.info("✅ Tavily Search API key configured successfully.")
    
    if TavilySearchResults:
        app.state.search_tool = TavilySearchResults(
            max_results=3, 
            tavily_api_key=tavily_key or "dummy_key_for_init"
        )

    # Initialize DB
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    if supabase_url and supabase_key:
        init_db(supabase_url, supabase_key)
        logger.info("✅ Supabase Database initialized.")
    else:
        logger.info("ℹ️ Supabase credentials omitted — using local JSON storage fallback.")

    logger.info("✨ Travel Buddy API backend ready to serve requests!")
    yield
    logger.info("🛑 Shutting down Travel Buddy FastAPI backend.")

app = FastAPI(title="Travel Buddy API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trips.router, prefix="/api/trips", tags=["trips"])
app.include_router(stream.router, prefix="/api/ws", tags=["stream"])
app.include_router(profiles.router, prefix="/api", tags=["profiles"])
app.include_router(surprise.router, prefix="/api/surprise", tags=["surprise"])
app.include_router(concierge.router, prefix="/api/concierge", tags=["concierge"])

@app.get("/")
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Travel Buddy API is live"}
