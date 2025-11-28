from rest_framework import serializers
from .models import (
    Material, Weapon, Clothing, Recipe, RecipeIngredient, Player, Inventory, MapCell, CellMaterial,
    GatheringLog, CraftingLog, Workstation, PlayerWorkstation,
    Skill, PlayerSkill, TalentNode, PlayerTalent, GameConfig, EquippedItem,
    Achievement, PlayerAchievement, BuildingType, BuildingRecipe, Building,
    DroppedItem, Mob, Vehicle, Shop, ShopItem, Transaction, Quest, PlayerQuest, DynamicEvent,
    TradeOffer, Leaderboard
)

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


class MobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mob
        fields = '__all__'
from django.contrib.auth.models import User

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'

class WorkstationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workstation
        fields = '__all__'

class RecipeIngredientSerializer(serializers.ModelSerializer):
    material = MaterialSerializer(read_only=True)
    material_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'material', 'material_id', 'quantity']

class RecipeIngredientAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = ['id', 'recipe', 'material', 'quantity']

class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True, read_only=True)
    result_material = MaterialSerializer(read_only=True)
    required_workstation = WorkstationSerializer(read_only=True)
    energy_cost = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_energy_cost(self, obj):
        # Energy cost for crafting loaded from GameConfig
        try:
            cfg = GameConfig.get_config('crafting_config', {})
            return cfg.get('energy_cost_per_craft', 2)
        except Exception:
            return 2

class RecipeAdminSerializer(serializers.ModelSerializer):
    # writable foreign keys
    result_material_id = serializers.IntegerField(write_only=True, required=True)
    required_workstation_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'description', 'icon', 'result_material_id', 'result_quantity', 'required_workstation_id']

class PlayerWorkstationSerializer(serializers.ModelSerializer):
    workstation = WorkstationSerializer(read_only=True)

    class Meta:
        model = PlayerWorkstation
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class EquippedItemSerializer(serializers.ModelSerializer):
    material = MaterialSerializer(read_only=True)

    class Meta:
        model = EquippedItem
        fields = ['id', 'slot', 'material']

class InventorySerializer(serializers.ModelSerializer):
    material = MaterialSerializer()
    category = serializers.CharField(source='material.category', read_only=True)
    durability_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Inventory
        fields = ['id', 'material', 'quantity', 'category', 'durability_current', 'durability_max', 'durability_percentage']
        read_only_fields = ['player']

    def get_durability_percentage(self, obj):
        if obj.durability_max == 0:
            return 100
        return int((obj.durability_current / obj.durability_max) * 100) if obj.durability_max > 0 else 100

class PlayerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    inventory = InventorySerializer(many=True, read_only=True)
    workstations = PlayerWorkstationSerializer(many=True, read_only=True)
    equipped_items = EquippedItemSerializer(many=True, read_only=True)
    current_carry_weight = serializers.FloatField(read_only=True)
    effective_carry_capacity = serializers.FloatField(read_only=True)
    is_overencumbered = serializers.BooleanField(read_only=True)

    class Meta:
        model = Player
        fields = ['id', 'user', 'current_x', 'current_y', 'grid_x', 'grid_y',
                 'energy', 'max_energy', 'health', 'max_health',
                 'hunger', 'max_hunger', 'thirst', 'max_thirst', 'radiation',
                 'strength', 'agility', 'intelligence', 'luck',
                 'level', 'experience', 'money', 'credit_card_balance', 'inventory',
                 'workstations', 'equipped_items',
                 'total_defense', 'total_attack', 'total_speed_bonus',
                 'current_carry_weight', 'effective_carry_capacity', 'is_overencumbered']



class CellMaterialSerializer(serializers.ModelSerializer):
    material = MaterialSerializer(read_only=True)

    class Meta:
        model = CellMaterial
        fields = '__all__'

class DroppedItemSerializer(serializers.ModelSerializer):
    material = MaterialSerializer(read_only=True)
    dropped_by_name = serializers.CharField(source='dropped_by.user.username', read_only=True, allow_null=True)

    class Meta:
        model = DroppedItem
        fields = ['id', 'material', 'quantity', 'durability_current', 'durability_max',
                  'dropped_by', 'dropped_by_name', 'dropped_at']

class MapCellSerializer(serializers.ModelSerializer):
    materials = CellMaterialSerializer(many=True, read_only=True)
    dropped_items = DroppedItemSerializer(many=True, read_only=True)
    buildings = serializers.SerializerMethodField()

    class Meta:
        model = MapCell
        fields = '__all__'

    def get_buildings(self, obj):
        """Get buildings on this cell"""
        from game.services import building_service
        return building_service.get_cell_buildings(obj)

class GatheringLogSerializer(serializers.ModelSerializer):
    material = MaterialSerializer(read_only=True)

    class Meta:
        model = GatheringLog
        fields = '__all__'

class CraftingLogSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer(read_only=True)

    class Meta:
        model = CraftingLog
        fields = '__all__'

# --- Skills & Talents ---

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'code', 'name', 'description']

class PlayerSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)

    class Meta:
        model = PlayerSkill
        fields = ['id', 'skill', 'level', 'xp', 'xp_to_next', 'total_xp']

class TalentNodeSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)

    class Meta:
        model = TalentNode
        fields = ['id', 'skill', 'code', 'name', 'description', 'tier', 'xp_required', 'prereq_codes', 'effect_type', 'effect_value', 'params']

class PlayerTalentSerializer(serializers.ModelSerializer):
    talent_node = TalentNodeSerializer(read_only=True)

    class Meta:
        model = PlayerTalent
        fields = ['id', 'talent_node', 'unlocked_at']

# --- Game Configuration ---

class GameConfigSerializer(serializers.ModelSerializer):
    """Serializer for game configuration with automatic JSON parsing"""
    parsed_value = serializers.SerializerMethodField()

    class Meta:
        model = GameConfig
        fields = ['id', 'key', 'value', 'parsed_value', 'description']

    def get_parsed_value(self, obj):
        """Return the parsed JSON value"""
        return obj.get_value()

# --- Achievements ---

class AchievementSerializer(serializers.ModelSerializer):
    """Serializer for achievements"""
    class Meta:
        model = Achievement
        fields = [
            'id', 'name', 'description', 'icon', 'category',
            'requirement_type', 'requirement_value', 'requirement_target',
            'reward_xp', 'hidden', 'created_at'
        ]

class PlayerAchievementSerializer(serializers.ModelSerializer):
    """Serializer for player achievement progress"""
    achievement = AchievementSerializer(read_only=True)
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = PlayerAchievement
        fields = ['id', 'achievement', 'progress', 'completed', 'completed_at', 'progress_percentage']

    def get_progress_percentage(self, obj):
        """Calculate progress percentage"""
        if obj.achievement.requirement_value == 0:
            return 100 if obj.completed else 0
        return min(100, int((obj.progress / obj.achievement.requirement_value) * 100))



# --- Building Serializers ---

class BuildingRecipeSerializer(serializers.ModelSerializer):
    material = MaterialSerializer(read_only=True)

    class Meta:
        model = BuildingRecipe
        fields = ['id', 'material', 'quantity']


class BuildingTypeSerializer(serializers.ModelSerializer):
    recipe_materials = BuildingRecipeSerializer(many=True, read_only=True)

    class Meta:
        model = BuildingType
        fields = '__all__'


class BuildingSerializer(serializers.ModelSerializer):
    building_type = BuildingTypeSerializer(read_only=True)
    cell_info = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Building
        fields = '__all__'

    def get_cell_info(self, obj):
        return {
            'id': obj.cell.id,
            'grid_x': obj.cell.grid_x,
            'grid_y': obj.cell.grid_y,
            'biome': obj.cell.biome,
        }

    def get_owner(self, obj):
        return obj.player.user.username


# --- Economy Serializers ---

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


class QuestSerializer(serializers.ModelSerializer):
    """Serializer for quests"""
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    type_display = serializers.CharField(source='get_quest_type_display', read_only=True)

    class Meta:
        model = Quest
        fields = ['id', 'name', 'description', 'story_text', 'icon', 'quest_type', 'type_display',
                 'difficulty', 'difficulty_display', 'required_level', 'requirements',
                 'reward_xp', 'reward_money', 'reward_items', 'is_repeatable',
                 'cooldown_hours', 'start_npc', 'prerequisite_quest']


class PlayerQuestSerializer(serializers.ModelSerializer):
    """Serializer for player quests with progress"""
    quest = QuestSerializer(read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PlayerQuest
        fields = ['id', 'quest', 'status', 'status_display', 'progress', 'progress_percentage',
                 'accepted_at', 'completed_at', 'can_repeat_at', 'times_completed']

    def get_progress_percentage(self, obj):
        return obj.progress_percentage()


class DynamicEventSerializer(serializers.ModelSerializer):
    """Serializer for dynamic events"""
    type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    cell_info = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    participant_count = serializers.SerializerMethodField()

    class Meta:
        model = DynamicEvent
        fields = ['id', 'name', 'description', 'icon', 'event_type', 'type_display',
                 'cell_info', 'rewards', 'started_at', 'expires_at', 'is_active',
                 'is_expired', 'max_participants', 'participant_count']

    def get_cell_info(self, obj):
        return {
            'grid_x': obj.cell.grid_x,
            'grid_y': obj.cell.grid_y,
            'biome': obj.cell.biome
        }

    def get_is_expired(self, obj):
        return obj.is_expired()

    def get_participant_count(self, obj):
        return obj.participants.count()


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


class LeaderboardSerializer(serializers.ModelSerializer):
    """Serializer for leaderboard entries"""
    player_name = serializers.CharField(source='player.user.username', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = Leaderboard
        fields = ['id', 'category', 'category_display', 'player', 'player_name',
                 'score', 'rank', 'metadata', 'last_updated']
        read_only_fields = ['rank', 'score', 'last_updated']

