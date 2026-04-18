# BB® Symfony Project Conventions

> Standards applicables à tout projet Symfony 7.x développé chez BB® Switzerland.
> Maintenu par l'équipe back — dernière révision : février 2026.

## Création d'un nouveau projet

```bash
composer create-project symfony/skeleton bb-<client>-<projet>-api
cd bb-<client>-<projet>-api
composer require webapp
```

Repo GitLab : `bb-<client>-<projet>-api` (suffixe `-api` pour les backends, `-front` pour les fronts).

## Structure de projet

```
bb-<projet>-api/
├── config/
│   ├── packages/
│   │   ├── doctrine.yaml
│   │   ├── security.yaml
│   │   └── messenger.yaml
│   └── routes.yaml
├── migrations/
├── src/
│   ├── Controller/
│   │   └── Api/              # Controllers API REST
│   ├── Entity/
│   ├── Repository/
│   ├── Service/              # Logique métier — pas dans les controllers
│   ├── EventSubscriber/
│   ├── Command/              # Commandes CLI Symfony
│   └── Dto/                  # Data Transfer Objects pour l'API
├── templates/                # Vide pour les API pures, Twig pour les apps monolithes
├── tests/
│   ├── Unit/
│   └── Functional/
├── docker-compose.dev.yml    # PostgreSQL + Redis pour le dev local
├── .env
└── Makefile                  # Raccourcis standards BB®
```

## Conventions de code

### Nommage

- Controllers : `<Entité><Action>Controller` (ex. `UserCreateController`, `InvoiceListController`)
- Services : `<Domaine>Service` (ex. `InvoiceCalculationService`)
- DTOs : `<Entité><Action>Dto` (ex. `UserCreateDto`)
- Events : `<Entité><Action>Event` (ex. `OrderConfirmedEvent`)

### Routing

Convention REST stricte :

| Action | Méthode | Route | Controller |
|---|---|---|---|
| Lister | GET | `/api/v1/users` | `UserListController` |
| Détail | GET | `/api/v1/users/{id}` | `UserShowController` |
| Créer | POST | `/api/v1/users` | `UserCreateController` |
| Modifier | PUT | `/api/v1/users/{id}` | `UserUpdateController` |
| Supprimer | DELETE | `/api/v1/users/{id}` | `UserDeleteController` |

Préfixe `/api/v1/` obligatoire. On versione l'API dès le jour 1.

### Validation

- Utiliser les attributs PHP 8 (`#[Assert\NotBlank]`, etc.) sur les DTOs
- Valider dans le controller via `$validator->validate($dto)`
- Retourner un JSON normalisé en cas d'erreur :

```json
{
  "status": 422,
  "errors": [
    {"field": "email", "message": "Cette valeur n'est pas une adresse email valide."}
  ]
}
```

## Base de données

- **PostgreSQL 16** en production (jamais MySQL, c'est une règle BB®)
- Doctrine ORM avec migrations versionnées
- Convention de nommage SQL : `snake_case`, préfixe `bb_` sur les tables (`bb_user`, `bb_invoice`)
- UUID v7 comme clé primaire sur toutes les entités (meilleur pour l'indexation que UUID v4)

## Tests

- Tests fonctionnels obligatoires sur tous les endpoints API
- PHPUnit 11+
- Fixtures via `doctrine/doctrine-fixtures-bundle`
- Couverture minimale attendue : 60% pour un MVP, 80% pour une V1

```bash
make test             # Lance tous les tests
make test-unit        # Tests unitaires seuls
make test-functional  # Tests fonctionnels seuls
make coverage         # Rapport de couverture HTML
```

## Makefile standard

Chaque projet Symfony BB® inclut ce Makefile :

```makefile
.PHONY: install dev test migrate fixtures

install:
	composer install
	php bin/console doctrine:database:create --if-not-exists
	php bin/console doctrine:migrations:migrate --no-interaction

dev:
	symfony server:start --port=8000

test:
	php bin/phpunit

migrate:
	php bin/console doctrine:migrations:migrate --no-interaction

fixtures:
	php bin/console doctrine:fixtures:load --no-interaction
```

## Sécurité

- Authentification via JWT (`lexik/jwt-authentication-bundle`)
- Refresh tokens avec `gesdinet/jwt-refresh-token-bundle`
- Rate limiting sur les endpoints d'auth : 5 requêtes / minute / IP
- CORS configuré par environnement via `nelmio/cors-bundle`
- Pas de données sensibles dans les logs — utiliser le `#[SensitiveParameter]` de PHP 8.2

## Déploiement

Voir `bb-deployment-ovh-checklist.md`. En résumé :
1. `composer install --no-dev --optimize-autoloader`
2. `php bin/console doctrine:migrations:migrate --no-interaction`
3. `php bin/console cache:clear --env=prod`
4. Redémarrer PHP-FPM
