import os
import pandas as pd
from pypdf import PdfReader
from app.services.text_cleaning_service import clean_extracted_text


def extract_text_from_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        return file.read()


def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)

    text_parts = []

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text_parts.append(page_text)

    return "\n".join(text_parts)


def extract_text_from_csv(file_path: str) -> str:
    dataframe = pd.read_csv(file_path)
    return dataframe.to_string(index=False)


def extract_text_from_document(file_path: str, content_type: str | None) -> str:
    if content_type == "text/plain":
        extracted_text = extract_text_from_txt(file_path)
    elif content_type == "application/pdf":
        extracted_text = extract_text_from_pdf(file_path)
    elif content_type == "text/csv":
        extracted_text = extract_text_from_csv(file_path)
    else:
        raise ValueError("Unsupported file type")

    return clean_extracted_text(extracted_text)

