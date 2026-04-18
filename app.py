"""Point d'entrée Streamlit de l'Assistant Technique BB®. Le code réel est dans ui/."""

import streamlit as st

from evaluation.sus_form import rendre_formulaire_sus
from ui import (
    config_thread,
    init,
    injecter_styles,
    reset,
    vue_accueil,
    vue_finale,
    vue_hitl_question,
    vue_hitl_scaffolding,
)

st.set_page_config(
    page_title="Assistant Technique BB®",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def main() -> None:
    injecter_styles()
    init()

    if st.session_state.afficher_sus:
        _vue_sus()
        return

    state = st.session_state.graphe.get_state(config_thread())

    if not state.values:
        vue_accueil()
        return

    payload = _interrupt_en_cours(state)
    if payload is not None:
        if payload.get("mode") == "scaffolding":
            vue_hitl_scaffolding(payload)
        else:
            vue_hitl_question(payload)
        return

    vue_finale(state.values)


def _interrupt_en_cours(state) -> dict | None:
    for task in state.tasks:
        if task.interrupts:
            return task.interrupts[0].value
    return None


def _vue_sus() -> None:
    rendre_formulaire_sus()
    if st.button("Retour"):
        st.session_state.afficher_sus = False
        reset()
        st.rerun()


if __name__ == "__main__":
    main()
