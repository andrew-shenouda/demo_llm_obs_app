# entry point for the backend
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from agent_endpoints import agent_router

# Create the FastAPI application instance
app = FastAPI()

# Add CORS middleware to allow cross-origin requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Allow all origins
    allow_credentials=True,     # Allow cookies and authentication headers
    allow_methods=["*"],        # Allow all HTTP methods
    allow_headers=["*"],        # Allow all headers
)

# Include the API router from endpoints.py
app.include_router(agent_router)
