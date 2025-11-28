"""
Ensure all players have health system initialized
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from game.models import Player
from game.services.health_service import initialize_player_health

def ensure_all_players_have_health():
    """Initialize health system for all players"""
    players = Player.objects.all()

    for player in players:
        if not hasattr(player, 'health_status'):
            print(f"Initializing health for player: {player.user.username}")
            initialize_player_health(player)
        else:
            print(f"Player {player.user.username} already has health system")

    print("\n✅ All players have health system initialized!")

if __name__ == '__main__':
    ensure_all_players_have_health()
