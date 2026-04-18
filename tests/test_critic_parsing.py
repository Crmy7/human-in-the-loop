"""Tests du parseur JSON du Critic (sans appel LLM)."""

from graph.critic import parser_rapport


def test_parse_json_pur():
    texte = '{"confidence_score": 0.8, "source_grounding": "high", "convention_alignment": "n/a", "warnings": [], "sources_cited": ["a.md"]}'
    rapport = parser_rapport(texte)
    assert rapport is not None
    assert rapport["confidence_score"] == 0.8
    assert rapport["sources_cited"] == ["a.md"]


def test_parse_json_entoure_de_markdown():
    texte = """Voici le rapport :

```json
{"confidence_score": 0.5, "source_grounding": "medium", "convention_alignment": "low", "warnings": ["hop"], "sources_cited": []}
```

Fin."""
    rapport = parser_rapport(texte)
    assert rapport is not None
    assert rapport["source_grounding"] == "medium"
    assert rapport["warnings"] == ["hop"]


def test_parse_echec_retourne_none():
    assert parser_rapport("pas de JSON ici") is None
    assert parser_rapport("{incomplete") is None


def test_parse_json_multiligne():
    texte = """{
      "confidence_score": 0.9,
      "source_grounding": "high",
      "convention_alignment": "high",
      "warnings": [],
      "sources_cited": ["bb-nuxt-template-README.md"]
    }"""
    rapport = parser_rapport(texte)
    assert rapport is not None
    assert rapport["sources_cited"] == ["bb-nuxt-template-README.md"]
