"""Interface Streamlit de l'Assistant Technique BB® — deux modes + démo dégradée."""

import re
import uuid
from pathlib import Path

import streamlit as st
from langgraph.types import Command

from evaluation.sus_form import rendre_formulaire_sus
from graph.builder import construire_graphe

st.set_page_config(page_title="Assistant Technique BB®", layout="centered")

FORMULE_REFUS = (
    "La documentation interne BB® et les sources publiques indexées ne couvrent pas ce point."
)

EXT_TO_LANG = {
    ".ts": "typescript", ".tsx": "typescript",
    ".js": "javascript", ".jsx": "javascript",
    ".py": "python",
    ".json": "json",
    ".yaml": "yaml", ".yml": "yaml",
    ".md": "markdown",
    ".sh": "bash", ".bash": "bash",
    ".php": "php",
    ".vue": "html",
    ".html": "html",
    ".css": "css", ".scss": "scss",
    ".env": "ini", ".example": "ini",
    ".toml": "toml",
}


def _langage_pour(path: str) -> str:
    if path.endswith("Makefile") or path.endswith("makefile"):
        return "makefile"
    if path.endswith("Dockerfile"):
        return "dockerfile"
    suffix = Path(path).suffix.lower()
    return EXT_TO_LANG.get(suffix, "text")


# --------------------------------------------------------------------------- #
# Session
# --------------------------------------------------------------------------- #

def _init() -> None:
    st.session_state.setdefault("mode_usage", "question")        # "question" | "scaffolding"
    st.session_state.setdefault("degrade", False)
    st.session_state.setdefault("thread_id", str(uuid.uuid4()))
    st.session_state.setdefault("mode", "normal")                # state UI du HITL
    st.session_state.setdefault("afficher_sus", False)
    st.session_state.setdefault("historique", [])
    st.session_state.setdefault("dernier_rejet", None)
    _assurer_graphe()


def _assurer_graphe() -> None:
    """Recompile le graphe si degrade a changé (ou première fois)."""
    signature = ("degrade" if st.session_state.degrade else "nominal")
    if st.session_state.get("_graphe_signature") != signature:
        st.session_state.graphe = construire_graphe(
            interactif=True,
            degrade=st.session_state.degrade,
        )
        st.session_state._graphe_signature = signature


def _config() -> dict:
    return {"configurable": {"thread_id": st.session_state.thread_id}}


def _reset() -> None:
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.mode = "normal"
    st.session_state.historique = []
    st.session_state.dernier_rejet = None


# --------------------------------------------------------------------------- #
# Utilitaires
# --------------------------------------------------------------------------- #

_RE_CITATION = re.compile(r"\[([a-zA-Z0-9_\-./#]+\.md|/[a-zA-Z0-9_\-./]+)\]")


def _citations(texte: str) -> set[str]:
    return set(_RE_CITATION.findall(texte or ""))


def _hallucinations(reponse: str, passages: list[dict]) -> list[str]:
    dispo: set[str] = set()
    for p in passages:
        m = p.get("metadata") or {}
        if m.get("source_path"):
            dispo.add(m["source_path"])
        if m.get("url"):
            dispo.add(m["url"])
    return sorted(_citations(reponse) - dispo)


def _detecter_mode_reponse(brouillon: str, rapport: dict, hallus: list[str]) -> str:
    if FORMULE_REFUS.lower() in (brouillon or "").lower():
        return "refus"
    score = float(rapport.get("confidence_score", 0.0))
    warnings = rapport.get("warnings") or []
    if hallus or warnings or score < 0.5 or rapport.get("source_grounding") == "low":
        return "attention"
    return "confiance"


# --------------------------------------------------------------------------- #
# Exécution avec progression live
# --------------------------------------------------------------------------- #

