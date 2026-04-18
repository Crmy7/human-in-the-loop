"""Découpage des documents en chunks de 500-800 tokens avec overlap."""

import re
from typing import Optional

import tiktoken

CHUNK_SIZE_TOKENS = 600
CHUNK_OVERLAP_TOKENS = 100

_encoding = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """Nombre de tokens cl100k_base du texte."""
    return len(_encoding.encode(text))


def _last_heading(text: str) -> str:
    """Dernier titre markdown (#, ##, ###) trouvé dans le texte, sinon chaîne vide."""
    matches = re.findall(r"^#{1,3}\s+(.+?)\s*$", text, flags=re.MULTILINE)
    return matches[-1].strip() if matches else ""


def chunk_document(content: str, metadata: dict) -> list[dict]:
    """Découpe content en chunks de ~600 tokens (overlap 100) en conservant metadata."""
    tokens = _encoding.encode(content)
    if len(tokens) == 0:
        return []

    section_root = _last_heading(content.split("\n", 1)[0]) or metadata.get("section", "")

    if len(tokens) <= CHUNK_SIZE_TOKENS:
        meta = {**metadata, "section": _last_heading(content) or section_root}
        return [{"content": content, "metadata": meta}]

    chunks: list[dict] = []
    step = CHUNK_SIZE_TOKENS - CHUNK_OVERLAP_TOKENS
    for start in range(0, len(tokens), step):
        end = start + CHUNK_SIZE_TOKENS
        window = tokens[start:end]
        if not window:
            break
        chunk_text = _encoding.decode(window)
        scope_text = _encoding.decode(tokens[: start + 20])
        meta = {**metadata, "section": _last_heading(scope_text) or section_root}
        chunks.append({"content": chunk_text, "metadata": meta})
        if end >= len(tokens):
            break
    return chunks


def chunk_many(documents: list[dict]) -> list[dict]:
    """Applique chunk_document à une liste [{content, metadata}, ...]."""
    out: list[dict] = []
    for doc in documents:
        out.extend(chunk_document(doc["content"], doc["metadata"]))
    return out
