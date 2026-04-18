# BB® — Design Tokens SCSS

> Variables SCSS partagées entre tous les projets front BB® Switzerland.
> Source de vérité : fichier `_variables.scss` dans le template `bb-nuxt-starter`.

## Couleurs

```scss
// Couleurs de marque BB®
$bb-primary: #1A1A2E;        // Bleu nuit — couleur principale
$bb-primary-light: #2D2D44;
$bb-secondary: #E94560;      // Rouge accent — CTA, liens actifs
$bb-secondary-light: #FF6B81;

// Neutres
$bb-white: #FFFFFF;
$bb-gray-50: #F8F9FA;
$bb-gray-100: #E9ECEF;
$bb-gray-200: #DEE2E6;
$bb-gray-300: #CED4DA;
$bb-gray-500: #6C757D;
$bb-gray-700: #495057;
$bb-gray-900: #212529;
$bb-black: #000000;

// Sémantiques
$bb-success: #28A745;
$bb-warning: #FFC107;
$bb-danger: #DC3545;
$bb-info: #17A2B8;

// Fond de page
$bb-bg-light: $bb-gray-50;
$bb-bg-dark: $bb-primary;
```

## Typographie

```scss
// Familles
$bb-font-primary: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
$bb-font-mono: 'JetBrains Mono', 'Fira Code', monospace;

// Tailles (base 16px)
$bb-text-xs: 0.75rem;    // 12px
$bb-text-sm: 0.875rem;   // 14px
$bb-text-base: 1rem;     // 16px
$bb-text-lg: 1.125rem;   // 18px
$bb-text-xl: 1.25rem;    // 20px
$bb-text-2xl: 1.5rem;    // 24px
$bb-text-3xl: 2rem;      // 32px
$bb-text-4xl: 2.5rem;    // 40px

// Poids
$bb-font-light: 300;
$bb-font-regular: 400;
$bb-font-medium: 500;
$bb-font-semibold: 600;
$bb-font-bold: 700;

// Line height
$bb-leading-tight: 1.25;
$bb-leading-normal: 1.5;
$bb-leading-relaxed: 1.75;
```

## Espacement

```scss
// Échelle de spacing (base 4px)
$bb-space-1: 0.25rem;    // 4px
$bb-space-2: 0.5rem;     // 8px
$bb-space-3: 0.75rem;    // 12px
$bb-space-4: 1rem;       // 16px
$bb-space-5: 1.25rem;    // 20px
$bb-space-6: 1.5rem;     // 24px
$bb-space-8: 2rem;       // 32px
$bb-space-10: 2.5rem;    // 40px
$bb-space-12: 3rem;      // 48px
$bb-space-16: 4rem;      // 64px
$bb-space-20: 5rem;      // 80px
```

## Breakpoints

```scss
$bb-breakpoint-sm: 640px;
$bb-breakpoint-md: 768px;
$bb-breakpoint-lg: 1024px;
$bb-breakpoint-xl: 1280px;
$bb-breakpoint-2xl: 1536px;

// Mixins responsive
@mixin bb-media-up($breakpoint) {
  @media (min-width: $breakpoint) {
    @content;
  }
}

@mixin bb-media-down($breakpoint) {
  @media (max-width: $breakpoint - 1px) {
    @content;
  }
}
```

## Ombres

```scss
$bb-shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
$bb-shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
$bb-shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
$bb-shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15);
```

## Bordures

```scss
$bb-radius-sm: 4px;
$bb-radius-md: 8px;
$bb-radius-lg: 12px;
$bb-radius-xl: 16px;
$bb-radius-full: 9999px;

$bb-border-color: $bb-gray-200;
$bb-border-width: 1px;
```

## Transitions

```scss
$bb-transition-fast: 150ms ease;
$bb-transition-normal: 250ms ease;
$bb-transition-slow: 350ms ease;
```

## Utilisation

```scss
// Exemple dans un composant
.bb-card {
  background: $bb-white;
  border: $bb-border-width solid $bb-border-color;
  border-radius: $bb-radius-md;
  padding: $bb-space-6;
  box-shadow: $bb-shadow-sm;
  transition: box-shadow $bb-transition-normal;

  &:hover {
    box-shadow: $bb-shadow-md;
  }

  &__title {
    font-family: $bb-font-primary;
    font-size: $bb-text-xl;
    font-weight: $bb-font-semibold;
    color: $bb-primary;
    margin-bottom: $bb-space-3;
  }
}
```

## Règle BB®

Chaque projet front utilise ces tokens. Pas de valeurs magiques en dur dans les composants. Si une couleur ou un spacing n'existe pas dans les tokens, on l'ajoute ici avant de l'utiliser — jamais l'inverse.
