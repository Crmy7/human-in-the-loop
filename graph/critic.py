"""Nœud Critic : audite la réponse du Generator et produit un JSON normalisé."""

import json
import logging
import re

from anthropic import Anthropic

from config import ANTHROPIC_API_KEY, LLM_MODEL
from graph.prompts import CRITIC_SYSTEM
from graph.state import EtatAssistant

logger = logging.getLogger(__name__)

MAX_TOKENS_CRITIC = 800
MAX_RETRIES_PARSE = 2

_anthropic_client: Anthropic | None = None


def _client() -> Anthropic:
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
    return _anthropic_client


def parser_rapport(texte: str) -> dict | None:
    """Tente d'extraire le JSON du rapport Critic ; retourne None si échec."""
    try:
        return json.loads(texte)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", texte, flags=re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def _formater_passages(passages: list[dict]) -> str:
    blocs = []
    for i, p in enumerate(passages, start=1):
        meta = p.get("metadata", {})
        source = meta.get("source_path") or meta.get("url") or "source_inconnue"
        blocs.append(f"[{i}] source_path: {source}\n{p['content']}")
    return "\n\n---\n\n".join(blocs)


def _construire_message_utilisateur(
    question: str,
    passages: list[dict],
    reponse: str,
) -> str:
    return (
        f"QUESTION :\n{question}\n\n"
        f"PASSAGES :\n{_formater_passages(passages)}\n\n"
        f"RÉPONSE :\n{reponse}"
    )


def _rapport_par_defaut() -> dict:
    """Rapport minimal quand le Critic n'a pas pu produire de JSON valide."""
    return {
        "confidence_score": 0.0,
        "source_grounding": "low",
        "convention_alignment": "n/a",
        "warnings": ["Critic indisponible : rapport non parsable après plusieurs essais."],
        "sources_cited": [],
    }


def auditer(question: str, passages: list[dict], reponse: str) -> dict:
    """Appelle le Critic jusqu'à obtenir un JSON valide (max MAX_RETRIES_PARSE+1 essais)."""
    message = _construire_message_utilisateur(question, passages, reponse)
    system_prompt = CRITIC_SYSTEM

    for essai in range(MAX_RETRIES_PARSE + 1):
        response = _client().messages.create(
            model=LLM_MODEL,
            max_tokens=MAX_TOKENS_CRITIC,
            system=system_prompt,
            messages=[{"role": "user", "content": message}],
        )
        brut = response.content[0].text
        rapport = parser_rapport(brut)
        if rapport is not None:
            return rapport
        logger.warning("Critic : JSON non parsable (essai %d), on rejoue", essai + 1)
        system_prompt = (
            CRITIC_SYSTEM
            + "\n\nRAPPEL : ta sortie précédente n'était pas un JSON strict. "
            "Retourne UNIQUEMENT un objet JSON, sans bloc de code, sans texte annexe."
        )

    logger.error("Critic : échec après %d essais, rapport par défaut", MAX_RETRIES_PARSE + 1)
    return _rapport_par_defaut()


def noeud_critic(etat: EtatAssistant) -> dict:
    """Nœud LangGraph : enrichit l'état avec le rapport d'audit."""
    rapport = auditer(
        question=etat["question"],
        passages=etat.get("passages", []),
        reponse=etat["reponse_brouillon"],
    )
    return {"rapport_critique": rapport}
