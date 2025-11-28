"""
Biome Views

API endpoints for biome information.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from game.services.biome_service import BiomeService
from game.models import Player


class BiomeViewSet(viewsets.ViewSet):
    """ViewSet for biome information"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def list_all(self, request):
        """Get information about all biomes"""
        try:
            biomes = BiomeService.get_all_biomes()
            return Response(biomes)
        except Exception as e:
            return Response(
                {'error': f'Failed to fetch biomes: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get detailed information about the player's current biome"""
        try:
            player = Player.objects.get(user=request.user)
            
            # Get current biome
            biome = BiomeService.get_biome_at_location(
                player.current_y,
                player.current_x,
                player.grid_x,
                player.grid_y
            )
            
            # Get biome details
            biome_info = BiomeService.get_biome_details(biome)
            
            # Get dangers
            dangers = BiomeService.get_biome_dangers(biome)
            
            # Check environmental damage
            damage_info = BiomeService.check_environmental_damage(player, biome)
            
            # Get ambient description
            ambient = BiomeService.get_biome_ambient_description(biome)
            
            return Response({
                'biome': biome,
                'info': biome_info,
                'dangers': dangers,
                'environmental_damage': damage_info,
                'ambient': ambient,
            })
        except Player.DoesNotExist:
            return Response(
                {'error': 'Player not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to fetch biome info: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def details(self, request):
        """Get details about a specific biome"""
        biome_code = request.query_params.get('biome')
        
        if not biome_code:
            return Response(
                {'error': 'Biome parameter required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            biome_info = BiomeService.get_biome_details(biome_code)
            dangers = BiomeService.get_biome_dangers(biome_code)
            difficulty = BiomeService.get_biome_difficulty(biome_code)
            
            return Response({
                'biome': biome_code,
                'info': biome_info,
                'dangers': dangers,
                'difficulty': difficulty,
            })
        except Exception as e:
            return Response(
                {'error': f'Failed to fetch biome details: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
