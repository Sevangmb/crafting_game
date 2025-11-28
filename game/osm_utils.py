"""
Utilities for fetching OpenStreetMap data and mapping to game materials
"""
import requests
import time

# Simple in-memory cache for OSM results
_OSM_CACHE = {}
_OSM_CACHE_TTL_SECONDS = 6 * 3600  # 6 hours TTL

# Circuit breaker state (process-level)
_OSM_CB = {
    'fail_count': 0,
    'opened_until': 0,  # epoch seconds when breaker closes again
}

def fetch_osm_features(lat, lon, radius=50):
    """
    Fetch OSM features around a location using Overpass API
    radius: in meters (default 50m for cell size)
    """
    # Cache key with rounded coords to group nearby requests in same cell
    key = (round(lat, 4), round(lon, 4), int(radius))
    now = time.time()
    cached = _OSM_CACHE.get(key)
    if cached and (now - cached['ts'] < _OSM_CACHE_TTL_SECONDS):
        return cached['features']

    # Circuit breaker: if opened, serve stale cache (if any) or empty
    if now < _OSM_CB.get('opened_until', 0):
        if cached:
            return cached['features']
        return []
    # Try multiple Overpass API servers for better reliability
    overpass_urls = [
        "https://overpass-api.de/api/interpreter",
        "https://lz4.overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://overpass.openstreetmap.ru/api/interpreter",
        "https://overpass.osm.ch/api/interpreter"
    ]

    # Query for shops, amenities, natural features, landuse, waterways, and leisure
    overpass_query = f"""
    [out:json][timeout:5];
    (
      node(around:{radius},{lat},{lon})["shop"];
      node(around:{radius},{lat},{lon})["amenity"];
      node(around:{radius},{lat},{lon})["natural"];
      node(around:{radius},{lat},{lon})["building"];
      way(around:{radius},{lat},{lon})["shop"];
      way(around:{radius},{lat},{lon})["amenity"];
      way(around:{radius},{lat},{lon})["natural"];
      way(around:{radius},{lat},{lon})["landuse"];
      way(around:{radius},{lat},{lon})["building"];
      way(around:{radius},{lat},{lon})["waterway"];
      way(around:{radius},{lat},{lon})["leisure"];
    );
    out body;
    """

    for overpass_url in overpass_urls:
        try:
            print(f"DEBUG: Trying OSM API: {overpass_url} for coords ({lat}, {lon})")
            print(f"DEBUG: Query timeout: 8s, Overpass timeout: 5s")
            start_time = time.time()
            # Add headers to avoid some SSL issues
            headers = {'User-Agent': 'CraftingGame/1.0 (crafting-game@example.com)'}
            response = requests.get(overpass_url, params={'data': overpass_query}, timeout=8, headers=headers)
            elapsed = time.time() - start_time
            print(f"DEBUG: Request to {overpass_url} took {elapsed:.2f}s")
            if response.status_code == 200:
                data = response.json()
                print(f"DEBUG: OSM response elements count: {len(data.get('elements', []))}")
                features = parse_osm_features(data)
                print(f"DEBUG: OSM Success! Found {len(features)} features at ({lat}, {lon})")
                if len(features) > 0:
                    print(f"DEBUG: Feature types: {[f.get('category') + ':' + f.get('subcategory', 'unknown') for f in features[:5]]}")
                # Store in cache
                _OSM_CACHE[key] = {'ts': now, 'features': features}
                # reset circuit breaker
                _OSM_CB['fail_count'] = 0
                _OSM_CB['opened_until'] = 0
                print(f"DEBUG: Circuit breaker reset")
                return features
            else:
                print(f"DEBUG: OSM API error {response.status_code} from {overpass_url}")
        except requests.exceptions.SSLError as ssl_e:
            print(f"DEBUG: SSL Error fetching from {overpass_url}: {str(ssl_e)}")
            continue
        except requests.exceptions.Timeout:
            print(f"DEBUG: Timeout fetching from {overpass_url}")
            continue
        except requests.exceptions.ConnectionError as conn_e:
            print(f"DEBUG: Connection Error fetching from {overpass_url}: {str(conn_e)}")
            continue
        except Exception as e:
            print(f"DEBUG: General error fetching from {overpass_url}: {str(e)}")
            continue

    print(f"DEBUG: All OSM APIs failed for ({lat}, {lon})")
    # Increment circuit breaker and backoff (exponential-ish)
    _OSM_CB['fail_count'] = _OSM_CB.get('fail_count', 0) + 1
    backoff = min(3600, 120 * (2 ** min(5, _OSM_CB['fail_count'] - 1)))  # 2m,4m,8m,16m,32m,64m max 60m
    _OSM_CB['opened_until'] = now + backoff
    print(f"DEBUG: Circuit breaker activated - fail_count: {_OSM_CB['fail_count']}, backoff: {backoff}s")

    # Serve stale if available
    if cached:
        print(f"DEBUG: Serving stale cache with {len(cached['features'])} features")
        return cached['features']

    print(f"DEBUG: No cache available, returning empty list")
    # Cache empty result to avoid hammering
    _OSM_CACHE[key] = {'ts': now, 'features': []}
    return []


