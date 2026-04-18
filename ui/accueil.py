"""Vue d'accueil : hero + sélecteur de mode + chat input + exemples + options scaffolding."""

import streamlit as st

from ui.helpers import ouvrir_picker_dossier
from ui.session import assurer_graphe, lancer, reset


def vue_accueil() -> None:
    _hero()
    _selecteur_mode()
    _entree_principale()
    _exemples()
    if st.session_state.mode_usage == "scaffolding":
        with st.expander("Options", expanded=False):
            _options_scaffolding()


def _hero() -> None:
    st.markdown(
        '<div class="bb-hero">'
        '<h1>Assistant Technique BB®</h1>'
        '<div class="bb-hero-tagline">RAG sur la doc interne, Nuxt 3, Symfony 7. '
        'Validation humaine obligatoire avant chaque livraison.</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def _selecteur_mode() -> None:
    mode = st.segmented_control(
        "Mode",
        options=["question", "scaffolding"],
        format_func=lambda m: "Question" if m == "question" else "Scaffolding",
        default=st.session_state.mode_usage,
        label_visibility="collapsed",
        key="_seg_mode",
    )
    if mode and mode != st.session_state.mode_usage:
        st.session_state.mode_usage = mode
        reset()


def _entree_principale() -> None:
    placeholder = (
        "Pose ta question…"
        if st.session_state.mode_usage == "question"
        else "Décris le projet à initialiser…"
    )
    question = st.chat_input(placeholder)
    if question:
        lancer(question.strip())


def _exemples() -> None:
    if st.session_state.mode_usage == "question":
        exemples = [
            "Convention de nommage BB® pour un projet Nuxt ?",
            "Structure Symfony BB® avec Matomo ?",
            "Process de facturation BB® pour un client récurrent ?",
        ]
    else:
        exemples = [
            "Nuxt 3 pour Raiffeisen avec Matomo et OVH.",
            "Symfony 7 pour Etat de Genève avec API REST.",
        ]

    st.caption("Essayer :")
    for q in exemples:
        if st.button(q, use_container_width=True, key=f"ex_{hash(q)}"):
            lancer(q)
            return


def _options_scaffolding() -> None:
    c1, c2 = st.columns([3, 1])
    c1.markdown("**Dossier de destination**")
    c1.caption(f"`{st.session_state.base_dir}`")

    def on_parcourir():
        choix = ouvrir_picker_dossier("Dossier de destination BB®")
        if choix:
            st.session_state.base_dir = choix

    c2.button(
        "Parcourir",
        use_container_width=True,
        on_click=on_parcourir,
        key="_btn_parcourir",
    )

    st.divider()

    st.checkbox(
        "Mode démonstration dégradée",
        key="degrade",
        help=(
            "Désactive Critic et HITL. Écriture immédiate sans validation. "
            "Pour la soutenance uniquement."
        ),
    )
    assurer_graphe()
    if st.session_state.degrade:
        st.warning(
            "Mode dégradé actif : les fichiers seront écrits "
            "sans vérification ni validation humaine."
        )
