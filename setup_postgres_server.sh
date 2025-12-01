#!/bin/bash
# Script to configure PostgreSQL server for remote access
# Run this script ON THE POSTGRESQL SERVER (82.65.121.46)

echo "🚀 Configuration du serveur PostgreSQL pour accès distant..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Find PostgreSQL config directory
PG_VERSION=$(psql --version | grep -oP '\d+' | head -1)
PG_CONF_DIR="/etc/postgresql/${PG_VERSION}/main"

if [ ! -d "$PG_CONF_DIR" ]; then
    # Try alternative locations
    PG_CONF_DIR="/var/lib/pgsql/data"
    if [ ! -d "$PG_CONF_DIR" ]; then
        PG_CONF_DIR="/usr/local/pgsql/data"
    fi
fi

echo -e "${YELLOW}Configuration directory: $PG_CONF_DIR${NC}"

# Backup original files
echo "📋 Sauvegarde des fichiers de configuration..."
sudo cp "$PG_CONF_DIR/postgresql.conf" "$PG_CONF_DIR/postgresql.conf.backup.$(date +%Y%m%d)"
sudo cp "$PG_CONF_DIR/pg_hba.conf" "$PG_CONF_DIR/pg_hba.conf.backup.$(date +%Y%m%d)"

# Configure postgresql.conf to listen on all interfaces
echo "⚙️  Configuration de postgresql.conf..."
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "$PG_CONF_DIR/postgresql.conf"
sudo sed -i "s/listen_addresses = 'localhost'/listen_addresses = '*'/" "$PG_CONF_DIR/postgresql.conf"

# Add entry to pg_hba.conf for remote connections
echo "🔐 Configuration de pg_hba.conf..."
if ! grep -q "host.*crafting_game.*sevans" "$PG_CONF_DIR/pg_hba.conf"; then
    echo "host    crafting_game    sevans    0.0.0.0/0    md5" | sudo tee -a "$PG_CONF_DIR/pg_hba.conf" > /dev/null
    echo -e "${GREEN}✅ Ajout de la règle d'accès distant${NC}"
else
    echo -e "${YELLOW}⚠️  Règle d'accès distant déjà présente${NC}"
fi

# Configure firewall (UFW)
echo "🔥 Configuration du pare-feu..."
if command -v ufw &> /dev/null; then
    sudo ufw allow 5432/tcp
    echo -e "${GREEN}✅ Port 5432 ouvert dans UFW${NC}"
elif command -v firewall-cmd &> /dev/null; then
    sudo firewall-cmd --permanent --add-port=5432/tcp
    sudo firewall-cmd --reload
    echo -e "${GREEN}✅ Port 5432 ouvert dans firewalld${NC}"
else
    echo -e "${YELLOW}⚠️  Pare-feu non détecté, vérifiez manuellement${NC}"
fi

# Create database and user
echo "🗄️  Création de la base de données et de l'utilisateur..."
sudo -u postgres psql <<EOF
-- Create user if not exists
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'sevans') THEN
        CREATE USER sevans WITH PASSWORD 'Oketos2727!';
    END IF;
END
\$\$;

-- Create database if not exists
SELECT 'CREATE DATABASE crafting_game OWNER sevans'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'crafting_game')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE crafting_game TO sevans;

-- Connect to database and grant schema privileges
\c crafting_game
GRANT ALL PRIVILEGES ON SCHEMA public TO sevans;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sevans;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sevans;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO sevans;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO sevans;

-- Show result
\l crafting_game
\du sevans
EOF

# Restart PostgreSQL
echo "🔄 Redémarrage de PostgreSQL..."
if command -v systemctl &> /dev/null; then
    sudo systemctl restart postgresql
    echo -e "${GREEN}✅ PostgreSQL redémarré (systemctl)${NC}"
elif command -v service &> /dev/null; then
    sudo service postgresql restart
    echo -e "${GREEN}✅ PostgreSQL redémarré (service)${NC}"
else
    echo -e "${RED}❌ Impossible de redémarrer PostgreSQL automatiquement${NC}"
    echo "Redémarrez manuellement PostgreSQL"
fi

# Test connection
echo "🧪 Test de connexion..."
if sudo -u postgres psql -d crafting_game -U sevans -c "SELECT version();" &> /dev/null; then
    echo -e "${GREEN}✅ Connexion à la base de données réussie${NC}"
else
    echo -e "${RED}❌ Échec de la connexion à la base de données${NC}"
fi

# Show PostgreSQL status
echo "📊 État de PostgreSQL:"
if command -v systemctl &> /dev/null; then
    sudo systemctl status postgresql --no-pager -l
fi

echo ""
echo -e "${GREEN}✨ Configuration terminée !${NC}"
echo ""
echo "📝 Informations de connexion:"
echo "   Host: 82.65.121.46"
echo "   Port: 5432"
echo "   Database: crafting_game"
echo "   User: sevans"
echo "   Password: Oketos2727!"
echo ""
echo "🔍 Vérifiez que PostgreSQL écoute bien:"
echo "   sudo netstat -plnt | grep 5432"
echo ""
echo "🧪 Testez la connexion depuis l'extérieur:"
echo "   psql -h 82.65.121.46 -p 5432 -U sevans -d crafting_game"
