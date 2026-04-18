# BB® — Monitoring d'erreurs avec Sentry

> Configuration et bonnes pratiques Sentry pour les projets BB® Switzerland.
> Instance : Sentry SaaS (`bb-digital.sentry.io`)
> Plan : Team (50k events/mois)

## Pourquoi Sentry

Chaque projet BB® en production doit avoir un monitoring d'erreurs actif. Les `console.error` et les logs serveur ne suffisent pas — on a besoin d'alertes proactives, de stack traces contextualisées, et d'un historique des régressions.

## Création d'un projet Sentry

1. Se connecter à `bb-digital.sentry.io` avec le SSO Google Workspace
2. Créer un projet sous l'équipe `#bb-engineering`
3. Nommer le projet `bb-<client>-<front|api>` (ex. `bb-raiffeisen-front`)
4. Récupérer le DSN et le stocker dans 1Password sous `Sentry / <client> / DSN`
5. Ajouter le DSN dans les variables d'environnement du projet

## Intégration Nuxt 3

### Installation

```bash
pnpm add @sentry/vue
```

### Plugin Sentry

Créer `plugins/sentry.client.ts` :

```typescript
import * as Sentry from '@sentry/vue'

export default defineNuxtPlugin((nuxtApp) => {
  const config = useRuntimeConfig()

  if (!config.public.sentryDsn) return

  Sentry.init({
    app: nuxtApp.vueApp,
    dsn: config.public.sentryDsn,
    environment: process.env.NODE_ENV,
    tracesSampleRate: 0.2,  // 20% des transactions pour le tracing perf
    replaysSessionSampleRate: 0,
    replaysOnErrorSampleRate: 0.5,  // 50% des sessions avec erreur
    integrations: [
      Sentry.browserTracingIntegration({
        router: useRouter(),
      }),
    ],
  })
})
```

### Capturer des erreurs manuellement

```typescript
import * as Sentry from '@sentry/vue'

try {
  await riskyOperation()
} catch (error) {
  Sentry.captureException(error, {
    tags: { module: 'payment', client: 'raiffeisen' },
    extra: { orderId: order.id },
  })
}
```

## Intégration Symfony

### Installation

```bash
composer require sentry/sentry-symfony
```

### Configuration

```yaml
# config/packages/sentry.yaml
sentry:
  dsn: '%env(SENTRY_DSN)%'
  options:
    environment: '%kernel.environment%'
    traces_sample_rate: 0.2
    send_default_pii: false  # RGPD — jamais de données personnelles par défaut
```

### Contexte utilisateur

```php
// src/EventSubscriber/SentryUserSubscriber.php
class SentryUserSubscriber implements EventSubscriberInterface
{
    public static function getSubscribedEvents(): array
    {
        return [RequestEvent::class => 'onRequest'];
    }

    public function onRequest(RequestEvent $event): void
    {
        $user = $this->security->getUser();
        if ($user) {
            \Sentry\configureScope(function (\Sentry\State\Scope $scope) use ($user): void {
                $scope->setUser([
                    'id' => $user->getId(),
                    'email' => $user->getEmail(), // Attention RGPD — OK si consentement
                ]);
            });
        }
    }
}
```

## Alertes

### Configuration standard BB®

| Règle | Condition | Action |
|---|---|---|
| Nouvelle erreur | Premier événement d'une issue | Notification Slack `#dev-alerts` |
| Régression | Issue résolue qui réapparaît | Notification Slack + email au dev qui a résolu |
| Spike | > 50 events en 5 minutes | Notification Slack `#dev-urgences` + email tech lead |

### Canal Slack

- `#dev-alerts` : toutes les nouvelles erreurs, volume modéré
- `#dev-urgences` : spikes et erreurs critiques uniquement

## Bonnes pratiques

1. **Résoudre ou ignorer chaque issue dans Sentry.** Pas d'issues "pending" vieilles de 6 mois.
2. **Taguer les erreurs par module** (`payment`, `auth`, `pdf`, `api`) pour faciliter le tri.
3. **Ne pas capturer les erreurs attendues** (404, validation) — ça noie le signal.
4. **Vérifier le quota** mensuellement. À 80% du quota, alerter le tech lead.
5. **Source maps** : uploader les source maps en production pour des stack traces lisibles.

```bash
# Upload des source maps Nuxt
pnpm sentry:sourcemaps  # Script à ajouter dans package.json
```

## Revue hebdomadaire

Chaque lundi, le dev de garde fait une revue de 15 minutes des issues Sentry ouvertes :
- Trier les nouvelles issues (assigner, résoudre, ou ignorer)
- Vérifier qu'il n'y a pas de régression sur les issues résolues
- Confirmer que les alertes fonctionnent (test ping si doute)
