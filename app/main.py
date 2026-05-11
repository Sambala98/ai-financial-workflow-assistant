from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Backend API for financial document upload, RAG question answering, and AI workflow automation."
)


@app.get("/")
def root():
    return {
        "message": f"{settings.PROJECT_NAME} API is running",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }