from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from game.models import Player, Bank, Transaction, MapCell
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_banks(request):
    """Get banks available at player's current location"""
    try:
        player = Player.objects.get(user=request.user)
        current_cell = MapCell.objects.filter(
            grid_x=player.grid_x,
            grid_y=player.grid_y
        ).first()

        if not current_cell:
            return Response({'banks': []})

        banks = Bank.objects.filter(cell=current_cell)
        banks_data = [{
            'id': bank.id,
            'name': bank.name,
            'description': bank.description,
            'icon': bank.icon,
            'deposit_fee_percent': bank.deposit_fee_percent,
            'withdrawal_fee_percent': bank.withdrawal_fee_percent,
        } for bank in banks]

        return Response({
            'banks': banks_data,
            'player_cash': player.money,
            'player_card_balance': player.credit_card_balance
        })

    except Player.DoesNotExist:
        return Response({'error': 'Player not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error fetching banks: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deposit_money(request):
    """Deposit cash into credit card account"""
    try:
        amount = int(request.data.get('amount', 0))
        bank_id = request.data.get('bank_id')

        if amount <= 0:
            return Response({'error': 'Le montant doit être positif'}, status=status.HTTP_400_BAD_REQUEST)

        player = Player.objects.get(user=request.user)

        # Check if player has enough cash
        if player.money < amount:
            return Response({
                'error': f'Pas assez d\'argent liquide. Vous avez {player.money}₡'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get bank and calculate fee
        bank = Bank.objects.get(id=bank_id)
        fee = int(amount * (bank.deposit_fee_percent / 100))
        net_amount = amount - fee

        with transaction.atomic():
            # Deduct cash
            player.money -= amount
            # Add to card (after fee)
            player.credit_card_balance += net_amount
            player.save()

            # Create transaction record
            Transaction.objects.create(
                player=player,
                transaction_type='deposit',
                amount=-amount,  # Negative because cash decreases
                balance_after=player.money,
                description=f'Dépôt de {amount}₡ à {bank.name} (frais: {fee}₡)'
            )

        return Response({
            'success': True,
            'message': f'Dépôt de {amount}₡ effectué (frais: {fee}₡). Montant crédité: {net_amount}₡',
            'player_cash': player.money,
            'player_card_balance': player.credit_card_balance,
            'fee': fee,
            'net_amount': net_amount
        })

    except Bank.DoesNotExist:
        return Response({'error': 'Banque introuvable'}, status=status.HTTP_404_NOT_FOUND)
    except Player.DoesNotExist:
        return Response({'error': 'Joueur introuvable'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error depositing money: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdraw_money(request):
    """Withdraw money from credit card to cash"""
    try:
        amount = int(request.data.get('amount', 0))
        bank_id = request.data.get('bank_id')

        if amount <= 0:
            return Response({'error': 'Le montant doit être positif'}, status=status.HTTP_400_BAD_REQUEST)

        player = Player.objects.get(user=request.user)

        # Get bank and calculate fee
        bank = Bank.objects.get(id=bank_id)
        fee = int(amount * (bank.withdrawal_fee_percent / 100))
        total_needed = amount + fee

        # Check if player has enough on card
        if player.credit_card_balance < total_needed:
            return Response({
                'error': f'Solde insuffisant sur la carte. Vous avez {player.credit_card_balance}₡ (frais: {fee}₡)'
            }, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Deduct from card (amount + fee)
            player.credit_card_balance -= total_needed
            # Add cash
            player.money += amount
            player.save()

            # Create transaction record
            Transaction.objects.create(
                player=player,
                transaction_type='withdrawal',
                amount=amount,  # Positive because cash increases
                balance_after=player.money,
                description=f'Retrait de {amount}₡ à {bank.name} (frais: {fee}₡)'
            )

        return Response({
            'success': True,
            'message': f'Retrait de {amount}₡ effectué (frais: {fee}₡)',
            'player_cash': player.money,
            'player_card_balance': player.credit_card_balance,
            'fee': fee
        })

    except Bank.DoesNotExist:
        return Response({'error': 'Banque introuvable'}, status=status.HTTP_404_NOT_FOUND)
    except Player.DoesNotExist:
        return Response({'error': 'Joueur introuvable'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error withdrawing money: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
