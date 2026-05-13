from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Backend API for financial document upload, RAG question answering, and AI workflow automation."
)

app.include_router(auth_router)


@app.get("/")
def root():
    return {
        "message": f"{settings.APP_NAME} API is running",
        "environment": settings.APP_ENV
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }