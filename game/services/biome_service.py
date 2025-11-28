"""
Biome Service

Manages biome-related logic, effects, and information.
"""
from typing import Dict, Any, List
from ..resource_generator import BIOME_DATA, get_biome_info, get_biome_from_coordinates
from ..models import Player
import random


class BiomeService:
    """Service for biome-related operations"""
    
    @staticmethod
    def get_biome_details(biome: str) -> Dict[str, Any]:
        """
        Get detailed information about a biome.
        
        Args:
            biome: The biome code
        
        Returns:
            Dictionary with biome details
        """
        return get_biome_info(biome)
    
    @staticmethod
    def get_all_biomes() -> Dict[str, Dict[str, Any]]:
        """
        Get information about all biomes.
        
        Returns:
            Dictionary mapping biome codes to their data
        """
        return BIOME_DATA
    
    @staticmethod
    def get_biome_at_location(lat: float, lon: float, grid_x: int, grid_y: int) -> str:
        """
        Determine the biome at a specific location.
        
        Args:
            lat: Latitude
            lon: Longitude
            grid_x: Grid X coordinate
            grid_y: Grid Y coordinate
        
        Returns:
            Biome code
        """
        return get_biome_from_coordinates(lat, lon, grid_x, grid_y)
    
    @staticmethod
    def apply_biome_effects(player: Player, biome: str, action: str) -> Dict[str, float]:
        """
        Calculate biome-specific bonuses/penalties for an action.
        
        Args:
            player: The player instance
            biome: The biome code
            action: The action type ('gathering', 'hunting', 'mining', 'fishing', 'scavenging')
        
        Returns:
            Dictionary with bonus multipliers
        """
        biome_info = get_biome_info(biome)
        effects = {}
        
        # Gathering bonus
        if action == 'gathering':
            effects['bonus'] = biome_info.get('gathering_bonus', 1.0)
            effects['penalty'] = biome_info.get('gathering_penalty', 1.0)
        
        # Hunting bonus
        elif action == 'hunting':
            effects['bonus'] = biome_info.get('hunting_bonus', 1.0)
        
        # Mining bonus
        elif action == 'mining':
            effects['bonus'] = biome_info.get('mining_bonus', 1.0)
        
        # Fishing bonus
        elif action == 'fishing':
            effects['bonus'] = biome_info.get('fishing_bonus', 1.0)
        
        # Scavenging bonus
        elif action == 'scavenging':
            effects['bonus'] = biome_info.get('scavenging_bonus', 1.0)
        
        return effects
    
    @staticmethod
    def get_biome_dangers(biome: str) -> List[str]:
        """
        Get list of dangers in a biome.
        
        Args:
            biome: The biome code
        
        Returns:
            List of danger descriptions
        """
        biome_info = get_biome_info(biome)
        return biome_info.get('dangers', [])
    
    @staticmethod
    def check_environmental_damage(player: Player, biome: str) -> Dict[str, Any]:
        """
        Check if player takes environmental damage in this biome.
        
        Args:
            player: The player instance
            biome: The biome code
        
        Returns:
            Dictionary with damage info
        """
        biome_info = get_biome_info(biome)
        damage_info = {
            'has_damage': False,
            'damage_type': None,
            'damage_amount': 0,
            'message': None
        }
        
        # Cold damage (glacier, tundra)
        if biome_info.get('cold_damage'):
            # Check if player has warm clothing (future implementation)
            damage_info['has_damage'] = True
            damage_info['damage_type'] = 'cold'
            damage_info['damage_amount'] = 5
            damage_info['message'] = '❄️ Le froid extrême vous inflige des dégâts!'
        
        # Heat damage (volcano, desert in summer)
        elif biome_info.get('heat_damage'):
            damage_info['has_damage'] = True
            damage_info['damage_type'] = 'heat'
            damage_info['damage_amount'] = 8
            damage_info['message'] = '🔥 La chaleur intense vous brûle!'
        
        # Thirst rate increase (desert)
        if biome_info.get('thirst_rate', 1.0) > 1.0:
            damage_info['thirst_multiplier'] = biome_info['thirst_rate']
        
        return damage_info
    
    @staticmethod
    def get_biome_ambient_description(biome: str) -> str:
        """
        Get ambient description for immersion.
        
        Args:
            biome: The biome code
        
        Returns:
            Ambient description string
        """
        biome_info = get_biome_info(biome)
        return biome_info.get('ambient', 'Silence...')
    
    @staticmethod
    def get_biome_difficulty(biome: str) -> int:
        """
        Get difficulty rating of a biome (1-5).
        
        Args:
            biome: The biome code
        
        Returns:
            Difficulty rating
        """
        biome_info = get_biome_info(biome)
        return biome_info.get('difficulty', 1)
    
    @staticmethod
    def suggest_nearby_biomes(current_biome: str) -> List[str]:
        """
        Suggest biomes that could be nearby (for transitions).
        
        Args:
            current_biome: Current biome code
        
        Returns:
            List of compatible nearby biomes
        """
        # Biome compatibility matrix
        compatible_biomes = {
            'plains': ['forest', 'steppe', 'farmland', 'wetland'],
            'forest': ['plains', 'taiga', 'rainforest', 'mushroom_forest'],
            'mountain': ['plains', 'glacier', 'canyon', 'volcano'],
            'desert': ['canyon', 'savanna', 'steppe'],
            'coast': ['plains', 'wetland', 'coral_reef'],
            'jungle': ['rainforest', 'swamp'],
            'tundra': ['taiga', 'glacier'],
            'glacier': ['mountain', 'tundra'],
            'volcano': ['mountain', 'desert'],
            'swamp': ['wetland', 'bog', 'jungle'],
            'urban': ['plains', 'farmland'],
        }
        
        return compatible_biomes.get(current_biome, ['plains'])