def _invoquer(entree) -> None:
    with st.status("Traitement en cours…", expanded=True) as status:
        for update in st.session_state.graphe.stream(
            entree, config=_config(), stream_mode="updates"
        ):
            for node in update:
                if node == "retriever":
                    n = len(update[node].get("passages", []))
                    st.write(f"🔍 Recherche — {n} passages trouvés")
                elif node == "generator":
                    mode_usage = st.session_state.mode_usage
                    label = "🧱 Génération scaffolding" if mode_usage == "scaffolding" else "✍️ Rédaction"
                    st.write(label)
                elif node == "critic":
                    score = (update[node].get("rapport_critique") or {}).get("confidence_score", 0)
                    st.write(f"🔬 Vérification — confiance {score:.2f}")
                elif node == "__interrupt__":
                    st.write("✋ À toi de décider")
                elif node == "executor":
                    out = update[node].get("executor_output") or {}
                    st.write(f"💾 Écriture — {out.get('nb_fichiers', '?')} fichiers sur disque")
        status.update(label="✅ Prêt", state="complete", expanded=False)
    _maj_historique()


def _maj_historique() -> None:
    state = st.session_state.graphe.get_state(_config())
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


# --------------------------------------------------------------------------- #
# Accueil
# --------------------------------------------------------------------------- #

def _vue_accueil() -> None:
    st.title("Assistant Technique BB®")
    st.write(
        "Assistant RAG avec **validation humaine obligatoire**. "
        "Corpus : docs internes BB®, Nuxt 3, Symfony 7."
    )

    mode = st.radio(
        "Mode",
        options=["question", "scaffolding"],
        format_func=lambda m: "❓ Question technique" if m == "question" else "🧱 Scaffolding projet",
        horizontal=True,
        index=0 if st.session_state.mode_usage == "question" else 1,
        key="_radio_mode",
    )
    if mode != st.session_state.mode_usage:
        st.session_state.mode_usage = mode
        _reset()

    if st.session_state.mode_usage == "scaffolding":
        _bandeau_degrade()

    with st.container(border=True):
        if st.session_state.mode_usage == "question":
            st.markdown(
                "**Question technique**  \n"
                "1. Tu poses ta question  \n"
                "2. L'IA cherche dans la doc et rédige un brouillon + le Critic l'audite  \n"
                "3. Tu **valides**, **modifies** ou **refais** (max 3 itérations)"
            )
            exemples = [
                "Quelle est la convention de nommage BB® pour un projet Nuxt ?",
                "Donne-moi la structure d'un projet Symfony BB® avec intégration Matomo.",
                "Quel est le process de facturation BB® pour un client récurrent ?",
            ]
        else:
            st.markdown(
                "**Scaffolding projet**  \n"
                "1. Tu décris le projet à initialiser  \n"
                "2. L'IA propose **4 à 6 fichiers à créer** + le Critic les audite  \n"
                "3. Tu **valides** → les fichiers sont écrits dans `./scaffolding_output/`  \n"
                "4. Ou tu **modifies** chaque fichier · ou tu **refais** avec un retour"
            )
            exemples = [
                "Initialise un projet Nuxt 3 pour le client Raiffeisen avec intégration Matomo côté serveur et déploiement OVH, en respectant les conventions BB®.",
                "Scaffolde un nouveau projet Symfony 7 BB® pour le client Etat de Genève avec API REST.",
            ]

    st.markdown("### Ta question")
    question = st.chat_input("Entrée pour envoyer")

    st.caption("Ou essaie un exemple :")
    for q in exemples:
        if st.button(q, use_container_width=True, key=f"ex_{hash(q)}"):
            _lancer(q)
            return

    if question:
        _lancer(question.strip())


def _bandeau_degrade() -> None:
    st.checkbox(
        "⚠️ **Mode démonstration dégradée (vibe coding — ne pas utiliser en production)**",
        key="degrade",
        help="Active un pipeline sans Critic ni HITL : les fichiers sont écrits immédiatement, sans validation humaine. Ce mode existe uniquement pour illustrer la différence avec le pipeline nominal.",
    )
    _assurer_graphe()
    if st.session_state.degrade:
        st.error(
            "🚨 **Mode dégradé actif.** Le Critic et le HITL sont désactivés. "
            "Les fichiers seront **écrits sur disque sans vérification et sans validation humaine**, "
            "directement après la génération. À utiliser uniquement pour la démo de soutenance."
        )


