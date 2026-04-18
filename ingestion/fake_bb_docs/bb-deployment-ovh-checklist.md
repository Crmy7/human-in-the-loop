# BB® — Checklist de déploiement OVH

> Procédure standard pour les mises en production sur l'infrastructure OVH BB®.
> Infra : serveurs dédiés OVH Bare Metal, datacenter Gravelines (GRA) et Zurich (ZRH).

## Pré-requis accès

- Accès SSH au serveur cible (clé SSH dans le vault 1Password, jamais de mot de passe)
- Accès au panel OVH via le compte `infra@bb-digital.ch`
- Accès GitLab CI/CD pour vérifier le statut du pipeline

## Environnements

| Env | Serveur | Usage |
|---|---|---|
| `dev` | Local | Développement |
| `staging` | `staging.bb-digital.ch` (GRA) | Validation client + QA interne |
| `production` | `<client>.bb-digital.ch` (ZRH) | Production |

Règle BB® : **staging freeze 48h avant chaque MEP**. Aucun merge sur `staging` dans les 48 heures précédant un déploiement en production. Ça permet de valider un état stable.

## Procédure de déploiement — Frontend Nuxt

### 1. Vérifications pré-déploiement

```bash
# Sur ta machine locale
pnpm lint          # Zéro erreur
pnpm typecheck     # Zéro erreur
pnpm build         # Build réussi
pnpm preview       # Vérification visuelle rapide
```

### 2. Merge et tag

```bash
git checkout main
git merge staging --no-ff
git tag -a v<X.Y.Z> -m "Release <X.Y.Z> — <description courte>"
git push origin main --tags
```

Convention de versioning : SemVer strict. Le numéro de version est aussi dans `package.json`.

### 3. Déploiement sur le serveur

```bash
ssh deploy@<serveur>
cd /var/www/<projet>
git pull origin main
pnpm install --frozen-lockfile
pnpm build
pm2 restart <projet>
```

### 4. Vérifications post-déploiement

- [ ] Le site répond en HTTPS
- [ ] Les pages clés se chargent (home, contact, mentions légales)
- [ ] Le tracking Matomo remonte des hits (vérifier dans Temps réel)
- [ ] Sentry ne lève pas d'erreurs nouvelles dans les 15 minutes
- [ ] Les images et assets sont servis correctement
- [ ] Le cache Nginx est purgé si nécessaire (`sudo nginx -s reload`)

## Procédure de déploiement — Backend Symfony

### 1. Vérifications pré-déploiement

```bash
make test                    # Tous les tests passent
composer validate --strict   # composer.json valide
php bin/console lint:yaml config/  # Config YAML valide
```

### 2. Déploiement

```bash
ssh deploy@<serveur>
cd /var/www/<projet>-api
git pull origin main
composer install --no-dev --optimize-autoloader
php bin/console doctrine:migrations:migrate --no-interaction
php bin/console cache:clear --env=prod
sudo systemctl restart php8.3-fpm
```

### 3. Vérifications post-déploiement

- [ ] L'endpoint `/api/v1/health` retourne `200 OK`
- [ ] Les migrations se sont bien exécutées
- [ ] Les workers Messenger tournent (`sudo supervisorctl status`)
- [ ] Les logs ne montrent pas d'erreurs critiques (`tail -f var/log/prod.log`)

## Rollback

En cas de problème post-MEP :

```bash
# Identifier le commit précédent
git log --oneline -5

# Revenir au tag précédent
git checkout v<X.Y.Z-1>
pnpm install --frozen-lockfile && pnpm build && pm2 restart <projet>  # Front
# ou
composer install --no-dev && php bin/console cache:clear --env=prod && sudo systemctl restart php8.3-fpm  # Back
```

**Règle BB® : si le rollback n'est pas résolu en 30 minutes, on revient à la version précédente et on post-mortem le lendemain.**

## Configuration Nginx type

```nginx
server {
    listen 443 ssl http2;
    server_name <client>.bb-digital.ch;

    ssl_certificate /etc/letsencrypt/live/<client>.bb-digital.ch/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/<client>.bb-digital.ch/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:3000;  # Nuxt SSR
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;  # Symfony
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Certificats SSL

Renouvellement automatique via Certbot (Let's Encrypt). Cron déjà en place sur les serveurs. Vérifier l'expiration si un client signale un warning SSL :

```bash
sudo certbot certificates
```
