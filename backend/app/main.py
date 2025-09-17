from fastapi import FastAPI
import logging
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from .api import router
from .models import Base, engine

# Load environment variables
load_dotenv()

# Honor LOG_LEVEL but rely on Uvicorn --log-config for format/colors
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()
logging.getLogger().setLevel(LOG_LEVEL)

app = FastAPI(
    title="Hidden Channels Backend",
    description="Backend for secret message game",
    version="0.1.0"
)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    _log = logging.getLogger("app.startup")
    _log.debug("hello world (debug)")
    _log.warning("hello world (warning)")
    async with engine.begin() as conn:
        # Create tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Hidden Channels API",
        "version": "0.1.0",
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)