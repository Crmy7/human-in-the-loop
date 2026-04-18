"""Interface Streamlit de l'Assistant Technique BB® — validation humaine obligatoire."""

import uuid

import streamlit as st
from langgraph.types import Command

from evaluation.sus_form import rendre_formulaire_sus
from graph.builder import construire_graphe

st.set_page_config(page_title="Assistant Technique BB®", layout="wide")


def _init_session() -> None:
    if "graphe" not in st.session_state:
        st.session_state.graphe = construire_graphe(interactif=True)
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    if "mode_ui" not in st.session_state:
        st.session_state.mode_ui = "normal"
    if "afficher_sus" not in st.session_state:
        st.session_state.afficher_sus = False


def _config_thread() -> dict:
    return {"configurable": {"thread_id": st.session_state.thread_id}}


def _reset_thread() -> None:
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.mode_ui = "normal"


def _interrupt_en_cours(state) -> dict | None:
    for task in state.tasks:
        if task.interrupts:
            return task.interrupts[0].value
    return None


def _afficher_sources(passages: list[dict]) -> None:
    st.subheader("Sources récupérées")
    if not passages:
        st.info("Aucun passage retourné par le retriever.")
        return
    for i, p in enumerate(passages, start=1):
        meta = p.get("metadata") or {}
        label = meta.get("source_path") or meta.get("url") or "source inconnue"
        section = meta.get("section") or ""
        entete = f"[{i}] {label}"
        if section:
            entete += f" · {section}"
        with st.expander(entete):
            distance = p.get("distance")
            if distance is not None:
                st.caption(f"distance cosinus : {distance:.3f}")
            st.markdown(p.get("content", ""))


def _afficher_critic(rapport: dict) -> None:
    st.subheader("Rapport du Critic")
    score = float(rapport.get("confidence_score", 0.0))
    st.progress(min(max(score, 0.0), 1.0), text=f"confiance : {score:.2f}")

    col_g, col_d = st.columns(2)
    col_g.metric("ancrage sources", rapport.get("source_grounding", "n/a"))
    col_d.metric("conventions BB®", rapport.get("convention_alignment", "n/a"))

    warnings = rapport.get("warnings") or []
    if warnings:
        st.markdown("**Alertes**")
        for w in warnings:
            st.warning(w)

    citees = rapport.get("sources_cited") or []
    if citees:
        st.markdown("**Sources citées dans la réponse**")
        for s in citees:
            st.markdown(f"- `{s}`")


def _envoyer_decision(decision: dict) -> None:
    st.session_state.graphe.invoke(
        Command(resume=decision),
        config=_config_thread(),
    )
    st.session_state.mode_ui = "normal"
    st.rerun()


def _boutons_hitl(payload: dict) -> None:
    iteration = payload.get("iteration", 1)
    st.caption(f"Itération {iteration}")

    if st.session_state.mode_ui == "normal":
        col1, col2, col3 = st.columns(3)
        if col1.button("✓ Approuver", use_container_width=True, type="primary"):
            _envoyer_decision({"action": "approve"})
        if col2.button("✎ Modifier", use_container_width=True):
            st.session_state.mode_ui = "edit"
            st.rerun()
        if col3.button("✗ Rejeter", use_container_width=True):
            st.session_state.mode_ui = "reject"
            st.rerun()

    elif st.session_state.mode_ui == "edit":
        texte = st.text_area(
            "Réponse corrigée",
            value=payload["reponse_brouillon"],
            height=260,
        )
        col1, col2 = st.columns(2)
        if col1.button("Valider la modification", type="primary"):
            _envoyer_decision({"action": "edit", "texte": texte})
        if col2.button("Annuler"):
            st.session_state.mode_ui = "normal"
            st.rerun()

    elif st.session_state.mode_ui == "reject":
        commentaire = st.text_area(
            "Ce qui ne va pas (sera réinjecté dans le prompt du Generator)",
            height=140,
            placeholder="Exemple : la structure proposée oublie le dossier bb-matomo/...",
        )
        col1, col2 = st.columns(2)
        if col1.button("Envoyer le rejet", type="primary", disabled=not commentaire.strip()):
            _envoyer_decision({"action": "reject", "commentaire": commentaire.strip()})
        if col2.button("Annuler"):
            st.session_state.mode_ui = "normal"
            st.rerun()


def _vue_hitl(payload: dict) -> None:
    st.header("Question")
    st.markdown(payload["question"])

    st.header("Réponse (brouillon, en attente de validation)")
    st.markdown(payload["reponse_brouillon"])

    col_sources, col_critic = st.columns(2)
    with col_sources:
        _afficher_sources(payload.get("passages", []))
    with col_critic:
        _afficher_critic(payload.get("rapport_critique") or {})

    st.divider()
    _boutons_hitl(payload)


def _vue_finale(state_values: dict) -> None:
    st.header("Question")
    st.markdown(state_values.get("question", ""))

    decision = state_values.get("decision_humaine") or "terminé"
    st.success(f"Décision : **{decision}**")

    st.header("Réponse finale")
    st.markdown(state_values.get("reponse_finale") or "(vide)")

    st.divider()
    col1, col2 = st.columns(2)
    if col1.button("Nouvelle question", type="primary"):
        _reset_thread()
        st.rerun()
    if col2.button("Terminer la session et évaluer l'outil"):
        st.session_state.afficher_sus = True
        st.rerun()


def _vue_accueil() -> None:
    st.title("Assistant Technique BB®")
    st.caption(
        "RAG agentique avec validation humaine obligatoire. "
        "Corpus : docs internes BB®, Nuxt 3 officielle, Symfony 7 officielle."
    )
    question = st.text_area(
        "Pose ta question à l'assistant",
        placeholder="Exemple : quelle est la convention de nommage BB® pour un projet Nuxt ?",
        height=120,
    )
    if st.button("Poser la question", type="primary", disabled=not question.strip()):
        _reset_thread()
        st.session_state.graphe.invoke(
            {"question": question.strip(), "iteration": 0},
            config=_config_thread(),
        )
        st.rerun()


def main() -> None:
    _init_session()

    if st.session_state.afficher_sus:
        rendre_formulaire_sus()
        if st.button("Retour à l'assistant"):
            st.session_state.afficher_sus = False
            _reset_thread()
            st.rerun()
        return

    state = st.session_state.graphe.get_state(_config_thread())

    if not state.values:
        _vue_accueil()
        return

    payload = _interrupt_en_cours(state)
    if payload is not None:
        _vue_hitl(payload)
        return

    _vue_finale(state.values)


if __name__ == "__main__":
    main()
