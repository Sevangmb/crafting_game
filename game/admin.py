from django.contrib import admin
from .models import Material, Recipe, RecipeIngredient, Player, Inventory, MapCell, CellMaterial, GatheringLog, CraftingLog, Workstation, PlayerWorkstation, Achievement, PlayerAchievement, BuildingType, Building, BuildingRecipe, Vehicle, Weapon, Clothing, PlayerVehicle, EquippedItem, Skill, PlayerSkill, TalentNode, PlayerTalent, GameConfig, Mob, CombatLog, House, DroppedItem, Quest, PlayerQuest, DynamicEvent, TradeOffer, Leaderboard

class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1

class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInline]
    list_display = ['name', 'result_material', 'result_quantity', 'required_workstation']
    list_filter = ['required_workstation']

class CellMaterialInline(admin.TabularInline):
    model = CellMaterial
    extra = 1

class MapCellAdmin(admin.ModelAdmin):
    inlines = [CellMaterialInline]
    list_display = ['grid_x', 'grid_y', 'biome', 'last_regenerated']

class AchievementAdmin(admin.ModelAdmin):
    list_display = ['icon', 'name', 'category', 'requirement_type', 'requirement_value', 'reward_xp', 'hidden']
    list_filter = ['category', 'requirement_type', 'hidden']
    search_fields = ['name', 'description']

class PlayerAchievementAdmin(admin.ModelAdmin):
    list_display = ['player', 'achievement', 'progress', 'completed', 'completed_at']
    list_filter = ['completed', 'achievement__category']
    search_fields = ['player__user__username', 'achievement__name']
    readonly_fields = ['completed_at']

class BuildingRecipeInline(admin.TabularInline):
    model = BuildingRecipe
    extra = 1

class BuildingTypeAdmin(admin.ModelAdmin):
    inlines = [BuildingRecipeInline]
    list_display = ['icon', 'name', 'category', 'required_level', 'construction_time', 'energy_regeneration_bonus', 'storage_bonus']
    list_filter = ['category']

class BuildingAdmin(admin.ModelAdmin):
    list_display = ['player', 'building_type', 'cell', 'status', 'construction_progress', 'construction_started_at']
    list_filter = ['status', 'building_type__category']
    search_fields = ['player__user__username', 'building_type__name']

class GameConfigAdmin(admin.ModelAdmin):
    list_display = ['key', 'value_preview', 'description', 'last_modified']
    list_filter = ['last_modified']
    search_fields = ['key', 'description', 'value']
    ordering = ['key']
    readonly_fields = ['last_modified']

    fieldsets = (
        ('Configuration', {
            'fields': ('key', 'value', 'description')
        }),
        ('Metadata', {
            'fields': ('last_modified',),
            'classes': ('collapse',)
        }),
    )

    def value_preview(self, obj):
        """Show a preview of the value (truncated if too long)"""
        value = str(obj.value) if obj.value else ''
        if len(value) > 50:
            return value[:50] + '...'
        return value
    value_preview.short_description = 'Value'

    # Add categorized sections for better organization
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs

    class Media:
        css = {
            'all': ('admin/css/gameconfig_admin.css',)
        }

admin.site.register(Material)
admin.site.register(Workstation)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Player)
admin.site.register(Inventory)
admin.site.register(PlayerWorkstation)
admin.site.register(MapCell, MapCellAdmin)
admin.site.register(GatheringLog)
admin.site.register(CraftingLog)
admin.site.register(Achievement, AchievementAdmin)
admin.site.register(PlayerAchievement, PlayerAchievementAdmin)
admin.site.register(BuildingType, BuildingTypeAdmin)
admin.site.register(Building, BuildingAdmin)
admin.site.register(Vehicle)
admin.site.register(Weapon)
admin.site.register(Clothing)
admin.site.register(PlayerVehicle)
admin.site.register(EquippedItem)
admin.site.register(Skill)
admin.site.register(PlayerSkill)
admin.site.register(TalentNode)
admin.site.register(PlayerTalent)
admin.site.register(GameConfig, GameConfigAdmin)
admin.site.register(Mob)
admin.site.register(CombatLog)
admin.site.register(House)
admin.site.register(DroppedItem)


