# AI Financial Workflow Assistant

![CI](https://github.com/Sambala98/ai-financial-workflow-assistant/actions/workflows/ci.yml/badge.svg)

A production-style AI document workflow backend built with FastAPI, PostgreSQL, pgvector, Redis, Celery, Docker Compose, JWT authentication, automated tests, and GitHub Actions CI.

This project demonstrates how a real backend system can process uploaded documents asynchronously, convert document text into embeddings, store vectors in PostgreSQL using pgvector, and answer user questions using Retrieval-Augmented Generation, also known as RAG.

---

## Project Overview

AI Financial Workflow Assistant is a backend system that allows authenticated users to upload documents, process them in the background, search document content semantically, and generate AI-powered answers grounded in uploaded document chunks.

The project focuses on real-world backend engineering concepts:

- REST API design
- JWT authentication
- PostgreSQL data modeling
- Alembic migrations
- Redis and Celery background processing
- Document ingestion pipeline
- Text extraction and cleanup
- Chunking with overlap
- Embedding generation
- pgvector semantic search
- OpenAI-backed RAG answer generation
- User-isolated retrieval
- Automated testing with pytest
- GitHub Actions CI
- Docker Compose full-stack setup

---

## Tech Stack

### Backend

- Python
- FastAPI
- Pydantic v2
- SQLAlchemy ORM
- Alembic

### Database

- PostgreSQL
- pgvector

### Background Processing

- Redis
- Celery

### AI / RAG

- Sentence Transformers
- pgvector similarity search
- OpenAI API
- Source-grounded RAG responses

### DevOps / Testing

- Docker
- Docker Compose
- Pytest
- GitHub Actions CI

---

## Core Features

### Authentication

- User registration
- User login
- JWT-based authentication
- Protected API routes
- Authenticated RAG search and answer endpoints

### Document Management

- Upload documents
- Store document metadata
- Track document processing status
- Retrieve uploaded documents
- Retrieve document chunks

Supported document statuses:

```text
UPLOADED
PROCESSING
PROCESSED
FAILED
````

---

## Document Processing Pipeline

Uploaded documents are processed through this pipeline:

```text
Document Upload
↓
Text Extraction
↓
Text Cleanup
↓
Chunking with Overlap
↓
Embedding Generation
↓
pgvector Storage
↓
Semantic Search
↓
RAG Answer Generation
```

The document processing work runs asynchronously using Celery and Redis, so long-running work does not block API requests.

---

## Text Cleanup

The system includes a text cleanup layer to improve poor PDF extraction quality.

Example:

```text
Before:
A l p h a  B e t a
D a t a  E n g i n e e r

After:
Alpha Beta
Data Engineer
```

This improves:

* Chunk quality
* Embedding quality
* Semantic search accuracy
* Final RAG answer relevance

---

## Chunking with Overlap

The project uses overlap-based chunking to preserve context across chunk boundaries.

Example:

```text
Chunk 1:
Redis and Celery are used for background document processing...

Chunk 2:
background document processing helps avoid blocking API requests...
```

This prevents important information from being cut off between chunks.

---

## RAG Search

The `/rag/search` endpoint performs semantic search over document chunks stored in PostgreSQL with pgvector.

Example request:

```json
{
  "query": "What tools are used for background processing?",
  "top_k": 3
}
```

The system generates an embedding for the question, compares it with stored document chunk embeddings, and returns the most relevant chunks.

---

## RAG Answer Generation

The `/rag/answer` endpoint retrieves relevant chunks, builds a grounded prompt, sends the context to OpenAI, and returns an answer with source chunks.

Response includes:

* User question
* Generated answer
* Source chunks
* Document IDs
* Chunk indexes
* Similarity distance

The system also includes a safe fallback when `OPENAI_API_KEY` is not configured.

---

## Architecture

```text
User
↓
FastAPI API
↓
JWT Authentication
↓
Document Upload
↓
PostgreSQL Metadata Storage
↓
Redis Queue
↓
Celery Worker
↓
Text Extraction
↓
Text Cleanup
↓
Chunking
↓
Embedding Generation
↓
PostgreSQL + pgvector
↓
RAG Search
↓
OpenAI Answer Generation
↓
Answer + Sources
```

---

## API Endpoints

### Auth

```text
POST /auth/register
POST /auth/login
GET  /auth/me
```

### Documents

```text
POST /documents/upload
GET  /documents
GET  /documents/{document_id}
POST /documents/{document_id}/extract-text
POST /documents/{document_id}/chunks
GET  /documents/{document_id}/chunks
POST /documents/{document_id}/process
```

### RAG

```text
POST /rag/search
POST /rag/answer
```

### Health

```text
GET /health
```

---

## Background Processing

Document processing runs asynchronously using Celery and Redis.

The worker handles:

* Text extraction
* Text cleanup
* Chunk generation
* Embedding generation
* Old chunk cleanup during reprocessing
* Document status updates
* Failure handling

Successful processing:

```text
UPLOADED → PROCESSING → PROCESSED
```

Failed processing:

```text
UPLOADED → PROCESSING → FAILED
```

This prevents documents from staying stuck in `PROCESSING` when extraction, chunking, or embedding generation fails.

---

## User Isolation

RAG retrieval is scoped by authenticated user ID.

This means one user cannot retrieve another user's document chunks.

Example:

```text
User A uploads a financial document.
User B asks a related question.
User B cannot retrieve User A's document chunks.
```

This is important for financial and private document workflows.

---

## Testing

The project includes automated tests for:

* Database connection
* User registration
* User login
* Protected route access
* Health check
* RAG authentication protection
* RAG search
* RAG answer
* RAG source retrieval
* RAG user isolation
* Text cleanup
* Chunking with overlap
* Celery document processing success path
* Celery document processing failure path
* Test database cleanup fixture

Current test status:

```text
20 passed
```

Run tests locally:

```bash
python -m pytest -v
```

---

## CI Pipeline

GitHub Actions CI runs automatically on push and pull requests.

The CI workflow:

```text
Checkout code
↓
Set up Python
↓
Start PostgreSQL with pgvector
↓
Start Redis
↓
Install dependencies
↓
Run Alembic migrations
↓
Run Pytest
```

If tests fail, the CI pipeline fails.

---

## Docker Setup

Start the full backend stack:

```bash
docker compose up -d
```

Services included:

```text
FastAPI API
Celery worker
PostgreSQL with pgvector
Redis
```

Check running containers:

```bash
docker compose ps
```

---

## Local Development Setup

### 1. Clone the repository

```bash
git clone https://github.com/Sambala98/ai-financial-workflow-assistant.git
cd ai-financial-workflow-assistant
```

### 2. Create and activate virtual environment

Windows:

```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start Docker services

```bash
docker compose up -d
```

### 5. Run migrations

```bash
python -m alembic upgrade head
```

### 6. Run tests

```bash
python -m pytest -v
```

### 7. Start API locally

```bash
python -m uvicorn app.main:app --reload
```

Swagger UI:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/health
```

---

## Environment Variables

Example `.env`:

```env
APP_NAME=AI Financial Workflow Assistant
APP_ENV=development

DATABASE_URL=postgresql+psycopg2://postgres:postgres123@localhost:5433/ai_financial_db

JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

REDIS_URL=redis://localhost:6379/0

OPENAI_API_KEY=
OPENAI_MODEL=gpt-5.2
```

If `OPENAI_API_KEY` is missing, the system returns a safe fallback response instead of crashing.

---

## Key Engineering Highlights

### Production-Style Backend Architecture

The project separates responsibilities across API routes, services, database models, background tasks, and tests.

### Async Document Processing

Long-running document processing is handled by Celery workers instead of blocking API requests.

### Reliable RAG Pipeline

The RAG flow includes text cleanup, overlap-based chunking, embeddings, semantic search, and source-grounded answer generation.

### User-Isolated Retrieval

RAG search filters chunks by authenticated user ID to prevent cross-user data leakage.

### Failure Handling

If document processing fails, the document is marked as `FAILED` instead of remaining stuck in `PROCESSING`.

### Automated Testing

The project includes meaningful tests for both success and failure paths, not just basic endpoint checks.

### CI Automation

GitHub Actions runs the test suite automatically using PostgreSQL with pgvector and Redis.

---


## Future Improvements

Planned production-level improvements:

* Cloud deployment
* S3/object storage for uploaded files
* Secrets manager integration
* Structured logging
* Monitoring and error tracking
* Admin dashboard
* Role-based admin APIs
* Load testing
* CD deployment pipeline
* HTTPS/domain setup

---

## Project Status

```text
Production-style backend project
Core backend + RAG pipeline completed
Docker Compose full stack completed
Automated tests completed
GitHub Actions CI completed
20 tests passing
```

This project demonstrates backend engineering, AI/RAG architecture, async processing, database design, testing, and CI practices.

````

