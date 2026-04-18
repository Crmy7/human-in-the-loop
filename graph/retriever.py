"""Nœud Retriever : similarity search k=5 sur ChromaDB, filtre source_type optionnel."""

from typing import Optional

import chromadb
from openai import OpenAI

from config import (
    CHROMA_COLLECTION,
    CHROMA_PERSIST_DIR,
    EMBEDDING_MODEL,
    OPENAI_API_KEY,
    RETRIEVER_K,
)
from graph.state import EtatAssistant


_openai_client: Optional[OpenAI] = None
_collection = None


def _client_openai() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=OPENAI_API_KEY)
    return _openai_client


def _collection_chroma():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        _collection = client.get_collection(name=CHROMA_COLLECTION)
    return _collection


def rechercher(
    question: str,
    k: int = RETRIEVER_K,
    source_type: Optional[str] = None,
) -> list[dict]:
    """Retourne les k passages les plus proches sémantiquement de la question."""
    embedding = _client_openai().embeddings.create(
        model=EMBEDDING_MODEL,
        input=[question],
    ).data[0].embedding

    where = {"source_type": source_type} if source_type else None
    resultats = _collection_chroma().query(
        query_embeddings=[embedding],
        n_results=k,
        where=where,
    )

    passages: list[dict] = []
    for doc, meta, dist in zip(
        resultats["documents"][0],
        resultats["metadatas"][0],
        resultats["distances"][0],
    ):
        passages.append(
            {
                "content": doc,
                "metadata": meta,
                "distance": dist,
            }
        )
    return passages


def noeud_retriever(etat: EtatAssistant) -> dict:
    """Nœud LangGraph : enrichit l'état avec les passages trouvés."""
    question = etat["question"]
    passages = rechercher(question)
    return {"passages": passages}
