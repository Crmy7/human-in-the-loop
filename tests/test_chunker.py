"""Tests pour ingestion/chunker.py."""

from ingestion.chunker import (
    CHUNK_OVERLAP_TOKENS,
    CHUNK_SIZE_TOKENS,
    chunk_document,
    chunk_many,
    count_tokens,
)


def test_document_court_retourne_un_seul_chunk():
    content = "# Titre\n\nUn paragraphe très court."
    result = chunk_document(content, {"source_type": "test", "source_path": "a.md"})
    assert len(result) == 1
    assert result[0]["content"] == content
    assert result[0]["metadata"]["section"] == "Titre"


def test_document_long_est_decoupe_avec_overlap():
    paragraphe = "Phrase de remplissage qui contient assez de tokens pour générer un chunk. " * 80
    content = f"# Intro\n\n{paragraphe}\n\n## Section Deux\n\n{paragraphe}"
    total_tokens = count_tokens(content)
    assert total_tokens > CHUNK_SIZE_TOKENS

    result = chunk_document(content, {"source_type": "test", "source_path": "b.md"})
    assert len(result) >= 2

    for chunk in result:
        taille = count_tokens(chunk["content"])
        assert taille <= CHUNK_SIZE_TOKENS
        assert chunk["metadata"]["source_type"] == "test"
        assert chunk["metadata"]["source_path"] == "b.md"

    first_tokens = chunk_document.__globals__["_encoding"].encode(result[0]["content"])
    second_tokens = chunk_document.__globals__["_encoding"].encode(result[1]["content"])
    tail = first_tokens[-CHUNK_OVERLAP_TOKENS:]
    head = second_tokens[:CHUNK_OVERLAP_TOKENS]
    assert tail == head


def test_section_reflete_dernier_titre_visible():
    content = (
        "# Intro\n\n"
        + ("intro. " * 200)
        + "\n\n## Déploiement\n\n"
        + ("deploy. " * 200)
    )
    result = chunk_document(content, {"source_type": "test", "source_path": "c.md"})
    sections = [c["metadata"]["section"] for c in result]
    assert "Intro" in sections
    assert "Déploiement" in sections


def test_chunk_many_concatene():
    docs = [
        {"content": "# A\n\ncourt", "metadata": {"source_type": "t", "source_path": "a.md"}},
        {"content": "# B\n\ncourt", "metadata": {"source_type": "t", "source_path": "b.md"}},
    ]
    result = chunk_many(docs)
    assert len(result) == 2
    assert {c["metadata"]["source_path"] for c in result} == {"a.md", "b.md"}


def test_document_vide():
    assert chunk_document("", {"source_type": "t", "source_path": "x.md"}) == []
