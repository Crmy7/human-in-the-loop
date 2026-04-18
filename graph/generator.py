"""Nœud Generator : produit une réponse ancrée sur les passages récupérés.

Deux modes :
- question : sortie en prose Markdown avec citations inline
- scaffolding : sortie JSON strict {project_name, description, files[]}
"""

import json
import logging
import re

from graph.llm_client import appeler_llm
from graph.prompts import GENERATOR_SCAFFOLDING_SYSTEM, GENERATOR_SYSTEM
from graph.state import EtatAssistant

logger = logging.getLogger(__name__)

MAX_TOKENS_GENERATION = 1200
MAX_TOKENS_SCAFFOLDING = 3000
MAX_RETRIES_JSON = 1


def _formater_passages(passages: list[dict]) -> str:
    blocs: list[str] = []
    for i, p in enumerate(passages, start=1):
        meta = p.get("metadata", {})
        source = meta.get("source_path") or meta.get("url") or "source_inconnue"
        section = meta.get("section", "")
        entete = f"[{i}] source_path: {source}"
        if section:
            entete += f" | section: {section}"
        blocs.append(f"{entete}\n{p['content']}")
    return "\n\n---\n\n".join(blocs)


def _construire_message_utilisateur(
    question: str,
    passages: list[dict],
    commentaire_rejet: str | None,
) -> str:
    parties = [f"QUESTION :\n{question}"]
    parties.append("PASSAGES :\n" + _formater_passages(passages))
    if commentaire_rejet:
        parties.append(
            "RETOUR HUMAIN SUR LA VERSION PRÉCÉDENTE (à corriger) :\n" + commentaire_rejet
        )
    return "\n\n".join(parties)


def generer_reponse(
    question: str,
    passages: list[dict],
    commentaire_rejet: str | None = None,
) -> str:
    """Mode question : retourne une réponse Markdown."""
    message = _construire_message_utilisateur(question, passages, commentaire_rejet)
    return appeler_llm(
        system=GENERATOR_SYSTEM,
        user=message,
        max_tokens=MAX_TOKENS_GENERATION,
    )


def _extraire_json(texte: str) -> dict | None:
    try:
        return json.loads(texte)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", texte, flags=re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return None


def generer_scaffolding(
    question: str,
    passages: list[dict],
    commentaire_rejet: str | None = None,
) -> dict:
    """Mode scaffolding : retourne un dict {project_name, description, files}."""
    message = _construire_message_utilisateur(question, passages, commentaire_rejet)
    system = GENERATOR_SCAFFOLDING_SYSTEM

    for essai in range(MAX_RETRIES_JSON + 1):
        brut = appeler_llm(
            system=system,
            user=message,
            max_tokens=MAX_TOKENS_SCAFFOLDING,
            json_mode=True,
        )
        parsed = _extraire_json(brut)
        if parsed and isinstance(parsed.get("files"), list):
            return parsed
        logger.warning("Scaffolding : JSON non parsable (essai %d), on rejoue", essai + 1)
        system = (
            GENERATOR_SCAFFOLDING_SYSTEM
            + "\n\nRAPPEL : ta sortie précédente n'était pas un JSON valide avec un "
            "champ 'files' de type liste. Retourne UNIQUEMENT le JSON strict."
        )

    raise RuntimeError("Scaffolding : le Generator n'a pas produit de JSON valide après plusieurs essais.")


def _apercu_scaffolding_markdown(scaffolding: dict) -> str:
    """Rend un aperçu Markdown lisible du scaffolding, pour affichage fallback."""
    nom = scaffolding.get("project_name", "?")
    desc = scaffolding.get("description", "")
    files = scaffolding.get("files") or []
    lignes = [f"**Scaffolding proposé** : `{nom}/`", ""]
    if desc:
        lignes.append(f"_{desc}_\n")
    lignes.append(f"**{len(files)} fichiers** :")
    for f in files:
        lignes.append(f"- `{f.get('path', '?')}`")
    return "\n".join(lignes)


def noeud_generator(etat: EtatAssistant) -> dict:
    """Nœud LangGraph : génère la réponse (mode question) ou le scaffolding."""
    mode = etat.get("mode", "question")
    question = etat["question"]
    passages = etat.get("passages", [])
    commentaire = etat.get("commentaire_rejet")

    if mode == "scaffolding":
        scaffolding = generer_scaffolding(question, passages, commentaire)
        apercu = _apercu_scaffolding_markdown(scaffolding)
        return {
            "scaffolding_propose": scaffolding,
            "reponse_brouillon": apercu,
            "iteration": etat.get("iteration", 0) + 1,
            "commentaire_rejet": None,
        }

    reponse = generer_reponse(question, passages, commentaire)
    return {
        "reponse_brouillon": reponse,
        "iteration": etat.get("iteration", 0) + 1,
        "commentaire_rejet": None,
    }
