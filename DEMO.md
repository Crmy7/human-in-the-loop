# Scénario de démo — soutenance

Script de la démo live, avec plan B si le LLM part en vrille. Durée cible : **3 minutes**.

## Objectif pédagogique

Le jury doit comprendre sans explication textuelle ce que fait le HITL. On lui
fait vivre trois moments :

1. Un **pipeline complet avec validation humaine** qui rattrape un défaut
2. Le même pipeline sur un **second essai** qui aboutit à une écriture disque
3. Le même prompt en **mode dégradé (vibe coding)** qui écrit directement —
   et on ouvre le fichier pour pointer le défaut que le Critic aurait détecté

## Avant de lancer

```bash
# Vérifier que l'ingestion est à jour
python -m ingestion.run_all

# Nettoyer scaffolding_output/ pour une démo propre
rm -rf ./scaffolding_output/

# Lancer l'app
streamlit run app.py
```

Ouvre aussi deux onglets / fenêtres :
- **Navigateur** : Streamlit sur `localhost:8501`
- **Éditeur** : le repo ouvert sur le dossier `./scaffolding_output/` (pour montrer les fichiers après écriture)

## Question posée (copier-coller)

> Initialise un projet Nuxt 3 pour le client Raiffeisen avec intégration Matomo côté serveur et déploiement OVH, en respectant les conventions BB®.

## Déroulé minute par minute

### Temps 1 — Pipeline nominal, premier tour (0:00 → 1:00)

1. Sur l'accueil, sélectionner **🧱 Scaffolding projet**.
2. Laisser la case "mode dégradé" **décochée**.
3. Cliquer sur l'exemple Raiffeisen (ou coller la question).
4. Le bloc de statut affiche en live : *Recherche → Génération scaffolding → Vérification → À toi*.
5. **L'écran HITL apparaît**. Pointer au jury :
   - L'**arborescence** proposée : 4-6 fichiers
   - Le **bandeau Critic** (warning ou confiance selon le cas)
   - Les **3 boutons** : Valider / Modifier / Refaire

> Phrase à prononcer :
> *« Sans HITL, ces fichiers seraient déjà sur mon disque. Là, rien n'est écrit tant que je n'ai pas validé. »*

6. Ouvrir le rapport Critic et **montrer un warning concret**. Exemples probables :
   - `@nuxt/image en version obsolète par rapport à bb-nuxt-template`
   - `pas de .env.example alors que des clés API sont manipulées`
   - `pas de plugin Sentry malgré la convention bb-error-monitoring-sentry`

7. Cliquer **🔁 Faire une autre tentative**, cliquer **"↓ Reprendre les alertes du Critic"** pour pré-remplir le commentaire, puis **Envoyer et relancer**.

### Temps 2 — Second tour + écriture disque (1:00 → 2:00)

1. Le statut repart. Nouvelle itération.
2. L'écran HITL affiche **itération 2/3**, le Critic confirme une confiance haute.
3. Cliquer **✅ Valider et écrire sur disque**.
4. L'écran final affiche le chemin `./scaffolding_output/bb-raiffeisen-ebanking-front/`.
5. Basculer sur l'éditeur. **Ouvrir le dossier créé**. Montrer les 4-6 fichiers.

> Phrase à prononcer :
> *« Mon feu vert a déclenché l'écriture. C'est la matérialisation du HITL. »*

### Temps 3 — Mode dégradé, rejeu (2:00 → 3:00)

1. Retour à l'accueil (**🆕 Nouvelle demande**).
2. Cocher **⚠️ Mode démonstration dégradée**. Lire à voix haute le bandeau rouge.
3. Relancer la **même** question.
4. Le statut enchaîne Recherche → Génération → Écriture. **Pas de Critic, pas de HITL.**
5. L'écran final affiche les fichiers écrits dans `./scaffolding_output/bb-raiffeisen-ebanking-front-2/`.
6. Basculer sur l'éditeur. **Ouvrir le `package.json` de la version 2**. Pointer le défaut (version `^3.8.0` vs `3.15+`, ou absence de `.env.example`).

> Phrase à prononcer :
> *« Sans Critic ni relecture, le défaut part en prod. C'est ce que le HITL évite. »*

## Plan B — Si le LLM part en vrille ou l'API est down

Deux dossiers pré-peuplés existent dans `./demo_scaffolding/` pour servir de
plan de repli :

- `demo_scaffolding/bb-raiffeisen-ebanking-front/` — version nominale, propre
- `demo_scaffolding/bb-raiffeisen-ebanking-front-2/` — version dégradée avec les défauts

### Procédure de repli

```bash
# Copier les dossiers de démo dans scaffolding_output/
mkdir -p scaffolding_output
cp -r demo_scaffolding/bb-raiffeisen-ebanking-front scaffolding_output/
cp -r demo_scaffolding/bb-raiffeisen-ebanking-front-2 scaffolding_output/
```

Ensuite, tu fais la démo "sur rails" : tu narres le scénario en ouvrant
directement les fichiers dans l'éditeur. Tu perds l'effet live mais tu gardes
le message.

## Défauts visibles dans la version dégradée (pour pointer au jury)

Dans `bb-raiffeisen-ebanking-front-2/` :

1. **`package.json`** : `nuxt ^3.8.0` au lieu de `^3.15.0` (obsolète vs convention BB®) · `@nuxt/image ^0.7.1` (très obsolète) · pas d'`engines` Node · pas de scripts `lint` ni `typecheck` ni `preview` · pas de `@sentry/nuxt`
2. **`nuxt.config.ts`** : 3 lignes, pas de `runtimeConfig`, pas de Sentry, pas de citation source
3. **`plugins/matomo.client.ts`** : `siteId` **hardcodé** à `"1"` (anti-pattern), pas de désactivation dev, pas de `setTrackerUrl`, pas de citation
4. **Pas de `.env.example`** — alors que le script Matomo consomme des variables
5. **`README.md`** minimal, aucune référence aux conventions BB®

Chacun de ces points est un **warning que le Critic aurait soulevé** en mode nominal.

## Commandes utiles pendant la démo

```bash
# Reset complet
rm -rf scaffolding_output/

# Relancer l'app (si plantage)
streamlit run app.py

# Voir les fichiers générés
ls -la scaffolding_output/
tree scaffolding_output/ 2>/dev/null || find scaffolding_output/ -type f

# Ouvrir un fichier dans VS Code depuis le terminal
code scaffolding_output/bb-raiffeisen-ebanking-front/package.json
```

## Checklist avant soutenance

- [ ] Ingestion ChromaDB à jour (407+ chunks)
- [ ] Clés API valides dans `.env` (Anthropic OU OpenAI selon `LLM_PROVIDER`)
- [ ] `scaffolding_output/` vide (supprimé)
- [ ] `demo_scaffolding/` présent comme plan B
- [ ] App lancée avant de parler (éviter la latence de cold start)
- [ ] Deux onglets ouverts : Streamlit + éditeur de code
- [ ] Démo répétée trois fois avec chronomètre, ≤ 3 min
