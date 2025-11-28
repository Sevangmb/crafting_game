"""
Leaderboard Service - Manages global rankings
"""
from django.db import transaction
from game.models import Leaderboard, Player, GatheringLog, CraftingLog, CombatLog, PlayerQuest
from django.db.models import Sum, Count
import logging

logger = logging.getLogger(__name__)


class LeaderboardService:
    """Service for managing leaderboards"""

    @staticmethod
    @transaction.atomic
    def update_all_leaderboards():
        """Update all leaderboard categories"""
        updated_count = 0

        updated_count += LeaderboardService.update_level_leaderboard()
        updated_count += LeaderboardService.update_wealth_leaderboard()
        updated_count += LeaderboardService.update_gatherer_leaderboard()
        updated_count += LeaderboardService.update_crafter_leaderboard()
        updated_count += LeaderboardService.update_explorer_leaderboard()
        updated_count += LeaderboardService.update_combatant_leaderboard()
        updated_count += LeaderboardService.update_quests_leaderboard()

        logger.info(f"Updated {updated_count} leaderboard entries")
        return updated_count

    @staticmethod
    def update_level_leaderboard():
        """Update level leaderboard"""
        players = Player.objects.all().order_by('-level', '-experience')
        count = 0

        for rank, player in enumerate(players, start=1):
            entry, created = Leaderboard.objects.update_or_create(
                category='level',
                player=player,
                defaults={
                    'score': player.level * 1000000 + player.experience,
                    'rank': rank,
                    'metadata': {
                        'level': player.level,
                        'experience': player.experience
                    }
                }
            )
            count += 1

        return count

    @staticmethod
    def update_wealth_leaderboard():
        """Update wealth leaderboard"""
        players = Player.objects.all().order_by('-money', '-bank_balance')
        count = 0

        for rank, player in enumerate(players, start=1):
            total_wealth = player.money + player.bank_balance
            entry, created = Leaderboard.objects.update_or_create(
                category='wealth',
                player=player,
                defaults={
                    'score': total_wealth,
                    'rank': rank,
                    'metadata': {
                        'money': player.money,
                        'bank_balance': player.bank_balance,
                        'total': total_wealth
                    }
                }
            )
            count += 1

        return count

    @staticmethod
    def update_gatherer_leaderboard():
        """Update gatherer leaderboard"""
        # Count total gathering actions
        stats = GatheringLog.objects.values('player').annotate(
            total=Count('id')
        ).order_by('-total')

        count = 0
        for rank, stat in enumerate(stats, start=1):
            try:
                player = Player.objects.get(id=stat['player'])
                entry, created = Leaderboard.objects.update_or_create(
                    category='gatherer',
                    player=player,
                    defaults={
                        'score': stat['total'],
                        'rank': rank,
                        'metadata': {
                            'total_gathered': stat['total']
                        }
                    }
                )
                count += 1
            except Player.DoesNotExist:
                continue

        return count

    @staticmethod
    def update_crafter_leaderboard():
        """Update crafter leaderboard"""
        # Count total crafting actions
        stats = CraftingLog.objects.values('player').annotate(
            total=Sum('quantity')
        ).order_by('-total')

        count = 0
        for rank, stat in enumerate(stats, start=1):
            try:
                player = Player.objects.get(id=stat['player'])
                entry, created = Leaderboard.objects.update_or_create(
                    category='crafter',
                    player=player,
                    defaults={
                        'score': stat['total'] or 0,
                        'rank': rank,
                        'metadata': {
                            'total_crafted': stat['total'] or 0
                        }
                    }
                )
                count += 1
            except Player.DoesNotExist:
                continue

        return count

    @staticmethod
    def update_explorer_leaderboard():
        """Update explorer leaderboard"""
        players = Player.objects.all().order_by('-total_moves')
        count = 0

        for rank, player in enumerate(players, start=1):
            entry, created = Leaderboard.objects.update_or_create(
                category='explorer',
                player=player,
                defaults={
                    'score': player.total_moves,
                    'rank': rank,
                    'metadata': {
                        'total_moves': player.total_moves,
                        'current_pos': f"({player.grid_x}, {player.grid_y})"
                    }
                }
            )
            count += 1

        return count

    @staticmethod
    def update_combatant_leaderboard():
        """Update combatant leaderboard"""
        # Count victories
        stats = CombatLog.objects.filter(
            result='victory'
        ).values('player').annotate(
            victories=Count('id')
        ).order_by('-victories')

        count = 0
        for rank, stat in enumerate(stats, start=1):
            try:
                player = Player.objects.get(id=stat['player'])
                entry, created = Leaderboard.objects.update_or_create(
                    category='combatant',
                    player=player,
                    defaults={
                        'score': stat['victories'],
                        'rank': rank,
                        'metadata': {
                            'victories': stat['victories']
                        }
                    }
                )
                count += 1
            except Player.DoesNotExist:
                continue

        return count

    @staticmethod
    def update_quests_leaderboard():
        """Update quests leaderboard"""
        # Count completed quests
        stats = PlayerQuest.objects.filter(
            status='completed'
        ).values('player').annotate(
            total=Sum('times_completed')
        ).order_by('-total')

        count = 0
        for rank, stat in enumerate(stats, start=1):
            try:
                player = Player.objects.get(id=stat['player'])
                entry, created = Leaderboard.objects.update_or_create(
                    category='quests',
                    player=player,
                    defaults={
                        'score': stat['total'] or 0,
                        'rank': rank,
                        'metadata': {
                            'quests_completed': stat['total'] or 0
                        }
                    }
                )
                count += 1
            except Player.DoesNotExist:
                continue

        return count

    @staticmethod
    def get_leaderboard(category, limit=100):
        """Get top players for a category"""
        return Leaderboard.objects.filter(
            category=category
        ).select_related('player__user').order_by('rank')[:limit]

    @staticmethod
    def get_player_rank(player, category):
        """Get player's rank in a category"""
        try:
            entry = Leaderboard.objects.get(category=category, player=player)
            return {
                'rank': entry.rank,
                'score': entry.score,
                'metadata': entry.metadata
            }
        except Leaderboard.DoesNotExist:
            return None

    @staticmethod
    def get_all_player_ranks(player):
        """Get player's ranks in all categories"""
        entries = Leaderboard.objects.filter(player=player)

        ranks = {}
        for entry in entries:
            ranks[entry.category] = {
                'rank': entry.rank,
                'score': entry.score,
                'metadata': entry.metadata,
                'category_display': entry.get_category_display()
            }

        return ranks