def _lancer(question: str) -> None:
    _reset()
    _invoquer(
        {"question": question, "mode": st.session_state.mode_usage, "iteration": 0}
    )
    st.rerun()


# --------------------------------------------------------------------------- #
# HITL — mode Question
# --------------------------------------------------------------------------- #

def _vue_hitl_question(payload: dict) -> None:
    iteration = payload.get("iteration", 1)
    brouillon = payload.get("reponse_brouillon", "")
    passages = payload.get("passages", [])
    rapport = payload.get("rapport_critique") or {}
    citees = _citations(brouillon)
    hallus = _hallucinations(brouillon, passages)
    mode_rep = _detecter_mode_reponse(brouillon, rapport, hallus)

    st.caption("TA QUESTION")
    st.markdown(f"> {payload['question']}")

    _bandeau_contexte_question(mode_rep, rapport)

    if hallus:
        st.error(
            "🚨 **Hallucination détectée** : la réponse cite des sources absentes des passages :\n\n"
            + "\n".join(f"- `{s}`" for s in hallus)
        )

    entete = "### Brouillon à valider"
    if iteration > 1:
        entete += f"  · _itération {iteration}/3_"
    st.markdown(entete)
    with st.container(border=True):
        st.markdown(brouillon)
        if citees:
            st.caption("Sources citées : " + " ".join(f"`{c}`" for c in sorted(citees)))

    _zone_decision_question(payload, mode_rep)

    st.divider()
    st.caption("Creuse si besoin")
    with st.expander(f"📚 {len(passages)} passages consultés"):
        _details_passages(passages, citees)
    with st.expander("🔍 Rapport d'audit complet"):
        _details_critic(rapport, hallus)
    if len(st.session_state.historique) > 1:
        with st.expander(f"🔁 {len(st.session_state.historique) - 1} version(s) précédente(s)"):
            _details_historique()


def _bandeau_contexte_question(mode_rep: str, rapport: dict) -> None:
    score = float(rapport.get("confidence_score", 0.0))
    if mode_rep == "refus":
        st.info(
            "🛑 **L'assistant dit qu'il ne sait pas.** Si ta question est hors doc, "
            "**confirme le refus**."
        )
    elif mode_rep == "attention":
        st.warning(
            f"⚠️ **Le Critic a des réserves** (confiance {score:.2f}). "
            "Lis avant de décider."
        )
    else:
        st.success(f"✓ **Confiance {score:.2f}** — réponse bien ancrée. Relis rapidement et publie.")


# --------------------------------------------------------------------------- #
# HITL — mode Scaffolding
# --------------------------------------------------------------------------- #

def _vue_hitl_scaffolding(payload: dict) -> None:
    iteration = payload.get("iteration", 1)
    scaffolding = payload.get("scaffolding_propose") or {}
    passages = payload.get("passages", [])
    rapport = payload.get("rapport_critique") or {}
    files = scaffolding.get("files") or []

    st.caption("TA DEMANDE")
    st.markdown(f"> {payload['question']}")

    _bandeau_contexte_scaffolding(rapport)

    entete = "### Scaffolding proposé"
    if iteration > 1:
        entete += f"  · _itération {iteration}/3_"
    st.markdown(entete)

    project_name = scaffolding.get("project_name", "?")
    description = scaffolding.get("description", "")
    with st.container(border=True):
        st.markdown(f"📁 **`{project_name}/`** ({len(files)} fichiers)")
        if description:
            st.caption(description)
        for f in files:
            st.markdown(f"- `{f.get('path', '?')}`")

    st.markdown("#### Contenu des fichiers")
    for f in files:
        path = f.get("path", "?")
        with st.expander(f"📄 `{path}`"):
            st.code(f.get("content", ""), language=_langage_pour(path))

    _zone_decision_scaffolding(payload)

    st.divider()
    st.caption("Creuse si besoin")
    with st.expander(f"📚 {len(passages)} passages consultés"):
        _details_passages(passages, set())
    with st.expander("🔍 Rapport d'audit complet"):
        _details_critic(rapport, [])
    if len(st.session_state.historique) > 1:
        with st.expander(f"🔁 {len(st.session_state.historique) - 1} version(s) précédente(s)"):
            _details_historique_scaffolding()


