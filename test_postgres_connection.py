#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to test PostgreSQL connection
"""
import sys
import psycopg2
from psycopg2 import OperationalError

def test_connection():
    """Test PostgreSQL connection"""

    config = {
        'host': '82.65.121.46',
        'port': 5432,
        'database': 'crafting_game',
        'user': 'sevans',
        'password': 'Oketos2727!',
    }

    print("🧪 Test de connexion PostgreSQL...")
    print(f"   Host: {config['host']}")
    print(f"   Port: {config['port']}")
    print(f"   Database: {config['database']}")
    print(f"   User: {config['user']}")
    print()

    try:
        print("📡 Tentative de connexion...")
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['user'],
            password=config['password'],
            connect_timeout=10
        )

        print("✅ Connexion réussie !")

        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"📊 Version PostgreSQL: {version[:50]}...")

        # Check database
        cursor.execute("SELECT current_database();")
        db = cursor.fetchone()[0]
        print(f"🗄️  Base de données: {db}")

        # Check privileges
        cursor.execute("""
            SELECT
                has_database_privilege('sevans', 'crafting_game', 'CONNECT') as can_connect,
                has_database_privilege('sevans', 'crafting_game', 'CREATE') as can_create;
        """)
        privs = cursor.fetchone()
        print(f"🔐 Privilèges:")
        print(f"   - CONNECT: {privs[0]}")
        print(f"   - CREATE: {privs[1]}")

        cursor.close()
        conn.close()

        print()
        print("✨ Tout est OK ! Vous pouvez lancer les migrations.")
        return True

    except OperationalError as e:
        print(f"❌ Erreur de connexion: {e}")
        print()
        print("🔍 Vérifications à faire:")
        print("   1. Le serveur PostgreSQL est-il démarré ?")
        print("      sudo systemctl status postgresql")
        print()
        print("   2. PostgreSQL écoute-t-il sur toutes les interfaces ?")
        print("      Vérifiez listen_addresses dans postgresql.conf")
        print()
        print("   3. Le pare-feu autorise-t-il le port 5432 ?")
        print("      sudo ufw status")
        print("      sudo ufw allow 5432/tcp")
        print()
        print("   4. pg_hba.conf autorise-t-il les connexions distantes ?")
        print("      Ajoutez: host  crafting_game  sevans  0.0.0.0/0  md5")
        print()
        print("   5. Testez depuis le serveur:")
        print("      psql -U sevans -d crafting_game")
        print()
        return False

    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)
