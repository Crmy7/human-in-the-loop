"""Script one-shot : charge tous les corpus, chunk, embed et peuple ChromaDB."""

import logging

import chromadb
from openai import OpenAI

from config import (
    CHROMA_COLLECTION,
    CHROMA_PERSIST_DIR,
    EMBEDDING_MODEL,
    OPENAI_API_KEY,
)
from ingestion.chunker import chunk_many
from ingestion.docusaurus import lire_fake_bb_docs
from ingestion.github import crawler_nuxt, crawler_symfony

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("ingestion.run_all")

EMBEDDING_BATCH_SIZE = 100


def _embed_batch(client: OpenAI, textes: list[str]) -> list[list[float]]:
    """Calcule les embeddings pour une liste de textes, par lots."""
    sorties: list[list[float]] = []
    for i in range(0, len(textes), EMBEDDING_BATCH_SIZE):
        lot = textes[i : i + EMBEDDING_BATCH_SIZE]
        response = client.embeddings.create(model=EMBEDDING_MODEL, input=lot)
        sorties.extend(item.embedding for item in response.data)
        logger.info("embeddings : %d / %d", min(i + EMBEDDING_BATCH_SIZE, len(textes)), len(textes))
    return sorties


def ingerer() -> None:
    """Pipeline complet d'ingestion : corpus → chunks → embeddings → Chroma."""
    logger.info("1/4 — chargement des corpus")
    documents = lire_fake_bb_docs()
    logger.info("  BB® internes : %d", len(documents))

    nuxt = crawler_nuxt()
    logger.info("  Nuxt : %d", len(nuxt))
    documents.extend(nuxt)

    symfony = crawler_symfony()
    logger.info("  Symfony : %d", len(symfony))
    documents.extend(symfony)

    if not documents:
        raise RuntimeError("Aucun document chargé. Vérifie le corpus BB® et la connectivité.")

    logger.info("2/4 — découpage en chunks")
    chunks = chunk_many(documents)
    logger.info("  total chunks : %d", len(chunks))

    logger.info("3/4 — calcul des embeddings OpenAI (%s)", EMBEDDING_MODEL)
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    textes = [c["content"] for c in chunks]
    embeddings = _embed_batch(openai_client, textes)

    logger.info("4/4 — upsert dans ChromaDB (%s)", CHROMA_PERSIST_DIR)
    chroma = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    try:
        chroma.delete_collection(CHROMA_COLLECTION)
    except Exception:
        pass
    collection = chroma.create_collection(
        name=CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )

    ids = [f"{c['metadata']['source_path']}#{i}" for i, c in enumerate(chunks)]
    metadatas = [c["metadata"] for c in chunks]
    collection.add(ids=ids, embeddings=embeddings, documents=textes, metadatas=metadatas)
    logger.info("  %d chunks indexés dans la collection '%s'", len(chunks), CHROMA_COLLECTION)


if __name__ == "__main__":
    ingerer()
