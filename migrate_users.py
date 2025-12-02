import os
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Connect to old SQLite database
conn = sqlite3.connect('db.sqlite3.bak')
cursor = conn.cursor()

# Get all users from SQLite
cursor.execute('SELECT username, email, password, is_staff, is_superuser, is_active FROM auth_user')
users = cursor.fetchall()

print(f"Found {len(users)} users in SQLite database")

for username, email, password_hash, is_staff, is_superuser, is_active in users:
    if User.objects.filter(username=username).exists():
        print(f"User {username} already exists, skipping...")
        continue
    
    # Create user with the hashed password from SQLite
    user = User(
        username=username,
        email=email or '',
        password=password_hash,  # Use the existing hash
        is_staff=bool(is_staff),
        is_superuser=bool(is_superuser),
        is_active=bool(is_active)
    )
    user.save()
    print(f"Created user: {username} (Staff: {is_staff}, Super: {is_superuser})")

conn.close()
print("\nUser migration complete!")
