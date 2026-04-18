"""Onglets de détail affichés sous le brouillon : sources, audit Critic, historique."""

import streamlit as st

from ui.helpers import source_label


def details_en_onglets(
    passages: list[dict],
    rapport: dict,
    citees: set[str],
    hallus: list[str],
    mode_usage: str,
) -> None:
    """Affiche un bloc de 2-3 onglets sous le brouillon/scaffolding."""
    labels = [f"Sources ({len(passages)})", "Audit"]
    if len(st.session_state.historique) > 1:
        labels.append(f"Historique ({len(st.session_state.historique) - 1})")
    tabs = st.tabs(labels)

    with tabs[0]:
        _details_passages(passages, citees)
    with tabs[1]:
        _details_critic(rapport, hallus)
    if len(labels) == 3:
        with tabs[2]:
            if mode_usage == "scaffolding":
                details_historique_scaffolding()
            else:
                details_historique()


def _details_passages(passages: list[dict], citees: set[str]) -> None:
    if not passages:
        st.info("Aucun passage.")
        return

    def est_cite(p: dict) -> bool:
        m = p.get("metadata") or {}
        return m.get("source_path") in citees or m.get("url") in citees

    for p in sorted(passages, key=lambda p: not est_cite(p)):
        m = p.get("metadata") or {}
        label = m.get("source_path") or m.get("url") or "source"
        cite = est_cite(p)
        prefixe = "✦ " if cite else ""
        entete = f"{prefixe}{source_label(m.get('source_type', ''))} · {label}"
        with st.expander(entete, expanded=cite):
            d = p.get("distance")
            if d is not None:
                st.caption(f"distance {d:.3f}")
            st.markdown(p.get("content", ""))


def _details_critic(rapport: dict, hallus: list[str]) -> None:
    score = float(rapport.get("confidence_score", 0.0))
    st.progress(min(max(score, 0.0), 1.0), text=f"Confiance {score:.2f}")

    c1, c2 = st.columns(2)
    c1.metric("Ancrage sources", rapport.get("source_grounding", "n/a"))
    c2.metric("Conventions BB®", rapport.get("convention_alignment", "n/a"))

    warnings = rapport.get("warnings") or []
    if warnings:
        for w in warnings:
            st.warning(w)
    elif not hallus:
        st.success("Aucune alerte.")

    citees = rapport.get("sources_cited") or []
    if citees:
        st.caption("Sources citées par le Critic : " + ", ".join(f"`{s}`" for s in citees))


def details_historique() -> None:
    for e in st.session_state.historique[:-1]:
        with st.container(border=True):
            st.caption(
                f"Itération {e['iteration']} · "
                f"confiance {e['rapport'].get('confidence_score', 0):.2f}"
            )
            st.markdown(e["brouillon"])
    derniere = st.session_state.historique[-1]
    if derniere.get("rejet_precedent"):
        st.info(f"Ton commentaire précédent : *{derniere['rejet_precedent']}*")


def details_historique_scaffolding() -> None:
    for e in st.session_state.historique[:-1]:
        scaf = e.get("scaffolding") or {}
        with st.container(border=True):
            st.caption(
                f"Itération {e['iteration']} · "
                f"confiance {e['rapport'].get('confidence_score', 0):.2f} · "
                f"`{scaf.get('project_name', '?')}` · {len(scaf.get('files') or [])} fichiers"
            )
            for f in scaf.get("files") or []:
                st.markdown(f"- `{f.get('path', '?')}`")
    derniere = st.session_state.historique[-1]
    if derniere.get("rejet_precedent"):
        st.info(f"Ton commentaire précédent : *{derniere['rejet_precedent']}*")
