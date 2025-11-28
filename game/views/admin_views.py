"""
Admin ViewSets for Mobs, Vehicles, Weapons and Clothing
"""
from rest_framework import viewsets, permissions
from ..models import Mob, Vehicle, Weapon, Clothing
from ..serializers import MobSerializer, VehicleSerializer, WeaponSerializer, ClothingSerializer


class MobViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing mobs (admin only for create/update/delete)
    """
    queryset = Mob.objects.all()
    serializer_class = MobSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """
        Allow read for all authenticated users, but write only for staff
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]


class VehicleViewSet(viewsets.ModelViewSet):
    """Admin ViewSet for vehicle types"""
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]


class WeaponViewSet(viewsets.ModelViewSet):
    """Admin ViewSet for weapons"""
    queryset = Weapon.objects.all()
    serializer_class = WeaponSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]


class ClothingViewSet(viewsets.ModelViewSet):
    """Admin ViewSet for clothing"""
    queryset = Clothing.objects.all()
    serializer_class = ClothingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
