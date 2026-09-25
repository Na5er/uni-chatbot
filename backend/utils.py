import re

def normalize_arabic(text: str) -> str:
    """
    Normalizes Arabic text by:
    1. Removing diacritics (Tashkeel).
    2. Unifying Alef forms (أ, إ, آ -> ا).
    3. Unifying Yeh forms (ى -> ي).
    4. Unifying Teh Marbuta (ة -> ه).
    """
    if not text:
        return ""

    # Remove Diacritics (Fatha, Damma, Kasra, etc.)
    text = re.sub(r'[\u064B-\u065F\u0670]', '', text)

    # Unify Alef (أ, إ, آ -> ا)
    text = re.sub(r'[أإآ]', 'ا', text)

    # Unify Yeh (ى -> ي)
    text = re.sub(r'ى', 'ي', text)

    # Unify Teh Marbuta (ة -> ه)
    text = re.sub(r'ة', 'ه', text)

    return text.strip()
