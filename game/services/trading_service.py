"""
Trading Service - Manages player-to-player trades
"""
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from game.models import TradeOffer, Player, Material, Inventory
import logging

logger = logging.getLogger(__name__)


class TradingService:
    """Service for managing trades between players"""

    @staticmethod
    def create_trade_offer(from_player, to_player_id, offered_items, offered_money,
                          requested_items, requested_money, message="", duration_hours=24):
        """Create a new trade offer"""
        try:
            to_player = Player.objects.get(id=to_player_id)

            # Validate: can't trade with yourself
            if from_player.id == to_player.id:
                return None, "Vous ne pouvez pas échanger avec vous-même"

            # Validate offered items exist in inventory
            for item in offered_items:
                material_id = item.get('material_id')
                quantity = item.get('quantity', 1)

                try:
                    inv = Inventory.objects.get(player=from_player, material_id=material_id)
                    if inv.quantity < quantity:
                        material = Material.objects.get(id=material_id)
                        return None, f"Quantité insuffisante de {material.name}"
                except Inventory.DoesNotExist:
                    material = Material.objects.get(id=material_id)
                    return None, f"{material.name} non disponible"

            # Validate money
            if offered_money > from_player.money:
                return None, f"Argent insuffisant. Vous avez {from_player.money} coins"

            # Create trade offer
            expires_at = timezone.now() + timedelta(hours=duration_hours)

            trade = TradeOffer.objects.create(
                from_player=from_player,
                to_player=to_player,
                offered_items=offered_items,
                offered_money=offered_money,
                requested_items=requested_items,
                requested_money=requested_money,
                message=message,
                expires_at=expires_at
            )

            logger.info(f"Trade offer created: {from_player.user.username} → {to_player.user.username}")
            return trade, None

        except Player.DoesNotExist:
            return None, "Joueur introuvable"
        except Material.DoesNotExist:
            return None, "Matériau introuvable"
        except Exception as e:
            logger.error(f"Error creating trade: {e}")
            return None, str(e)

    @staticmethod
    @transaction.atomic
    def accept_trade(trade_id, accepting_player):
        """Accept a trade offer"""
        try:
            trade = TradeOffer.objects.select_for_update().get(
                id=trade_id,
                to_player=accepting_player
            )

            # Validate trade can be accepted
            can_accept, error = trade.can_accept()
            if not can_accept:
                return False, error

            # Check if accepting player has requested items
            for item in trade.requested_items:
                material_id = item.get('material_id')
                quantity = item.get('quantity', 1)

                try:
                    inv = Inventory.objects.get(player=accepting_player, material_id=material_id)
                    if inv.quantity < quantity:
                        material = Material.objects.get(id=material_id)
                        return False, f"Vous n'avez pas assez de {material.name}"
                except Inventory.DoesNotExist:
                    material = Material.objects.get(id=material_id)
                    return False, f"Vous n'avez pas de {material.name}"

            # Check money
            if trade.requested_money > accepting_player.money:
                return False, f"Argent insuffisant. Requis: {trade.requested_money}"

            # Verify from_player still has offered items
            for item in trade.offered_items:
                material_id = item.get('material_id')
                quantity = item.get('quantity', 1)

                try:
                    inv = Inventory.objects.get(player=trade.from_player, material_id=material_id)
                    if inv.quantity < quantity:
                        material = Material.objects.get(id=material_id)
                        return False, f"L'offrant n'a plus assez de {material.name}"
                except Inventory.DoesNotExist:
                    return False, "L'offre n'est plus valide"

            # Verify from_player money
            if trade.offered_money > trade.from_player.money:
                return False, "L'offrant n'a plus assez d'argent"

            # Execute trade: Remove from from_player
            for item in trade.offered_items:
                material_id = item.get('material_id')
                quantity = item.get('quantity', 1)

                inv = Inventory.objects.get(player=trade.from_player, material_id=material_id)
                inv.quantity -= quantity
                if inv.quantity <= 0:
                    inv.delete()
                else:
                    inv.save()

            # Remove money from from_player
            trade.from_player.money -= trade.offered_money
            trade.from_player.save()

            # Remove from to_player (accepting player)
            for item in trade.requested_items:
                material_id = item.get('material_id')
                quantity = item.get('quantity', 1)

                inv = Inventory.objects.get(player=accepting_player, material_id=material_id)
                inv.quantity -= quantity
                if inv.quantity <= 0:
                    inv.delete()
                else:
                    inv.save()

            # Remove money from accepting player
            accepting_player.money -= trade.requested_money
            accepting_player.save()

            # Add to accepting player
            for item in trade.offered_items:
                material_id = item.get('material_id')
                quantity = item.get('quantity', 1)
                material = Material.objects.get(id=material_id)

                inv, created = Inventory.objects.get_or_create(
                    player=accepting_player,
                    material=material,
                    defaults={'quantity': 0}
                )
                inv.quantity += quantity
                inv.save()

            # Add money to accepting player
            accepting_player.money += trade.offered_money
            accepting_player.save()

            # Add to from_player
            for item in trade.requested_items:
                material_id = item.get('material_id')
                quantity = item.get('quantity', 1)
                material = Material.objects.get(id=material_id)

                inv, created = Inventory.objects.get_or_create(
                    player=trade.from_player,
                    material=material,
                    defaults={'quantity': 0}
                )
                inv.quantity += quantity
                inv.save()

            # Add money to from_player
            trade.from_player.money += trade.requested_money
            trade.from_player.save()

            # Mark trade as completed
            trade.status = 'completed'
            trade.completed_at = timezone.now()
            trade.save()

            logger.info(f"Trade completed: {trade.from_player.user.username} ↔ {accepting_player.user.username}")
            return True, None

        except TradeOffer.DoesNotExist:
            return False, "Offre introuvable"
        except Exception as e:
            logger.error(f"Error accepting trade: {e}")
            return False, str(e)

    @staticmethod
    def reject_trade(trade_id, player):
        """Reject a trade offer"""
        try:
            trade = TradeOffer.objects.get(
                id=trade_id,
                to_player=player,
                status='pending'
            )

            trade.status = 'rejected'
            trade.save()

            logger.info(f"Trade rejected by {player.user.username}")
            return True, None

        except TradeOffer.DoesNotExist:
            return False, "Offre introuvable"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def cancel_trade(trade_id, player):
        """Cancel own trade offer"""
        try:
            trade = TradeOffer.objects.get(
                id=trade_id,
                from_player=player,
                status='pending'
            )

            trade.status = 'cancelled'
            trade.save()

            logger.info(f"Trade cancelled by {player.user.username}")
            return True, None

        except TradeOffer.DoesNotExist:
            return False, "Offre introuvable"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_received_trades(player):
        """Get trades received by player"""
        return TradeOffer.objects.filter(
            to_player=player,
            status='pending'
        ).select_related('from_player', 'to_player').order_by('-created_at')

    @staticmethod
    def get_sent_trades(player):
        """Get trades sent by player"""
        return TradeOffer.objects.filter(
            from_player=player,
            status='pending'
        ).select_related('from_player', 'to_player').order_by('-created_at')

    @staticmethod
    def get_trade_history(player, limit=50):
        """Get trade history"""
        from django.db.models import Q
        return TradeOffer.objects.filter(
            Q(from_player=player) | Q(to_player=player)
        ).exclude(
            status='pending'
        ).select_related('from_player', 'to_player').order_by('-updated_at')[:limit]

    @staticmethod
    def expire_old_trades():
        """Mark expired trades as expired (called by cron/celery)"""
        from django.db import models as django_models

        expired_count = TradeOffer.objects.filter(
            status='pending',
            expires_at__lt=timezone.now()
        ).update(status='expired')

        if expired_count > 0:
            logger.info(f"Expired {expired_count} old trade offers")

        return expired_count
