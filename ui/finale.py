"""Vue finale : affichage de la réponse validée ou du scaffolding écrit sur disque."""

import streamlit as st

from ui.details import details_historique, details_historique_scaffolding
from ui.helpers import langage_pour
from ui.hitl import entete_question
from ui.session import reset


def vue_finale(values: dict) -> None:
    mode_usage = values.get("mode", "question")
    decision = values.get("decision_humaine")
    executor_output = values.get("executor_output") or {}

    if st.session_state.degrade:
        st.error("Mode dégradé — écriture sans validation humaine ni Critic.")
    else:
        libelle = {
            "approve": "Validée",
            "edit": "Éditée et validée",
            "reject": "Diffusée après 3 rejets",
        }.get(decision, "Terminée")
        st.success(libelle)

    entete_question(values.get("question", ""))

    if mode_usage == "scaffolding":
        _vue_finale_scaffolding(values, executor_output)
    else:
        _vue_finale_question(values)

    if len(st.session_state.historique) > 1:
        fn = details_historique_scaffolding if mode_usage == "scaffolding" else details_historique
        with st.expander(f"Historique · {len(st.session_state.historique) - 1} version(s)"):
            fn()

    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("Nouvelle demande", type="primary", use_container_width=True):
        reset()
        st.rerun()
    if c2.button("Noter l'outil (SUS)", use_container_width=True):
        st.session_state.afficher_sus = True
        st.rerun()


def _vue_finale_question(values: dict) -> None:
    st.markdown("### Réponse finale")
    with st.container(border=True):
        st.markdown(values.get("reponse_finale") or "(vide)")


def _vue_finale_scaffolding(values: dict, executor_output: dict) -> None:
    if executor_output:
        with st.container(border=True):
            st.markdown(f"**Fichiers créés** · {executor_output.get('nb_fichiers', '?')}")
            st.caption(f"`{executor_output.get('dossier_ecrit', '?')}`")

    scaf = values.get("scaffolding_propose") or {}
    if scaf.get("files"):
        with st.expander("Revoir les fichiers"):
            for f in scaf["files"]:
                path = f.get("path", "?")
                st.markdown(f"**`{path}`**")
                st.code(f.get("content", ""), language=langage_pour(path))
