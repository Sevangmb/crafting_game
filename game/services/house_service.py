'''House service utilities'''

from django.db import transaction
from ..models import House, Player


def create_house(player: Player, cell, level: int = 1):
    """Create a House for the given player on the specified cell.

    Args:
        player (Player): The player who will own the house.
        cell (MapCell): The map cell where the house will be placed. Must have ``grid_x`` and ``grid_y`` attributes.
        level (int, optional): Starting level of the house. Defaults to 1.

    Returns:
        tuple[House, bool]: The House instance and a boolean indicating whether it was created (True) or already existed (False).
    """
    # Use a transaction to avoid race conditions during concurrent creation.
    with transaction.atomic():
        house, created = House.objects.get_or_create(
            player=player,
            grid_x=cell.grid_x,
            grid_y=cell.grid_y,
            defaults={
                "level": level,
                "material_requirements": {},
            },
        )
    return house, created
