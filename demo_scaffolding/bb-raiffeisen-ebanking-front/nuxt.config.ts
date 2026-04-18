// Configuration Nuxt 3 pour bb-raiffeisen-ebanking-front
// source: bb-nuxt-template-README.md, bb-tracking-matomo-setup.md

export default defineNuxtConfig({
  devtools: { enabled: true },
  modules: ["@nuxt/image", "@sentry/nuxt/module"],

  runtimeConfig: {
    // Secrets côté serveur uniquement
    matomoApiToken: process.env.MATOMO_API_TOKEN,
    public: {
      matomoSiteId: process.env.MATOMO_SITE_ID,
      sentryDsn: process.env.SENTRY_DSN,
    },
  },

  typescript: {
    strict: true,
  },

  // Dossier plugins/ : matomo.client.ts et sentry.client.ts chargés automatiquement
})
