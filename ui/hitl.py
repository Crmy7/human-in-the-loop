"""Vues HITL : question (brouillon texte) et scaffolding (proposition de fichiers)."""

import streamlit as st

from ui.details import details_en_onglets
from ui.helpers import (
    badge,
    citations,
    hallucinations,
    langage_pour,
    mode_qualite,
    ouvrir_picker_dossier,
)
from ui.session import decider


# --------------------------------------------------------------------------- #
# Communs
# --------------------------------------------------------------------------- #

def entete_question(question: str) -> None:
    st.caption("QUESTION")
    st.markdown(f"**{question}**")


def _bloc_reject(payload: dict) -> None:
    warnings = (payload.get("rapport_critique") or {}).get("warnings") or []
    if warnings:
        suggestion = " · ".join(warnings)
        if st.button("Reprendre les alertes du Critic"):
            st.session_state["_prerempli"] = suggestion
            st.rerun()

    valeur = st.session_state.pop("_prerempli", "")
    commentaire = st.text_area(
        "Ton retour",
        value=valeur,
        height=140,
        placeholder="Ce qui cloche — sera réinjecté dans le prompt.",
        label_visibility="collapsed",
    )
    c1, c2 = st.columns(2)
    if c1.button(
        "Envoyer et relancer",
        type="primary",
        disabled=not commentaire.strip(),
        use_container_width=True,
    ):
        decider({"action": "reject", "commentaire": commentaire.strip()})
    if c2.button("Annuler", use_container_width=True):
        st.session_state.mode = "normal"
        st.rerun()


# --------------------------------------------------------------------------- #
# Mode question
# --------------------------------------------------------------------------- #

def vue_hitl_question(payload: dict) -> None:
    iteration = payload.get("iteration", 1)
    brouillon = payload.get("reponse_brouillon", "")
    passages = payload.get("passages", [])
    rapport = payload.get("rapport_critique") or {}
    citees = citations(brouillon)
    hallus = hallucinations(brouillon, passages)
    mode_q, label, classe = mode_qualite(rapport, brouillon, hallus)

    entete_question(payload["question"])

    suffix = f" · itération {iteration}/3" if iteration > 1 else ""
    st.markdown(
        f'<h3>Brouillon à valider{suffix}{badge(label, classe)}</h3>',
        unsafe_allow_html=True,
    )

    if hallus:
        st.error(
            "Hallucination détectée — sources citées absentes des passages : "
            + ", ".join(f"`{s}`" for s in hallus)
        )

    with st.container(border=True):
        st.markdown(brouillon)
        if citees:
            st.caption("Sources citées : " + " ".join(f"`{c}`" for c in sorted(citees)))

    _actions_question(payload, mode_q == "refus")

    st.divider()
    details_en_onglets(passages, rapport, citees, hallus, mode_usage="question")


def _actions_question(payload: dict, est_refus: bool) -> None:
    mode_ui = st.session_state.mode
    if est_refus:
        v, m, r = "Valider le refus", "Écrire moi-même", "Relancer"
    else:
        v, m, r = "Valider", "Corriger", "Refaire"

    if mode_ui == "normal":
        c1, c2, c3 = st.columns(3)
        if c1.button(v, type="primary", use_container_width=True):
            decider({"action": "approve"})
        if c2.button(m, use_container_width=True):
            st.session_state.mode = "edit"
            st.rerun()
        if c3.button(r, use_container_width=True):
            st.session_state.mode = "reject"
            st.rerun()
        if payload.get("iteration", 1) >= 3:
            st.caption("Itération 3/3 — dernière tentative.")

    elif mode_ui == "edit":
        texte = st.text_area(
            "Édite",
            value=payload["reponse_brouillon"],
            height=260,
            label_visibility="collapsed",
        )
        c1, c2 = st.columns(2)
        if c1.button("Publier cette version", type="primary", use_container_width=True):
            decider({"action": "edit", "texte": texte})
        if c2.button("Annuler", use_container_width=True):
            st.session_state.mode = "normal"
            st.rerun()

    elif mode_ui == "reject":
        _bloc_reject(payload)


# --------------------------------------------------------------------------- #
# Mode scaffolding
# --------------------------------------------------------------------------- #

