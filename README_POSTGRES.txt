========================================
MIGRATION POSTGRESQL - INSTRUCTIONS
========================================

Serveur: 82.65.121.46:5432
Database: crafting_game
User: sevans
Password: Oketos2727!

========================================
ETAPE 1: CONFIGURER LE SERVEUR POSTGRES
========================================

Vous devez executer ces commandes SUR LE SERVEUR (82.65.121.46):

ssh sevans@82.65.121.46

Ensuite, copier/coller ce script:

----------------------------------------
#!/bin/bash

# Trouver la version PostgreSQL
PG_VERSION=$(ls /etc/postgresql/ 2>/dev/null | head -1)
PG_CONF="/etc/postgresql/${PG_VERSION}/main"

# Backup
sudo cp "$PG_CONF/postgresql.conf" "$PG_CONF/postgresql.conf.bak"
sudo cp "$PG_CONF/pg_hba.conf" "$PG_CONF/pg_hba.conf.bak"

# Configurer pour écouter partout
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "$PG_CONF/postgresql.conf"
sudo sed -i "s/listen_addresses = 'localhost'/listen_addresses = '*'/" "$PG_CONF/postgresql.conf"

# Autoriser connexions distantes
echo "host    crafting_game    sevans    0.0.0.0/0    md5" | sudo tee -a "$PG_CONF/pg_hba.conf"

# Ouvrir pare-feu
sudo ufw allow 5432/tcp

# Créer DB et user
sudo -u postgres psql <<SQL
CREATE USER sevans WITH PASSWORD 'Oketos2727!';
CREATE DATABASE crafting_game OWNER sevans;
GRANT ALL PRIVILEGES ON DATABASE crafting_game TO sevans;
\c crafting_game
GRANT ALL PRIVILEGES ON SCHEMA public TO sevans;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO sevans;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO sevans;
SQL

# Redémarrer PostgreSQL
sudo systemctl restart postgresql

# Vérifier
sudo netstat -plnt | grep 5432
psql -h localhost -U sevans -d crafting_game -c "SELECT version();"

echo "Configuration terminée!"
----------------------------------------

========================================
ETAPE 2: TESTER LA CONNEXION
========================================

Sur votre machine Windows:

python test_db.py

Si ça affiche "SUCCESS", passez à l'étape 3!

========================================
ETAPE 3: MIGRER LES DONNEES
========================================

Lancez le script de migration automatique:

python migrate_to_postgres.py

Le script va:
1. Tester la connexion PostgreSQL
2. Sauvegarder les données SQLite
3. Appliquer les migrations sur PostgreSQL
4. Restaurer les données
5. Peupler les configurations initiales

========================================
PROBLEMES COURANTS
========================================

1. "Connection timeout"
   -> PostgreSQL n'est pas accessible
   -> Vérifiez pare-feu: sudo ufw status
   -> Vérifiez que PG écoute: netstat -plnt | grep 5432

2. "Authentication failed"
   -> Mauvais mot de passe
   -> Vérifiez pg_hba.conf

3. "Database does not exist"
   -> Créez la manuellement sur le serveur
   -> sudo -u postgres createdb -O sevans crafting_game

========================================
AIDE RAPIDE
========================================

Scripts disponibles:
- test_db.py : Tester connexion PostgreSQL
- migrate_to_postgres.py : Migration automatique
- setup_postgres_server.sh : Config serveur (Linux)
- setup_remote_postgres.ps1 : Config serveur (via SSH depuis Windows)
- POSTGRES_SETUP.md : Documentation complète

Commandes PostgreSQL utiles:
- Se connecter : psql -h 82.65.121.46 -U sevans -d crafting_game
- Lister tables : \dt
- Voir données : SELECT * FROM game_player;
- Quitter : \q

========================================
BESOIN D'AIDE ?
========================================

Consultez: POSTGRES_SETUP.md

Ou contactez-moi avec:
- Le message d'erreur exact
- La sortie de: python test_db.py
- La sortie de: sudo netstat -plnt | grep 5432 (sur le serveur)

========================================
