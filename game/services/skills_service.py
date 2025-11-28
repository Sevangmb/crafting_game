"""
Skills and Talents Service

Manages player skills, XP progression, talent unlocking, and active effects.
"""
from typing import Dict, Tuple
from ..models import Skill, PlayerSkill, TalentNode, PlayerTalent, GameConfig, Player
from django.core.management import call_command


def ensure_default_skills() -> None:
    """
    Ensure default skills exist in the database.
    Creates the crafting skill and populates talents via management command.
    """
    crafting, _ = Skill.objects.get_or_create(code='crafting', defaults={'name': 'Artisanat'})
    # Use management command to populate talents
    try:
        call_command('populate_talents')
    except Exception as e:
        print(f"Warning: Could not populate talents: {e}")


def get_or_create_player_skill(player: Player, skill_code: str) -> PlayerSkill:
    """
    Get or create a PlayerSkill instance for the given player and skill.
    
    Args:
        player: The player instance
        skill_code: The skill code (e.g., 'crafting', 'gathering', 'hunting')
    
    Returns:
        PlayerSkill instance
    """
    ensure_default_skills()
    skill = Skill.objects.get(code=skill_code)
    default_skill_xp = GameConfig.get_config('default_skill_xp_to_next', 50)
    ps, _ = PlayerSkill.objects.get_or_create(
        player=player, 
        skill=skill, 
        defaults={
            'level': 1, 
            'xp': 0, 
            'xp_to_next': default_skill_xp, 
            'total_xp': 0
        }
    )
    return ps


def award_xp(player: Player, skill_code: str, amount: int) -> Tuple[PlayerSkill, bool]:
    """
    Award XP to a player's skill and handle level ups.
    
    Args:
        player: The player instance
        skill_code: The skill code
        amount: Amount of XP to award
    
    Returns:
        Tuple of (PlayerSkill instance, whether player leveled up)
    """
    ps = get_or_create_player_skill(player, skill_code)
    ps.xp += amount
    ps.total_xp += amount
    leveled = False
    
    while ps.xp >= ps.xp_to_next:
        ps.xp -= ps.xp_to_next
        ps.level += 1
        skill_level_multiplier = GameConfig.get_config('skill_level_multiplier', 50)
        ps.xp_to_next = skill_level_multiplier * ps.level
        leveled = True
    
    ps.save()
    
    # Try auto unlock talents after XP change
    auto_unlock_talents(player, skill_code)
    return ps, leveled


def auto_unlock_talents(player: Player, skill_code: str) -> None:
    """
    Automatically unlock talents based on player's total XP and prerequisites.
    
    Args:
        player: The player instance
        skill_code: The skill code
    """
    skill = Skill.objects.get(code=skill_code)
    ps = PlayerSkill.objects.get(player=player, skill=skill)
    owned_codes = set(
        PlayerTalent.objects.filter(player=player, talent_node__skill=skill)
        .values_list('talent_node__code', flat=True)
    )
    
    for node in TalentNode.objects.filter(skill=skill).order_by('tier', 'xp_required'):
        if node.code in owned_codes:
            continue
        
        # Check if prerequisites are met
        if any(req not in owned_codes for req in (node.prereq_codes or [])):
            continue
        
        # Check if total XP threshold is met
        if ps.total_xp >= node.xp_required:
            PlayerTalent.objects.create(player=player, talent_node=node)
            owned_codes.add(node.code)


def get_active_effects(player: Player, skill_code: str) -> Dict[str, int]:
    """
    Get all active talent effects for a player's skill.
    
    Args:
        player: The player instance
        skill_code: The skill code
    
    Returns:
        Dictionary mapping effect types to their maximum values
    """
    skill = Skill.objects.get(code=skill_code)
    talents = PlayerTalent.objects.filter(
        player=player, 
        talent_node__skill=skill
    ).select_related('talent_node')
    
    effects = {}
    for pt in talents:
        effect_type = pt.talent_node.effect_type
        effects[effect_type] = max(effects.get(effect_type, 0), pt.talent_node.effect_value)
    
    return effects
