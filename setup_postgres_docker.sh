#!/bin/bash
# Script to setup PostgreSQL in Docker container on Unraid
# Run this script ON THE UNRAID SERVER

echo "=========================================="
echo "PostgreSQL Docker Setup for Unraid"
echo "=========================================="

# Find PostgreSQL container
echo ""
echo "Looking for PostgreSQL container..."
POSTGRES_CONTAINER=$(docker ps --format '{{.Names}}' | grep -i postgres | head -1)

if [ -z "$POSTGRES_CONTAINER" ]; then
    echo "ERROR: No PostgreSQL container found!"
    echo ""
    echo "Available containers:"
    docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
    echo ""
    echo "Please specify container name manually:"
    echo "  export POSTGRES_CONTAINER=your_container_name"
    echo "  bash $0"
    exit 1
fi

echo "Found container: $POSTGRES_CONTAINER"

# Check if container is running
if ! docker ps | grep -q "$POSTGRES_CONTAINER"; then
    echo "ERROR: Container $POSTGRES_CONTAINER is not running!"
    echo "Please start it first in Unraid Docker interface"
    exit 1
fi

# Get container IP
CONTAINER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$POSTGRES_CONTAINER")
echo "Container IP: $CONTAINER_IP"

# Check port mapping
echo ""
echo "Checking port mapping..."
PORT_MAPPING=$(docker port "$POSTGRES_CONTAINER" 5432 2>/dev/null)
if [ -z "$PORT_MAPPING" ]; then
    echo "WARNING: Port 5432 is NOT mapped to host!"
    echo "You need to edit the container in Unraid and add:"
    echo "  Container Port: 5432"
    echo "  Host Port: 5432"
    echo ""
    echo "After adding the port mapping, restart the container and run this script again."
    echo ""
    echo "For now, you can use the container IP: $CONTAINER_IP"
else
    echo "Port mapping: $PORT_MAPPING"
fi

# Create database and user
echo ""
echo "=========================================="
echo "Creating database and user..."
echo "=========================================="

docker exec -i "$POSTGRES_CONTAINER" psql -U postgres <<'EOF'
-- Create user if not exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'sevans') THEN
        CREATE USER sevans WITH PASSWORD 'Oketos2727!';
        RAISE NOTICE 'User sevans created';
    ELSE
        RAISE NOTICE 'User sevans already exists';
        ALTER USER sevans WITH PASSWORD 'Oketos2727!';
    END IF;
END
$$;

-- Create database if not exists
SELECT 'CREATE DATABASE crafting_game OWNER sevans'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'crafting_game')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE crafting_game TO sevans;

-- Connect to database
\c crafting_game

-- Grant schema privileges
GRANT ALL PRIVILEGES ON SCHEMA public TO sevans;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO sevans;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO sevans;

-- Verify
\l crafting_game
\du sevans

-- Test query
SELECT 'PostgreSQL is ready for crafting_game!' as status;
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "SUCCESS! Database configured"
    echo "=========================================="
    echo ""
    echo "Connection details:"
    echo "  Host: 82.65.121.46 (or $CONTAINER_IP)"
    echo "  Port: 5432"
    echo "  Database: crafting_game"
    echo "  User: sevans"
    echo "  Password: Oketos2727!"
    echo ""
    echo "Test from within container:"
    echo "  docker exec -it $POSTGRES_CONTAINER psql -U sevans -d crafting_game"
    echo ""

    if [ -n "$PORT_MAPPING" ]; then
        echo "Test from Windows:"
        echo "  python test_db.py"
    else
        echo "To access from Windows, you need to:"
        echo "  1. Edit container in Unraid Docker"
        echo "  2. Add port mapping: 5432:5432"
        echo "  3. Apply and restart container"
        echo ""
        echo "Or use container IP in Django settings:"
        echo "  HOST: '$CONTAINER_IP'"
    fi

    echo ""
    echo "=========================================="
else
    echo ""
    echo "ERROR: Database setup failed"
    exit 1
fi

# Check firewall
echo ""
echo "Checking firewall..."
if command -v iptables >/dev/null 2>&1; then
    if ! iptables -L INPUT -n | grep -q "tcp dpt:5432"; then
        echo "Opening port 5432 in firewall..."
        iptables -A INPUT -p tcp --dport 5432 -j ACCEPT
        echo "Port 5432 opened"
    else
        echo "Port 5432 already open"
    fi
fi

echo ""
echo "Done!"
