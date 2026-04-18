# BB® — Modèle de branching Git

> Convention de gestion des branches pour tous les projets BB® Switzerland.
> Hébergement : GitLab self-hosted (`gitlab.bb-digital.ch`)

## Branches permanentes

| Branche | Rôle | Protection |
|---|---|---|
| `main` | Code en production | Push direct interdit, merge via MR uniquement |
| `staging` | Pré-production, validation client | Push direct interdit |
| `develop` | Intégration continue | Push direct autorisé pour hotfixes mineurs |

## Branches de travail

Convention de nommage : `<type>/<ticket>-<description-courte>`

Types autorisés :
- `feature/` — nouvelle fonctionnalité
- `fix/` — correction de bug
- `hotfix/` — correction urgente en production
- `chore/` — maintenance, refactoring, mise à jour de dépendances
- `docs/` — documentation uniquement

Exemples :
- `feature/BB-142-formulaire-contact`
- `fix/BB-207-erreur-500-login`
- `hotfix/BB-310-fuite-memoire-pdf`
- `chore/BB-089-upgrade-nuxt-3.15`

## Flux de travail standard

```
feature/BB-142-xxx  →  develop  →  staging  →  main
         ↑                ↑           ↑          ↑
       Développeur     Merge MR    Merge MR   Merge MR
                       auto-merge   après QA   après OK client
```

1. Créer la branche depuis `develop`
2. Développer, committer régulièrement
3. Ouvrir une Merge Request vers `develop`
4. Code review par au moins 1 autre développeur BB®
5. Merge dans `develop` (squash merge autorisé)
6. Tester sur l'environnement de dev
7. Merge `develop → staging` pour validation client
8. Après OK client : merge `staging → main` + tag de version

## Commits

Format : `<type>(<scope>): <description>`

```
feat(auth): ajouter la connexion OAuth2 Raiffeisen
fix(pdf): corriger l'encodage UTF-8 des factures
chore(deps): mettre à jour Nuxt 3.14 → 3.15
docs(api): documenter l'endpoint /api/v1/invoices
```

Le scope est optionnel mais recommandé. La description est en français, à l'impératif, sans point final.

Longueur max du titre : 72 caractères. Détails dans le body si nécessaire, séparé par une ligne vide.

## Merge Requests

### Checklist MR BB®

Chaque MR doit inclure :
- [ ] Titre avec le numéro de ticket (`BB-142 : Formulaire de contact`)
- [ ] Description du changement (quoi et pourquoi)
- [ ] Screenshots si changement visuel
- [ ] Tests ajoutés ou mis à jour
- [ ] Pas de `console.log` ou `dump()` oubliés
- [ ] Pas de TODO non-résolu

### Règles de review

- **1 approbation minimum** pour merger dans `develop`
- **2 approbations** pour merger dans `main`
- Le reviewer vérifie : logique métier, sécurité, performance, lisibilité
- Les commentaires de review sont en français
- Convention : `nit:` pour les suggestions non-bloquantes, `blocker:` pour les points à corriger avant merge

## Hotfix

Procédure accélérée pour les bugs critiques en production :

```
main → hotfix/BB-310-xxx → main (direct)
                         → develop (cherry-pick)
```

1. Brancher depuis `main`
2. Corriger le bug
3. MR directe vers `main` — 1 review suffit, pas besoin de passer par staging
4. Tag immédiat après merge
5. Cherry-pick du fix dans `develop` pour ne pas perdre la correction

## Tags et versions

Format SemVer : `vX.Y.Z`
- **X** (majeur) : changement d'API cassant, refonte majeure
- **Y** (mineur) : nouvelle feature
- **Z** (patch) : bugfix

Chaque merge dans `main` est accompagné d'un tag. Pas d'exception.