def vue_hitl_scaffolding(payload: dict) -> None:
    iteration = payload.get("iteration", 1)
    scaffolding = payload.get("scaffolding_propose") or {}
    passages = payload.get("passages", [])
    rapport = payload.get("rapport_critique") or {}
    _, label, classe = mode_qualite(rapport, "", [])
    base_actuelle = payload.get("base_dir") or st.session_state.base_dir
    project_name = scaffolding.get("project_name", "projet")
    files = scaffolding.get("files") or []

    entete_question(payload["question"])

    suffix = f" · itération {iteration}/3" if iteration > 1 else ""
    st.markdown(
        f'<h3>Scaffolding proposé{suffix}{badge(label, classe)}</h3>',
        unsafe_allow_html=True,
    )
    st.caption(f"`{project_name}/` · {len(files)} fichiers")

    description = scaffolding.get("description", "")
    if description:
        with st.container(border=True):
            st.markdown(description)

    st.markdown("\n".join(f"- `{f.get('path', '?')}`" for f in files))

    for f in files:
        path = f.get("path", "?")
        with st.expander(f"`{path}`"):
            st.code(f.get("content", ""), language=langage_pour(path))

    _selecteur_destination(base_actuelle, project_name, key_prefix="hitl")
    _actions_scaffolding(payload)

    st.divider()
    details_en_onglets(passages, rapport, set(), [], mode_usage="scaffolding")


def _actions_scaffolding(payload: dict) -> None:
    mode_ui = st.session_state.mode
    scaffolding = payload.get("scaffolding_propose") or {}
    project_name = scaffolding.get("project_name", "projet")

    if mode_ui == "normal":
        dest = st.session_state.get(
            "_dest_val_hitl",
            payload.get("base_dir") or st.session_state.base_dir,
        )
        c1, c2, c3 = st.columns(3)
        if c1.button("Valider et écrire", type="primary", use_container_width=True):
            decider({"action": "approve", "base_dir": dest})
        if c2.button("Modifier les fichiers", use_container_width=True):
            st.session_state.mode = "edit"
            st.rerun()
        if c3.button("Refaire", use_container_width=True):
            st.session_state.mode = "reject"
            st.rerun()
        if payload.get("iteration", 1) >= 3:
            st.caption("Itération 3/3 — dernière tentative.")

    elif mode_ui == "edit":
        files = scaffolding.get("files") or []
        if not files:
            st.warning("Rien à éditer.")
            return
        onglets = st.tabs([f["path"] for f in files])
        edited: list[dict] = []
        for ongl, f in zip(onglets, files):
            with ongl:
                contenu = st.text_area(
                    f["path"],
                    value=f.get("content", ""),
                    height=300,
                    label_visibility="collapsed",
                    key=f"edit_{f['path']}",
                )
                edited.append({"path": f["path"], "content": contenu})
        dest = st.session_state.get("_dest_val_hitl", st.session_state.base_dir)
        c1, c2 = st.columns(2)
        if c1.button("Écrire ma version", type="primary", use_container_width=True):
            nouveau = {
                "project_name": project_name,
                "description": scaffolding.get("description", ""),
                "files": edited,
            }
            decider({"action": "edit", "scaffolding": nouveau, "base_dir": dest})
        if c2.button("Annuler", use_container_width=True):
            st.session_state.mode = "normal"
            st.rerun()

    elif mode_ui == "reject":
        _bloc_reject(payload)


def _selecteur_destination(base_actuelle: str, project_name: str, key_prefix: str) -> None:
    key_val = f"_dest_val_{key_prefix}"
    if key_val not in st.session_state:
        st.session_state[key_val] = base_actuelle

    def on_parcourir():
        choix = ouvrir_picker_dossier(f"Destination pour {project_name}")
        if choix:
            st.session_state[key_val] = choix

    c1, c2 = st.columns([4, 1])
    c1.caption(f"Écriture dans `{st.session_state[key_val]}/{project_name}/`")
    c2.button(
        "Parcourir",
        use_container_width=True,
        on_click=on_parcourir,
        key=f"_btn_parcourir_{key_prefix}",
    )
