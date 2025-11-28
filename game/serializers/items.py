from rest_framework import serializers
from ..models import Material, Weapon, Clothing, Vehicle, EquippedItem, DroppedItem

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'

class WeaponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weapon
        fields = '__all__'

class ClothingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clothing
        fields = '__all__'

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'

class EquippedItemSerializer(serializers.ModelSerializer):
    material = MaterialSerializer(read_only=True)

    class Meta:
        model = EquippedItem
        fields = ['id', 'slot', 'material']

class DroppedItemSerializer(serializers.ModelSerializer):
    material = MaterialSerializer(read_only=True)
    dropped_by_name = serializers.CharField(source='dropped_by.user.username', read_only=True, allow_null=True)

    class Meta:
        model = DroppedItem
        fields = ['id', 'material', 'quantity', 'durability_current', 'durability_max',
                  'dropped_by', 'dropped_by_name', 'dropped_at']
