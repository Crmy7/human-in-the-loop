# BB® — Fiche technique client : État de Genève

> Référence technique pour les projets avec l'administration cantonale genevoise.
> Chef de projet BB® : Marc D. | Contact client : Catherine L. (DGSI)
> Marché public attribué en 2025.

## Contexte

L'État de Genève a mandaté BB® pour la refonte de trois portails citoyens. Contraintes administratives fortes : appels d'offres publics, conformité stricte, processus de validation longs.

## Projets

### 1. Portail démarches en ligne (`bb-ge-demarches`)

- **Stack front** : Nuxt 3, design system État de Genève (composants fournis)
- **Stack back** : Symfony 7, PostgreSQL 16, Keycloak (SSO cantonal)
- **Hébergement** : Infra cantonale (on livre, ils déploient sur leur OpenShift)
- **Particularités** :
  - Accessibilité WCAG 2.1 AA **obligatoire** (audit externe prévu)
  - Multilingue fr uniquement (administration genevoise)
  - Formulaires complexes avec sauvegarde brouillon
  - Signature électronique via SwissID

### 2. Intranet RH (`bb-ge-intranet-rh`)

- **Stack** : Symfony 7 monolithe (Twig), PostgreSQL, LDAP cantonal
- **Particularités** :
  - Pas de framework JS — Twig + Stimulus (exigence client)
  - Authentification LDAP, pas de JWT
  - Export Excel des données RH via PhpSpreadsheet

## Contraintes spécifiques État de Genève

1. **Hébergement cantonal** : tout tourne sur l'infra de la DGSI. Pas d'OVH, pas de cloud public.
2. **Livraison par artefact** : on ne déploie pas. On livre un `.tar.gz` avec le code buildé + un runbook.
3. **Pas de SaaS externe** : pas de Sentry SaaS, pas de Matomo cloud. Tout doit être auto-hébergé ou fourni par le canton.
4. **Cycle de validation long** : chaque livraison passe par QA interne DGSI (5 jours ouvrés), puis validation fonctionnelle (5 jours), puis comité de déploiement (1 semaine). Total : ~3 semaines entre livraison et MEP.
5. **Code source auditable** : le canton a le droit d'auditer le code à tout moment. Pas de dépendance obscure, pas de code obfusqué.
6. **Documentation exhaustive** : chaque livraison est accompagnée d'un document de release (changelog, impacts, procédure de rollback).

## Design system cantonal

L'État de Genève fournit son propre design system (composants Vue 3) : `@etat-geneve/design-system`.

Règles :
- Utiliser **exclusivement** les composants du design system cantonal pour l'UI
- Pas de TailwindCSS — le design system a son propre système de styles
- Charte graphique stricte : logo cantonal, couleurs officielles, typographie Frutiger

## Environnements

| Env | Accès | Géré par |
|---|---|---|
| Dev | Local BB® | BB® |
| Recette BB® | `ge-recette.bb-digital.ch` | BB® |
| Recette DGSI | Infra cantonale | DGSI |
| Prod | Infra cantonale | DGSI |

## Process de livraison

1. BB® développe et teste sur l'environnement de recette BB®
2. BB® produit l'artefact de livraison :
   ```bash
   pnpm build  # ou composer install --no-dev
   tar -czf livraison-v1.2.3.tar.gz --exclude=node_modules --exclude=.git .
   ```
3. BB® rédige le document de release
4. Transfert sécurisé de l'artefact via le portail DGSI (pas par email)
5. DGSI déploie sur recette → QA → comité → production

## Contacts

| Rôle | Nom | Canal |
|---|---|---|
| Responsable projet DGSI | Catherine L. | Email officiel |
| Architecte DGSI | Philippe R. | Email |
| PO métier | Nathalie S. | Email + calls bi-hebdo |
| CP BB® | Marc D. | Slack interne |
