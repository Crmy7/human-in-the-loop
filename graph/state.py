"""État partagé du graphe LangGraph, typé via TypedDict."""

from typing import Optional, TypedDict


class EtatAssistant(TypedDict, total=False):
    """État transverse aux nœuds retriever, generator, critic et hitl."""

    # Entrée
    question: str

    # Sortie retriever
    passages: list[dict]

    # Boucle generator ↔ critic
    reponse_brouillon: str
    rapport_critique: dict
    iteration: int
    commentaire_rejet: Optional[str]

    # HITL
    decision_humaine: Optional[str]  # "approve" | "edit" | "reject"
    reponse_finale: Optional[str]
