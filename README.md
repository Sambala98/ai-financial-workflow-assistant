\# AI Financial Workflow Assistant

![CI](https://github.com/Sambala98/ai-financial-workflow-assistant/actions/workflows/ci.yml/badge.svg)



A production-style FastAPI backend for financial document upload, asynchronous document processing, semantic search, and OpenAI-backed RAG question answering.



This project demonstrates backend engineering, document processing, vector search, background jobs, Docker-based local infrastructure, and LLM integration.



\---



\## Features



\- User registration and login

\- JWT authentication

\- Protected API endpoints

\- Document upload

\- Text extraction from uploaded documents

\- Document chunking

\- Sentence-transformer embedding generation

\- PostgreSQL + pgvector vector storage

\- Semantic search over document chunks

\- OpenAI-backed RAG answer generation

\- Source chunks returned with generated answers

\- Redis + Celery background document processing

\- Docker Compose stack for API, worker, PostgreSQL, and Redis

\- Pytest coverage for auth, health, database, and RAG endpoints



\---



| Layer | Technology |
|---|---|
| Backend API | FastAPI |
| Language | Python |
| Database | PostgreSQL |
| Vector Search | pgvector |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Auth | JWT |
| Background Jobs | Celery |
| Broker/Backend | Redis |
| Embeddings | sentence-transformers |
| LLM | OpenAI API |
| Containers | Docker, Docker Compose |
| Testing | pytest, FastAPI TestClient |



\---



## Architecture

```text
User / Swagger / Frontend
        |
        v
FastAPI API
        |
        +--> JWT Authentication
        |
        +--> Document Upload
        |
        +--> PostgreSQL Metadata
        |
        +--> Redis Queue
                  |
                  v
            Celery Worker
                  |
                  v
        Text Extraction + Chunking + Embeddings
                  |
                  v
        PostgreSQL + pgvector
                  |
                  v
        RAG Search + OpenAI Answer Generation
                  |
                  v
        Answer + Source Chunks
```
