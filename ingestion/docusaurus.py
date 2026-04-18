"""Ingestion des fichiers Markdown locaux (fake_bb_docs par défaut, ou dossier arbitraire)."""

from pathlib import Path

from config import FAKE_BB_DOCS_DIR


def lire_dossier_markdown(
    dossier: Path,
    source_type: str = "bb_internal",
) -> list[dict]:
    """Retourne la liste des documents [{content, metadata}] pour tous les .md du dossier."""
    dossier = Path(dossier)
    if not dossier.exists():
        raise FileNotFoundError(f"Dossier introuvable : {dossier}")

    documents: list[dict] = []
    for path in sorted(dossier.rglob("*.md")):
        content = path.read_text(encoding="utf-8")
        if not content.strip():
            continue
        rel = path.relative_to(dossier)
        documents.append(
            {
                "content": content,
                "metadata": {
                    "source_type": source_type,
                    "source_path": str(rel),
                    "section": "",
                    "url": "",
                },
            }
        )
    return documents


def lire_fake_bb_docs() -> list[dict]:
    """Raccourci pour le corpus BB® par défaut."""
    return lire_dossier_markdown(FAKE_BB_DOCS_DIR, source_type="bb_internal")
