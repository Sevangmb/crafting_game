import random
from ..models import MapCell, CellMaterial, Material, GatheringLog, Inventory
from ..resource_generator import get_biome_from_coordinates, get_smart_resources, get_location_description_smart
from ..osm_utils import fetch_osm_features
from . import player_service
from .survival_service import SurvivalService
from .durability_service import DurabilityService
from .quest_service import QuestService
from ..utils.config_helper import GameSettings
from .osm_biome_service import detect_biome_from_osm, get_osm_context

# Import extracted services to expose them
from .gathering_service import gather_material
from .hunting_service import hunt_at_location
from .scavenging_service import scavenge_location

def populate_cell_materials(cell):
    """Populate cell with materials using smart resource generation"""
    # Fetch OSM features to refine biome and resource hints
    features = []
    try:
        features = fetch_osm_features(cell.center_lat, cell.center_lon, radius=100)
        print(f"DEBUG: Fetched {len(features)} OSM features for cell ({cell.grid_x}, {cell.grid_y})")
    except Exception as e:
        print(f"DEBUG: OSM fetch failed in populate_cell_materials: {str(e)}")
        features = []

    # Use centralized OSM biome detection
    osm_biome = detect_biome_from_osm(features) if features else None
    osm_context = get_osm_context(features) if features else {}

    # Extract context flags
    has_residential = osm_context.get('has_residential', False)
    has_water = osm_context.get('has_water', False)
    has_forest = osm_context.get('has_forest', False)
    has_mountain = osm_context.get('has_mountain', False)

    # Extract feature categories for later use
    cats_set = set()
    for feat in features:
        for key, value in feat.get('tags', {}).items():
            cats_set.add(f"{key}:{value}")
            cats_set.add(key)

    # Apply OSM biome if detected (OSM has ABSOLUTE PRIORITY)
    if osm_biome:
        original_biome = cell.biome
        cell.biome = osm_biome
        print(f"[OSM] Changed biome from '{original_biome}' to '{osm_biome}' based on real-world data")
        print(f"   Location: ({cell.center_lat:.4f}, {cell.center_lon:.4f})")
    else:
        print(f"[INFO] No OSM biome detected, keeping procedural biome: '{cell.biome}'")

    # Store OSM features for future reference
    cell.osm_features = features
    cell.save()
    # After setting biome, automatically create a house if residential area detected
    if has_residential:
        try:
            from ..services.house_service import create_house
            from ..models import Player
            owner = Player.objects.first()
            if owner:
                house, created = create_house(owner, cell)
                if created:
                    print(f"DEBUG: Created house for player {owner.user.username} at ({cell.grid_x}, {cell.grid_y})")
        except Exception as e:
            print(f"DEBUG: Failed to create house: {str(e)}")



    # After adjusting biome, check if we need to regenerate features with new biome context
    if has_water or has_forest or has_mountain:
        # Re-fetch with potentially different radius for water/forest detection
        try:
            features = fetch_osm_features(cell.center_lat, cell.center_lon, radius=100)
            cell.osm_features = features
            cell.save()
        except Exception as e:
            print(f"DEBUG: Failed to re-fetch OSM features after biome adjustment: {str(e)}")
            features = cell.osm_features or []

    # Use smart resource system based on coordinates (with possibly adjusted biome)
    smart_materials = get_smart_resources(
        cell.center_lat,
        cell.center_lon,
        cell.grid_x,
        cell.grid_y,
        cell.biome,
        osm_context={
            'has_water': has_water,
            'has_forest': has_forest,
            'urban': ('urban' in cats_set),
        }
    )

    print(f"DEBUG: Smart materials before OSM guarantees: {smart_materials}")
    print(f"DEBUG: OSM context - has_water: {has_water}, has_forest: {has_forest}, urban: {'urban' in cats_set}")

    # Ensure biome-specific guarantees from OSM hints
    if has_water:
        old_fish = smart_materials.get('Poisson', 0)
        smart_materials['Poisson'] = max(old_fish, 20)
        print(f"DEBUG: Set Poisson guarantee: {old_fish} -> {smart_materials['Poisson']}")
    if has_forest:
        old_wood = smart_materials.get('Bois', 0)
        old_meat = smart_materials.get('Viande', 0)
        smart_materials['Bois'] = max(old_wood, 40)
        smart_materials['Viande'] = max(old_meat, 10)
        print(f"DEBUG: Set forest guarantees - Bois: {old_wood} -> {smart_materials['Bois']}, Viande: {old_meat} -> {smart_materials['Viande']}")
    if has_mountain:
        old_stone = smart_materials.get('Pierre', 0)
        smart_materials['Pierre'] = max(old_stone, 40)
        print(f"DEBUG: Set mountain guarantees - Pierre: {old_stone} -> {smart_materials['Pierre']}")

    # Generate location description
    base_desc = get_location_description_smart(
        cell.center_lat,
        cell.center_lon,
        cell.grid_x,
        cell.grid_y,
        cell.biome,
        smart_materials
    )
    # Enrich with OSM-based hints
    hints = []
    if has_water:
        hints.append('🎣 Pêche possible')
    if has_forest:
        hints.append('🏹 Chasse possible')
    if has_mountain:
        hints.append('⛏️ Minage favorable')
        
    cell.location_description = base_desc + (" | " + " | ".join(hints) if hints else '')
    cell.save()

    print(f"Generated resources for cell ({cell.grid_x}, {cell.grid_y}): {smart_materials}")

    # Filter to only include existing raw materials (not crafted items)
    crafted_items = ['Planches', 'Bâton', 'Barre de Fer', 'Barre d\'Or', 'Pioche', 'Épée']
    filtered_materials = {k: v for k, v in smart_materials.items() if k not in crafted_items}
    print(f"DEBUG: Filtered out crafted items {crafted_items}, remaining materials: {filtered_materials}")

    for material_name, quantity in filtered_materials.items():
        print(f"DEBUG: Attempting to create CellMaterial for {material_name} with quantity {quantity}")
        try:
            material = Material.objects.get(name=material_name)
            cell_mat, created = CellMaterial.objects.get_or_create(
                cell=cell,
                material=material,
                defaults={
                    'quantity': quantity,
                    'max_quantity': 100
                }
            )
            print(f"DEBUG: CellMaterial {'created' if created else 'exists'} for {material_name}: quantity={cell_mat.quantity}")
        except Material.DoesNotExist:
            print(f"Warning: Material '{material_name}' does not exist in database")

