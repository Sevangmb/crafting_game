#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Complete migration script to PostgreSQL
"""
import os
import sys
import subprocess
import json

def run_command(cmd, description):
    """Run a command and print status"""
    print(f"\n[*] {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"[OK] {description} completed")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed: {e.stderr}")
        return None

def main():
    print("="*60)
    print("PostgreSQL Migration Script")
    print("="*60)

    # Step 1: Test PostgreSQL connection
    print("\n[1/7] Testing PostgreSQL connection...")
    result = subprocess.run(
        ["python", "test_db.py"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("[ERROR] Cannot connect to PostgreSQL!")
        print(result.stdout)
        print(result.stderr)
        print("\nPlease configure PostgreSQL first:")
        print("  - Run: setup_remote_postgres.ps1")
        print("  - Or follow: POSTGRES_SETUP.md")
        return 1

    print("[OK] PostgreSQL connection successful")

    # Step 2: Backup current database
    print("\n[2/7] Backing up current SQLite database...")

    # Temporarily switch to SQLite
    settings_file = "backend/settings.py"
    with open(settings_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Save original
    with open(settings_file + '.postgres_backup', 'w', encoding='utf-8') as f:
        f.write(content)

    # Replace with SQLite config
    sqlite_config = """DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}"""

    pg_start = content.find("DATABASES = {")
    pg_end = content.find("}", pg_start) + 1
    content_sqlite = content[:pg_start] + sqlite_config + content[pg_end:]

    with open(settings_file, 'w', encoding='utf-8') as f:
        f.write(content_sqlite)

    # Backup data
    result = run_command(
        "python manage.py dumpdata --natural-foreign --natural-primary "
        "-e contenttypes -e auth.Permission --indent 2 > data_backup.json",
        "Dumping SQLite data"
    )

    if result is None:
        print("[WARNING] Data backup failed or no data to backup")

    # Restore PostgreSQL config
    with open(settings_file + '.postgres_backup', 'r', encoding='utf-8') as f:
        content = f.read()

    with open(settings_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print("[OK] Database backup completed")

    # Step 3: Run migrations on PostgreSQL
    print("\n[3/7] Running migrations on PostgreSQL...")
    result = run_command(
        "python manage.py migrate",
        "Applying migrations"
    )

    if result is None:
        print("[ERROR] Migration failed!")
        return 1

    # Step 4: Create superuser prompt
    print("\n[4/7] Superuser setup...")
    print("Do you want to create a superuser? (y/n): ", end='')
    choice = input().lower()

    if choice == 'y':
        subprocess.run(["python", "manage.py", "createsuperuser"])

    # Step 5: Load data
    print("\n[5/7] Loading data into PostgreSQL...")

    if os.path.exists('data_backup.json'):
        # Check if file has data
        with open('data_backup.json', 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                if len(data) > 0:
                    result = run_command(
                        "python manage.py loaddata data_backup.json",
                        "Loading backed up data"
                    )
                    if result is None:
                        print("[WARNING] Some data may not have loaded correctly")
                else:
                    print("[INFO] No data to restore (empty backup)")
            except json.JSONDecodeError:
                print("[WARNING] Backup file is invalid or empty")
    else:
        print("[INFO] No backup file found, starting fresh")

    # Step 6: Run populate scripts
    print("\n[6/7] Populating initial data...")
    print("Do you want to populate game data (configs, quests, etc.)? (y/n): ", end='')
    choice = input().lower()

    if choice == 'y':
        run_command("python manage.py populate_configs", "Populating game configs")
        run_command("python manage.py populate_quests", "Populating quests")
        run_command("python manage.py populate_enemies", "Populating enemies (if exists)")

    # Step 7: Verify
    print("\n[7/7] Verifying migration...")
    result = run_command(
        "python manage.py check",
        "Running Django checks"
    )

    if result is None:
        print("[ERROR] Verification failed!")
        return 1

    print("\n" + "="*60)
    print("Migration Complete!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Test the application:")
    print("     python manage.py runserver")
    print("\n  2. Check data integrity in admin:")
    print("     http://localhost:8000/admin")
    print("\n  3. Commit the changes:")
    print("     git add backend/settings.py")
    print("     git commit -m 'feat: Migrate to PostgreSQL'")
    print("="*60)

    return 0

if __name__ == '__main__':
    sys.exit(main())
