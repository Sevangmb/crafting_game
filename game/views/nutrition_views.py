"""
API endpoints for advanced nutrition system
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from game.models import Player, Material
from game.services.advanced_nutrition_service import AdvancedNutritionService
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_nutrition_status(request, player_id):
    """
    Get player's current nutritional status
    GET /api/players/<player_id>/nutrition/

    Returns:
    - Overall nutrition score
    - Macronutrient stores (proteins, carbs, fats)
    - Vitamin and mineral levels
    - Health effects (immune system, stamina regen, healing rate)
    - Body composition
    - Digesting food count
    - Food poisoning status
    """
    try:
        player = get_object_or_404(Player, id=player_id)

        # Check permission
        if player.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Vous ne pouvez voir que votre propre statut nutritionnel'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get nutrition summary
        summary = AdvancedNutritionService.get_nutrition_summary(player)

        return Response(summary, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error getting nutrition status for player {player_id}: {str(e)}")
        return Response(
            {'error': 'Erreur lors de la récupération du statut nutritionnel'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def consume_food(request, player_id):
    """
    Consume food item from inventory
    POST /api/players/<player_id>/nutrition/consume/

    Body:
    {
        "material_id": 123,
        "quantity_grams": 100  (optional, default 100g)
    }

    Returns:
    - Success/failure message
    - Nutrients consumed
    - Digestion time
    """
    try:
        player = get_object_or_404(Player, id=player_id)

        # Check permission
        if player.user != request.user:
            return Response(
                {'error': 'Vous ne pouvez consommer de la nourriture que pour votre propre personnage'},
                status=status.HTTP_403_FORBIDDEN
            )

        material_id = request.data.get('material_id')
        quantity_grams = request.data.get('quantity_grams', 100)

        if not material_id:
            return Response(
                {'error': 'material_id requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity_grams = float(quantity_grams)
            if quantity_grams <= 0 or quantity_grams > 1000:
                return Response(
                    {'error': 'Quantité invalide (doit être entre 1 et 1000g)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {'error': 'Quantité invalide'},
                status=status.HTTP_400_BAD_REQUEST
            )

        material = get_object_or_404(Material, id=material_id)

        # Check if player has this item in inventory
        from game.models import Inventory
        inventory_item = Inventory.objects.filter(
            player=player,
            material=material
        ).first()

        if not inventory_item or inventory_item.quantity < 1:
            return Response(
                {'error': f"Vous n'avez pas de {material.name} dans votre inventaire"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Consume the food
        result = AdvancedNutritionService.eat_food(player, material, quantity_grams)

        if not result['success']:
            return Response(
                {'error': result['message']},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Remove 1 item from inventory (representing the consumed portion)
        inventory_item.quantity -= 1
        if inventory_item.quantity <= 0:
            inventory_item.delete()
        else:
            inventory_item.save()

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error consuming food for player {player_id}: {str(e)}")
        return Response(
            {'error': 'Erreur lors de la consommation de nourriture'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_player_digestion(request, player_id):
    """
    Manually trigger digestion processing (usually done automatically via tasks)
    POST /api/players/<player_id>/nutrition/digest/

    Returns:
    - Amount of nutrients absorbed
    """
    try:
        player = get_object_or_404(Player, id=player_id)

        # Check permission
        if player.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Permission refusée'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Process digestion
        absorbed = AdvancedNutritionService.process_digestion(player)

        return Response({
            'message': 'Digestion traitée',
            'absorbed': absorbed
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error processing digestion for player {player_id}: {str(e)}")
        return Response(
            {'error': 'Erreur lors du traitement de la digestion'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_player_metabolism(request, player_id):
    """
    Manually trigger metabolism update (usually done automatically via tasks)
    POST /api/players/<player_id>/nutrition/metabolism/

    Returns:
    - Confirmation message
    """
    try:
        player = get_object_or_404(Player, id=player_id)

        # Check permission
        if player.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Permission refusée'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Update metabolism
        AdvancedNutritionService.update_metabolism(player)

        return Response({
            'message': 'Métabolisme mis à jour'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error updating metabolism for player {player_id}: {str(e)}")
        return Response(
            {'error': 'Erreur lors de la mise à jour du métabolisme'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_food_nutrition_info(request, material_id):
    """
    Get detailed nutritional information for a food item
    GET /api/nutrition/food/<material_id>/

    Returns:
    - Complete nutritional profile
    - Macronutrients (proteins, carbs, fats, fiber, water)
    - Vitamins
    - Minerals
    - Digestion time
    - Toxicity info
    """
    try:
        material = get_object_or_404(Material, id=material_id)

        try:
            nutrition = material.nutrition

            return Response({
                'material_name': material.name,
                'macronutrients': {
                    'proteins': nutrition.proteins,
                    'carbohydrates': nutrition.carbohydrates,
                    'fats': nutrition.fats,
                    'fiber': nutrition.fiber,
                    'water': nutrition.water,
                    'calories': nutrition.calories,
                },
                'vitamins': {
                    'a': nutrition.vitamin_a,
                    'b1': nutrition.vitamin_b1,
                    'b2': nutrition.vitamin_b2,
                    'b3': nutrition.vitamin_b3,
                    'b6': nutrition.vitamin_b6,
                    'b12': nutrition.vitamin_b12,
                    'c': nutrition.vitamin_c,
                    'd': nutrition.vitamin_d,
                    'e': nutrition.vitamin_e,
                    'k': nutrition.vitamin_k,
                },
                'minerals': {
                    'calcium': nutrition.calcium,
                    'iron': nutrition.iron,
                    'magnesium': nutrition.magnesium,
                    'phosphorus': nutrition.phosphorus,
                    'potassium': nutrition.potassium,
                    'sodium': nutrition.sodium,
                    'zinc': nutrition.zinc,
                },
                'digestion': {
                    'time_minutes': nutrition.digestion_time,
                    'absorption_rate': nutrition.absorption_rate,
                },
                'quality': {
                    'is_perishable': nutrition.is_perishable,
                    'freshness_decay_rate': nutrition.freshness_decay_rate,
                },
                'safety': {
                    'is_toxic': nutrition.is_toxic,
                    'toxicity_level': nutrition.toxicity_level,
                }
            }, status=status.HTTP_200_OK)

        except:
            return Response(
                {'error': f"{material.name} n'a pas de profil nutritionnel"},
                status=status.HTTP_404_NOT_FOUND
            )

    except Exception as e:
        logger.error(f"Error getting food nutrition info for material {material_id}: {str(e)}")
        return Response(
            {'error': 'Erreur lors de la récupération des informations nutritionnelles'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