def refresh_cell_environment(cell):
    """Refresh biome and description using OSM hints without changing materials"""
    # Base biome from coordinates (may have updated rules)
    try:
        base_biome = get_biome_from_coordinates(cell.center_lat, cell.center_lon, cell.grid_x, cell.grid_y)
    except Exception:
        base_biome = cell.biome or 'plains'

    # Fetch OSM features
    features = []
    try:
        features = fetch_osm_features(cell.center_lat, cell.center_lon, radius=100)
    except Exception as e:
        print(f"DEBUG: OSM fetch failed in refresh_cell_environment: {str(e)}")
        features = []

    # Detect environment from OSM with same priority logic as populate_cell_materials
    cats = [(f.get('category'), f.get('subcategory')) for f in features]
    subs = {s for (_, s) in cats if s}
    
    # Detect specific features
    has_water = any(s in subs for s in ['river', 'stream', 'canal', 'pond', 'lake', 'reservoir', 'water', 'bay'])
    has_coastline = any(s in subs for s in ['coastline', 'beach'])
    has_wetland = any(s in subs for s in ['wetland', 'marsh', 'swamp'])
    has_forest = any(
        (c == 'landuse' and s in ['forest']) or (c == 'natural' and s in ['wood', 'forest'])
        for (c, s) in cats
    )
    has_farmland = any(s in subs for s in ['farmland', 'orchard', 'vineyard', 'meadow'])
    has_grassland = any(s in subs for s in ['grassland', 'grass', 'heath'])
    has_scrub = any(s in subs for s in ['scrub'])
    has_glacier = any(s in subs for s in ['glacier'])
    has_volcano = any(s in subs for s in ['volcano'])
    
    # Mountain / Rock features
    has_mountain = any(s in subs for s in ['peak', 'cliff', 'bare_rock', 'rock', 'stone', 'scree'])
    
    # Desert / Sand features
    has_desert = any(s in subs for s in ['sand', 'desert', 'dune'])

    # Urban detection
    building_count = sum(1 for c, s in cats if c == 'building')
    amenity_count = sum(1 for c, s in cats if c == 'amenity')
    has_residential = any(s in subs for s in ['residential', 'apartments', 'house'])
    has_commercial = any(s in subs for s in ['commercial', 'retail', 'office'])
    has_industrial = any(s in subs for s in ['industrial', 'factory', 'warehouse'])
    is_urban = building_count >= 2 or amenity_count >= 2 or has_residential or has_commercial or has_industrial

    # OSM Biome Detection with PRIORITY ORDER
    new_biome = base_biome  # Default to procedural
    
    if has_glacier:
        new_biome = 'glacier'
    elif has_volcano:
        new_biome = 'volcano'
    elif has_mountain:
        new_biome = 'mountain'
    elif has_water and not has_coastline:
        new_biome = 'water'
    elif has_coastline:
        new_biome = 'coast'
    elif has_wetland:
        new_biome = 'wetland'
    elif has_desert:
        new_biome = 'desert'
    elif has_forest:
        new_biome = 'forest'
    elif has_farmland:
        new_biome = 'farmland'
    elif has_scrub:
        new_biome = 'savanna'
    elif has_grassland:
        new_biome = 'plains'
    elif is_urban:
        new_biome = 'urban'

    changed = (cell.biome != new_biome) or (cell.osm_features != features)
    if changed:
        cell.biome = new_biome
        cell.osm_features = features

        # Update description with hints (no materials context here)
        try:
            base_desc = get_location_description_smart(
                cell.center_lat,
                cell.center_lon,
                cell.grid_x,
                cell.grid_y,
                new_biome,
                {}
            )
        except Exception:
            base_desc = cell.location_description or 'Zone inconnue'
        hints = []
        if has_water or new_biome == 'water':
            hints.append('🎣 Pêche possible')
        if has_forest:
            hints.append('🏹 Chasse possible')
        if has_mountain:
            hints.append('⛏️ Minage favorable')
            
        cell.location_description = base_desc + (" | " + " | ".join(hints) if hints else '')
        cell.save()