def _bandeau_contexte_scaffolding(rapport: dict) -> None:
    score = float(rapport.get("confidence_score", 0.0))
    warnings = rapport.get("warnings") or []
    if warnings:
        st.warning(
            f"⚠️ **Le Critic a remonté {len(warnings)} alerte(s)** (confiance {score:.2f}). "
            "Lis-les dans le rapport avant d'écrire sur disque."
        )
    elif score < 0.5:
        st.warning(f"⚠️ **Faible confiance** ({score:.2f}) — vérifie avant d'écrire.")
    else:
        st.success(
            f"✓ **Confiance {score:.2f}** — la proposition respecte les conventions BB®. "
            "Si ça te va, tu peux valider pour créer les fichiers."
        )


# --------------------------------------------------------------------------- #
# Zones de décision
# --------------------------------------------------------------------------- #

def _zone_decision_question(payload: dict, mode_rep: str) -> None:
    if mode_rep == "refus":
        v_label = "✅ Valider le refus"
        v_aide = "Accepter que l'assistant dise 'je ne sais pas'"
        m_label = "✎ Écrire la réponse moi-même"
        r_label = "🔁 Relancer l'IA"
    else:
        v_label = "✅ Valider"
        v_aide = "Le brouillon devient la réponse finale"
        m_label = "✎ Modifier le texte"
        r_label = "🔁 Faire une autre tentative"

    if st.session_state.mode == "normal":
        st.markdown("**Ton rôle : relire le brouillon ci-dessus et choisir.**")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button(v_label, use_container_width=True, type="primary"):
                _decider({"action": "approve"})
            st.caption(v_aide)
        with c2:
            if st.button(m_label, use_container_width=True):
                st.session_state.mode = "edit"
                st.rerun()
            st.caption("Tu l'édites toi-même")
        with c3:
            if st.button(r_label, use_container_width=True):
                st.session_state.mode = "reject"
                st.rerun()
            st.caption("Tu dis ce qui cloche, l'IA retente")
        if payload.get("iteration", 1) >= 3:
            st.warning("⚠️ Itération 3/3 — dernière tentative.")

    elif st.session_state.mode == "edit":
        st.caption("Édite le texte. Il sera publié tel quel.")
        texte = st.text_area(
            "Ta version",
            value=payload["reponse_brouillon"],
            height=260,
            label_visibility="collapsed",
        )
        c1, c2 = st.columns(2)
        if c1.button("✅ Publier ma version", type="primary", use_container_width=True):
            _decider({"action": "edit", "texte": texte})
        if c2.button("Annuler", use_container_width=True):
            st.session_state.mode = "normal"
            st.rerun()

    elif st.session_state.mode == "reject":
        _zone_reject(payload)


def _zone_decision_scaffolding(payload: dict) -> None:
    scaffolding = payload.get("scaffolding_propose") or {}

    if st.session_state.mode == "normal":
        st.markdown("**Ton rôle : relire la proposition ci-dessus et décider.**")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("✅ Valider et écrire sur disque", use_container_width=True, type="primary"):
                _decider({"action": "approve"})
            st.caption("Les fichiers sont créés sous scaffolding_output/")
        with c2:
            if st.button("✎ Modifier les fichiers", use_container_width=True):
                st.session_state.mode = "edit"
                st.rerun()
            st.caption("Tu édites le contenu avant écriture")
        with c3:
            if st.button("🔁 Faire une autre tentative", use_container_width=True):
                st.session_state.mode = "reject"
                st.rerun()
            st.caption("Tu dis ce qui cloche, l'IA retente")
        if payload.get("iteration", 1) >= 3:
            st.warning("⚠️ Itération 3/3 — dernière tentative.")

    elif st.session_state.mode == "edit":
        st.caption("Édite chaque fichier puis publie ta version complète.")
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
        c1, c2 = st.columns(2)
        if c1.button("✅ Écrire ma version sur disque", type="primary", use_container_width=True):
            nouveau = {
                "project_name": scaffolding.get("project_name", "projet"),
                "description": scaffolding.get("description", ""),
                "files": edited,
            }
            _decider({"action": "edit", "scaffolding": nouveau})
        if c2.button("Annuler", use_container_width=True):
            st.session_state.mode = "normal"
            st.rerun()

    elif st.session_state.mode == "reject":
        _zone_reject(payload)


