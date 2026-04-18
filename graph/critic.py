"""Nœud Critic : audite la réponse du Generator et produit un JSON normalisé.

Deux modes : audit de la réponse en prose (mode question) ou de la proposition
scaffolding JSON (mode scaffolding).
"""

import json
import logging
import re

from graph.llm_client import appeler_llm
from graph.prompts import CRITIC_SCAFFOLDING_SYSTEM, CRITIC_SYSTEM
from graph.state import EtatAssistant

logger = logging.getLogger(__name__)

MAX_TOKENS_CRITIC = 800
MAX_RETRIES_PARSE = 2


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


def _construire_message_scaffolding(
    question: str,
    passages: list[dict],
    scaffolding: dict,
) -> str:
    return (
        f"QUESTION :\n{question}\n\n"
        f"PASSAGES :\n{_formater_passages(passages)}\n\n"
        f"PROPOSITION (JSON) :\n{json.dumps(scaffolding, ensure_ascii=False, indent=2)}"
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


def _auditer(system_base: str, message: str) -> dict:
    """Boucle d'audit commune aux deux modes avec retry parsing."""
    system_prompt = system_base
    for essai in range(MAX_RETRIES_PARSE + 1):
        brut = appeler_llm(
            system=system_prompt,
            user=message,
            max_tokens=MAX_TOKENS_CRITIC,
            json_mode=True,
        )
        rapport = parser_rapport(brut)
        if rapport is not None:
            return rapport
        logger.warning("Critic : JSON non parsable (essai %d), on rejoue", essai + 1)
        system_prompt = (
            system_base
            + "\n\nRAPPEL : ta sortie précédente n'était pas un JSON strict. "
            "Retourne UNIQUEMENT un objet JSON, sans bloc de code, sans texte annexe."
        )

    logger.error("Critic : échec après %d essais, rapport par défaut", MAX_RETRIES_PARSE + 1)
    return _rapport_par_defaut()


def auditer(question: str, passages: list[dict], reponse: str) -> dict:
    """Mode question : audite une réponse en prose."""
    return _auditer(CRITIC_SYSTEM, _construire_message_utilisateur(question, passages, reponse))


def auditer_scaffolding(question: str, passages: list[dict], scaffolding: dict) -> dict:
    """Mode scaffolding : audite une proposition JSON de scaffolding."""
    return _auditer(
        CRITIC_SCAFFOLDING_SYSTEM,
        _construire_message_scaffolding(question, passages, scaffolding),
    )


def noeud_critic(etat: EtatAssistant) -> dict:
    """Nœud LangGraph : audite selon le mode (question ou scaffolding)."""
    mode = etat.get("mode", "question")
    if mode == "scaffolding":
        rapport = auditer_scaffolding(
            question=etat["question"],
            passages=etat.get("passages", []),
            scaffolding=etat.get("scaffolding_propose") or {},
        )
    else:
        rapport = auditer(
            question=etat["question"],
            passages=etat.get("passages", []),
            reponse=etat["reponse_brouillon"],
        )
    return {"rapport_critique": rapport}
