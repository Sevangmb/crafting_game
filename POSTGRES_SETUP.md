# Configuration PostgreSQL Complète

## Serveur: 82.65.121.46
## Database: crafting_game
## User: sevans
## Password: Oketos2727!

---

## Option 1: Configuration Automatique (Recommandé)

### Sur Windows (votre machine actuelle):

```powershell
# Via PowerShell
.\setup_remote_postgres.ps1
```

Ou via SSH manuel:

```bash
# Copier le script sur le serveur
scp setup_postgres_server.sh sevans@82.65.121.46:/tmp/

# Se connecter et l'exécuter
ssh sevans@82.65.121.46
bash /tmp/setup_postgres_server.sh
```

---

## Option 2: Configuration Manuelle (Étape par Étape)

### 1. Se connecter au serveur PostgreSQL

```bash
ssh sevans@82.65.121.46
```

### 2. Vérifier la version de PostgreSQL

```bash
psql --version
# ou
sudo -u postgres psql -c "SELECT version();"
```

### 3. Configurer PostgreSQL pour écouter sur toutes les interfaces

```bash
# Trouver le fichier de configuration
PG_VERSION=$(psql --version | grep -oP '\d+' | head -1)
sudo nano /etc/postgresql/${PG_VERSION}/main/postgresql.conf

# Chercher et modifier:
listen_addresses = '*'

# Sauvegarder (Ctrl+X, Y, Enter)
```

### 4. Autoriser les connexions distantes dans pg_hba.conf

```bash
sudo nano /etc/postgresql/${PG_VERSION}/main/pg_hba.conf

# Ajouter à la fin du fichier:
host    crafting_game    sevans    0.0.0.0/0    md5

# Sauvegarder (Ctrl+X, Y, Enter)
```

### 5. Créer la base de données et l'utilisateur

```bash
sudo -u postgres psql
```

Dans psql:

```sql
-- Créer l'utilisateur s'il n'existe pas
CREATE USER sevans WITH PASSWORD 'Oketos2727!';

-- Créer la base de données
CREATE DATABASE crafting_game OWNER sevans;

-- Donner tous les privilèges
GRANT ALL PRIVILEGES ON DATABASE crafting_game TO sevans;

-- Se connecter à la base
\c crafting_game

-- Donner les privilèges sur le schéma
GRANT ALL PRIVILEGES ON SCHEMA public TO sevans;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO sevans;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO sevans;

-- Vérifier
\l crafting_game
\du sevans

-- Quitter
\q
```

### 6. Configurer le pare-feu

#### Si vous utilisez UFW:
```bash
sudo ufw allow 5432/tcp
sudo ufw reload
sudo ufw status
```

#### Si vous utilisez firewalld:
```bash
sudo firewall-cmd --permanent --add-port=5432/tcp
sudo firewall-cmd --reload
sudo firewall-cmd --list-all
```

#### Si vous utilisez iptables:
```bash
sudo iptables -A INPUT -p tcp --dport 5432 -j ACCEPT
sudo iptables-save
```

### 7. Redémarrer PostgreSQL

```bash
sudo systemctl restart postgresql
# ou
sudo service postgresql restart
```

### 8. Vérifier que PostgreSQL écoute

```bash
sudo netstat -plnt | grep 5432
# ou
sudo ss -plnt | grep 5432
```

Vous devriez voir:
```
tcp        0      0 0.0.0.0:5432            0.0.0.0:*               LISTEN
```

### 9. Tester la connexion locale

```bash
psql -h localhost -U sevans -d crafting_game
```

Mot de passe: `Oketos2727!`

Si ça marche, sortez avec `\q`

### 10. Tester depuis votre machine Windows

Sur votre machine Windows:

```bash
python test_db.py
```

Si la connexion réussit, vous êtes prêt!

---

## Option 3: PostgreSQL Local (Alternative)

Si vous ne pouvez pas accéder au serveur distant, installez PostgreSQL localement:

### Sur Windows:

1. **Télécharger PostgreSQL:**
   https://www.postgresql.org/download/windows/

2. **Installer PostgreSQL**
   - Port: 5432
   - Password: Oketos2727!

3. **Créer la base de données:**
   ```bash
   psql -U postgres
   ```

   ```sql
   CREATE USER sevans WITH PASSWORD 'Oketos2727!';
   CREATE DATABASE crafting_game OWNER sevans;
   GRANT ALL PRIVILEGES ON DATABASE crafting_game TO sevans;
   ```

4. **Modifier settings.py:**
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'crafting_game',
           'USER': 'sevans',
           'PASSWORD': 'Oketos2727!',
           'HOST': 'localhost',  # <- localhost au lieu de 82.65.121.46
           'PORT': '5432',
       }
   }
   ```

---

## Migration des Données

Une fois PostgreSQL accessible:

### 1. Revenir temporairement à SQLite pour le backup

Éditez `backend/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### 2. Sauvegarder les données SQLite

```bash
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 2 > data_backup.json
```

### 3. Revenir à PostgreSQL

Remettre la configuration PostgreSQL dans `backend/settings.py`

### 4. Appliquer les migrations

```bash
python manage.py migrate
```

### 5. Charger les données

```bash
python manage.py loaddata data_backup.json
```

### 6. Créer un superutilisateur (si nécessaire)

```bash
python manage.py createsuperuser
```

### 7. Tester

```bash
python manage.py check
python manage.py runserver
```

---

## Dépannage

### Erreur: "Connection timeout"

- Vérifiez que PostgreSQL est démarré
- Vérifiez le pare-feu
- Vérifiez que PostgreSQL écoute sur 0.0.0.0

### Erreur: "Authentication failed"

- Vérifiez le mot de passe
- Vérifiez pg_hba.conf
- Redémarrez PostgreSQL après modification

### Erreur: "Database does not exist"

- Créez la base manuellement
- Vérifiez les privilèges

### PostgreSQL n'écoute pas sur 0.0.0.0

```bash
sudo grep listen_addresses /etc/postgresql/*/main/postgresql.conf
```

Devrait afficher: `listen_addresses = '*'`

---

## Commandes Utiles

```bash
# Voir les bases de données
sudo -u postgres psql -c "\l"

# Voir les utilisateurs
sudo -u postgres psql -c "\du"

# Se connecter à une base
psql -h 82.65.121.46 -U sevans -d crafting_game

# Voir les tables
\dt

# Voir le schéma d'une table
\d nom_table

# Exécuter une requête
SELECT * FROM game_player LIMIT 5;

# Quitter
\q
```

---

## Support

Si vous rencontrez des problèmes, vérifiez les logs:

### Logs PostgreSQL:
```bash
sudo tail -f /var/log/postgresql/postgresql-*-main.log
```

### Logs Django:
```bash
tail -f logs/game.log
```
