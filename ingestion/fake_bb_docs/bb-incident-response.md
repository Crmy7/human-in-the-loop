# BB® — Procédure de gestion des incidents

> Quoi faire quand ça casse en production.
> Objectif : rétablir le service d'abord, comprendre ensuite.

## Niveaux de sévérité

| Niveau | Définition | Temps de réponse | Exemple |
|---|---|---|---|
| P1 — Critique | Service indisponible pour tous les utilisateurs | 15 minutes | Site down, API 500 généralisé |
| P2 — Majeur | Fonctionnalité critique dégradée | 1 heure | Paiements échouent, login cassé |
| P3 — Mineur | Bug visible mais contournable | 4 heures | Affichage cassé sur mobile, traduction manquante |
| P4 — Cosmétique | Bug mineur sans impact fonctionnel | Prochain sprint | Alignement CSS, typo |

## Qui est de garde

Rotation hebdomadaire, planning dans le calendrier Google partagé `BB® On-Call`.

Le dev de garde :
- A Slack sur son téléphone avec notifications activées pour `#dev-urgences`
- A accès SSH aux serveurs de production
- Connaît les procédures de rollback
- Peut joindre le tech lead en cas de P1

## Procédure P1 / P2

### 1. Détecter (0-5 min)
- Alerte Sentry (spike d'erreurs)
- Alerte monitoring OVH (serveur down)
- Signalement client (via Slack `#bb-<client>` ou email)

### 2. Confirmer (5-10 min)
- Vérifier que le problème est réel (pas un faux positif)
- Identifier le périmètre : quel service, quel client, quelle fonctionnalité
- Poster dans `#dev-urgences` : "Incident P1/P2 sur [projet] — [description courte] — je prends"

### 3. Rétablir (10-30 min)
- **Rollback** si le problème est lié au dernier déploiement (voir `bb-deployment-ovh-checklist.md`)
- **Restart** si le serveur est bloqué (`sudo systemctl restart php8.3-fpm`, `pm2 restart all`)
- **Hotfix** si le fix est évident et rapide (< 15 min de code)
- **Mitigation** si le fix prend du temps (page de maintenance, redirection, désactivation de feature)

### 4. Communiquer
- Mettre à jour `#dev-urgences` toutes les 15 minutes pendant l'incident
- Prévenir le chef de projet pour qu'il informe le client
- Quand c'est résolu : message de clôture avec durée de l'incident et impact

### 5. Post-mortem (dans les 48h)

Document à remplir dans le Drive BB® sous `Incidents / <date>-<projet>.md` :

```markdown
## Incident — [Date] — [Projet]

**Sévérité** : P1 / P2
**Durée** : HH:MM — HH:MM (X minutes)
**Impact** : [nombre d'utilisateurs affectés, fonctionnalités impactées]

### Timeline
- HH:MM — Détection : [comment]
- HH:MM — Confirmation : [quoi]
- HH:MM — Action : [quoi]
- HH:MM — Résolution : [quoi]

### Cause racine
[Description technique]

### Ce qui a bien marché
- ...

### Ce qui peut être amélioré
- ...

### Actions correctives
- [ ] [Action] — Responsable — Deadline
```

## Règle BB®

**Pas de blame.** Le post-mortem analyse le système, pas les personnes. Si quelqu'un a fait une erreur, la question est "comment le système a-t-il permis cette erreur ?" et non "qui a fait cette erreur ?".

Les post-mortems sont partagés avec toute l'équipe. On apprend ensemble.
