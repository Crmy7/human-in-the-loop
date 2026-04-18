# NOTES — journal des choix et points d'attention

Notes consignées au fil de l'eau pendant le dev, comme demandé dans le brief.

## Choix de conception non-évidents

### Chunker — `section` active au début du chunk (pas à la fin)

Premier jet : la métadonnée `section` prenait le dernier titre vu jusqu'à la
fin du chunk. Problème : quand un chunk chevauche un changement de section,
il se retrouvait étiqueté avec la section qu'il quitte à peine. Semantique
plus utile pour le RAG : la section à laquelle le chunk appartient, c'est-à-dire
celle active à son point d'entrée. Je prends donc le dernier titre vu dans
`tokens[:start+20]` — le `+20` permet de capter un titre qui ouvrirait le chunk.

### Retriever — clients OpenAI et Chroma mis en cache module

Éviter les handshakes TLS répétés à chaque question. Variables de module,
initialisées paresseusement. Pas de DI container, pas de factory — juste une
closure modulaire. Conforme au « pas d'over-engineering » du brief.

### Generator — incrémentation d'`iteration` dans le nœud

L'incrémentation est faite dans le Generator, pas dans le routeur. Raison :
chaque appel au Generator est une itération, par définition. Ça garde le
routeur purement décisionnel et permet de capper le nombre d'appels LLM
(coût) plutôt que le nombre de rejets UI.

### Critic — rapport par défaut si le JSON dérive 3 fois

Le brief dit « fail early, fail loud ». Vrai pour les crashs. Mais si le
modèle rend du JSON mal formé malgré 2 retries avec rappel explicite, on
préfère un rapport `confidence_score=0.0 / source_grounding=low` plutôt que
de crasher l'UI. C'est l'information « le Critic n'a rien pu dire », elle
reste utile à l'utilisateur. Warning logué côté serveur.

### Builder — mode `interactif=False` pour l'éval

Le même graphe alimente l'UI (avec `interrupt()` réel) et le runner RAGAS
(auto-approve). Un flag à la compilation, pas un second graphe. Évite la
duplication.

### HITL / Streamlit — pas de `st.form`

`st.form` mettrait en cache les interactions jusqu'au submit, ce qui
casserait le rendu différencié selon `mode_ui` (normal / edit / reject).
J'utilise `st.session_state.mode_ui` + `st.rerun()` après chaque action.

### Ingestion idempotente

`ingestion.run_all` supprime puis recrée la collection à chaque run. Plus
simple à raisonner qu'un upsert fin. Pour un POC (quelques centaines de
chunks, quelques secondes d'embeddings), c'est acceptable. Pour un vrai
pipeline, il faudrait diff par content hash.

## Versions de libs critiques

- **LangGraph ≥ 0.3** : API utilisée — `StateGraph.compile(checkpointer=InMemorySaver())`,
  `langgraph.types.interrupt`, `Command(resume=...)`,
  `graph.get_state(config).tasks[*].interrupts[*].value`. Vérifié que
  `InMemorySaver` est bien le nom stable à partir de la 0.3. Si une future
  version renomme à `MemorySaver`, un seul import à changer dans
  `graph/builder.py`.

- **RAGAS ≥ 0.2** : API utilisée — `SingleTurnSample`, `EvaluationDataset`,
  `evaluate(dataset=..., metrics=[...], llm=..., embeddings=...)`,
  wrappers `LangchainLLMWrapper` et `LangchainEmbeddingsWrapper`. Les
  métriques sont instanciées (`Faithfulness()` etc.) — c'est la forme
  recommandée en 0.2+.

- **ChromaDB ≥ 0.5** : `PersistentClient(path=...)`. Je passe les embeddings
  pré-calculés explicitement à `collection.add(embeddings=...)` plutôt que
  de configurer une `embedding_function` — plus lisible pour le jury et
  évite la dépendance Chroma → OpenAI.

- **Anthropic SDK** : `client.messages.create(model, max_tokens, system, messages)`.
  Modèle par défaut `claude-sonnet-4-5-20250929`, surchargeable via
  `LLM_MODEL` dans `.env`.

## Points d'hésitation / à trancher avec Charles

### Crawl Nuxt/Symfony vs seed HTML

Le brief prévoit un fallback offline via des fichiers HTML pré-téléchargés.
Je n'ai pas committé de seed (coût en taille de repo, difficile de choisir
quelles pages). L'implémentation se contente d'un warning + skip si une URL
échoue. Conséquence : sans réseau, seule la doc BB® est indexée. À arbitrer
si Charles veut un vrai offline pour la démo jury.

### Taille des prompts

Les prompts Generator et Critic font ~30-40 lignes chacun. En-dessous des
30 lignes fixées comme seuil dans le brief, mais proches. Si on itère et
qu'ils dépassent, les sortir en fichiers `.txt` comme suggéré.

### Pas de limite sur la longueur des passages concaténés dans le Generator

Si les 5 passages font chacun 800 tokens, on envoie ~4k tokens en input au
Generator. Claude Sonnet encaisse sans problème (contexte 200k), mais ça
gonfle la facture. Pas de tronquage pour l'instant ; à surveiller si le
coût dérive.

### Évaluation RAGAS — budget

Les 30 questions × (1 appel generator + 1 appel critic) = 60 appels Claude
pour le run du graphe, puis RAGAS fait ses propres appels d'évaluation
(multiple appels LLM par métrique × par sample). Compter ~200 appels LLM
totaux par exécution de `ragas_runner.py`. À ne pas lancer à la légère.

## Ce qui ne marche pas (encore) sur mon poste

Rien de bloquant à date. Tous les tests pytest passent (19/19). Les
imports des modules lourds (LangGraph, RAGAS, Streamlit) sont OK. La
compilation du graphe fonctionne. Pas encore testé de bout en bout avec
de vraies clés API — ça reste à faire lors de la première démo.
