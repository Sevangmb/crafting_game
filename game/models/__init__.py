from .items import Material, Weapon, Clothing, DroppedItem
from .vehicles import (
    VehicleType, VehiclePart, PlayerVehicle, PlayerVehiclePart,
    VehicleMaintenanceLog, FuelStation, Garage
)
# Keep old Vehicle for backwards compatibility during migration
from .items import Vehicle
from .world import MapCell, CellMaterial, GatheringLog
from .crafting import Workstation, Recipe, RecipeIngredient, CraftingLog
from .buildings import BuildingType, BuildingRecipe, Building, House
from .combat import Mob, CombatLog
from .economy import Shop, ShopItem, Bank, Transaction, TradeOffer
from .skills import Skill, TalentNode
from .achievements import Achievement, PlayerAchievement
from .quests import Quest, PlayerQuest
from .events import DynamicEvent
from .leaderboard import Leaderboard
from .config import GameConfig
from .player import Player, PlayerWorkstation, Inventory, EquippedItem, PlayerSkill, PlayerTalent
# PlayerVehicle is now imported from vehicles module
from .nutrition import NutritionalProfile, PlayerNutrition, DigestingFood
from .health import BodyPart, PlayerBodyPart, PlayerHealthStatus, Disease, PlayerDisease, MedicalItem
