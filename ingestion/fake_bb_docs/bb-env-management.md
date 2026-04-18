# BB® — Gestion des variables d'environnement

> Comment on gère les secrets et la configuration par environnement chez BB®.

## Principe

**Aucun secret dans le code.** Jamais. Pas même "temporairement". Pas même "juste pour tester". Si un secret finit dans un commit, on considère qu'il est compromis et on le régénère immédiatement.

## Structure des fichiers `.env`

### Projet Nuxt

```
.env.example          # Template versionné, valeurs factices
.env.local             # Valeurs dev locales — dans .gitignore
.env.staging           # Valeurs staging — dans le vault 1Password
.env.production        # Valeurs prod — dans le vault 1Password
```

### Projet Symfony

```
.env                   # Valeurs par défaut (versionné, pas de secrets)
.env.local             # Override local — dans .gitignore
.env.test              # Override pour les tests — versionné
```

## Catégories de variables

| Catégorie | Exemple | Où les stocker |
|---|---|---|
| Secrets | `DATABASE_PASSWORD`, `API_KEY` | 1Password vault `Engineering` |
| Config technique | `DATABASE_HOST`, `REDIS_URL` | `.env` par environnement |
| Feature flags | `FEATURE_NEW_DASHBOARD=true` | `.env` par environnement |
| URLs | `API_BASE_URL`, `MATOMO_URL` | `.env` par environnement |

## Vault 1Password

Structure du vault `Engineering` :

```
Engineering/
├── Raiffeisen/
│   ├── Staging/
│   │   ├── .env.staging (fichier complet)
│   │   ├── JWT_SECRET
│   │   └── SENTRY_DSN
│   └── Production/
│       ├── .env.production (fichier complet)
│       ├── JWT_SECRET
│       └── SENTRY_DSN
├── Matomo/
│   ├── Token API
│   └── Admin password
├── OVH/
│   ├── Panel credentials
│   └── SSH keys
└── Services/
    ├── Sentry DSN (par projet)
    ├── DeepL API key
    └── Mailjet credentials
```

## Règles BB®

1. **`.env.example` toujours à jour.** Quand tu ajoutes une variable, tu l'ajoutes aussi dans le `.env.example` avec une valeur factice et un commentaire.
2. **Pas de valeur par défaut pour les secrets.** Si la variable est un secret, elle doit être définie explicitement — pas de fallback silencieux.
3. **Validation au démarrage.** L'application vérifie la présence des variables critiques au boot et crashe avec un message clair si une manque.
4. **Pas de `print()` ou `console.log()` de secrets.** Même en dev. Ça finit toujours par se retrouver dans un screenshot ou un log partagé.
5. **Rotation annuelle.** Les secrets de production sont renouvelés au moins une fois par an. Date de dernière rotation notée dans 1Password.

## En cas de fuite

Si un secret est commité par erreur :

1. **Révoquer immédiatement** le secret concerné (régénérer la clé, changer le mot de passe)
2. Supprimer le commit de l'historique Git (`git filter-branch` ou `bfg`)
3. Force-push (seul cas où c'est autorisé)
4. Informer le tech lead
5. Vérifier les logs d'accès du service concerné

Ce n'est pas une procédure théorique — c'est arrivé deux fois en 2024. Les deux fois, le secret a été régénéré dans l'heure.
