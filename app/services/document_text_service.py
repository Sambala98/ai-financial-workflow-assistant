import os
import pandas as pd
from pypdf import PdfReader


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
    if not os.path.exists(file_path):
        raise FileNotFoundError("File not found")

    if content_type == "text/plain":
        return extract_text_from_txt(file_path)

    if content_type == "application/pdf":
        return extract_text_from_pdf(file_path)

    if content_type == "text/csv":
        return extract_text_from_csv(file_path)

    raise ValueError("Unsupported file type")