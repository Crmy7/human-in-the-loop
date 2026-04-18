"""Adaptateur LLM : dispatche vers Anthropic ou OpenAI selon LLM_PROVIDER."""

from anthropic import Anthropic
from openai import OpenAI

from config import (
    ANTHROPIC_API_KEY,
    LLM_MODEL,
    LLM_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_CHAT_MODEL,
)

_anthropic_client: Anthropic | None = None
_openai_client: OpenAI | None = None


def _anthropic() -> Anthropic:
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
    return _anthropic_client


def _openai() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=OPENAI_API_KEY)
    return _openai_client


def appeler_llm(system: str, user: str, max_tokens: int, json_mode: bool = False) -> str:
    """Appel LLM unifié. Si json_mode=True, force une sortie JSON côté OpenAI."""
    if LLM_PROVIDER == "openai":
        kwargs = {
            "model": OPENAI_CHAT_MODEL,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        response = _openai().chat.completions.create(**kwargs)
        return (response.choices[0].message.content or "").strip()

    if LLM_PROVIDER == "anthropic":
        # Pas de json_mode natif côté Anthropic : on s'appuie sur le prompt (les
        # prompts Critic et Scaffolding imposent déjà le format JSON strict).
        response = _anthropic().messages.create(
            model=LLM_MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return response.content[0].text.strip()

    raise ValueError(f"LLM_PROVIDER inconnu : {LLM_PROVIDER!r}. Attendu : 'anthropic' ou 'openai'.")
