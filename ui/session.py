"""Gestion du session_state, compilation du graphe, invocation avec progression."""

import uuid

import streamlit as st
from langgraph.types import Command

from graph.builder import construire_graphe
from graph.executor import SCAFFOLDING_BASE


def init() -> None:
    """Initialise toutes les clés de session_state + le graphe."""
    st.session_state.setdefault("mode_usage", "question")
    st.session_state.setdefault("degrade", False)
    st.session_state.setdefault("thread_id", str(uuid.uuid4()))
    st.session_state.setdefault("mode", "normal")  # UI: normal | edit | reject
    st.session_state.setdefault("afficher_sus", False)
    st.session_state.setdefault("historique", [])
    st.session_state.setdefault("dernier_rejet", None)
    st.session_state.setdefault("base_dir", str(SCAFFOLDING_BASE))
    assurer_graphe()


def assurer_graphe() -> None:
    """(Re)compile le graphe si le flag degrade a changé."""
    signature = "degrade" if st.session_state.degrade else "nominal"
    if st.session_state.get("_graphe_signature") != signature:
        st.session_state.graphe = construire_graphe(
            interactif=True, degrade=st.session_state.degrade
        )
        st.session_state._graphe_signature = signature


def config_thread() -> dict:
    """Config LangGraph avec le thread_id courant."""
    return {"configurable": {"thread_id": st.session_state.thread_id}}


def reset() -> None:
    """Reset le thread (nouvelle question), garde mode_usage et base_dir."""
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.mode = "normal"
    st.session_state.historique = []
    st.session_state.dernier_rejet = None


def invoquer(entree) -> None:
    """Stream le graphe et affiche la progression dans st.status."""
    with st.status("Traitement…", expanded=True) as status:
        for update in st.session_state.graphe.stream(
            entree, config=config_thread(), stream_mode="updates"
        ):
            for node in update:
                if node == "retriever":
                    n = len(update[node].get("passages", []))
                    st.write(f"Recherche · **{n}** passages")
                elif node == "generator":
                    label = (
                        "Génération du scaffolding"
                        if st.session_state.mode_usage == "scaffolding"
                        else "Rédaction"
                    )
                    st.write(label)
                elif node == "critic":
                    score = (update[node].get("rapport_critique") or {}).get("confidence_score", 0)
                    st.write(f"Audit · confiance **{score:.2f}**")
                elif node == "__interrupt__":
                    st.write("En attente de ta décision")
                elif node == "executor":
                    out = update[node].get("executor_output") or {}
                    st.write(f"Écriture · **{out.get('nb_fichiers', '?')}** fichiers")
        status.update(label="Terminé", state="complete", expanded=False)
    _maj_historique()


def _maj_historique() -> None:
    """Capture la version courante du brouillon dans l'historique si on est en HITL."""
    state = st.session_state.graphe.get_state(config_thread())
    for task in state.tasks:
        if task.interrupts:
            p = task.interrupts[0].value
            entree = {
                "iteration": p.get("iteration", 1),
                "brouillon": p.get("reponse_brouillon", ""),
                "scaffolding": p.get("scaffolding_propose") or {},
                "rapport": p.get("rapport_critique") or {},
                "rejet_precedent": st.session_state.dernier_rejet,
            }
            h = st.session_state.historique
            if not h or h[-1]["iteration"] != entree["iteration"]:
                h.append(entree)
            st.session_state.dernier_rejet = None
            break


def lancer(question: str) -> None:
    """Démarre un nouveau thread avec la question (reset + invoke + rerun)."""
    reset()
    entree: dict = {
        "question": question,
        "mode": st.session_state.mode_usage,
        "iteration": 0,
    }
    if st.session_state.mode_usage == "scaffolding":
        entree["base_dir"] = st.session_state.base_dir
    invoquer(entree)
    st.rerun()


def decider(decision: dict) -> None:
    """Envoie la décision humaine au graphe (approve/edit/reject), relance l'invocation."""
    if decision.get("action") == "reject":
        st.session_state.dernier_rejet = decision.get("commentaire")
    invoquer(Command(resume=decision))
    st.session_state.mode = "normal"
    st.rerun()
