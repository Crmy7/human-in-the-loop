# BB® — Stratégie de tests

> Approche pragmatique du testing chez BB® Switzerland.
> On ne vise pas 100% de couverture. On vise la confiance au moment du deploy.

## Philosophie

La pyramide de tests BB® est simple :
1. **Tests unitaires** pour la logique métier isolée (calculs, transformations, validations)
2. **Tests fonctionnels** pour les endpoints API (le contrat avec le front)
3. **Tests E2E** uniquement sur les parcours critiques (login, paiement, formulaire principal)

On ne teste pas :
- Le framework (Symfony/Nuxt sait déjà faire du routing)
- Les getters/setters triviaux
- Le CSS (les yeux suffisent, Playwright si budget client)

## Backend Symfony

### Tests unitaires

```php
// tests/Unit/Service/InvoiceCalculationServiceTest.php
class InvoiceCalculationServiceTest extends TestCase
{
    public function testCalculateTotalWithTva(): void
    {
        $service = new InvoiceCalculationService();
        $total = $service->calculateTotal(1000.00, tvaRate: 8.1);

        $this->assertSame(1081.00, $total);
    }

    public function testCalculateTotalWithZeroTva(): void
    {
        $service = new InvoiceCalculationService();
        $total = $service->calculateTotal(1000.00, tvaRate: 0.0);

        $this->assertSame(1000.00, $total);
    }
}
```

### Tests fonctionnels

```php
// tests/Functional/Controller/Api/UserCreateControllerTest.php
class UserCreateControllerTest extends WebTestCase
{
    public function testCreateUserReturns201(): void
    {
        $client = static::createClient();
        $client->request('POST', '/api/v1/users', [], [], [
            'CONTENT_TYPE' => 'application/json',
            'HTTP_AUTHORIZATION' => 'Bearer ' . $this->getAdminToken(),
        ], json_encode([
            'email' => 'nouveau@bb-digital.ch',
            'firstName' => 'Jean',
            'lastName' => 'Dupont',
        ]));

        $this->assertResponseStatusCodeSame(201);
        $data = json_decode($client->getResponse()->getContent(), true);
        $this->assertSame('nouveau@bb-digital.ch', $data['data']['attributes']['email']);
    }
}
```

### Couverture cible

| Type de projet | Couverture minimum |
|---|---|
| MVP / POC | 40% |
| V1 production | 60% |
| Projet mature | 80% |
| Module critique (paiement, auth) | 90% |

## Frontend Nuxt

### Tests unitaires (Vitest)

```typescript
// tests/unit/composables/useInvoice.test.ts
import { describe, it, expect } from 'vitest'
import { calculateTotal } from '~/utils/invoice'

describe('calculateTotal', () => {
  it('calculates total with Swiss TVA', () => {
    expect(calculateTotal(1000, 8.1)).toBe(1081)
  })

  it('handles zero amount', () => {
    expect(calculateTotal(0, 8.1)).toBe(0)
  })
})
```

### Tests de composants (Vitest + Vue Test Utils)

Uniquement pour les composants avec de la logique :
- Composants de formulaire avec validation
- Composants avec état complexe
- Composables avec effets de bord

Pas de tests pour :
- Composants purement visuels (`BbFooter`, `BbHeader`)
- Pages qui ne font que composer des composants

### Tests E2E (Playwright)

Réservés aux parcours critiques, coûteux à maintenir :

```typescript
// e2e/login.spec.ts
test('user can login and see dashboard', async ({ page }) => {
  await page.goto('/login')
  await page.fill('[data-test="email"]', 'test@bb-digital.ch')
  await page.fill('[data-test="password"]', 'TestPassword123!')
  await page.click('[data-test="submit"]')
  await expect(page).toHaveURL('/dashboard')
  await expect(page.locator('h1')).toContainText('Tableau de bord')
})
```

Convention : `data-test="..."` pour les sélecteurs E2E. Jamais de sélecteur CSS fragile.

## Données de test

- **Fixtures Doctrine** pour le backend : jeu de données réaliste, pas de "test test test"
- **Factories Vitest** pour le front : objets typés qui ressemblent aux réponses API réelles
- **Jamais de données client réelles** dans les tests ou fixtures — données fictives uniquement

## CI — Pipeline GitLab

```yaml
# .gitlab-ci.yml (extrait)
test:unit:
  stage: test
  script:
    - composer install
    - php bin/phpunit --testsuite=unit

test:functional:
  stage: test
  services:
    - postgres:16-alpine
  script:
    - composer install
    - php bin/console doctrine:migrations:migrate --no-interaction --env=test
    - php bin/phpunit --testsuite=functional

test:front:
  stage: test
  script:
    - pnpm install
    - pnpm test:unit
```

Les tests tournent à chaque push. Une MR ne peut pas être mergée si le pipeline échoue.
