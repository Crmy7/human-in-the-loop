# BB® — Guidelines de conception API REST

> Standards pour toutes les APIs développées par BB® Switzerland.
> Basé sur les conventions JSON:API simplifiées et l'expérience terrain de l'équipe.

## Principes généraux

1. **REST stricte** : les verbes HTTP ont un sens, on ne fait pas de POST pour tout.
2. **Versionning dès le jour 1** : préfixe `/api/v1/`. On ne casse jamais un contrat sans nouvelle version.
3. **JSON uniquement** : `Content-Type: application/json` partout. Pas de XML, pas de form-urlencoded sur les API.
4. **Stateless** : chaque requête porte son authentification (JWT). Pas de sessions serveur.

## Structure des réponses

### Succès (200, 201)

```json
{
  "data": {
    "id": "01912345-abcd-7890-ef01-234567890abc",
    "type": "user",
    "attributes": {
      "email": "thomas@raiffeisen.ch",
      "firstName": "Thomas",
      "lastName": "Keller",
      "createdAt": "2026-01-15T10:30:00Z"
    }
  }
}
```

### Collection (200)

```json
{
  "data": [
    { "id": "...", "type": "user", "attributes": { ... } }
  ],
  "meta": {
    "total": 142,
    "page": 1,
    "perPage": 20,
    "lastPage": 8
  }
}
```

### Erreur (4xx, 5xx)

```json
{
  "status": 422,
  "message": "Validation failed",
  "errors": [
    { "field": "email", "message": "Cette adresse email est déjà utilisée." },
    { "field": "password", "message": "Le mot de passe doit contenir au moins 12 caractères." }
  ]
}
```

## Pagination

- Paramètres : `?page=1&per_page=20`
- Défaut : `per_page=20`, max `per_page=100`
- Toujours inclure le bloc `meta` avec `total`, `page`, `perPage`, `lastPage`

## Filtres et tri

- Filtres : `?filter[status]=active&filter[city]=geneve`
- Tri : `?sort=-created_at` (préfixe `-` pour descendant)
- Recherche texte : `?search=raiffeisen`

## Authentification

- JWT via header `Authorization: Bearer <token>`
- Durée de vie du access token : 15 minutes
- Refresh token : 7 jours, stocké en httpOnly cookie
- Endpoints d'auth :
  - `POST /api/v1/auth/login` — retourne access + refresh token
  - `POST /api/v1/auth/refresh` — renouvelle le access token
  - `POST /api/v1/auth/logout` — invalide le refresh token

## Codes de statut HTTP

| Code | Usage |
|---|---|
| 200 | Succès (GET, PUT) |
| 201 | Ressource créée (POST) |
| 204 | Succès sans contenu (DELETE) |
| 400 | Requête malformée |
| 401 | Non authentifié |
| 403 | Authentifié mais pas autorisé |
| 404 | Ressource non trouvée |
| 422 | Erreur de validation |
| 429 | Rate limit atteint |
| 500 | Erreur serveur |

## Rate limiting

- Endpoints publics : 60 requêtes / minute / IP
- Endpoints authentifiés : 120 requêtes / minute / utilisateur
- Endpoints d'auth (login, refresh) : 5 requêtes / minute / IP
- Headers de réponse : `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## CORS

Configuré par environnement via `nelmio/cors-bundle` :

```yaml
# config/packages/nelmio_cors.yaml
nelmio_cors:
  defaults:
    origin_regex: true
    allow_origin: ['%env(CORS_ALLOW_ORIGIN)%']
    allow_methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    allow_headers: ['Content-Type', 'Authorization']
    max_age: 3600
```

## Documentation API

Chaque API BB® est documentée via OpenAPI 3.1 (Swagger). Le fichier `openapi.yaml` est :
- Généré automatiquement par API Platform (Symfony)
- Accessible en staging sur `/api/docs`
- Pas accessible en production (désactivé via config)

## Checklist avant mise en production d'un nouvel endpoint

- [ ] Validation des inputs (types, longueurs, formats)
- [ ] Authentification et autorisation vérifiées
- [ ] Rate limiting en place
- [ ] Test fonctionnel écrit
- [ ] Documentation OpenAPI à jour
- [ ] Pas de données sensibles dans la réponse (pas de password hash, pas de tokens internes)
