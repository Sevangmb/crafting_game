import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = 'sevans'
email = 'sevans@hotmail.fr'
password = 'Oketos2727!'

if not User.objects.filter(username=username).exists():
    print(f"Creating superuser {username}...")
    User.objects.create_superuser(username, email, password)
    print("Superuser created.")
else:
    print(f"Superuser {username} already exists.")
