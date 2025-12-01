from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MaterialViewSet, RecipeViewSet, PlayerViewSet, InventoryViewSet, MapCellViewSet, CraftingViewSet, WorkstationViewSet, PlayerWorkstationViewSet, RecipeIngredientViewSet
from .views.config_views import GameConfigViewSet
from .views.achievement_views import AchievementViewSet
from .views.building_views import BuildingTypeViewSet, BuildingViewSet
from .views.poi_views import POIViewSet
from .views.admin_views import MobViewSet, VehicleViewSet, WeaponViewSet, ClothingViewSet
from .views.shop_views import ShopViewSet, TransactionViewSet
from .views.quest_views import QuestViewSet, DynamicEventViewSet
from .views.trading_views import TradeViewSet
from .views.leaderboard_views import LeaderboardViewSet
from .views.biome_views import BiomeViewSet
from .views.encounter_views import EncounterViewSet
from .views import combat_views, vehicle_views, upload_views, bank_views, nutrition_views, health_views, character_sheet_views
from . import views

router = DefaultRouter()
router.register(r'materials', views.MaterialViewSet)
router.register(r'recipes', views.RecipeViewSet)
router.register(r'recipe-ingredients', views.RecipeIngredientViewSet)
router.register(r'players', views.PlayerViewSet)
router.register(r'inventory', views.InventoryViewSet, basename='inventory')
router.register(r'map', views.MapCellViewSet, basename='map')
router.register(r'crafting', views.CraftingViewSet, basename='crafting')
router.register(r'config', views.GameConfigViewSet)
router.register(r'workstations', views.WorkstationViewSet)
router.register(r'player-workstations', views.PlayerWorkstationViewSet, basename='player-workstations')
router.register(r'equipment', views.EquipmentViewSet, basename='equipment')
router.register(r'achievements', AchievementViewSet, basename='achievements')
router.register(r'building-types', BuildingTypeViewSet, basename='building-types')
router.register(r'buildings', BuildingViewSet, basename='buildings')
router.register(r'poi', POIViewSet, basename='poi')
router.register(r'mobs', MobViewSet, basename='mobs')
router.register(r'vehicle-types', VehicleViewSet, basename='vehicle-types')
router.register(r'weapons', WeaponViewSet, basename='weapons')
router.register(r'clothing', ClothingViewSet, basename='clothing')
router.register(r'shops', ShopViewSet, basename='shops')
router.register(r'transactions', TransactionViewSet, basename='transactions')
router.register(r'quests', QuestViewSet, basename='quests')
router.register(r'events', DynamicEventViewSet, basename='events')
router.register(r'trades', TradeViewSet, basename='trades')
router.register(r'leaderboards', LeaderboardViewSet, basename='leaderboards')
router.register(r'biomes', BiomeViewSet, basename='biomes')
router.register(r'encounters', EncounterViewSet, basename='encounters')

urlpatterns = [
    path('', include(router.urls)),
    
    # Combat endpoints
    path('combat/start/', combat_views.start_combat, name='combat-start'),
    path('combat/action/', combat_views.combat_action, name='combat-action'),
    path('combat/history/', combat_views.combat_history, name='combat-history'),
    path('combat/search/', combat_views.search_for_mob, name='combat-search'),

    # Vehicle endpoints
    path('vehicles/', vehicle_views.get_vehicles, name='get-vehicles'),
    path('vehicles/<int:vehicle_id>/equip/', vehicle_views.equip_vehicle, name='equip-vehicle'),
    path('vehicles/unequip/', vehicle_views.unequip_vehicle, name='unequip-vehicle'),
    
    # Upload endpoints
    path('upload/icon/', upload_views.upload_icon, name='upload-icon'),

    # Bank endpoints
    path('banks/current/', bank_views.get_current_banks, name='get-current-banks'),
    path('banks/deposit/', bank_views.deposit_money, name='deposit-money'),
    path('banks/withdraw/', bank_views.withdraw_money, name='withdraw-money'),

    # Nutrition endpoints
    path('players/<int:player_id>/nutrition/', nutrition_views.get_nutrition_status, name='nutrition-status'),
    path('players/<int:player_id>/nutrition/consume/', nutrition_views.consume_food, name='nutrition-consume'),
    path('players/<int:player_id>/nutrition/digest/', nutrition_views.process_player_digestion, name='nutrition-digest'),
    path('players/<int:player_id>/nutrition/metabolism/', nutrition_views.update_player_metabolism, name='nutrition-metabolism'),
    path('nutrition/food/<int:material_id>/', nutrition_views.get_food_nutrition_info, name='food-nutrition-info'),

    # Health endpoints
    path('health/status/', health_views.get_health_status, name='health-status'),
    path('health/body-parts/', health_views.get_body_parts, name='health-body-parts'),
    path('health/diseases/', health_views.get_diseases, name='health-diseases'),
    path('health/diseases/all/', health_views.list_all_diseases, name='health-diseases-all'),
    path('health/diseases/contract/', health_views.infect_disease, name='health-disease-contract'),
    path('health/bandage/', health_views.use_bandage, name='health-bandage'),
    path('health/splint/', health_views.use_splint, name='health-splint'),
    path('health/heal/', health_views.heal_part, name='health-heal'),
    path('health/damage/', health_views.damage_part, name='health-damage'),

    # Character Sheet endpoints (SCUM-style comprehensive character info)
    path('character/sheet/', character_sheet_views.get_character_sheet, name='character-sheet'),
    path('character/metabolism/', character_sheet_views.get_metabolism_details, name='character-metabolism'),
    path('character/eat/', character_sheet_views.consume_food, name='character-eat'),
    path('character/drink/', character_sheet_views.drink, name='character-drink'),
    path('character/bathroom/', character_sheet_views.bathroom, name='character-bathroom'),
    path('character/metabolism/update/', character_sheet_views.update_metabolism, name='character-metabolism-update'),
    path('character/health-display/', character_sheet_views.get_health_display, name='character-health-display'),

    # Time endpoint
    path('time/', views.time_views.get_game_time, name='game-time'),
]
