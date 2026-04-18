"""État partagé du graphe LangGraph, typé via TypedDict."""

from typing import Optional, TypedDict


class EtatAssistant(TypedDict, total=False):
    """État transverse aux nœuds retriever, generator, critic, hitl et executor."""

    # Entrée
    question: str
    mode: str  # "question" | "scaffolding"
    base_dir: Optional[str]  # dossier parent d'écriture (scaffolding uniquement)

    # Sortie retriever
    passages: list[dict]

    # Boucle generator ↔ critic
    reponse_brouillon: str
    scaffolding_propose: dict  # {project_name, description, files: [{path, content}]}
    rapport_critique: dict
    iteration: int
    commentaire_rejet: Optional[str]

    # HITL
    decision_humaine: Optional[str]  # "approve" | "edit" | "reject"
    reponse_finale: Optional[str]

    # Executor (mode scaffolding uniquement)
    executor_output: dict  # {dossier_ecrit, nb_fichiers}