# Quest System Admin
class QuestAdmin(admin.ModelAdmin):
    list_display = ['icon', 'name', 'quest_type', 'difficulty', 'required_level', 'is_repeatable', 'is_active']
    list_filter = ['quest_type', 'difficulty', 'is_repeatable', 'is_active']
    search_fields = ['name', 'description', 'story_text']
    fieldsets = (
        ('Informations de Base', {
            'fields': ('name', 'description', 'story_text', 'icon')
        }),
        ('Propriétés', {
            'fields': ('quest_type', 'difficulty', 'required_level', 'prerequisite_quest')
        }),
        ('Objectifs', {
            'fields': ('requirements',),
            'description': 'Format JSON: {"gather": [{"material_id": 1, "quantity": 10}], ...}'
        }),
        ('Récompenses', {
            'fields': ('reward_xp', 'reward_money', 'reward_items'),
            'description': 'reward_items format: [{"material_id": 1, "quantity": 5}]'
        }),
        ('Répétabilité', {
            'fields': ('is_repeatable', 'cooldown_hours', 'is_active')
        }),
        ('NPC', {
            'fields': ('start_npc',),
            'classes': ('collapse',)
        })
    )


class PlayerQuestAdmin(admin.ModelAdmin):
    list_display = ['player', 'quest', 'status', 'progress_percentage', 'accepted_at', 'completed_at', 'times_completed']
    list_filter = ['status', 'quest__difficulty', 'quest__quest_type']
    search_fields = ['player__user__username', 'quest__name']
    readonly_fields = ['accepted_at', 'completed_at']

    def progress_percentage(self, obj):
        return f"{obj.progress_percentage()}%"
    progress_percentage.short_description = 'Progression'


class DynamicEventAdmin(admin.ModelAdmin):
    list_display = ['icon', 'name', 'event_type', 'cell_location', 'is_active', 'started_at', 'expires_at']
    list_filter = ['event_type', 'is_active']
    search_fields = ['name', 'description']
    filter_horizontal = ['participants']

    def cell_location(self, obj):
        return f"({obj.cell.grid_x}, {obj.cell.grid_y})"
    cell_location.short_description = 'Position'


admin.site.register(Quest, QuestAdmin)
admin.site.register(PlayerQuest, PlayerQuestAdmin)
admin.site.register(DynamicEvent, DynamicEventAdmin)


# Trading System Admin
class TradeOfferAdmin(admin.ModelAdmin):
    list_display = ['id', 'from_player_name', 'to_player_name', 'status', 'offered_money', 'requested_money', 'created_at', 'expires_at']
    list_filter = ['status', 'created_at', 'expires_at']
    search_fields = ['from_player__user__username', 'to_player__user__username', 'message']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    fieldsets = (
        ('Joueurs', {
            'fields': ('from_player', 'to_player')
        }),
        ('Offre', {
            'fields': ('offered_items', 'offered_money'),
            'description': 'Format JSON: [{"material_id": 1, "quantity": 10}]'
        }),
        ('Demande', {
            'fields': ('requested_items', 'requested_money'),
            'description': 'Format JSON: [{"material_id": 1, "quantity": 10}]'
        }),
        ('Status et Temps', {
            'fields': ('status', 'message', 'created_at', 'updated_at', 'expires_at', 'completed_at')
        })
    )

    def from_player_name(self, obj):
        return obj.from_player.user.username
    from_player_name.short_description = 'De'

    def to_player_name(self, obj):
        return obj.to_player.user.username
    to_player_name.short_description = 'Vers'


# Leaderboard System Admin
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ['rank', 'player_name', 'category', 'score', 'last_updated']
    list_filter = ['category', 'last_updated']
    search_fields = ['player__user__username']
    readonly_fields = ['last_updated']
    ordering = ['category', 'rank']

    def player_name(self, obj):
        return obj.player.user.username
    player_name.short_description = 'Joueur'


admin.site.register(TradeOffer, TradeOfferAdmin)
admin.site.register(Leaderboard, LeaderboardAdmin)
