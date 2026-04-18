"""Configuration centralisée du POC, chargée depuis .env."""

import sys
from pathlib import Path

from dotenv import load_dotenv
import os

load_dotenv()


def _require_env(name: str) -> str:
    """Lit une variable d'environnement obligatoire ou quitte avec un message clair."""
    value = os.getenv(name)
    if not value:
        print(f"ERREUR : la variable d'environnement {name} est manquante. Voir .env.example.")
        sys.exit(1)
    return value


# --- Clés API ---
ANTHROPIC_API_KEY: str = _require_env("ANTHROPIC_API_KEY")
OPENAI_API_KEY: str = _require_env("OPENAI_API_KEY")

# --- Modèles ---
LLM_MODEL: str = os.getenv("LLM_MODEL", "claude-sonnet-4-5-20250929")
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# --- ChromaDB ---
CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")
CHROMA_COLLECTION: str = os.getenv("CHROMA_COLLECTION", "bb_technical_docs")

# --- Retriever ---
RETRIEVER_K: int = int(os.getenv("RETRIEVER_K", "5"))

# --- Graphe ---
MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "3"))

# --- Chemins utiles ---
PROJECT_ROOT: Path = Path(__file__).parent
DATA_DIR: Path = PROJECT_ROOT / "data"
FAKE_BB_DOCS_DIR: Path = PROJECT_ROOT / "ingestion" / "fake_bb_docs"
