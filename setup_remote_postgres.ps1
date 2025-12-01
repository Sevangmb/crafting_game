# PowerShell script to configure remote PostgreSQL server via SSH
# Run this script on Windows to configure the remote server

$SERVER_IP = "82.65.121.46"
$SERVER_USER = "sevans"  # or your SSH user
$DB_NAME = "crafting_game"
$DB_USER = "sevans"
$DB_PASSWORD = "Oketos2727!"

Write-Host "Configuring PostgreSQL on remote server $SERVER_IP..." -ForegroundColor Green
Write-Host ""

# Create the setup script content
$setupScript = @"
#!/bin/bash
echo 'Starting PostgreSQL configuration...'

# Find PostgreSQL version and config directory
PG_VERSION=\$(psql --version 2>/dev/null | grep -oP '\d+' | head -1)
if [ -z "\$PG_VERSION" ]; then
    PG_VERSION=\$(ls /etc/postgresql/ 2>/dev/null | head -1)
fi

PG_CONF_DIR="/etc/postgresql/\${PG_VERSION}/main"
if [ ! -d "\$PG_CONF_DIR" ]; then
    PG_CONF_DIR="/var/lib/pgsql/data"
fi

echo "PostgreSQL config directory: \$PG_CONF_DIR"

# Backup configs
sudo cp "\$PG_CONF_DIR/postgresql.conf" "\$PG_CONF_DIR/postgresql.conf.bak" 2>/dev/null
sudo cp "\$PG_CONF_DIR/pg_hba.conf" "\$PG_CONF_DIR/pg_hba.conf.bak" 2>/dev/null

# Configure postgresql.conf
echo 'Configuring postgresql.conf...'
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "\$PG_CONF_DIR/postgresql.conf"
sudo sed -i "s/listen_addresses = 'localhost'/listen_addresses = '*'/" "\$PG_CONF_DIR/postgresql.conf"

# Configure pg_hba.conf
echo 'Configuring pg_hba.conf...'
if ! sudo grep -q 'host.*crafting_game.*sevans' "\$PG_CONF_DIR/pg_hba.conf"; then
    echo 'host    crafting_game    sevans    0.0.0.0/0    md5' | sudo tee -a "\$PG_CONF_DIR/pg_hba.conf"
fi

# Open firewall
echo 'Configuring firewall...'
if command -v ufw &> /dev/null; then
    sudo ufw allow 5432/tcp
elif command -v firewall-cmd &> /dev/null; then
    sudo firewall-cmd --permanent --add-port=5432/tcp
    sudo firewall-cmd --reload
fi

# Create database and user
echo 'Creating database and user...'
sudo -u postgres psql <<EOSQL
DO \\\$\\\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = '$DB_USER') THEN
        CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
    END IF;
END
\\\$\\\$;

SELECT 'CREATE DATABASE $DB_NAME OWNER $DB_USER'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec

GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

\c $DB_NAME
GRANT ALL PRIVILEGES ON SCHEMA public TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;
EOSQL

# Restart PostgreSQL
echo 'Restarting PostgreSQL...'
if command -v systemctl &> /dev/null; then
    sudo systemctl restart postgresql
elif command -v service &> /dev/null; then
    sudo service postgresql restart
fi

# Check status
echo ''
echo 'Configuration complete!'
echo 'Checking status...'
sudo netstat -plnt 2>/dev/null | grep 5432 || ss -plnt 2>/dev/null | grep 5432

echo ''
echo 'Testing local connection...'
psql -h localhost -U $DB_USER -d $DB_NAME -c 'SELECT version();'
"@

# Save script to temp file
$tempScript = [System.IO.Path]::GetTempFileName() + ".sh"
$setupScript | Out-File -FilePath $tempScript -Encoding UTF8

Write-Host "Step 1: Copying setup script to server..." -ForegroundColor Yellow
scp $tempScript "${SERVER_USER}@${SERVER_IP}:/tmp/setup_postgres.sh"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Step 2: Making script executable..." -ForegroundColor Yellow
    ssh "${SERVER_USER}@${SERVER_IP}" "chmod +x /tmp/setup_postgres.sh"

    Write-Host "Step 3: Running setup script..." -ForegroundColor Yellow
    ssh "${SERVER_USER}@${SERVER_IP}" "bash /tmp/setup_postgres.sh"

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "SUCCESS! PostgreSQL configured." -ForegroundColor Green
        Write-Host ""
        Write-Host "Testing connection from this machine..." -ForegroundColor Yellow
        python test_db.py
    } else {
        Write-Host "ERROR: Setup script failed" -ForegroundColor Red
    }
} else {
    Write-Host "ERROR: Could not connect to server via SSH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run these commands manually on the server:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host $setupScript
}

# Cleanup
Remove-Item $tempScript -ErrorAction SilentlyContinue
