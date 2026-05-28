import re


def fix_spaced_letters(text: str) -> str:
    pattern = r"\b(?:[A-Za-z]\s){2,}[A-Za-z]\b"

    def join_match(match):
        return match.group(0).replace(" ", "")

    return re.sub(pattern, join_match, text)


def normalize_whitespace(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    return text.strip()


def clean_extracted_text(text: str) -> str:
    if not text:
        return ""

    text = fix_spaced_letters(text)
    text = normalize_whitespace(text)
    return text