# Standard library imports
import uvicorn
import gradio as gr
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Local imports
from src.api.endpoints.parser import router as resume_router
from configs.config import APP_CONFIG
from app import ResumeParser

# get constants
HOST = APP_CONFIG["HOST"]
PORT = APP_CONFIG["PORT"]

# create the fastapi app
app = FastAPI(
    title="Resume Parser",
    description="Advanced Resume Parsing API with LLM capabilities",
    version="1.0.0",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(resume_router, prefix="/api/v1")

# Create and mount Gradio interface
parser = ResumeParser()
demo = parser.create_interface()
app = gr.mount_gradio_app(app, demo, path="/")


if __name__ == "__main__":
    uvicorn.run("src.main:app", host=HOST, port=PORT, log_level="info", reload=True)
