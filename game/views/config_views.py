"""
Views for game configuration management
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from game.models import GameConfig
from game.serializers import GameConfigSerializer


class GameConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet for game configuration
    - List all configurations
    - Retrieve a specific configuration
    - Create, update, delete configurations (admin only)
    """
    queryset = GameConfig.objects.all()
    serializer_class = GameConfigSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Admin only for create, update, delete"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def all_configs(self, request):
        """
        Get all configurations as a single dictionary
        Returns: {key: parsed_value, ...}
        """
        configs = {}
        for config in GameConfig.objects.all():
            configs[config.key] = config.get_value()
        return Response(configs)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def update_config(self, request, key=None):
        """
        Update a configuration value (admin only)
        """
        try:
            config = GameConfig.objects.get(key=key)
            new_value = request.data.get('value')
            if new_value is not None:
                config.set_value(new_value)
                config.save()
                serializer = self.get_serializer(config)
                return Response(serializer.data)
            return Response(
                {'error': 'Value is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except GameConfig.DoesNotExist:
            return Response(
                {'error': 'Configuration not found'},
                status=status.HTTP_404_NOT_FOUND
            )