def _zone_reject(payload: dict) -> None:
    st.caption(
        "Écris ce qui ne va pas. Ton texte est réinjecté dans le prompt du Generator."
    )
    warnings = (payload.get("rapport_critique") or {}).get("warnings") or []
    if warnings:
        suggestion = " · ".join(warnings)
        if st.button("↓ Reprendre les alertes du Critic"):
            st.session_state["_prerempli"] = suggestion
            st.rerun()

    valeur = st.session_state.pop("_prerempli", "")
    commentaire = st.text_area(
        "Ton retour",
        value=valeur,
        height=140,
        placeholder="Exemple : tu as oublié le fichier .env.example et la version de @nuxt/image est obsolète.",
        label_visibility="collapsed",
    )
    c1, c2 = st.columns(2)
    if c1.button(
        "🔁 Envoyer et relancer",
        type="primary",
        disabled=not commentaire.strip(),
        use_container_width=True,
    ):
        _decider({"action": "reject", "commentaire": commentaire.strip()})
    if c2.button("Annuler", use_container_width=True):
        st.session_state.mode = "normal"
        st.rerun()


def _decider(decision: dict) -> None:
    if decision.get("action") == "reject":
        st.session_state.dernier_rejet = decision.get("commentaire")
    _invoquer(Command(resume=decision))
    st.session_state.mode = "normal"
    st.rerun()


# --------------------------------------------------------------------------- #
# Détails repliables
# --------------------------------------------------------------------------- #

def _source_label(source_type: str) -> str:
    return {
        "bb_internal": "BB®",
        "nuxt_official": "Nuxt",
        "symfony_official": "Symfony",
    }.get(source_type, source_type or "?")


def _details_passages(passages: list[dict], citees: set[str]) -> None:
    if not passages:
        st.info("Aucun passage récupéré.")
        return

    def est_cite(p):
        m = p.get("metadata") or {}
        return m.get("source_path") in citees or m.get("url") in citees

    for p in sorted(passages, key=lambda p: not est_cite(p)):
        m = p.get("metadata") or {}
        label = m.get("source_path") or m.get("url") or "source inconnue"
        cite = est_cite(p)
        prefixe = "⭐ cité · " if cite else ""
        entete = f"{prefixe}`{_source_label(m.get('source_type', ''))}` · {label}"
        with st.expander(entete, expanded=cite):
            d = p.get("distance")
            if d is not None:
                st.caption(f"distance cosinus : {d:.3f}")
            st.markdown(p.get("content", ""))


def _details_critic(rapport: dict, hallus: list[str]) -> None:
    score = float(rapport.get("confidence_score", 0.0))
    st.progress(min(max(score, 0.0), 1.0), text=f"Confiance : {score:.2f}")
    c1, c2 = st.columns(2)
    c1.metric("Ancrage sources", rapport.get("source_grounding", "n/a"))
    c2.metric("Conventions BB®", rapport.get("convention_alignment", "n/a"))

    warnings = rapport.get("warnings") or []
    if warnings:
        st.markdown("**Alertes :**")
        for w in warnings:
            st.warning(w)
    elif not hallus:
        st.success("Aucune alerte.")

    citees = rapport.get("sources_cited") or []
    if citees:
        st.caption("Sources identifiées : " + ", ".join(f"`{s}`" for s in citees))


