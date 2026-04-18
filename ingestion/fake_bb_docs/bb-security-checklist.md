# BB® — Checklist sécurité

> Vérifications obligatoires avant chaque mise en production.
> Basé sur OWASP Top 10 2021 + exigences spécifiques clients institutionnels.

## Authentification & Autorisation

- [ ] JWT avec expiration courte (15 min access, 7 jours refresh)
- [ ] Refresh token en httpOnly cookie, Secure, SameSite=Strict
- [ ] Mots de passe hashés avec bcrypt (coût 12) ou Argon2id
- [ ] Longueur minimum mot de passe : 12 caractères
- [ ] Rate limiting sur les endpoints d'auth (5 req/min/IP)
- [ ] Pas de message d'erreur révélant l'existence d'un compte ("Email ou mot de passe incorrect" — jamais "Email non trouvé")
- [ ] Vérification des permissions à chaque requête (pas seulement à l'auth)

## Injection

- [ ] Requêtes SQL paramétrées uniquement (Doctrine ORM, pas de raw SQL sans binding)
- [ ] Pas d'interpolation de variables dans les requêtes
- [ ] Validation et sanitisation de tous les inputs utilisateur
- [ ] Headers `Content-Type` vérifiés côté serveur

## XSS (Cross-Site Scripting)

- [ ] Échappement automatique des sorties (Twig `{{ }}` échappe par défaut, Vue aussi)
- [ ] Pas de `v-html` sans sanitisation explicite
- [ ] Content Security Policy (CSP) en place :

```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'nonce-{random}' analytics.bb-digital.ch; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' api.bb-digital.ch analytics.bb-digital.ch; font-src 'self';";
```

## CSRF

- [ ] Token CSRF sur tous les formulaires (automatique avec Symfony)
- [ ] SameSite cookie attribute en place
- [ ] Vérification du header `Origin` pour les requêtes cross-origin

## Headers de sécurité

```nginx
# À ajouter dans la config Nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

## Données sensibles

- [ ] Pas de secrets en dur dans le code (clés API, mots de passe, tokens)
- [ ] Pas de données sensibles dans les logs (`#[SensitiveParameter]` en PHP 8.2)
- [ ] Pas de stack traces exposées en production (`APP_DEBUG=false`)
- [ ] `.env` dans `.gitignore`
- [ ] Secrets stockés dans 1Password vault `Engineering`
- [ ] Variables d'environnement pour toute config sensible

## Dépendances

- [ ] `composer audit` sans vulnérabilité critique
- [ ] `pnpm audit` sans vulnérabilité critique
- [ ] Mise à jour des dépendances au moins mensuelle (ticket récurrent)
- [ ] Pas de dépendance abandonnée (vérifier la date du dernier commit)

## Infrastructure

- [ ] HTTPS partout (pas de mixed content)
- [ ] Certificats SSL valides et renouvelés automatiquement (Certbot)
- [ ] SSH par clé uniquement (pas de mot de passe)
- [ ] Pare-feu : seuls les ports 80, 443 et 22 ouverts
- [ ] Backups quotidiens de la base de données
- [ ] Backups testés (restauration vérifiée au moins une fois par trimestre)

## Conformité RGPD / nLPD

- [ ] Bandeau de consentement cookies en place
- [ ] Pas de tracking avant consentement
- [ ] Politique de confidentialité à jour
- [ ] Droit de suppression implémenté (endpoint ou procédure manuelle documentée)
- [ ] Données hébergées en Suisse pour les clients qui l'exigent
- [ ] Pas de transfert de données vers les USA sans base légale

## Audit annuel

Les clients institutionnels (Raiffeisen, État de Genève) exigent un audit de sécurité annuel. Procédure :
1. Le client mandate un auditeur tiers
2. BB® fournit l'accès au code source et à un environnement de staging
3. L'auditeur produit un rapport avec les vulnérabilités classées par sévérité
4. BB® corrige les critiques sous 48h, les majeures sous 2 semaines
5. Re-test par l'auditeur après corrections
