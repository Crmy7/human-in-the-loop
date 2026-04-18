# BB® — Budget de performance web

> Seuils de performance non-négociables pour les projets BB® client-facing.
> Outil de mesure : Lighthouse CI en pipeline + WebPageTest mensuel.

## Seuils Lighthouse

| Métrique | Minimum | Cible |
|---|---|---|
| Performance | 80 | 90+ |
| Accessibility | 90 | 100 |
| Best Practices | 90 | 100 |
| SEO | 90 | 100 |

Un score Lighthouse Performance sous 80 bloque la MEP. Pas de dérogation sans validation du tech lead.

## Core Web Vitals

| Métrique | Seuil "Bon" | Notre cible |
|---|---|---|
| LCP (Largest Contentful Paint) | < 2.5s | < 2.0s |
| FID (First Input Delay) | < 100ms | < 50ms |
| CLS (Cumulative Layout Shift) | < 0.1 | < 0.05 |
| INP (Interaction to Next Paint) | < 200ms | < 150ms |

## Budget de taille

### JavaScript

| Catégorie | Budget max |
|---|---|
| Bundle JS initial (gzippé) | 150 KB |
| Par route (lazy-loaded) | 50 KB |
| Total JS (toutes routes) | 500 KB |

### Images

- Format : WebP obligatoire, AVIF si support navigateur suffisant
- Images hero : max 200 KB
- Thumbnails : max 30 KB
- Toujours utiliser `<NuxtImg>` avec `loading="lazy"` sauf above-the-fold

### Fonts

- Max 2 familles de polices par projet
- Subset : latin uniquement sauf besoin spécifique
- Format : WOFF2 uniquement
- Hébergement local (pas de Google Fonts CDN — conformité RGPD)
- Budget total fonts : 100 KB

## Optimisations Nuxt obligatoires

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  experimental: {
    payloadExtraction: true,    // Réduit le JS initial
  },
  image: {
    provider: 'ipx',
    formats: ['webp', 'avif'],
  },
  routeRules: {
    '/': { prerender: true },
    '/blog/**': { isr: 3600 },  // ISR 1h pour le contenu blog
  },
})
```

## Monitoring continu

### Lighthouse CI

Intégré au pipeline GitLab, bloque la MR si les seuils ne sont pas respectés :

```yaml
# .gitlab-ci.yml (extrait)
lighthouse:
  stage: quality
  script:
    - pnpm build
    - lhci autorun --config=lighthouserc.json
  allow_failure: false
```

### WebPageTest

Test mensuel sur les pages clés (home, listing, détail). Résultats archivés dans le drive BB® sous `Perf / <client> / <date>`.

Responsable : le dev front du projet, avec notification calendrier le 1er de chaque mois.

## Checklist performance avant MEP

- [ ] Lighthouse score > 80 sur les 4 catégories
- [ ] Bundle JS initial < 150 KB gzippé
- [ ] Toutes les images en WebP avec lazy loading
- [ ] Fonts en WOFF2 hébergées localement
- [ ] Pas de render-blocking CSS/JS
- [ ] Cache headers configurés (assets statiques : 1 an, HTML : no-cache)
- [ ] Compression Brotli activée sur Nginx
