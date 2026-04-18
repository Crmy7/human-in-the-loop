# BB® — Pipeline CI/CD GitLab

> Configuration standard des pipelines GitLab CI pour les projets BB®.
> Instance GitLab : `gitlab.bb-digital.ch` (self-hosted, version 17.x)

## Architecture du pipeline

```
┌─────────┐    ┌──────┐    ┌─────────┐    ┌────────┐    ┌────────┐
│  Build  │ →  │ Lint │ →  │  Test   │ →  │ Quality│ →  │ Deploy │
└─────────┘    └──────┘    └─────────┘    └────────┘    └────────┘
```

Les stages Build, Lint, Test et Quality tournent à chaque push. Deploy est manuel et déclenché par un tag.

## `.gitlab-ci.yml` — Template Nuxt

```yaml
image: node:20-alpine

stages:
  - install
  - lint
  - test
  - quality
  - build
  - deploy

cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - node_modules/
    - .pnpm-store/

install:
  stage: install
  script:
    - corepack enable
    - pnpm install --frozen-lockfile

lint:
  stage: lint
  script:
    - pnpm lint
    - pnpm typecheck

test:unit:
  stage: test
  script:
    - pnpm test:unit --coverage
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml

quality:lighthouse:
  stage: quality
  script:
    - pnpm build
    - lhci autorun
  allow_failure: false

build:
  stage: build
  script:
    - pnpm build
  artifacts:
    paths:
      - .output/
    expire_in: 1 day

deploy:staging:
  stage: deploy
  environment: staging
  script:
    - ssh deploy@staging.bb-digital.ch "cd /var/www/$CI_PROJECT_NAME && git pull && pnpm install --frozen-lockfile && pnpm build && pm2 restart $CI_PROJECT_NAME"
  when: manual
  only:
    - staging

deploy:production:
  stage: deploy
  environment: production
  script:
    - ssh deploy@$PROD_SERVER "cd /var/www/$CI_PROJECT_NAME && git checkout $CI_COMMIT_TAG && pnpm install --frozen-lockfile && pnpm build && pm2 restart $CI_PROJECT_NAME"
  when: manual
  only:
    - tags
```

## `.gitlab-ci.yml` — Template Symfony

```yaml
image: php:8.3-cli

stages:
  - install
  - lint
  - test
  - quality

services:
  - postgres:16-alpine

variables:
  POSTGRES_DB: bb_test
  POSTGRES_USER: bb_test
  POSTGRES_PASSWORD: bb_test
  DATABASE_URL: "postgresql://bb_test:bb_test@postgres:5432/bb_test"

cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - vendor/

install:
  stage: install
  script:
    - composer install --no-interaction --prefer-dist

lint:
  stage: lint
  script:
    - vendor/bin/phpstan analyse src --level=6
    - php bin/console lint:yaml config/
    - php bin/console lint:twig templates/

test:
  stage: test
  script:
    - php bin/console doctrine:migrations:migrate --no-interaction --env=test
    - php bin/phpunit --coverage-text
  artifacts:
    reports:
      junit: var/log/junit.xml

quality:security:
  stage: quality
  script:
    - composer audit
  allow_failure: false
```

## Variables CI/CD

Configurées dans GitLab > Settings > CI/CD > Variables :

| Variable | Scope | Description |
|---|---|---|
| `PROD_SERVER` | Production | Hostname du serveur de prod |
| `SSH_PRIVATE_KEY` | All | Clé SSH pour le déploiement |
| `SENTRY_DSN` | Staging + Prod | DSN Sentry par environnement |
| `SONAR_TOKEN` | All | Token SonarQube |

**Toutes les variables sensibles sont marquées "Protected" et "Masked".**

## Runners

- 2 runners partagés sur le serveur GitLab BB®
- Executor : Docker
- Timeout global : 30 minutes
- Nettoyage automatique des images Docker toutes les semaines

## Règles BB®

1. **Le pipeline doit passer pour merger.** Pas de merge avec un pipeline rouge, même pour un "petit fix".
2. **Deploy toujours manuel.** Pas de déploiement automatique en staging ou en prod.
3. **Pas de `allow_failure: true`** sur les stages critiques (lint, test, security audit).
4. **Artifacts de build** : expiration 1 jour pour les builds, 30 jours pour les rapports de couverture.
5. **Monitoring du temps de pipeline** : si un pipeline dépasse 15 minutes, optimiser (cache, parallélisation).
