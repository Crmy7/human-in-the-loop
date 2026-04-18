"""Utilitaires transverses : picker dossier, détection langage, citations, qualité Critic."""

import re
import subprocess
import sys
from pathlib import Path

FORMULE_REFUS = (
    "La documentation interne BB® et les sources publiques indexées ne couvrent pas ce point."
)

EXT_TO_LANG: dict[str, str] = {
    ".ts": "typescript", ".tsx": "typescript",
    ".js": "javascript", ".jsx": "javascript",
    ".py": "python", ".json": "json",
    ".yaml": "yaml", ".yml": "yaml",
    ".md": "markdown", ".sh": "bash", ".bash": "bash",
    ".php": "php", ".vue": "html", ".html": "html",
    ".css": "css", ".scss": "scss",
    ".env": "ini", ".example": "ini", ".toml": "toml",
}


def langage_pour(path: str) -> str:
    """Détermine le langage à passer à st.code() depuis le nom de fichier."""
    if path.endswith("Makefile") or path.endswith("makefile"):
        return "makefile"
    if path.endswith("Dockerfile"):
        return "dockerfile"
    return EXT_TO_LANG.get(Path(path).suffix.lower(), "text")


def ouvrir_picker_dossier(titre: str = "Choisir un dossier") -> str | None:
    """Ouvre le picker natif de l'OS.

    macOS : AppleScript via osascript (vrai dialog Finder, pas d'app Python visible).
    Linux/Windows : fallback tkinter via subprocess.
    """
    if sys.platform == "darwin":
        titre_echape = titre.replace('"', '\\"')
        script = f'POSIX path of (choose folder with prompt "{titre_echape}")'
        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode == 0:
                return result.stdout.strip().rstrip("/") or None
            return None
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    code = (
        "import tkinter as tk\n"
        "from tkinter import filedialog\n"
        "r = tk.Tk(); r.withdraw(); r.attributes('-topmost', True)\n"
        f"p = filedialog.askdirectory(title={titre!r})\n"
        "r.destroy(); print(p)\n"
    )
    try:
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, timeout=300
        )
        return result.stdout.strip() or None
    except Exception:
        return None


_RE_CITATION = re.compile(r"\[([a-zA-Z0-9_\-./#]+\.md|/[a-zA-Z0-9_\-./]+)\]")


def citations(texte: str) -> set[str]:
    """Extrait les [source_path] cités inline dans une réponse Markdown."""
    return set(_RE_CITATION.findall(texte or ""))


def hallucinations(reponse: str, passages: list[dict]) -> list[str]:
    """Retourne les sources citées dans la réponse qui ne sont pas dans les passages."""
    dispo: set[str] = set()
    for p in passages:
        m = p.get("metadata") or {}
        if m.get("source_path"):
            dispo.add(m["source_path"])
        if m.get("url"):
            dispo.add(m["url"])
    return sorted(citations(reponse) - dispo)


def mode_qualite(rapport: dict, brouillon: str, hallus: list[str]) -> tuple[str, str, str]:
    """Retourne (mode, libellé court, classe-badge).

    mode ∈ {"refus", "attention", "confiance"}.
    """
    if FORMULE_REFUS.lower() in (brouillon or "").lower():
        return "refus", "refus", "bb-badge-stop"
    score = float(rapport.get("confidence_score", 0.0))
    warnings = rapport.get("warnings") or []
    if hallus or warnings or score < 0.5 or rapport.get("source_grounding") == "low":
        return "attention", f"attention · {score:.2f}", "bb-badge-warn"
    return "confiance", f"confiance {score:.2f}", "bb-badge-ok"


def badge(label: str, classe: str) -> str:
    """Markup HTML pour un badge pastillé (à passer à st.markdown unsafe_allow_html)."""
    return f'<span class="bb-badge {classe}">{label}</span>'


def source_label(source_type: str) -> str:
    """Libellé court pour l'affichage d'une source selon son type."""
    return {
        "bb_internal": "BB®",
        "nuxt_official": "Nuxt",
        "symfony_official": "Symfony",
    }.get(source_type, source_type or "?")