def parse_osm_features(osm_data):
    """Parse OSM JSON response and extract relevant features"""
    features = []

    for element in osm_data.get('elements', []):
        tags = element.get('tags', {})

        feature = {
            'type': element.get('type'),
            'id': element.get('id'),
            'tags': tags
        }

        # Extract the main category - priority order matters!
        if 'shop' in tags:
            feature['category'] = 'shop'
            feature['subcategory'] = tags['shop']
        elif 'amenity' in tags:
            feature['category'] = 'amenity'
            feature['subcategory'] = tags['amenity']
        elif 'natural' in tags:
            feature['category'] = 'natural'
            feature['subcategory'] = tags['natural']
        elif 'waterway' in tags:
            feature['category'] = 'waterway'
            feature['subcategory'] = tags['waterway']
        elif 'leisure' in tags:
            feature['category'] = 'leisure'
            feature['subcategory'] = tags['leisure']
        elif 'landuse' in tags:
            feature['category'] = 'landuse'
            feature['subcategory'] = tags['landuse']
        elif 'building' in tags:
            feature['category'] = 'building'
            feature['subcategory'] = tags['building']
        else:
            continue

        if 'name' in tags:
            feature['name'] = tags['name']

        features.append(feature)

    return features


def get_materials_from_osm_features(features):
    """
    Map OSM features to game materials (only raw materials, no crafted items)
    Returns a list of material names based on the location
    """
    materials = set()

    # Define mapping from OSM features to raw materials
    material_mapping = {
        # Shops
        'shop': {
            'supermarket': ['Baie', 'Pomme', 'Fraise', 'Champignon'],
            'bakery': ['Stone', 'Wood'],
            'butcher': ['Stone'],
            'greengrocer': ['Baie', 'Pomme', 'Fraise', 'Champignon'],
            'florist': ['Wood', 'Baie'],
            'hardware': ['Stone', 'Iron Ore', 'Coal', 'Wood'],
            'doityourself': ['Wood', 'Stone', 'Iron Ore', 'Coal'],
            'furniture': ['Wood'],
            'garden_centre': ['Wood', 'Stone', 'Baie'],
            'jewelry': ['Gold Ore', 'Diamond'],
            'general': ['Stone', 'Wood', 'Coal'],
            'convenience': ['Baie', 'Fraise', 'Pomme'],
            'clothes': ['Wood'],
            'books': ['Wood'],
            'mall': ['Stone', 'Iron Ore'],
        },
        # Amenities
        'amenity': {
            'restaurant': ['Baie', 'Pomme', 'Fraise', 'Champignon'],
            'cafe': ['Baie', 'Pomme'],
            'fast_food': ['Fraise', 'Baie'],
            'bar': ['Baie'],
            'pub': ['Stone', 'Wood'],
            'school': ['Stone', 'Wood'],
            'library': ['Wood'],
            'place_of_worship': ['Stone'],
            'parking': ['Stone', 'Coal'],
            'fuel': ['Coal', 'Iron Ore'],
            'bank': ['Gold Ore', 'Stone'],
            'hospital': ['Stone'],
            'police': ['Stone', 'Iron Ore'],
            'post_office': ['Wood'],
        },
        # Natural features
        'natural': {
            'tree': ['Wood', 'Baie', 'Pomme'],
            'wood': ['Wood', 'Champignon', 'Baie'],
            'forest': ['Wood', 'Champignon'],
            'grassland': ['Baie', 'Fraise'],
            'scrub': ['Wood', 'Baie'],
            'water': [],
            'rock': ['Stone', 'Iron Ore'],
            'stone': ['Stone'],
            'bare_rock': ['Stone', 'Iron Ore'],
            'cliff': ['Stone', 'Iron Ore'],
            'peak': ['Stone', 'Coal'],
        },
        # Land use
        'landuse': {
            'forest': ['Wood', 'Champignon', 'Baie'],
            'grass': ['Baie', 'Fraise'],
            'meadow': ['Baie', 'Fraise', 'Champignon'],
            'farmland': ['Baie', 'Fraise', 'Pomme'],
            'orchard': ['Pomme', 'Baie'],
            'vineyard': ['Baie'],
            'commercial': ['Stone', 'Iron Ore', 'Coal'],
            'industrial': ['Iron Ore', 'Coal', 'Stone'],
            'residential': ['Wood', 'Stone'],
            'quarry': ['Stone', 'Iron Ore', 'Coal', 'Gold Ore'],
            'construction': ['Stone', 'Iron Ore', 'Wood'],
            'retail': ['Stone', 'Iron Ore'],
        },
        # Buildings
        'building': {
            'house': ['Wood', 'Stone'],
            'apartments': ['Stone', 'Iron Ore'],
            'commercial': ['Stone', 'Iron Ore'],
            'industrial': ['Iron Ore', 'Coal'],
            'retail': ['Stone'],
            'church': ['Stone'],
            'school': ['Stone', 'Wood'],
            'yes': ['Stone', 'Wood'],  # Generic building
            'residential': ['Wood', 'Stone'],
        }
    }

    # Process each feature
    print(f"DEBUG: Processing {len(features)} OSM features for materials")
    osm_materials_found = set()
    for feature in features:
        category = feature.get('category')
        subcategory = feature.get('subcategory')
        print(f"DEBUG: Processing feature - category: {category}, subcategory: {subcategory}")

        if category in material_mapping:
            category_materials = material_mapping[category].get(subcategory, [])
            if category_materials:
                print(f"DEBUG: Found materials for {category}:{subcategory} -> {category_materials}")
                materials.update(category_materials)
                osm_materials_found.update(category_materials)
            else:
                print(f"DEBUG: No materials mapped for {category}:{subcategory}")
        else:
            print(f"DEBUG: Category '{category}' not in material mapping")

    print(f"DEBUG: OSM materials found: {osm_materials_found}")
    print(f"DEBUG: Total unique materials found: {len(materials)}")

    # If no specific materials found, add default ones
    if not materials:
        materials = {'Stone', 'Wood'}

    # Always ensure at least Stone is available
    materials.add('Stone')

    return list(materials)


