"""Formulaire SUS (System Usability Scale) intégré à Streamlit, 10 questions standard."""

import json
from datetime import datetime, timezone

import streamlit as st

from config import DATA_DIR

QUESTIONS_SUS: list[tuple[str, str]] = [
    ("positif", "Je pense que j'utiliserais cet outil fréquemment."),
    ("negatif", "J'ai trouvé cet outil inutilement complexe."),
    ("positif", "J'ai trouvé cet outil facile à utiliser."),
    ("negatif", "Je pense que j'aurais besoin de l'aide d'une personne technique pour pouvoir utiliser cet outil."),
    ("positif", "J'ai trouvé que les différentes fonctions de cet outil étaient bien intégrées."),
    ("negatif", "J'ai trouvé qu'il y avait trop d'incohérences dans cet outil."),
    ("positif", "J'imagine que la plupart des gens apprendraient à utiliser cet outil très rapidement."),
    ("negatif", "J'ai trouvé cet outil très lourd à utiliser."),
    ("positif", "Je me suis senti·e en confiance en utilisant cet outil."),
    ("negatif", "J'ai eu besoin d'apprendre beaucoup de choses avant de pouvoir commencer à utiliser cet outil."),
]

ECHELLE = ["1 — Pas du tout d'accord", "2", "3 — Neutre", "4", "5 — Tout à fait d'accord"]


def _calculer_score_sus(reponses: list[int]) -> float:
    """Score SUS normalisé 0-100 à partir de 10 réponses 1-5."""
    assert len(reponses) == 10
    total = 0
    for i, note in enumerate(reponses):
        if QUESTIONS_SUS[i][0] == "positif":
            total += note - 1
        else:
            total += 5 - note
    return total * 2.5


def _sauvegarder(score: float, reponses: list[int], commentaire: str) -> str:
    dossier = DATA_DIR / "eval_results"
    dossier.mkdir(parents=True, exist_ok=True)
    horodatage = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    chemin = dossier / f"sus_{horodatage}.json"
    rapport = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "score_sus": score,
        "reponses": [
            {"question": QUESTIONS_SUS[i][1], "ton": QUESTIONS_SUS[i][0], "note": r}
            for i, r in enumerate(reponses)
        ],
        "commentaire": commentaire,
    }
    chemin.write_text(json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(chemin)


def _interpreter(score: float) -> str:
    if score >= 80:
        return "Excellent (grade A)"
    if score >= 68:
        return "Bon (grade B)"
    if score >= 51:
        return "Correct (grade C)"
    return "Insuffisant (grade D ou F)"


def rendre_formulaire_sus() -> None:
    """Affiche le formulaire SUS à 10 questions et sauvegarde le score à la soumission."""
    st.header("Évaluation de l'outil — SUS")
    st.caption(
        "System Usability Scale (Brooke, 1996). Note chaque affirmation de 1 "
        "(pas du tout d'accord) à 5 (tout à fait d'accord)."
    )

    reponses: list[int] = []
    for i, (_, texte) in enumerate(QUESTIONS_SUS, start=1):
        choix = st.radio(
            f"{i}. {texte}",
            options=ECHELLE,
            index=2,
            key=f"sus_q{i}",
            horizontal=True,
        )
        reponses.append(int(choix[0]))

    commentaire = st.text_area(
        "Commentaire libre (optionnel)",
        placeholder="Ce qui t'a aidé·e, ce qui t'a gêné·e, idées d'amélioration…",
    )

    if st.button("Envoyer mon évaluation", type="primary"):
        score = _calculer_score_sus(reponses)
        chemin = _sauvegarder(score, reponses, commentaire.strip())
        st.success(f"Score SUS : **{score:.1f} / 100** — {_interpreter(score)}")
        st.caption(f"rapport sauvegardé : `{chemin}`")
