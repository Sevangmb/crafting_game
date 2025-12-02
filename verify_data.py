import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from game.models import Material, Quest, Mob

User = get_user_model()

def check_count(model, name):
    try:
        count = model.objects.count()
        print(f"[OK] {name}: {count}")
        return count
    except Exception as e:
        print(f"[ERROR] Could not count {name}: {e}")
        return 0

print("--- Verifying Database Content ---")
user_count = check_count(User, "Users")
material_count = check_count(Material, "Materials")
quest_count = check_count(Quest, "Quests")
mob_count = check_count(Mob, "Mobs")

if user_count > 0 and material_count > 0:
    print("\n[SUCCESS] Database connection works and data is present.")
else:
    print("\n[WARNING] Database seems empty or inaccessible.")
