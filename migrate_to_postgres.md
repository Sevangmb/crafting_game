# Migration vers PostgreSQL

## Étapes à suivre :

### 1. Remplacer le mot de passe
Éditez `backend/settings.py` ligne 86 et remplacez `YOUR_PASSWORD_HERE` par votre vrai mot de passe PostgreSQL.

### 2. Créer la base de données PostgreSQL
Connectez-vous à votre serveur PostgreSQL et exécutez :

```sql
CREATE DATABASE crafting_game;
GRANT ALL PRIVILEGES ON DATABASE crafting_game TO sevans;
```

Ou si vous avez déjà la base de données, assurez-vous que l'utilisateur `sevans` a les droits :

```sql
\c crafting_game
GRANT ALL PRIVILEGES ON SCHEMA public TO sevans;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sevans;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sevans;
```

### 3. Exporter les données de SQLite (optionnel si vous voulez garder les données)

```bash
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 2 > data_backup.json
```

### 4. Appliquer les migrations sur PostgreSQL

```bash
python manage.py migrate
```

### 5. Importer les données (si vous avez fait le backup)

```bash
python manage.py loaddata data_backup.json
```

### 6. Créer un superutilisateur (si nouvelle base)

```bash
python manage.py createsuperuser
```

### 7. Tester la connexion

```bash
python manage.py check --database default
python manage.py dbshell
```

## Script automatique

Si vous voulez tout faire d'un coup :

```bash
# 1. Backup des données
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 2 > data_backup.json

# 2. Appliquer les migrations
python manage.py migrate

# 3. Restaurer les données
python manage.py loaddata data_backup.json

# 4. Vérifier
python manage.py check
```

## En cas de problème

Si la migration échoue :
1. Vérifiez que PostgreSQL est accessible : `psql -h 82.65.121.46 -p 5432 -U sevans -d crafting_game`
2. Vérifiez les logs dans `logs/game.log`
3. Vérifiez que psycopg2 est installé : `pip show psycopg2-binary`
