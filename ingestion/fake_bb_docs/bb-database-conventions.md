# BB® — Conventions de base de données

> Standards PostgreSQL pour tous les projets BB® Switzerland.
> SGBD imposé : PostgreSQL 16+. Pas de MySQL, pas de MariaDB.

## Pourquoi PostgreSQL

1. **Types avancés** : JSONB, UUID natif, arrays — on les utilise régulièrement
2. **Performance** : meilleur query planner que MySQL pour nos cas d'usage (jointures complexes, full-text search)
3. **Extensions** : `pg_trgm` pour la recherche floue, `uuid-ossp` pour les UUID
4. **Standard BB®** depuis 2022 : uniformiser les compétences de l'équipe

## Conventions de nommage

| Élément | Convention | Exemple |
|---|---|---|
| Table | `snake_case`, préfixe `bb_` | `bb_user`, `bb_invoice` |
| Colonne | `snake_case` | `first_name`, `created_at` |
| Clé primaire | `id` (UUID v7) | `id` |
| Clé étrangère | `<table_référencée>_id` | `user_id`, `invoice_id` |
| Index | `idx_<table>_<colonnes>` | `idx_bb_user_email` |
| Index unique | `uniq_<table>_<colonnes>` | `uniq_bb_user_email` |
| Contrainte | `chk_<table>_<description>` | `chk_bb_invoice_amount_positive` |

## Colonnes standard

Chaque table BB® inclut ces colonnes :

```sql
CREATE TABLE bb_example (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- ... colonnes métier ...
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE  -- Soft delete si applicable
);
```

- **UUID v7** pour les clés primaires (séquentiel, meilleur pour les index B-tree que UUID v4)
- **Timestamps avec timezone** (`TIMESTAMP WITH TIME ZONE`) — jamais sans timezone
- **Soft delete** (`deleted_at`) uniquement quand c'est un besoin métier (audit, récupération). Par défaut, on supprime vraiment.

## Migrations Doctrine

### Règles

1. **Une migration = un changement atomique.** Pas de migration qui crée 5 tables et modifie 3 colonnes.
2. **Jamais de `down()` qui perd des données.** Si la migration ajoute une colonne NOT NULL, le `down()` ne peut pas simplement la supprimer si elle contient des données.
3. **Tester les migrations sur une copie de la prod** avant de déployer.
4. **Nommage** : Doctrine génère les noms automatiquement (`Version20260115_143022`). Ne pas les renommer.

### Workflow

```bash
# Créer une migration depuis les changements d'entités
php bin/console doctrine:migrations:diff

# Vérifier le SQL généré
cat migrations/Version*.php

# Exécuter
php bin/console doctrine:migrations:migrate

# En cas de problème
php bin/console doctrine:migrations:migrate prev
```

## Indexation

### Règles d'indexation BB®

1. **Index sur toutes les clés étrangères** — Doctrine le fait automatiquement
2. **Index sur les colonnes de filtrage fréquent** — `status`, `type`, `email`
3. **Index composite** pour les requêtes fréquentes avec WHERE multi-colonnes
4. **Pas d'index inutile** — chaque index ralentit les écritures. Ajouter un index quand on observe un problème de performance, pas préventivement.

```sql
-- Index fréquents
CREATE INDEX idx_bb_user_email ON bb_user(email);
CREATE INDEX idx_bb_invoice_status_created ON bb_invoice(status, created_at DESC);
CREATE UNIQUE INDEX uniq_bb_user_email ON bb_user(email) WHERE deleted_at IS NULL;
```

## Backups

- **Fréquence** : quotidien à 3h du matin (cron sur le serveur)
- **Rétention** : 30 jours
- **Outil** : `pg_dump` compressé
- **Stockage** : bucket S3 OVH Object Storage (Suisse)
- **Test de restauration** : au moins une fois par trimestre

```bash
# Script de backup (simplifié)
pg_dump -Fc -h localhost -U bb_prod bb_production > /backups/bb_prod_$(date +%Y%m%d).dump

# Restauration
pg_restore -h localhost -U bb_prod -d bb_production /backups/bb_prod_20260115.dump
```

## Requêtes — Bonnes pratiques

1. **Pas de `SELECT *`** — lister les colonnes explicitement
2. **Pagination systématique** sur les endpoints de liste (`LIMIT` + `OFFSET` ou cursor-based)
3. **`EXPLAIN ANALYZE`** sur toute requête suspecte avant de la mettre en prod
4. **Pas de requête dans une boucle** — utiliser des jointures ou des sous-requêtes
5. **Transactions explicites** pour les opérations multi-tables
