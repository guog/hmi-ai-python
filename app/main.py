"""Main entry point for the application."""

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import image2hmi, text2hmi

# Load environment variables
load_dotenv()

# Initialize FastAPI app with a maximum body size of 10 MB
app = FastAPI(max_body_size=10 * 1024 * 1024)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# Include API router
app.include_router(text2hmi.router)
app.include_router(image2hmi.router)
