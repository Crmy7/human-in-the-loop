# BB® — Standards d'accessibilité

> WCAG 2.1 niveau AA minimum sur toutes les interfaces client-facing.
> Certains clients (État de Genève, Raiffeisen) exigent contractuellement la conformité.

## Pourquoi c'est non-négociable

1. **Obligation légale** : la nLPD et le droit suisse sur l'égalité des personnes handicapées s'appliquent aux services numériques des entreprises suisses
2. **Exigence contractuelle** : nos clients institutionnels l'incluent dans leurs appels d'offres
3. **Bon sens** : 15% de la population a un handicap. Exclure ces utilisateurs est un choix de design qu'on refuse de faire.

## Checklist par composant

### Navigation

- [ ] Navigation au clavier possible sur tout le site (Tab, Shift+Tab, Enter, Escape)
- [ ] Focus visible sur tous les éléments interactifs (pas de `outline: none` sans alternative)
- [ ] Skip link en haut de page (`Aller au contenu principal`)
- [ ] Ordre de tabulation logique (suit l'ordre visuel)

### Images

- [ ] Attribut `alt` sur toutes les `<img>` — descriptif si informatif, vide (`alt=""`) si décoratif
- [ ] Pas de texte important dans les images (non lu par les lecteurs d'écran)
- [ ] Contraste suffisant entre le texte superposé et l'image de fond

### Formulaires

- [ ] Chaque champ a un `<label>` associé (via `for`/`id`, pas de placeholder seul)
- [ ] Messages d'erreur liés au champ via `aria-describedby`
- [ ] Champs obligatoires indiqués visuellement ET via `aria-required="true"`
- [ ] Autocomplétion activée (`autocomplete="email"`, `autocomplete="given-name"`, etc.)

### Couleurs et contrastes

- [ ] Ratio de contraste texte/fond ≥ 4.5:1 pour le texte normal
- [ ] Ratio de contraste ≥ 3:1 pour le texte large (≥ 18px bold ou ≥ 24px)
- [ ] L'information n'est jamais transmise uniquement par la couleur (ajouter icône ou texte)

### Contenu dynamique

- [ ] Les messages d'alerte utilisent `role="alert"` ou `aria-live="polite"`
- [ ] Les modales piègent le focus (`focus trap`) et se ferment avec Escape
- [ ] Les accordéons/tabs utilisent les patterns ARIA correspondants
- [ ] Les chargements asynchrones sont annoncés (`aria-busy`, `aria-live`)

## Outils de vérification

### Automatiques

- **axe-core** : intégré dans le pipeline CI via `@axe-core/playwright` ou `axe-linter`
- **Lighthouse** : score Accessibility ≥ 90 (voir `bb-performance-budget.md`)
- **eslint-plugin-vuejs-accessibility** : dans la config ESLint du template Nuxt

### Manuels (avant chaque MEP)

1. Naviguer sur le site uniquement au clavier — tout est-il accessible ?
2. Activer VoiceOver (macOS) ou NVDA (Windows) — le contenu est-il compréhensible ?
3. Zoom navigateur à 200% — la mise en page reste-t-elle utilisable ?
4. Désactiver les images — le contenu reste-t-il compréhensible ?

## Composants BB® accessibles

Le template `bb-nuxt-starter` inclut des composants pré-accessibilisés :

| Composant | Pattern ARIA |
|---|---|
| `BbModal` | `dialog` avec focus trap |
| `BbTabs` | `tablist` / `tab` / `tabpanel` |
| `BbAccordion` | `button` + `aria-expanded` |
| `BbDropdown` | `menu` / `menuitem` |
| `BbToast` | `role="alert"` + `aria-live="assertive"` |

**Utiliser ces composants plutôt que d'en recréer.** Si un composant manque, l'ajouter au design system, pas au projet client.

## Ressources

- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)
- [WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [axe-core Rules](https://dequeuniversity.com/rules/axe/)
