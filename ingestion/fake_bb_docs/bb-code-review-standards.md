# BB® — Standards de Code Review

> Guide pour les reviewers et les auteurs de Merge Requests chez BB® Switzerland.

## Philosophie

La code review chez BB® n'est pas un contrôle qualité — c'est un outil de partage de connaissances. L'objectif principal est que deux personnes comprennent le code au lieu d'une seule. La qualité est un effet secondaire bienvenu.

## Délais de review

- **MR standard** : review sous 24h ouvrées maximum
- **Hotfix** : review dans l'heure (ping Slack `#dev-urgences`)
- **MR > 500 lignes** : le reviewer a le droit de demander un split. Les MR de plus de 500 lignes modifiées sont systématiquement plus risquées et moins bien reviewées.

## Ce que le reviewer vérifie

### 1. Logique métier
- Le code fait-il ce que le ticket demande ?
- Les edge cases sont-ils gérés ?
- La solution est-elle proportionnée au problème (pas d'over-engineering) ?

### 2. Sécurité
- Pas d'injection SQL (requêtes paramétrées, ORM)
- Pas de XSS (échappement des sorties)
- Pas de données sensibles dans les logs ou les réponses API
- Tokens et secrets via variables d'environnement, jamais en dur

### 3. Performance
- Pas de requête N+1 (vérifier les `eager loading` Doctrine / relations Eloquent)
- Pas de boucle sur des appels réseau ou DB
- Images optimisées si ajoutées

### 4. Lisibilité
- Noms de variables et fonctions explicites
- Pas de fonction de plus de 40 lignes — signe qu'il faut découper
- Commentaires uniquement quand le code ne suffit pas

### 5. Tests
- Tests unitaires pour la logique métier
- Tests fonctionnels pour les endpoints API
- Les tests existants passent toujours

## Conventions de commentaires

| Préfixe | Signification | Bloquant ? |
|---|---|---|
| `blocker:` | Bug, faille de sécurité, crash potentiel | Oui |
| `question:` | Besoin de comprendre un choix | Non |
| `nit:` | Suggestion stylistique ou amélioration mineure | Non |
| `suggestion:` | Alternative proposée, à discuter | Non |
| `praise:` | Code particulièrement bien écrit | Non |

Règle BB® : **un `praise:` par review minimum**. Ça ne coûte rien et ça change la dynamique.

## Bonnes pratiques pour l'auteur

1. **Relire sa propre MR avant de demander une review.** Corriger les TODO oubliés, les `console.log`, les imports inutilisés.
2. **Fournir du contexte.** La description de la MR doit expliquer le "pourquoi", pas le "quoi" (le diff montre le quoi).
3. **Garder les MR courtes.** Moins de 300 lignes modifiées idéalement. Si c'est plus, découper en MR successives.
4. **Répondre à tous les commentaires** avant de merger, même les `nit:` — un "noté, pas corrigé volontairement parce que X" est une réponse valable.

## Résolution des désaccords

Si auteur et reviewer ne sont pas d'accord :
1. Discussion en commentaire (3 échanges max)
2. Si pas de consensus : appel de 10 minutes
3. Si toujours pas : le tech lead tranche
4. Documenter la décision dans la MR pour référence future

## Outils

- **GitLab** : MR, commentaires, approbations
- **ESLint / PHPStan** : vérifications automatiques dans le pipeline CI — le reviewer ne devrait pas avoir à signaler ce qu'un linter peut détecter
- **SonarQube** : analyse statique, dette technique, couverture — dashboard accessible sur `sonar.bb-digital.ch`
