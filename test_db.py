#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import psycopg2

config = {
    'host': '82.65.121.46',
    'port': 5432,
    'database': 'crafting_game',
    'user': 'sevans',
    'password': 'Oketos2727!',
}

print("Testing PostgreSQL connection...")
print(f"Host: {config['host']}:{config['port']}")
print(f"Database: {config['database']}")
print(f"User: {config['user']}")
print()

try:
    print("Connecting...")
    conn = psycopg2.connect(
        host=config['host'],
        port=config['port'],
        database=config['database'],
        user=config['user'],
        password=config['password'],
        connect_timeout=10
    )

    print("SUCCESS! Connection established.")

    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"PostgreSQL version: {version[:60]}...")

    cursor.execute("SELECT current_database();")
    db = cursor.fetchone()[0]
    print(f"Current database: {db}")

    cursor.close()
    conn.close()

    print()
    print("All checks passed! Ready to migrate.")
    sys.exit(0)

except psycopg2.OperationalError as e:
    print(f"ERROR: {e}")
    print()
    print("Troubleshooting steps:")
    print("1. Check if PostgreSQL is running on the server")
    print("2. Check if port 5432 is open in firewall")
    print("3. Check postgresql.conf: listen_addresses = '*'")
    print("4. Check pg_hba.conf: host crafting_game sevans 0.0.0.0/0 md5")
    print("5. Restart PostgreSQL after config changes")
    sys.exit(1)

except Exception as e:
    print(f"UNEXPECTED ERROR: {e}")
    sys.exit(1)
