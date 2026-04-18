# BB® — Checklist SEO

> Optimisations SEO standard pour les sites vitrines et portails BB®.
> Applicable aux projets Nuxt 3 avec SSR activé.

## Pré-requis technique

- **SSR obligatoire** pour les pages qui doivent être indexées. Pas de SPA pure pour un site vitrine.
- **`useHead()`** de Nuxt pour gérer les balises meta de manière réactive.

## Balises meta par page

Chaque page doit définir au minimum :

```typescript
useHead({
  title: 'Titre de la page — Nom du client',
  meta: [
    { name: 'description', content: 'Description de 150-160 caractères...' },
    { property: 'og:title', content: 'Titre pour les réseaux sociaux' },
    { property: 'og:description', content: 'Description pour les réseaux sociaux' },
    { property: 'og:image', content: 'https://example.ch/og-image.jpg' },
    { property: 'og:type', content: 'website' },
    { name: 'twitter:card', content: 'summary_large_image' },
  ],
  link: [
    { rel: 'canonical', href: 'https://example.ch/page-courante' },
  ],
})
```

## Sitemap

Généré automatiquement via `@nuxtjs/sitemap` :

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  modules: ['@nuxtjs/sitemap'],
  sitemap: {
    hostname: 'https://example.ch',
    exclude: ['/admin/**', '/preview/**'],
  },
})
```

Vérifier que le sitemap est accessible sur `/sitemap.xml` et soumis dans Google Search Console.

## Robots.txt

```
# public/robots.txt
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
Sitemap: https://example.ch/sitemap.xml
```

En staging, bloquer l'indexation :
```
# Staging uniquement
User-agent: *
Disallow: /
```

## Structure HTML sémantique

- Un seul `<h1>` par page
- Hiérarchie de titres logique : `h1 > h2 > h3` (pas de saut)
- Utiliser les balises sémantiques : `<header>`, `<nav>`, `<main>`, `<article>`, `<footer>`
- Données structurées JSON-LD pour les pages pertinentes (Organisation, FAQ, BreadcrumbList)

## Images

- Attribut `alt` descriptif sur toutes les images informatives
- Attribut `width` et `height` pour éviter le CLS
- Lazy loading sauf above-the-fold
- Format WebP avec fallback

## Performance et SEO

Le score Lighthouse SEO doit être ≥ 90. Les critères principaux :
- Pages crawlables (pas de `noindex` involontaire)
- Liens valides (pas de 404)
- Texte lisible (taille de police ≥ 12px sur mobile)
- Pas de plugins bloquants

## Multilingue et SEO

Pour les sites multilingues (voir `bb-i18n-guidelines.md`) :

```html
<link rel="alternate" hreflang="fr" href="https://example.ch/" />
<link rel="alternate" hreflang="de" href="https://example.ch/de/" />
<link rel="alternate" hreflang="x-default" href="https://example.ch/" />
```

Nuxt i18n génère ces balises automatiquement si configuré correctement.

## Checklist avant MEP

- [ ] Chaque page a un `<title>` unique et un `<meta description>` unique
- [ ] URL canonique définie sur chaque page
- [ ] Sitemap généré et accessible
- [ ] `robots.txt` correct (allow en prod, disallow en staging)
- [ ] Données structurées validées (Google Rich Results Test)
- [ ] Pas de liens cassés (vérifier avec Screaming Frog ou `broken-link-checker`)
- [ ] Redirections 301 en place si refonte (ancien site → nouveau site)
- [ ] Google Search Console configurée et vérifiée
- [ ] Score Lighthouse SEO ≥ 90
