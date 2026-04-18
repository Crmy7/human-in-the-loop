# BB® — Onboarding développeur

> Checklist d'intégration pour tout nouveau développeur rejoignant l'équipe BB® Switzerland.
> Durée estimée : 1 journée pour les accès, 1 semaine pour être autonome.

## Jour 1 — Accès et setup

### Accès à demander (via Sarah M. ou le tech lead)

- [ ] Compte Google Workspace BB® (`prenom@bb-digital.ch`)
- [ ] Accès GitLab (`gitlab.bb-digital.ch`) — groupe `@bb-engineering`
- [ ] Accès Slack workspace BB® — rejoindre `#dev-general`, `#dev-alerts`, `#dev-urgences`
- [ ] Accès 1Password vault `Engineering`
- [ ] Accès Sentry (`bb-digital.sentry.io`)
- [ ] Accès SonarQube (`sonar.bb-digital.ch`)
- [ ] Accès Matomo (`analytics.bb-digital.ch`) — rôle `view` sur tous les sites
- [ ] Accès au panel OVH — rôle `read-only` (demander au tech lead pour les droits écriture)
- [ ] Clé SSH générée et ajoutée aux serveurs staging/prod

### Setup local

```bash
# macOS — outils de base
brew install node@20 pnpm php@8.3 composer postgresql@16 redis

# Cloner le template Nuxt
git clone git@gitlab.bb-digital.ch:templates/bb-nuxt-starter.git ~/bb/templates/nuxt

# Cloner le template Symfony
git clone git@gitlab.bb-digital.ch:templates/bb-symfony-starter.git ~/bb/templates/symfony

# Configurer Git
git config --global user.name "Prénom Nom"
git config --global user.email "prenom@bb-digital.ch"
git config --global pull.rebase true
```

### IDE recommandé

- **VS Code** avec les extensions :
  - Vue - Official (anciennement Volar)
  - TypeScript Vue Plugin
  - ESLint
  - Prettier
  - PHP Intelephense
  - GitLens
- **PHPStorm** accepté pour les devs Symfony, licence fournie par BB®

## Semaine 1 — Montée en compétence

### Lire en priorité

1. Ce document
2. `bb-git-branching-model.md`
3. `bb-code-review-standards.md`
4. `bb-nuxt-template-README.md` ou `bb-symfony-project-conventions.md` selon ton affectation
5. La documentation du projet client sur lequel tu vas travailler

### Premier ticket

Le tech lead assigne un ticket `good-first-issue` dans le premier ou deuxième jour. C'est un ticket volontairement simple (fix CSS, ajout d'un champ, refacto mineur) dont l'objectif est de :
- Vérifier que le setup local fonctionne
- Passer par le cycle complet : branche → code → MR → review → merge
- Se familiariser avec le projet et les conventions

### Pair programming

Le premier jour sur un projet, le dev existant fait 2h de pair programming pour :
- Expliquer l'architecture du projet
- Montrer les patterns récurrents
- Pointer les pièges connus

## Rituels

| Rituel | Fréquence | Durée | Participants |
|---|---|---|---|
| Daily standup | Quotidien 9h30 | 10 min | Équipe projet |
| Code review | Continue | — | Tous les devs |
| Sprint planning | Bi-hebdo (lundi) | 1h | Équipe projet + PO |
| Retrospective | Bi-hebdo (vendredi) | 45 min | Équipe projet |
| Tech talk BB® | Mensuel (1er jeudi) | 30 min | Toute l'équipe dev |

## Culture technique BB®

- On préfère la simplicité à l'élégance. Un code ennuyeux qui marche vaut mieux qu'un code brillant qu'on ne comprend pas.
- On documente les décisions, pas le code. Le code change, les décisions restent.
- On review le code des autres comme on aimerait qu'on review le nôtre.
- On demande de l'aide après 30 minutes bloqué, pas après 3 heures.
- On ne merge pas un vendredi après 16h. Jamais.
