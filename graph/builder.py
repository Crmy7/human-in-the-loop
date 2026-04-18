"""Construction du StateGraph : deux modes (question/scaffolding) + flag démo dégradée.

Pipeline nominal (degrade=False) :
    START → retriever → generator → critic → hitl → [approve → executor (si scaffolding) → END]
                                                ├── [edit → executor (si scaffolding) → END]
                                                └── [reject (iter<3) → generator]

Pipeline dégradé (degrade=True) — aucun Critic, aucun HITL, scaffolding direct :
    START → retriever → generator → executor → END
"""

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from config import MAX_ITERATIONS
from graph.critic import noeud_critic
from graph.executor import noeud_executor
from graph.generator import noeud_generator
from graph.retriever import noeud_retriever
from graph.state import EtatAssistant


def noeud_hitl(etat: EtatAssistant) -> dict:
    """Pause le graphe et attend la décision humaine via Command(resume=...)."""
    payload = {
        "question": etat["question"],
        "mode": etat.get("mode", "question"),
        "reponse_brouillon": etat.get("reponse_brouillon", ""),
        "scaffolding_propose": etat.get("scaffolding_propose") or {},
        "rapport_critique": etat.get("rapport_critique") or {},
        "passages": etat.get("passages", []),
        "iteration": etat.get("iteration", 1),
    }
    decision = interrupt(payload)

    action = decision.get("action") if isinstance(decision, dict) else None
    mode = etat.get("mode", "question")

    if action == "approve":
        if mode == "scaffolding":
            return {"decision_humaine": "approve"}
        return {
            "decision_humaine": "approve",
            "reponse_finale": etat.get("reponse_brouillon", ""),
        }

    if action == "edit":
        if mode == "scaffolding":
            # L'édition peut remplacer le scaffolding complet (fichiers édités côté UI)
            nouveau = decision.get("scaffolding") or etat.get("scaffolding_propose") or {}
            return {
                "decision_humaine": "edit",
                "scaffolding_propose": nouveau,
            }
        return {
            "decision_humaine": "edit",
            "reponse_finale": decision.get("texte", etat.get("reponse_brouillon", "")),
        }

    if action == "reject":
        return {
            "decision_humaine": "reject",
            "commentaire_rejet": decision.get("commentaire", ""),
        }

    raise ValueError(f"Décision humaine invalide : {decision!r}")


def noeud_auto_approve(etat: EtatAssistant) -> dict:
    """Approbation automatique pour exécutions non-interactives (eval RAGAS)."""
    mode = etat.get("mode", "question")
    if mode == "scaffolding":
        return {"decision_humaine": "approve"}
    return {
        "decision_humaine": "approve",
        "reponse_finale": etat.get("reponse_brouillon", ""),
    }


def router_apres_hitl(etat: EtatAssistant) -> str:
    """Décide de la suite après la décision humaine, en tenant compte du mode."""
    decision = etat.get("decision_humaine")
    mode = etat.get("mode", "question")

    if decision in ("approve", "edit"):
        if mode == "scaffolding":
            return "executor"
        return "fin"
    if decision == "reject":
        if etat.get("iteration", 0) >= MAX_ITERATIONS:
            return "fin"
        return "regenerer"
    raise ValueError(f"Décision inconnue dans le routeur : {decision!r}")


def construire_graphe(interactif: bool = True, degrade: bool = False):
    """Compile le StateGraph. degrade=True bypass le Critic et le HITL (mode démo)."""
    builder = StateGraph(EtatAssistant)
    builder.add_node("retriever", noeud_retriever)
    builder.add_node("generator", noeud_generator)
    builder.add_node("executor", noeud_executor)

    builder.add_edge(START, "retriever")
    builder.add_edge("retriever", "generator")

    if degrade:
        # Mode vibe : pas de Critic, pas de HITL, scaffolding direct
        builder.add_edge("generator", "executor")
        builder.add_edge("executor", END)
    else:
        builder.add_node("critic", noeud_critic)
        builder.add_node("hitl", noeud_hitl if interactif else noeud_auto_approve)

        builder.add_edge("generator", "critic")
        builder.add_edge("critic", "hitl")
        builder.add_conditional_edges(
            "hitl",
            router_apres_hitl,
            {"fin": END, "regenerer": "generator", "executor": "executor"},
        )
        builder.add_edge("executor", END)

    checkpointer = InMemorySaver()
    return builder.compile(checkpointer=checkpointer)
