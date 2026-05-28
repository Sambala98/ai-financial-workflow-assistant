\# AI Financial Workflow Assistant



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



\## Tech Stack



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



\## Architecture



```text

User / Swagger / Frontend

&#x20;       |

&#x20;       v

FastAPI API

&#x20;       |

&#x20;       +--> JWT Authentication

&#x20;       |

&#x20;       +--> Document Upload

&#x20;       |

&#x20;       +--> PostgreSQL Metadata

&#x20;       |

&#x20;       +--> Redis Queue

&#x20;                 |

&#x20;                 v

&#x20;           Celery Worker

&#x20;                 |

&#x20;                 v

&#x20;       Text Extraction + Chunking + Embeddings

&#x20;                 |

&#x20;                 v

&#x20;       PostgreSQL + pgvector

&#x20;                 |

&#x20;                 v

&#x20;       RAG Search + OpenAI Answer Generation

&#x20;                 |

&#x20;                 v

&#x20;       Answer + Source Chunks

