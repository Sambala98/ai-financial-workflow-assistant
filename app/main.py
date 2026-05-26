from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from app.api.documents import router as documents_router
from app.core.config import settings
from app.api.rag import router as rag_router

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Backend API for financial document upload, RAG question answering, and AI workflow automation."
)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(documents_router)
app.include_router(rag_router)


@app.get("/")
def root():
    return {
        "message": f"{settings.app_name} API is running",
        "environment": settings.app_env
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }