from fastapi import FastAPI
from app.api import router as api_router

app = FastAPI(title="LLM Query Processor")

app.include_router(api_router, prefix="/api")
