# Assistant Technique BB® — POC mémoire

POC Python d'un Assistant Technique interne basé sur un RAG agentique avec
validation humaine obligatoire. Support du mémoire de Master MyDigitalSchool 2026
(BB® Switzerland).

## Architecture

Quatre nœuds LangGraph, un checkpoint humain, un nœud d'écriture disque pour
le mode scaffolding, et une boucle de retour plafonnée à 3 itérations :

```
START → retriever → generator → critic → hitl → [approve (question)     → END]
                                            ├── [approve (scaffolding)  → executor → END]
                                            ├── [edit    (question)     → END]
                                            ├── [edit    (scaffolding)  → executor → END]
                                            └── [reject  (iter<3)       → generator]
```

Deux modes d'usage :
- **Question technique** — réponse en prose, validation humaine avant
  publication.
- **Scaffolding projet** — proposition de 4-6 fichiers JSON, validation
  humaine avant **écriture effective sur disque** dans `scaffolding_output/`.

Un **mode démonstration dégradée** (vibe coding) court-circuite le Critic et
le HITL pour illustrer par contraste ce que l'architecture apporte.

- **Retriever** : similarity search k=5 sur ChromaDB, filtre optionnel par
  `source_type`. Embeddings OpenAI `text-embedding-3-small`.
- **Generator** : Claude Sonnet 4.5 avec prompt strict — réponse uniquement à
  partir des passages, citation systématique, formule littérale d'aveu
  d'ignorance si le corpus ne couvre pas.
- **Critic** : second appel Claude qui retourne un JSON normalisé
  (confidence_score, source_grounding, convention_alignment, warnings,
  sources_cited). Retry jusqu'à 3 fois si le JSON n'est pas parsable.
- **HITL** : `interrupt()` de LangGraph + reprise via `Command(resume=...)`,
  intégré à Streamlit via `st.session_state["thread_id"]` persistant.

## Corpus

Trois sources indexées :

1. **Documentation interne BB®** — 23 fichiers Markdown fictifs dans
   `ingestion/fake_bb_docs/` (conventions Nuxt/Symfony, déploiement OVH,
   GitLab, Matomo, Sentry, conventions clients, etc.).
2. **Documentation Nuxt 3 officielle** — 17 pages ciblées (Getting Started,
   Directory Structure, Guide).
3. **Documentation Symfony 7 officielle** — 13 pages ciblées (Setup,
   Configuration, Routing, Controllers, Best Practices, etc.).

## Prérequis

- Python 3.11 (testé sur macOS Darwin 25.4).
- Deux clés API : Anthropic et OpenAI.
- Accès réseau pour le premier crawl (cache local ensuite).

## Installation

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# édite .env avec tes clés ANTHROPIC_API_KEY et OPENAI_API_KEY
```

## Ingestion

Peuple la collection ChromaDB (`./data/chroma/` par défaut). Opération
idempotente : la collection est supprimée et recréée à chaque run.

```bash
python -m ingestion.run_all
```

Durée indicative : 1–3 minutes (crawl 30 pages + embeddings ~500 chunks).

## Lancement de l'application

```bash
streamlit run app.py
```

L'interface expose :

- un champ de question en haut ;
- la réponse brouillon en Markdown ;
- à gauche, les passages sources (expanders avec distance cosinus) ;
- à droite, le rapport du Critic (barre de confiance, métriques, warnings) ;
- trois boutons **Approuver / Modifier / Rejeter**. Un rejet avec commentaire
  réinjecte le feedback dans le prompt Generator, jusqu'à 3 itérations.

Un bouton _« Noter l'outil (SUS) »_ ouvre le formulaire System Usability Scale
à 10 questions standard.

### Mode scaffolding

Dans l'accueil, bascule le sélecteur sur **🧱 Scaffolding projet**. Tu décris
un projet (ex. *« Initialise un Nuxt 3 pour Raiffeisen avec Matomo et OVH »*),
l'IA propose 4-6 fichiers. Tu vois l'arborescence + le contenu de chaque
fichier. Tu **valides** (création effective dans `./scaffolding_output/`),
**modifies** fichier par fichier, ou **refais** avec un commentaire.

Le **mode démonstration dégradée** (case à cocher) désactive Critic et HITL.
À réserver à la soutenance, pour la comparaison avant/après. Voir `DEMO.md`
pour le scénario complet.

## Évaluation

Run RAGAS non-interactif sur les 30 questions du dataset (10 factuelles,
10 scaffolding, 10 hors corpus) :

```bash
python -m evaluation.ragas_runner
```

Métriques calculées : Faithfulness, Answer Relevancy, Context Precision,
Context Recall + taux de refus correct sur les 10 questions hors corpus.
Résultats sauvegardés dans `data/eval_results/ragas_<timestamp>.json`.

Les résultats SUS sont dans `data/eval_results/sus_<timestamp>.json`.

## Tests

```bash
pytest tests/ -v
```

Couvre le chunker (découpage, overlap, métadonnées), le parsing JSON du Critic
et le routage conditionnel du graphe (7 branches). Pas de test Streamlit.

## Structure du repo

```
.
├── app.py                        # Interface Streamlit
├── config.py                     # Config centralisée (.env)
├── requirements.txt
├── .env.example
├── graph/
│   ├── state.py                  # EtatAssistant (TypedDict)
│   ├── llm_client.py             # Adaptateur Anthropic / OpenAI
│   ├── retriever.py
│   ├── generator.py              # Modes question + scaffolding
│   ├── critic.py                 # Modes question + scaffolding
│   ├── executor.py               # Écriture disque validée (scaffolding)
│   ├── prompts.py                # 4 prompts : Generator/Critic × question/scaffolding
│   └── builder.py                # StateGraph + interrupt + routage
├── demo_scaffolding/             # Versions pré-peuplées pour plan B soutenance
├── DEMO.md                       # Scénario de soutenance
├── ingestion/
│   ├── chunker.py
│   ├── docusaurus.py             # Lecture fake_bb_docs + dossier .md
│   ├── github.py                 # Crawl Nuxt + Symfony
│   ├── run_all.py                # Script one-shot d'ingestion
│   └── fake_bb_docs/             # 23 README BB® fictifs
├── evaluation/
│   ├── dataset.py                # 30 questions de test
│   ├── ragas_runner.py
│   └── sus_form.py
├── tests/                        # pytest
└── data/                         # .gitignore : chroma, raw_html, eval_results
```

## Notes

Choix de conception, points d'arbitrage et versions de libs critiques :
voir `NOTES.md`.
