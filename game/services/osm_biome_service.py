"""
OSM-Biome Integration Service

Handles detection of biomes from OpenStreetMap features.
"""
from typing import List, Dict, Any, Optional, Tuple


def detect_biome_from_osm(features: List[Dict[str, Any]]) -> Optional[str]:
    """
    Detect biome from OSM features with priority-based logic.
    
    Args:
        features: List of OSM features
    
    Returns:
        Biome code if detected, None otherwise
    """
    if not features:
        return None
    
    # Extract categories and subcategories
    cats = [(f.get('category'), f.get('subcategory')) for f in features]
    subs = {s for (_, s) in cats if s}
    cats_set = {c for (c, _) in cats if c}
    
    # Count different types of features
    building_count = sum(1 for c, s in cats if c == 'building')
    amenity_count = sum(1 for c, s in cats if c == 'amenity')
    shop_count = sum(1 for c, s in cats if c == 'shop')
    
    # Detect specific features with expanded tags
    has_water = any(s in subs for s in [
        'river', 'stream', 'canal', 'pond', 'lake', 'reservoir', 'water', 
        'bay', 'waterway', 'riverbank'
    ])
    
    has_coastline = any(s in subs for s in ['coastline', 'beach', 'shore'])
    
    has_wetland = any(s in subs for s in [
        'wetland', 'marsh', 'swamp', 'bog', 'fen', 'reedbed'
    ])
    
    has_forest = any(
        (c == 'landuse' and s in ['forest', 'wood']) or 
        (c == 'natural' and s in ['wood', 'tree', 'forest', 'tree_row'])
        for (c, s) in cats
    )
    
    has_farmland = any(s in subs for s in [
        'farmland', 'orchard', 'vineyard', 'meadow', 'farm', 'farmyard',
        'allotments', 'plant_nursery'
    ])
    
    has_grassland = any(s in subs for s in [
        'grassland', 'grass', 'heath', 'fell'
    ])
    
    has_scrub = any(s in subs for s in ['scrub', 'shrubbery'])
    
    has_park = any(s in subs for s in [
        'park', 'nature_reserve', 'garden', 'recreation_ground',
        'village_green', 'common'
    ])
    
    has_glacier = any(s in subs for s in ['glacier', 'ice_shelf'])
    
    has_volcano = any(s in subs for s in ['volcano', 'volcanic'])
    
    # Mountain / Rock features
    has_mountain = any(s in subs for s in [
        'peak', 'cliff', 'bare_rock', 'rock', 'stone', 'scree',
        'ridge', 'arete', 'saddle'
    ])
    
    # Desert / Sand features
    has_desert = any(s in subs for s in [
        'sand', 'desert', 'dune', 'beach_sand'
    ])
    
    # Jungle / Tropical features
    has_jungle = any(s in subs for s in [
        'rainforest', 'jungle', 'mangrove'
    ])
    
    # Urban features
    has_residential = any(s in subs for s in [
        'residential', 'apartments', 'house', 'houses', 'detached',
        'terrace', 'dormitory'
    ])
    
    has_commercial = any(s in subs for s in [
        'commercial', 'retail', 'office', 'shop', 'supermarket'
    ])
    
    has_industrial = any(s in subs for s in [
        'industrial', 'factory', 'warehouse', 'depot'
    ])
    
    # Urban detection (more strict)
    is_urban = (
        (building_count >= 3) or 
        (amenity_count >= 3) or 
        (shop_count >= 2) or
        (has_residential and (has_commercial or amenity_count >= 2)) or
        has_industrial
    )
    
    # OSM Biome Detection with PRIORITY ORDER (most specific first)
    
    # Priority 1: Special natural features (highest priority)
    if has_glacier:
        return 'glacier'
    elif has_volcano:
        return 'volcano'
    
    # Priority 2: Mountain / Rock
    elif has_mountain:
        return 'mountain'
    
    # Priority 3: Water features
    elif has_water and not has_coastline:
        # Distinguish between large water bodies and wetlands
        if has_wetland:
            return 'wetland'
        return 'water'
    elif has_coastline:
        return 'coast'
    elif has_wetland:
        return 'wetland'
    
    # Priority 4: Desert
    elif has_desert:
        return 'desert'
    
    # Priority 5: Jungle/Tropical
    elif has_jungle:
        return 'jungle'
    
    # Priority 6: Vegetation
    elif has_forest:
        return 'forest'
    elif has_farmland:
        return 'farmland'
    elif has_scrub:
        return 'savanna'  # Scrubland is similar to savanna
    elif has_park or has_grassland:
        return 'plains'
    
    # Priority 7: Urban (lowest priority for natural features)
    elif is_urban:
        return 'urban'
    
    # No OSM biome detected
    return None


def get_osm_context(features: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extract context information from OSM features for resource generation.
    
    Args:
        features: List of OSM features
    
    Returns:
        Dictionary with context flags
    """
    if not features:
        return {}
    
    cats = [(f.get('category'), f.get('subcategory')) for f in features]
    subs = {s for (_, s) in cats if s}
    
    context = {
        'has_water': any(s in subs for s in [
            'river', 'stream', 'canal', 'pond', 'lake', 'reservoir', 'water'
        ]),
        'has_forest': any(
            (c == 'landuse' and s in ['forest', 'wood']) or 
            (c == 'natural' and s in ['wood', 'tree', 'forest'])
            for (c, s) in cats
        ),
        'urban': any(s in subs for s in [
            'residential', 'commercial', 'industrial', 'retail'
        ]),
        'has_farmland': any(s in subs for s in [
            'farmland', 'orchard', 'vineyard', 'meadow'
        ]),
        'has_mountain': any(s in subs for s in [
            'peak', 'cliff', 'bare_rock', 'rock'
        ]),
    }
    
    return context


def get_biome_with_osm_priority(
    lat: float, 
    lon: float, 
    grid_x: int, 
    grid_y: int, 
    osm_features: Optional[List[Dict[str, Any]]] = None
) -> Tuple[str, bool]:
    """
    Get biome with OSM priority over procedural generation.
    
    Args:
        lat: Latitude
        lon: Longitude
        grid_x: Grid X coordinate
        grid_y: Grid Y coordinate
        osm_features: Optional list of OSM features
    
    Returns:
        Tuple of (biome_code, is_from_osm)
    """
    from ..resource_generator import get_biome_from_coordinates
    
    # Try OSM detection first
    if osm_features:
        osm_biome = detect_biome_from_osm(osm_features)
        if osm_biome:
            return osm_biome, True
    
    # Fallback to procedural generation
    procedural_biome = get_biome_from_coordinates(lat, lon, grid_x, grid_y)
    return procedural_biome, False
