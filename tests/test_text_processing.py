from app.services.text_cleaning_service import clean_extracted_text
from app.services.chunking_service import chunk_text


def test_clean_extracted_text_fixes_spaced_letters():
    text = "A l p h a  B e t a\n\n\nD a t a     E n g i n e e r"

    cleaned = clean_extracted_text(text)

    assert "Alpha Beta" in cleaned
    assert "Data Engineer" in cleaned


def test_clean_extracted_text_normalizes_whitespace():
    text = "FastAPI      PostgreSQL\n\n\n\nRedis        Celery"

    cleaned = clean_extracted_text(text)

    assert "FastAPI PostgreSQL" in cleaned
    assert "Redis Celery" in cleaned
    assert "\n\n\n" not in cleaned


def test_chunk_text_returns_empty_list_for_empty_text():
    chunks = chunk_text("")

    assert chunks == []


def test_chunk_text_creates_overlapping_chunks():
    text = "abcdefghijklmnopqrstuvwxyz"

    chunks = chunk_text(text, chunk_size=10, overlap=3)

    assert chunks[0] == "abcdefghij"
    assert chunks[1] == "hijklmnopq"
    assert chunks[2] == "opqrstuvwx"


def test_chunk_text_rejects_invalid_overlap():
    try:
        chunk_text("sample text", chunk_size=10, overlap=10)
        assert False
    except ValueError as exc:
        assert str(exc) == "overlap must be smaller than chunk_size"