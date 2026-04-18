"""Nœud Executor : écrit sur disque le scaffolding validé, avec garde-fous stricts."""

import logging
import re
import unicodedata
from pathlib import Path

from config import PROJECT_ROOT
from graph.state import EtatAssistant

logger = logging.getLogger(__name__)

SCAFFOLDING_BASE = PROJECT_ROOT / "scaffolding_output"


def slugifier(nom: str) -> str:
    """ASCII lowercase, tirets, pas de caractères spéciaux."""
    if not nom:
        return "projet"
    nfkd = unicodedata.normalize("NFKD", nom)
    ascii_str = "".join(c for c in nfkd if not unicodedata.combining(c))
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_str).strip("-").lower()
    return slug or "projet"


def _path_est_sur(path: str, base: Path) -> bool:
    """Valide qu'un path relatif reste strictement à l'intérieur de base."""
    if not path or not isinstance(path, str):
        return False
    if path.startswith("/") or path.startswith("\\"):
        return False
    if "\\" in path:
        return False
    parts = path.split("/")
    if any(p in ("", "..", "~") or p.startswith("~") for p in parts):
        return False
    try:
        complet = (base / path).resolve()
        return complet.is_relative_to(base.resolve())
    except (ValueError, OSError):
        return False


def _dossier_unique(base: Path, slug: str) -> Path:
    """Retourne base/slug, ou base/slug-2, -3… si collision."""
    cible = base / slug
    if not cible.exists():
        return cible
    i = 2
    while True:
        alt = base / f"{slug}-{i}"
        if not alt.exists():
            return alt
        i += 1


def ecrire_scaffolding(scaffolding: dict, dry_run: bool = False) -> dict:
    """Écrit les fichiers du scaffolding dans un dossier unique sous scaffolding_output/.

    Atomique : si un path est invalide, aucune écriture. Retourne {dossier_ecrit, nb_fichiers}.
    """
    project_name = slugifier(scaffolding.get("project_name") or "projet")
    files = scaffolding.get("files") or []

    if not files:
        raise ValueError("Aucun fichier à écrire dans le scaffolding.")
    if not isinstance(files, list):
        raise ValueError("Le champ 'files' doit être une liste.")

    SCAFFOLDING_BASE.mkdir(parents=True, exist_ok=True)
    dossier_cible = _dossier_unique(SCAFFOLDING_BASE, project_name)

    # Validation all paths first — atomicité tout-ou-rien
    for f in files:
        if not isinstance(f, dict):
            raise ValueError(f"Fichier mal formé dans la liste : {f!r}")
        path = f.get("path", "")
        if not _path_est_sur(path, dossier_cible):
            raise ValueError(f"Path invalide rejeté : {path!r}")

    if dry_run:
        return {
            "dossier_ecrit": str(dossier_cible),
            "nb_fichiers": len(files),
            "dry_run": True,
        }

    dossier_cible.mkdir(parents=True)
    for f in files:
        chemin = dossier_cible / f["path"]
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(f.get("content", ""), encoding="utf-8")

    logger.info("Scaffolding écrit : %d fichiers dans %s", len(files), dossier_cible)
    return {
        "dossier_ecrit": str(dossier_cible),
        "nb_fichiers": len(files),
        "dry_run": False,
    }


def noeud_executor(etat: EtatAssistant) -> dict:
    """Nœud LangGraph : écrit le scaffolding validé sur disque."""
    scaffolding = etat.get("scaffolding_propose") or {}
    result = ecrire_scaffolding(scaffolding)
    return {"executor_output": result}
