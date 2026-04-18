# BB® — Fiche technique client : Raiffeisen Suisse

> Référence technique pour l'équipe BB® travaillant sur les projets Raiffeisen.
> Chef de projet BB® : Sarah M. | Contact client : Thomas K. (IT Raiffeisen)
> Contrat cadre actif depuis 2023.

## Contexte

Raiffeisen Suisse est le client principal de BB® en termes de volume. Trois projets actifs, un en maintenance. L'équipe dédiée est composée de 2 développeurs front, 1 développeur back, et 1 chef de projet.

## Projets actifs

### 1. Portail Partenaires (`bb-raiffeisen-partners`)

- **Stack front** : Nuxt 3.15, Pinia, i18n (fr/de/it), TailwindCSS
- **Stack back** : Symfony 7.2, API Platform, PostgreSQL 16
- **Hébergement** : OVH Bare Metal ZRH (exigence Raiffeisen : données en Suisse)
- **Auth** : OpenID Connect via Keycloak Raiffeisen
- **Particularités** :
  - Multilingue 3 langues obligatoire (fr, de, it)
  - Double validation sur les opérations financières (workflow Symfony)
  - Export PDF des relevés via Gotenberg (conteneur Docker dédié)
  - SLA : 99.5% uptime, temps de réponse API < 500ms au P95

### 2. Site vitrine corporate (`bb-raiffeisen-corporate`)

- **Stack** : Nuxt 3, contenu via Storyblok CMS
- **Hébergement** : OVH GRA (pas de contrainte de localisation pour le site public)
- **Particularités** :
  - SSR obligatoire pour le SEO
  - Performance : score Lighthouse > 90 sur toutes les métriques
  - Intégration Matomo (siteId: 7)
  - Bandeau cookie conforme nLPD

### 3. Dashboard analytics interne (`bb-raiffeisen-dashboard`)

- **Stack** : Nuxt 3, Chart.js, API interne Raiffeisen
- **Hébergement** : Infra interne Raiffeisen (on livre, ils déploient)
- **Particularités** :
  - Pas d'accès internet — uniquement réseau interne Raiffeisen
  - Build statique livré en `.tar.gz`
  - Données financières sensibles — jamais de mock avec des données réelles dans le repo

## Contraintes spécifiques Raiffeisen

1. **Sécurité renforcée** : audit de sécurité annuel par un tiers. Le code doit passer les tests OWASP Top 10.
2. **Localisation des données** : toutes les données clients en Suisse. Pas de CDN hors Suisse, pas de Google Fonts en direct (héberger localement).
3. **Accessibilité** : WCAG 2.1 AA obligatoire sur les interfaces client-facing.
4. **Processus de release** : validation par Thomas K. avant chaque MEP. Prévoir 48h de délai pour son OK.
5. **Communication** : canal Slack partagé `#bb-raiffeisen`, calls hebdomadaires le mardi 10h.

## Environnements

| Projet | Staging | Prod |
|---|---|---|
| Partners | `partners-staging.bb-digital.ch` | `partners.raiffeisen.ch` (DNS Raiffeisen) |
| Corporate | `raiffeisen-staging.bb-digital.ch` | `www.raiffeisen.ch` (DNS Raiffeisen) |
| Dashboard | N/A | Livré en build statique |

## Contacts

| Rôle | Nom | Canal |
|---|---|---|
| IT Lead Raiffeisen | Thomas K. | Email + Slack `#bb-raiffeisen` |
| PO Raiffeisen | Isabelle F. | Email |
| Sécurité Raiffeisen | Marc B. | Email (pour audits) |
| CP BB® | Sarah M. | Slack interne |
| Dev lead BB® | Charles R. | Slack interne |