def get_location_description(features):
    """Generate a description of the location based on OSM features"""
    if not features:
        return "Zone vide"

    # Count features by category
    shops = [f for f in features if f.get('category') == 'shop']
    amenities = [f for f in features if f.get('category') == 'amenity']
    natural = [f for f in features if f.get('category') == 'natural']
    landuse = [f for f in features if f.get('category') == 'landuse']

    descriptions = []

    if shops:
        shop_types = list(set([s.get('subcategory', 'magasin') for s in shops]))
        descriptions.append(f"{len(shops)} magasin(s): {', '.join(shop_types[:3])}")

    if amenities:
        amenity_types = list(set([a.get('subcategory', 'lieu') for a in amenities]))
        descriptions.append(f"Lieux: {', '.join(amenity_types[:3])}")

    if natural:
        natural_types = list(set([n.get('subcategory', 'nature') for n in natural]))
        descriptions.append(f"Nature: {', '.join(natural_types[:2])}")

    if landuse:
        landuse_types = list(set([l.get('subcategory', 'terrain') for l in landuse]))
        descriptions.append(f"Terrain: {', '.join(landuse_types[:2])}")

    if descriptions:
        return " | ".join(descriptions)

    return "Zone inconnue"


# Cache for reverse geocoding results
_GEOCODE_CACHE = {}
_GEOCODE_CACHE_TTL = 24 * 3600  # 24 hours

def reverse_geocode(lat, lon):
    """
    Get city and country from coordinates using Nominatim reverse geocoding
    Returns dict with 'city' and 'country' keys
    """
    # Cache key
    key = (round(lat, 3), round(lon, 3))
    now = time.time()
    
    # Check cache
    cached = _GEOCODE_CACHE.get(key)
    if cached and (now - cached['ts'] < _GEOCODE_CACHE_TTL):
        return cached['data']
    
    # Default fallback
    result = {'city': None, 'country': None}
    
    try:
        # Use Nominatim API for reverse geocoding
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            'lat': lat,
            'lon': lon,
            'format': 'json',
            'addressdetails': 1,
            'accept-language': 'fr'  # French for consistency with game
        }
        headers = {
            'User-Agent': 'CraftingGame/1.0 (crafting-game@example.com)'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})
            
            # Try to get city from various fields
            city = (address.get('city') or 
                   address.get('town') or 
                   address.get('village') or 
                   address.get('municipality') or
                   address.get('county'))
            
            country = address.get('country')
            
            result = {
                'city': city,
                'country': country
            }
            
            # Cache the result
            _GEOCODE_CACHE[key] = {'ts': now, 'data': result}
            print(f"DEBUG: Reverse geocoding success: {city}, {country}")
        else:
            print(f"DEBUG: Nominatim returned status {response.status_code}")
            
    except Exception as e:
        print(f"DEBUG: Reverse geocoding failed: {str(e)}")
    
    return result

