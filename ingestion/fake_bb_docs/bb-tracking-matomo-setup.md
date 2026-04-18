# BB® — Intégration Matomo (Server-Side)

> Procédure d'intégration du tracking Matomo pour les projets BB®.
> Instance Matomo hébergée : `analytics.bb-digital.ch`
> Version Matomo : 5.x

## Pourquoi Matomo et pas GA4

BB® utilise Matomo auto-hébergé pour trois raisons :
1. **Conformité RGPD / nLPD suisse** — les données restent sur notre infra OVH Suisse
2. **Pas de sampling** — contrairement à GA4, Matomo conserve 100% des hits
3. **Demande client récurrente** — Raiffeisen, Etat de Genève et plusieurs clients institutionnels l'exigent contractuellement

## Configuration côté Matomo

1. Créer un nouveau site dans Matomo (`Administration > Sites > Ajouter un site`)
2. Noter le `siteId` attribué
3. Créer un token API dédié au projet (`Administration > Sécurité > Tokens d'API`)
4. Stocker le token dans le vault 1Password BB® sous `Matomo / <client> / token-api`

## Intégration Nuxt 3

### Plugin client

Créer `plugins/matomo.client.ts` :

```typescript
export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  const siteId = config.public.matomoSiteId

  if (!siteId || siteId === '0') return // Désactivé en dev

  const script = document.createElement('script')
  script.async = true
  script.src = `https://analytics.bb-digital.ch/matomo.js`
  document.head.appendChild(script)

  window._paq = window._paq || []
  window._paq.push(['setTrackerUrl', 'https://analytics.bb-digital.ch/matomo.php'])
  window._paq.push(['setSiteId', siteId])
  window._paq.push(['trackPageView'])
  window._paq.push(['enableLinkTracking'])
})
```

### Tracking SPA

Pour le suivi des navigations SPA, ajouter dans `app.vue` ou un middleware global :

```typescript
const router = useRouter()
router.afterEach((to) => {
  if (window._paq) {
    window._paq.push(['setCustomUrl', to.fullPath])
    window._paq.push(['setDocumentTitle', document.title])
    window._paq.push(['trackPageView'])
  }
})
```

### Events custom

Convention de nommage des events BB® :

| Catégorie | Action | Nom | Exemple |
|---|---|---|---|
| `form` | `submit` | `<nom-formulaire>` | `form / submit / contact` |
| `cta` | `click` | `<identifiant-cta>` | `cta / click / hero-devis` |
| `download` | `click` | `<nom-fichier>` | `download / click / brochure-2026.pdf` |
| `video` | `play` | `<titre-video>` | `video / play / demo-produit` |

```typescript
// Composable réutilisable
export function useTracking() {
  function trackEvent(category: string, action: string, name?: string, value?: number) {
    if (window._paq) {
      window._paq.push(['trackEvent', category, action, name, value])
    }
  }
  return { trackEvent }
}
```

## Intégration Symfony (Server-Side Tracking)

Pour les événements backend (soumission de formulaire validée, paiement confirmé, etc.) :

```php
// src/Service/MatomoTrackingService.php
class MatomoTrackingService
{
    public function __construct(
        private readonly HttpClientInterface $httpClient,
        private readonly string $matomoUrl,
        private readonly string $matomoToken,
        private readonly int $matomoSiteId,
    ) {}

    public function trackServerEvent(string $category, string $action, string $name): void
    {
        $this->httpClient->request('GET', $this->matomoUrl . '/matomo.php', [
            'query' => [
                'idsite' => $this->matomoSiteId,
                'rec' => 1,
                'token_auth' => $this->matomoToken,
                'e_c' => $category,
                'e_a' => $action,
                'e_n' => $name,
            ],
        ]);
    }
}
```

## Vérification post-intégration

Checklist avant MEP :
- [ ] Le siteId est correct par environnement (0 en dev, réel en staging/prod)
- [ ] Le token API n'apparaît jamais côté client
- [ ] Le tracking SPA fonctionne (vérifier dans Matomo > Visiteurs > Temps réel)
- [ ] Les events custom remontent avec les bons noms
- [ ] Le bandeau cookie est en place et respecte le consentement (voir `bb-cookie-consent.md`)
- [ ] Le Content Security Policy autorise `analytics.bb-digital.ch`
