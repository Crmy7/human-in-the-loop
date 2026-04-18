"""Construction du StateGraph : retriever → generator → critic → hitl + routage conditionnel."""

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from config import MAX_ITERATIONS
from graph.critic import noeud_critic
from graph.generator import noeud_generator
from graph.retriever import noeud_retriever
from graph.state import EtatAssistant


def noeud_hitl(etat: EtatAssistant) -> dict:
    """Pause le graphe et attend la décision humaine via Command(resume=...)."""
    payload = {
        "question": etat["question"],
        "reponse_brouillon": etat["reponse_brouillon"],
        "rapport_critique": etat["rapport_critique"],
        "passages": etat["passages"],
        "iteration": etat.get("iteration", 1),
    }
    decision = interrupt(payload)

    action = decision.get("action") if isinstance(decision, dict) else None
    if action == "approve":
        return {
            "decision_humaine": "approve",
            "reponse_finale": etat["reponse_brouillon"],
        }
    if action == "edit":
        return {
            "decision_humaine": "edit",
            "reponse_finale": decision.get("texte", etat["reponse_brouillon"]),
        }
    if action == "reject":
        return {
            "decision_humaine": "reject",
            "commentaire_rejet": decision.get("commentaire", ""),
        }
    raise ValueError(f"Décision humaine invalide : {decision!r}")


def noeud_auto_approve(etat: EtatAssistant) -> dict:
    """Approbation automatique pour exécutions non-interactives (eval RAGAS)."""
    return {
        "decision_humaine": "approve",
        "reponse_finale": etat["reponse_brouillon"],
    }


def router_apres_hitl(etat: EtatAssistant) -> str:
    """Décide de la suite après la décision humaine."""
    decision = etat.get("decision_humaine")
    if decision in ("approve", "edit"):
        return "fin"
    if decision == "reject":
        if etat.get("iteration", 0) >= MAX_ITERATIONS:
            return "fin"
        return "regenerer"
    raise ValueError(f"Décision inconnue dans le routeur : {decision!r}")


def construire_graphe(interactif: bool = True):
    """Compile le StateGraph. interactif=False bypass le HITL (utilisé par RAGAS)."""
    builder = StateGraph(EtatAssistant)
    builder.add_node("retriever", noeud_retriever)
    builder.add_node("generator", noeud_generator)
    builder.add_node("critic", noeud_critic)
    builder.add_node("hitl", noeud_hitl if interactif else noeud_auto_approve)

    builder.add_edge(START, "retriever")
    builder.add_edge("retriever", "generator")
    builder.add_edge("generator", "critic")
    builder.add_edge("critic", "hitl")
    builder.add_conditional_edges(
        "hitl",
        router_apres_hitl,
        {"fin": END, "regenerer": "generator"},
    )

    checkpointer = InMemorySaver()
    return builder.compile(checkpointer=checkpointer)
