# BB® Nuxt 3 Template — `bb-nuxt-starter`

> Template officiel pour tout nouveau projet front Nuxt 3 chez BB® Switzerland.
> Dernière mise à jour : mars 2026 — Nuxt 3.15+

## Prérequis

- Node.js 20 LTS
- pnpm 9+
- Accès au registre GitLab BB® (`npm.bb-digital.ch`)

## Initialisation d'un nouveau projet

```bash
npx degit git@gitlab.bb-digital.ch:templates/bb-nuxt-starter.git mon-projet
cd mon-projet
pnpm install
cp .env.example .env.local
```

## Convention de nommage

- Nom du repo : `bb-<client>-<projet>-front` (ex. `bb-raiffeisen-ebanking-front`)
- Branches : voir `bb-git-branching-model.md`
- Composants : PascalCase, préfixe `Bb` pour les composants internes réutilisables (`BbHeader.vue`, `BbFooter.vue`, `BbCookieBanner.vue`)
- Composables : `use` + camelCase (`useTracking`, `useAuth`)
- Pages : kebab-case, miroir de la route (`pages/mon-compte/index.vue`)

## Structure imposée

```
src/
├── assets/
│   ├── scss/
│   │   ├── _variables.scss      # Tokens BB® (couleurs, typo, spacing)
│   │   ├── _mixins.scss
│   │   └── main.scss
│   └── images/
├── components/
│   ├── Bb/                      # Composants design-system BB®
│   └── [Feature]/               # Composants métier par feature
├── composables/
├── layouts/
│   ├── default.vue
│   └── blank.vue                # Pour les landing pages sans nav
├── middleware/
├── pages/
├── plugins/
│   ├── matomo.client.ts         # Tracking côté client uniquement
│   └── sentry.client.ts
├── public/
│   └── favicon.ico
├── server/
│   └── api/                     # API routes BFF si nécessaire
├── stores/                      # Pinia stores
└── utils/
```

## Configuration Nuxt (`nuxt.config.ts`)

Paramètres imposés par la baseline BB® :

```ts
export default defineNuxtConfig({
  ssr: true,                          // SSR par défaut, désactiver au cas par cas
  devtools: { enabled: true },
  typescript: { strict: true },
  css: ['~/assets/scss/main.scss'],
  modules: [
    '@pinia/nuxt',
    '@nuxtjs/i18n',                   // Multilingue obligatoire en Suisse
    '@vueuse/nuxt',
  ],
  runtimeConfig: {
    matomoToken: '',                  // Jamais exposé côté client
    public: {
      matomoSiteId: '',
      sentryDsn: '',
      apiBaseUrl: '',
    },
  },
  i18n: {
    locales: ['fr', 'de', 'en'],      // Minimum fr + de pour la Suisse
    defaultLocale: 'fr',
    strategy: 'prefix_except_default',
  },
})
```

## Environnements

| Variable | Dev | Staging | Prod |
|---|---|---|---|
| `NUXT_PUBLIC_API_BASE_URL` | `http://localhost:8000/api` | `https://staging-api.bb-digital.ch` | `https://api.bb-digital.ch` |
| `NUXT_PUBLIC_MATOMO_SITE_ID` | `0` (désactivé) | `12` | `12` |
| `NUXT_PUBLIC_SENTRY_DSN` | vide | DSN staging | DSN prod |

## Déploiement

Voir `bb-deployment-ovh-checklist.md` pour la procédure complète.

Build de production :

```bash
pnpm build
node .output/server/index.mjs
```

Le port par défaut est `3000`. En production sur OVH, Nginx fait le reverse-proxy sur ce port.

## Scripts utiles

```bash
pnpm dev          # Dev server avec HMR
pnpm build        # Build production
pnpm preview      # Preview du build localement
pnpm lint         # ESLint + Prettier
pnpm typecheck    # Vérification TypeScript stricte
```

## Règles non-négociables

1. **Pas de `any`** dans le code TypeScript. Utiliser `unknown` + type guard si nécessaire.
2. **Pas de logique métier dans les composants**. Extraire dans les composables ou les stores.
3. **Pas d'appels API directs** dans les composants. Passer par un composable `useApi*`.
4. **Multilingue dès le jour 1**. Pas de texte en dur dans les templates.
5. **Accessibilité WCAG 2.1 AA minimum**. Vérifier avec axe-core avant chaque MEP.
