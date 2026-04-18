# bb-raiffeisen-ebanking-front

Projet Nuxt 3 pour le client **Raiffeisen** avec tracking Matomo et monitoring Sentry.

> Template conforme aux conventions BB® — voir `bb-nuxt-template-README.md`.

## Prérequis

- Node 20 LTS, pnpm 9+
- Accès `npm.bb-digital.ch`
- `.env.local` rempli à partir de `.env.example`

## Commandes

```bash
pnpm install
pnpm dev
pnpm build
pnpm preview
```

## Déploiement

Cible : serveur OVH Zurich (`raiffeisen.bb-digital.ch`). Voir
`bb-deployment-ovh-checklist.md` pour la procédure complète (staging freeze
48h, tag SemVer, merge staging → main, SSH pull).

<!-- source: bb-nuxt-template-README.md, bb-deployment-ovh-checklist.md -->
