import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

load_dotenv()


def openai_configured() -> bool:
    api_key = os.getenv("OPENAI_API_KEY")
    return bool(api_key and api_key.strip())


def build_rag_prompt(question: str, source_chunks: list[dict[str, Any]]) -> str:
    context_parts = []

    for index, chunk in enumerate(source_chunks, start=1):
        chunk_text = chunk.get("chunk_text", "")
        document_id = chunk.get("document_id")
        chunk_index = chunk.get("chunk_index")

        context_parts.append(
            f"""
Source {index}
Document ID: {document_id}
Chunk Index: {chunk_index}
Content:
{chunk_text}
""".strip()
        )

    context = "\n\n---\n\n".join(context_parts)

    return f"""
You are an AI assistant for a document-based RAG system.

Rules:
1. Answer the user's question using only the provided context.
2. If the answer is not clearly present in the context, say: "I could not find enough information in the uploaded documents."
3. Do not invent facts.
4. Keep the answer clear and natural.
5. Mention the most relevant source numbers when useful.

Context:
{context}

Question:
{question}

Answer:
""".strip()


def generate_llm_answer(question: str, source_chunks: list[dict[str, Any]]) -> str:
    if not source_chunks:
        return "I could not find enough relevant document chunks to answer this question."

    if not openai_configured():
        return (
            "OpenAI API key is not configured, so real LLM answer generation is disabled. "
            "Add OPENAI_API_KEY to your .env file, or use a local Ollama model as an alternative."
        )

    prompt = build_rag_prompt(question=question, source_chunks=source_chunks)

    model = os.getenv("OPENAI_MODEL", "gpt-5.2")

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.responses.create(
            model=model,
            input=prompt,
        )

        answer = response.output_text.strip()

        if not answer:
            return "The LLM returned an empty response."

        return answer

    except OpenAIError as exc:
        return f"LLM generation failed: {str(exc)}"

    except Exception as exc:
        return f"Unexpected LLM error: {str(exc)}"