# BB® — Configuration Docker pour le développement local

> Chaque projet BB® avec un backend Symfony utilise Docker pour les services locaux.
> On ne dockerise **pas** l'application PHP elle-même en dev — uniquement les services annexes.

## Pourquoi Docker en dev mais pas en prod

- En dev : Docker simplifie le setup PostgreSQL + Redis + Mailpit sans polluer la machine
- En prod : on tourne sur du bare metal OVH avec PHP-FPM natif — Docker ajouterait une couche de complexité inutile pour notre scale

## `docker-compose.dev.yml` standard

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: bb_${PROJECT_NAME}
      POSTGRES_USER: bb_dev
      POSTGRES_PASSWORD: bb_dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  mailpit:
    image: axllent/mailpit:latest
    ports:
      - "1025:1025"   # SMTP
      - "8025:8025"   # Interface web
    environment:
      MP_SMTP_AUTH_ACCEPT_ANY: 1

volumes:
  postgres_data:
```

## Utilisation

```bash
# Démarrer les services
docker compose -f docker-compose.dev.yml up -d

# Vérifier le statut
docker compose -f docker-compose.dev.yml ps

# Arrêter
docker compose -f docker-compose.dev.yml down

# Purger les données (reset complet)
docker compose -f docker-compose.dev.yml down -v
```

## Configuration Symfony associée

```env
# .env.local
DATABASE_URL="postgresql://bb_dev:bb_dev_password@127.0.0.1:5432/bb_${PROJECT_NAME}?serverVersion=16"
REDIS_URL="redis://127.0.0.1:6379"
MAILER_DSN="smtp://127.0.0.1:1025"
```

## Mailpit

Mailpit intercepte tous les emails envoyés par l'application en dev. Interface web accessible sur `http://localhost:8025`. Utile pour tester :
- Les emails de confirmation d'inscription
- Les notifications de workflow
- Les exports PDF envoyés par email

## Gotenberg (projets avec génération PDF)

Pour les projets qui génèrent des PDF (factures, relevés), ajouter Gotenberg :

```yaml
  gotenberg:
    image: gotenberg/gotenberg:8
    ports:
      - "3000:3000"
    command:
      - "gotenberg"
      - "--chromium-disable-javascript=true"
      - "--api-timeout=30s"
```

Utilisé actuellement sur `bb-raiffeisen-partners` pour les relevés partenaires.

## Règles BB®

1. **Ne jamais committer de `docker-compose.yml` sans le suffixe `.dev.yml`** — ça évite la confusion avec un éventuel Docker de production
2. **Pas de volumes bind-mount pour le code** — l'application tourne nativement, seuls les services sont dans Docker
3. **Ports standards** : PostgreSQL 5432, Redis 6379, Mailpit 8025. Ne pas changer sauf conflit.
4. **Mot de passe dev** : `bb_dev_password` partout en local. Ce n'est pas un secret, c'est un setup local.
