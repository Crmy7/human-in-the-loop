# BB® — Guidelines d'internationalisation (i18n)

> En Suisse, le multilingue n'est pas un nice-to-have. C'est un prérequis.
> Toute application BB® destinée au public supporte au minimum français et allemand.

## Langues par défaut

| Contexte | Langues | Langue par défaut |
|---|---|---|
| Client Suisse romande | fr, de | fr |
| Client Suisse alémanique | de, fr | de |
| Client national (ex. Raiffeisen) | fr, de, it | fr |
| Projet interne BB® | fr | fr |

L'anglais est ajouté uniquement sur demande explicite du client.

## Nuxt 3 — Configuration `@nuxtjs/i18n`

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  modules: ['@nuxtjs/i18n'],
  i18n: {
    locales: [
      { code: 'fr', iso: 'fr-CH', file: 'fr.json', name: 'Français' },
      { code: 'de', iso: 'de-CH', file: 'de.json', name: 'Deutsch' },
    ],
    defaultLocale: 'fr',
    strategy: 'prefix_except_default',
    lazy: true,
    langDir: 'locales/',
    detectBrowserLanguage: {
      useCookie: true,
      cookieKey: 'bb_i18n',
      redirectOn: 'root',
    },
  },
})
```

### Structure des fichiers de traduction

```
locales/
├── fr.json
└── de.json
```

Format JSON plat avec namespacing par point :

```json
{
  "common.save": "Enregistrer",
  "common.cancel": "Annuler",
  "common.delete": "Supprimer",
  "common.confirm": "Confirmer",
  "auth.login.title": "Connexion",
  "auth.login.email": "Adresse email",
  "auth.login.password": "Mot de passe",
  "auth.login.submit": "Se connecter",
  "auth.login.forgot": "Mot de passe oublié ?",
  "dashboard.title": "Tableau de bord",
  "dashboard.welcome": "Bienvenue, {name}"
}
```

### Utilisation dans les templates

```vue
<template>
  <h1>{{ $t('dashboard.title') }}</h1>
  <p>{{ $t('dashboard.welcome', { name: user.firstName }) }}</p>
  <button>{{ $t('common.save') }}</button>
</template>
```

**Règle absolue : jamais de texte en dur dans un template.** Même pour un "OK" ou un "×". Tout passe par `$t()`.

## Symfony — Traductions backend

Les messages d'erreur API et les emails sont traduits côté serveur :

```yaml
# translations/messages.fr.yaml
validation:
  email.unique: "Cette adresse email est déjà utilisée."
  password.too_short: "Le mot de passe doit contenir au moins {min} caractères."

email:
  welcome.subject: "Bienvenue chez {company}"
  welcome.body: "Bonjour {name}, votre compte a été créé."
```

La locale est déterminée par le header `Accept-Language` de la requête.

## Bonnes pratiques

1. **Clés en anglais, valeurs traduites.** Les clés sont un identifiant technique, pas du texte.
2. **Pas de concaténation de traductions.** `$t('hello') + ' ' + $t('world')` est interdit — les ordres de mots changent entre les langues.
3. **Utiliser les placeholders** pour les variables : `{name}`, `{count}`, pas de template literals.
4. **Pluralisation native** : utiliser les règles ICU quand le nombre change le texte.
5. **Dates et nombres** : toujours formater avec `Intl.DateTimeFormat` et `Intl.NumberFormat`, pas manuellement.

```typescript
// Bon
new Intl.NumberFormat('fr-CH', { style: 'currency', currency: 'CHF' }).format(1234.50)
// → "CHF 1'234.50"

// Mauvais
`CHF ${amount.toFixed(2)}`
```

6. **Tester les traductions** : vérifier que toutes les clés existent dans toutes les langues avant la MEP.

```bash
# Script de vérification des clés manquantes
pnpm i18n:check  # Compare fr.json et de.json, liste les clés manquantes
```

## Process de traduction

1. Le développeur ajoute les clés en français
2. Les traductions allemandes sont fournies par le client ou via DeepL Pro (compte BB®)
3. Relecture par un collaborateur germanophone avant MEP
4. Les traductions italiennes (si applicables) passent par un traducteur externe
