from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from ..models import Player, Material, Inventory, EquippedItem
from ..serializers import EquippedItemSerializer

class EquipmentViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """Get current equipment"""
        player = request.user.player
        equipped = EquippedItem.objects.filter(player=player)
        serializer = EquippedItemSerializer(equipped, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def equip(self, request):
        """Equip an item"""
        player = request.user.player
        material_id = request.data.get('material_id')
        slot = request.data.get('slot')

        if not material_id or not slot:
            return Response({'error': 'Material ID and slot are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # Check if player has the item
                inventory_item = Inventory.objects.select_for_update().get(player=player, material_id=material_id)
                
                if inventory_item.quantity < 1:
                    return Response({'error': 'Item not found in inventory'}, status=status.HTTP_400_BAD_REQUEST)

                material = inventory_item.material
                
                # Validate slot (optional: check if material is allowed in this slot)
                if material.is_equipment and material.equipment_slot and material.equipment_slot != slot:
                     return Response({'error': f'This item belongs in the {material.equipment_slot} slot'}, status=status.HTTP_400_BAD_REQUEST)

                # Check if slot is already occupied
                existing_item = EquippedItem.objects.filter(player=player, slot=slot).first()
                if existing_item:
                    # Unequip existing item (return to inventory)
                    existing_inv, created = Inventory.objects.get_or_create(
                        player=player, 
                        material=existing_item.material
                    )
                    existing_inv.quantity += 1
                    existing_inv.save()
                    existing_item.delete()

                # Remove from inventory
                inventory_item.quantity -= 1
                if inventory_item.quantity <= 0:
                    inventory_item.delete()
                else:
                    inventory_item.save()

                # Create equipped item
                EquippedItem.objects.create(
                    player=player,
                    material=material,
                    slot=slot
                )

                return Response({'message': 'Item equipped successfully'})

        except Inventory.DoesNotExist:
            return Response({'error': 'Item not found in inventory'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def unequip(self, request):
        """Unequip an item"""
        player = request.user.player
        slot = request.data.get('slot')

        if not slot:
            return Response({'error': 'Slot is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                equipped_item = EquippedItem.objects.select_for_update().get(player=player, slot=slot)
                
                # Return to inventory
                inventory_item, created = Inventory.objects.get_or_create(
                    player=player,
                    material=equipped_item.material
                )
                inventory_item.quantity += 1
                inventory_item.save()
                
                equipped_item.delete()

                return Response({'message': 'Item unequipped successfully'})

        except EquippedItem.DoesNotExist:
            return Response({'error': 'No item equipped in this slot'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
