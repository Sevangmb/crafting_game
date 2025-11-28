from rest_framework import serializers
from ..models import Shop, ShopItem, Transaction, TradeOffer, Material
from .items import MaterialSerializer

class ShopSerializer(serializers.ModelSerializer):
    """Serializer for shops"""
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Shop
        fields = ['id', 'name', 'description', 'icon', 'biome', 
                 'buy_price_multiplier', 'sell_price_multiplier', 'item_count']
    
    def get_item_count(self, obj):
        return obj.items.filter(available=True).count()

class ShopItemSerializer(serializers.ModelSerializer):
    """Serializer for shop items"""
    material = MaterialSerializer(read_only=True)
    effective_buy_price = serializers.IntegerField(read_only=True)
    effective_sell_price = serializers.IntegerField(read_only=True)
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    
    class Meta:
        model = ShopItem
        fields = ['id', 'shop', 'shop_name', 'material', 'base_buy_price', 'base_sell_price',
                 'effective_buy_price', 'effective_sell_price', 'stock', 'available', 'required_level']

class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for transactions"""
    material_name = serializers.CharField(source='material.name', read_only=True, allow_null=True)
    shop_name = serializers.CharField(source='shop.name', read_only=True, allow_null=True)

    class Meta:
        model = Transaction
        fields = ['id', 'transaction_type', 'amount', 'balance_after', 'description',
                 'material', 'material_name', 'shop', 'shop_name', 'timestamp']
        read_only_fields = ['player', 'balance_after', 'timestamp']

class TradeOfferSerializer(serializers.ModelSerializer):
    """Serializer for trade offers"""
    from_player_name = serializers.CharField(source='from_player.user.username', read_only=True)
    to_player_name = serializers.CharField(source='to_player.user.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_expired = serializers.SerializerMethodField()
    offered_items_details = serializers.SerializerMethodField()
    requested_items_details = serializers.SerializerMethodField()

    class Meta:
        model = TradeOffer
        fields = ['id', 'from_player', 'from_player_name', 'to_player', 'to_player_name',
                 'status', 'status_display', 'message', 'offered_items', 'offered_items_details',
                 'offered_money', 'requested_items', 'requested_items_details', 'requested_money',
                 'created_at', 'updated_at', 'expires_at', 'completed_at', 'is_expired']
        read_only_fields = ['from_player', 'status', 'created_at', 'updated_at', 'completed_at']

    def get_is_expired(self, obj):
        return obj.is_expired()

    def get_offered_items_details(self, obj):
        """Get material details for offered items"""
        items = []
        for item in obj.offered_items:
            try:
                material = Material.objects.get(id=item.get('material_id'))
                items.append({
                    'material_id': material.id,
                    'name': material.name,
                    'icon': material.icon,
                    'quantity': item.get('quantity', 1)
                })
            except Material.DoesNotExist:
                pass
        return items

    def get_requested_items_details(self, obj):
        """Get material details for requested items"""
        items = []
        for item in obj.requested_items:
            try:
                material = Material.objects.get(id=item.get('material_id'))
                items.append({
                    'material_id': material.id,
                    'name': material.name,
                    'icon': material.icon,
                    'quantity': item.get('quantity', 1)
                })
            except Material.DoesNotExist:
                pass
        return items
