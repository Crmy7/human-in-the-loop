"""Nœud Generator : produit une réponse ancrée sur les passages récupérés."""

from anthropic import Anthropic

from config import ANTHROPIC_API_KEY, LLM_MODEL
from graph.prompts import GENERATOR_SYSTEM
from graph.state import EtatAssistant

MAX_TOKENS_GENERATION = 1200

_anthropic_client: Anthropic | None = None


def _client() -> Anthropic:
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
    return _anthropic_client


def _formater_passages(passages: list[dict]) -> str:
    """Sérialise les passages pour le message utilisateur."""
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


def generer(
    question: str,
    passages: list[dict],
    commentaire_rejet: str | None = None,
) -> str:
    """Appelle Claude avec le prompt Generator et retourne la réponse brouillon."""
    message = _construire_message_utilisateur(question, passages, commentaire_rejet)
    response = _client().messages.create(
        model=LLM_MODEL,
        max_tokens=MAX_TOKENS_GENERATION,
        system=GENERATOR_SYSTEM,
        messages=[{"role": "user", "content": message}],
    )
    return response.content[0].text.strip()


def noeud_generator(etat: EtatAssistant) -> dict:
    """Nœud LangGraph : génère la réponse brouillon et incrémente iteration."""
    reponse = generer(
        question=etat["question"],
        passages=etat.get("passages", []),
        commentaire_rejet=etat.get("commentaire_rejet"),
    )
    return {
        "reponse_brouillon": reponse,
        "iteration": etat.get("iteration", 0) + 1,
        "commentaire_rejet": None,
    }