def _details_historique() -> None:
    for entree in st.session_state.historique[:-1]:
        with st.container(border=True):
            st.markdown(
                f"**Itération {entree['iteration']}** — "
                f"confiance {entree['rapport'].get('confidence_score', 0):.2f}"
            )
            st.markdown(entree["brouillon"])
    derniere = st.session_state.historique[-1]
    if derniere.get("rejet_precedent"):
        st.info(f"🗣️ Ton commentaire qui a relancé le Generator : _{derniere['rejet_precedent']}_")


def _details_historique_scaffolding() -> None:
    for entree in st.session_state.historique[:-1]:
        scaf = entree.get("scaffolding") or {}
        with st.container(border=True):
            st.markdown(
                f"**Itération {entree['iteration']}** — "
                f"confiance {entree['rapport'].get('confidence_score', 0):.2f}"
            )
            st.caption(f"`{scaf.get('project_name', '?')}/` — {len(scaf.get('files') or [])} fichiers")
            for f in scaf.get("files") or []:
                st.markdown(f"- `{f.get('path', '?')}`")
    derniere = st.session_state.historique[-1]
    if derniere.get("rejet_precedent"):
        st.info(f"🗣️ Ton commentaire qui a relancé : _{derniere['rejet_precedent']}_")


# --------------------------------------------------------------------------- #
# Vue finale
# --------------------------------------------------------------------------- #

def _vue_finale(values: dict) -> None:
    mode_usage = values.get("mode", "question")
    decision = values.get("decision_humaine")
    executor_output = values.get("executor_output") or {}

    libelle = {
        "approve": "Validée telle quelle",
        "edit": "Éditée puis validée",
        "reject": "Diffusée après 3 rejets (limite)",
    }.get(decision, "Terminée")

    if st.session_state.degrade:
        st.error(
            "🚨 **Mode dégradé** — les fichiers ont été écrits **sans validation humaine**. "
            "Ni Critic, ni HITL n'ont tourné."
        )
    else:
        st.success(f"✅ {libelle}")

    st.caption("TA DEMANDE")
    st.markdown(f"> {values.get('question', '')}")

    if mode_usage == "scaffolding":
        if executor_output:
            st.markdown("### Fichiers créés sur disque")
            with st.container(border=True):
                st.markdown(f"📁 **`{executor_output.get('dossier_ecrit', '?')}`**")
                st.caption(f"{executor_output.get('nb_fichiers', '?')} fichiers écrits")
        scaf = values.get("scaffolding_propose") or {}
        if scaf.get("files"):
            with st.expander(f"📄 Revoir les {len(scaf['files'])} fichiers"):
                for f in scaf["files"]:
                    path = f.get("path", "?")
                    st.markdown(f"**`{path}`**")
                    st.code(f.get("content", ""), language=_langage_pour(path))
    else:
        st.markdown("### Réponse finale")
        with st.container(border=True):
            st.markdown(values.get("reponse_finale") or "(vide)")

    if len(st.session_state.historique) > 1:
        fn = _details_historique_scaffolding if mode_usage == "scaffolding" else _details_historique
        with st.expander(f"🔁 Voir les {len(st.session_state.historique) - 1} version(s) précédente(s)"):
            fn()

    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("🆕 Nouvelle demande", type="primary", use_container_width=True):
        _reset()
        st.rerun()
    if c2.button("📝 Noter l'outil (SUS)", use_container_width=True):
        st.session_state.afficher_sus = True
        st.rerun()


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main() -> None:
    _init()

    if st.session_state.afficher_sus:
        rendre_formulaire_sus()
        if st.button("← Retour"):
            st.session_state.afficher_sus = False
            _reset()
            st.rerun()
        return

    state = st.session_state.graphe.get_state(_config())

    if not state.values:
        _vue_accueil()
        return

    payload = None
    for task in state.tasks:
        if task.interrupts:
            payload = task.interrupts[0].value
            break

    if payload is not None:
        if payload.get("mode") == "scaffolding":
            _vue_hitl_scaffolding(payload)
        else:
            _vue_hitl_question(payload)
        return

    _vue_finale(state.values)


if __name__ == "__main__":
    main()
