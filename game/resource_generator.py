"""
Smart resource generation system based on coordinates and biome
"""
import random
import math


# Comprehensive biome metadata
BIOME_DATA = {
    'plains': {
        'name': '🌾 Plaines',
        'description': 'Vastes étendues herbeuses sous un ciel dégagé, idéales pour débuter',
        'color': '#90EE90',
        'ambient': 'Vent doux, chants d\'oiseaux',
        'difficulty': 1,
        'temperature_range': (10, 25),
        'movement_modifier': 1.0,
        'gathering_bonus': 1.0,
        'dangers': [],
    },
    'forest': {
        'name': '🌲 Forêt',
        'description': 'Dense forêt verdoyante riche en bois et gibier',
        'color': '#228B22',
        'ambient': 'Bruissement de feuilles, chants d\'oiseaux',
        'difficulty': 2,
        'temperature_range': (8, 22),
        'movement_modifier': 0.9,
        'gathering_bonus': 1.2,
        'hunting_bonus': 1.3,
        'dangers': ['ours', 'loups'],
    },
    'mountain': {
        'name': '⛰️ Montagne',
        'description': 'Pics rocheux riches en minerais précieux mais difficiles d\'accès',
        'color': '#8B7355',
        'ambient': 'Vent fort, échos lointains',
        'difficulty': 4,
        'temperature_range': (-5, 15),
        'movement_modifier': 0.7,
        'mining_bonus': 1.5,
        'dangers': ['chutes de pierres', 'altitude'],
    },
    'desert': {
        'name': '🏜️ Désert',
        'description': 'Étendues arides et brûlantes, rares ressources mais trésors cachés',
        'color': '#EDC9AF',
        'ambient': 'Vent de sable, silence oppressant',
        'difficulty': 5,
        'temperature_range': (20, 45),
        'movement_modifier': 0.8,
        'thirst_rate': 2.0,
        'dangers': ['déshydratation', 'tempêtes de sable', 'scorpions'],
    },
    'jungle': {
        'name': '🦜 Jungle',
        'description': 'Végétation dense et humide grouillant de vie exotique',
        'color': '#1B5E20',
        'ambient': 'Cris d\'oiseaux exotiques, bruissements constants',
        'difficulty': 4,
        'temperature_range': (25, 35),
        'movement_modifier': 0.75,
        'gathering_bonus': 1.3,
        'hunting_bonus': 1.2,
        'dangers': ['serpents venimeux', 'plantes toxiques', 'maladies'],
    },
    'tundra': {
        'name': '❄️ Toundra',
        'description': 'Plaines gelées et désolées où seuls les plus résistants survivent',
        'color': '#E0F2F7',
        'ambient': 'Vent glacial, silence absolu',
        'difficulty': 4,
        'temperature_range': (-20, 5),
        'movement_modifier': 0.8,
        'cold_damage': True,
        'dangers': ['hypothermie', 'blizzards'],
    },
    'taiga': {
        'name': '🌲 Taïga',
        'description': 'Forêt boréale de conifères dans un climat froid',
        'color': '#2E7D32',
        'ambient': 'Craquements de glace, vent dans les sapins',
        'difficulty': 3,
        'temperature_range': (-10, 15),
        'movement_modifier': 0.85,
        'gathering_bonus': 1.1,
        'dangers': ['froid', 'loups'],
    },
    'glacier': {
        'name': '🧊 Glacier',
        'description': 'Immenses étendues de glace éternelle, dangereuses mais riches en cristaux',
        'color': '#B3E5FC',
        'ambient': 'Craquements de glace, vent hurlant',
        'difficulty': 5,
        'temperature_range': (-30, -5),
        'movement_modifier': 0.6,
        'cold_damage': True,
        'mining_bonus': 1.3,
        'dangers': ['hypothermie sévère', 'crevasses', 'yétis'],
    },
    'volcano': {
        'name': '🌋 Volcan',
        'description': 'Terre de feu et de lave, extrêmement dangereuse mais riche en gemmes',
        'color': '#D32F2F',
        'ambient': 'Grondements, crépitements de lave',
        'difficulty': 5,
        'temperature_range': (30, 60),
        'movement_modifier': 0.7,
        'heat_damage': True,
        'mining_bonus': 1.8,
        'dangers': ['lave', 'gaz toxiques', 'éruptions'],
    },
    'swamp': {
        'name': '🫧 Marais',
        'description': 'Terres humides et boueuses, riches en champignons et poissons',
        'color': '#558B2F',
        'ambient': 'Coassements, clapotis',
        'difficulty': 3,
        'temperature_range': (12, 28),
        'movement_modifier': 0.7,
        'gathering_bonus': 1.1,
        'dangers': ['maladies', 'enlisement'],
    },
    'coast': {
        'name': '🌊 Côte',
        'description': 'Rivages sablonneux riches en poissons et coquillages',
        'color': '#4FC3F7',
        'ambient': 'Vagues, cris de mouettes',
        'difficulty': 2,
        'temperature_range': (10, 25),
        'movement_modifier': 0.95,
        'fishing_bonus': 1.5,
        'dangers': ['marées'],
    },
    'coral_reef': {
        'name': '🪸 Récif Corallien',
        'description': 'Eaux cristallines abritant une vie marine extraordinaire',
        'color': '#00BCD4',
        'ambient': 'Vagues douces, vie sous-marine',
        'difficulty': 3,
        'temperature_range': (20, 28),
        'movement_modifier': 0.8,
        'fishing_bonus': 2.0,
        'diving_required': True,
        'dangers': ['requins', 'méduses'],
    },
    'rainforest': {
        'name': '🌳 Forêt Tropicale',
        'description': 'Forêt dense et humide d\'une biodiversité exceptionnelle',
        'color': '#2E7D32',
        'ambient': 'Pluie constante, cris d\'animaux',
        'difficulty': 3,
        'temperature_range': (22, 32),
        'movement_modifier': 0.8,
        'gathering_bonus': 1.4,
        'dangers': ['pluies torrentielles', 'insectes'],
    },
    'savanna': {
        'name': '🦒 Savane',
        'description': 'Prairies africaines parsemées d\'acacias, terrain de chasse',
        'color': '#FDD835',
        'ambient': 'Vent chaud, rugissements lointains',
        'difficulty': 3,
        'temperature_range': (18, 35),
        'movement_modifier': 1.0,
        'hunting_bonus': 1.4,
        'dangers': ['lions', 'chaleur'],
    },
    'canyon': {
        'name': '🏜️ Canyon',
        'description': 'Gorges profondes sculptées par l\'érosion, riches en fossiles',
        'color': '#D84315',
        'ambient': 'Échos, vent sifflant',
        'difficulty': 4,
        'temperature_range': (15, 40),
        'movement_modifier': 0.75,
        'mining_bonus': 1.3,
        'dangers': ['chutes', 'chaleur extrême'],
    },
    'mushroom_forest': {
        'name': '🍄 Forêt de Champignons',
        'description': 'Forêt mystique de champignons géants aux propriétés magiques',
        'color': '#9C27B0',
        'ambient': 'Silence étrange, spores flottantes',
        'difficulty': 3,
        'temperature_range': (12, 20),
        'movement_modifier': 0.9,
        'gathering_bonus': 1.5,
        'magic_affinity': True,
        'dangers': ['spores toxiques', 'champignons hallucinogènes'],
    },
    'urban': {
        'name': '🏘️ Zone Urbaine',
        'description': 'Ruines de civilisation, riches en matériaux de récupération',
        'color': '#757575',
        'ambient': 'Vent dans les ruines, silence inquiétant',
        'difficulty': 3,
        'temperature_range': (5, 30),
        'movement_modifier': 0.9,
        'scavenging_bonus': 1.5,
        'gathering_penalty': 0.5,
        'dangers': ['structures instables', 'pillards'],
    },
    'wetland': {
        'name': '🪵 Marécages',
        'description': 'Zones humides riches en vie aquatique et plantes médicinales',
        'color': '#689F38',
        'ambient': 'Clapotis, chants de grenouilles',
        'difficulty': 2,
        'temperature_range': (10, 25),
        'movement_modifier': 0.85,
        'fishing_bonus': 1.3,
        'gathering_bonus': 1.2,
        'dangers': ['boue', 'sangsues'],
    },
    'water': {
        'name': '💧 Lac/Rivière',
        'description': 'Étendues d\'eau douce poissonneuses',
        'color': '#2196F3',
        'ambient': 'Clapotis, oiseaux aquatiques',
        'difficulty': 2,
        'temperature_range': (5, 25),
        'movement_modifier': 0.5,
        'fishing_bonus': 1.8,
        'swimming_required': True,
        'dangers': ['noyade', 'courants'],
    },
    'steppe': {
        'name': '🌿 Steppe',
        'description': 'Prairies semi-arides balayées par le vent',
        'color': '#C5E1A5',
        'ambient': 'Vent constant, herbes ondulantes',
        'difficulty': 2,
        'temperature_range': (5, 30),
        'movement_modifier': 1.0,
        'hunting_bonus': 1.2,
        'dangers': ['sécheresse'],
    },
    'farmland': {
        'name': '🚜 Terres Agricoles',
        'description': 'Champs cultivés abandonnés, encore fertiles',
        'color': '#8BC34A',
        'ambient': 'Vent dans les cultures, silence pastoral',
        'difficulty': 1,
        'temperature_range': (8, 28),
        'movement_modifier': 1.0,
        'gathering_bonus': 1.3,
        'dangers': [],
    },
    'bog': {
        'name': '🫧 Tourbière',
        'description': 'Marais acide et sombre, dangereux mais riche en tourbe',
        'color': '#4E342E',
        'ambient': 'Bulles de gaz, brume épaisse',
        'difficulty': 4,
        'temperature_range': (5, 20),
        'movement_modifier': 0.6,
        'gathering_bonus': 1.1,
        'dangers': ['gaz toxiques', 'enlisement', 'brume'],
    },
    'bamboo_forest': {
        'name': '🎋 Forêt de Bambous',
        'description': 'Haute forêt de bambous bruissants, paisible et mystérieuse',
        'color': '#7CB342',
        'ambient': 'Cliquetis de bambous, vent doux',
        'difficulty': 2,
        'temperature_range': (15, 30),
        'movement_modifier': 0.85,
        'gathering_bonus': 1.4,
        'dangers': ['pandas agressifs'],
    },
    'mangrove': {
        'name': '🌿 Mangrove',
        'description': 'Forêt côtière d\'arbres aux racines entrelacées dans l\'eau saumâtre',
        'color': '#558B2F',
        'ambient': 'Clapotis, cris d\'oiseaux marins',
        'difficulty': 3,
        'temperature_range': (20, 32),
        'movement_modifier': 0.65,
        'fishing_bonus': 1.4,
        'gathering_bonus': 1.2,
        'dangers': ['crocodiles', 'marée montante', 'racines traîtresses'],
    },
    'alpine': {
        'name': '🏔️ Alpin',
        'description': 'Prairies d\'altitude fleuries entre neige et roche',
        'color': '#81C784',
        'ambient': 'Vent de montagne, cloches de vaches lointaines',
        'difficulty': 3,
        'temperature_range': (-5, 18),
        'movement_modifier': 0.8,
        'gathering_bonus': 1.3,
        'mining_bonus': 1.2,
        'dangers': ['altitude', 'orages soudains'],
    },
    'badlands': {
        'name': '🏜️ Badlands',
        'description': 'Terres érodées aux formations rocheuses spectaculaires',
        'color': '#BF360C',
        'ambient': 'Vent sec, silence minéral',
        'difficulty': 4,
        'temperature_range': (10, 40),
        'movement_modifier': 0.75,
        'mining_bonus': 1.4,
        'dangers': ['érosion', 'chaleur extrême', 'manque d\'eau'],
    },
    'oasis': {
        'name': '🏝️ Oasis',
        'description': 'Havre de verdure au milieu du désert, source de vie',
        'color': '#4DD0E1',
        'ambient': 'Eau qui coule, palmiers bruissants',
        'difficulty': 1,
        'temperature_range': (18, 35),
        'movement_modifier': 1.0,
        'gathering_bonus': 1.5,
        'fishing_bonus': 1.3,
        'dangers': [],
    },
    'kelp_forest': {
        'name': '🌊 Forêt de Kelp',
        'description': 'Forêt sous-marine d\'algues géantes, riche en vie marine',
        'color': '#00695C',
        'ambient': 'Bulles, courants sous-marins',
        'difficulty': 3,
        'temperature_range': (8, 18),
        'movement_modifier': 0.6,
        'fishing_bonus': 2.2,
        'diving_required': True,
        'dangers': ['requins', 'courants', 'noyade'],
    },
    'cave': {
        'name': '🕳️ Grotte',
        'description': 'Réseau souterrain sombre et humide, mystérieux',
        'color': '#37474F',
        'ambient': 'Gouttes d\'eau, échos',
        'difficulty': 4,
        'temperature_range': (8, 15),
        'movement_modifier': 0.65,
        'mining_bonus': 1.7,
        'light_required': True,
        'dangers': ['obscurité', 'chauves-souris', 'effondrements'],
    },
    'lava_field': {
        'name': '🔥 Champ de Lave',
        'description': 'Coulées de lave refroidies formant un paysage lunaire',
        'color': '#D84315',
        'ambient': 'Craquements, chaleur intense',
        'difficulty': 5,
        'temperature_range': (35, 70),
        'movement_modifier': 0.6,
        'heat_damage': True,
        'mining_bonus': 2.0,
        'dangers': ['chaleur extrême', 'gaz toxiques', 'lave active'],
    },
    'cherry_blossom': {
        'name': '🌸 Cerisiers en Fleurs',
        'description': 'Forêt de cerisiers en pleine floraison, d\'une beauté éthérée',
        'color': '#F8BBD0',
        'ambient': 'Pétales qui tombent, brise douce',
        'difficulty': 1,
        'temperature_range': (12, 22),
        'movement_modifier': 1.0,
        'gathering_bonus': 1.4,
        'magic_affinity': True,
        'dangers': [],
    },
    'autumn_forest': {
        'name': '🍂 Forêt d\'Automne',
        'description': 'Forêt aux couleurs flamboyantes de l\'automne',
        'color': '#FF6F00',
        'ambient': 'Feuilles qui craquent, vent frais',
        'difficulty': 2,
        'temperature_range': (5, 18),
        'movement_modifier': 0.95,
        'gathering_bonus': 1.5,
        'hunting_bonus': 1.2,
        'dangers': ['sangliers'],
    },
}


def get_biome_info(biome):
    """
    Get comprehensive information about a biome.
    
    Args:
        biome: The biome code
    
    Returns:
        Dictionary with biome metadata
    """
    return BIOME_DATA.get(biome, BIOME_DATA['plains'])



def _hash_noise(x, y, salt=0):
    # Simple deterministic hash-based noise in [0,1]
    n = int((x * 73856093) ^ (y * 19349663) ^ (salt * 83492791)) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFFFFFF) / 0xFFFFFFFF

def _fbm_noise(x, y, salt=0, octaves=4, lacunarity=2.0, gain=0.5):
    """Fractal Brownian Motion using hash-based noise."""
    amp = 1.0
    freq = 1.0
    total = 0.0
    norm = 0.0
    for i in range(octaves):
        nx = int(x * freq)
        ny = int(y * freq)
        total += amp * _hash_noise(nx, ny, salt + i)
        norm += amp
        amp *= gain
        freq *= lacunarity
    return total / max(1e-9, norm)

def get_biome_from_coordinates(lat, lon, grid_x, grid_y):
    """
    Determine biome using a simple temperature/moisture model + patterns.
    Deterministic per (lat,lon,grid_x,grid_y).
    """
    try:
        # Normalize coordinates for noise (float domain)
        fx = grid_x / 8.0 + lat * 0.5
        fy = grid_y / 8.0 + lon * 0.5

        # Temperature model: latitude influence + noise
        # 0=cold ... 1=hot
        lat_factor = max(0.0, min(1.0, 0.5 - (lat - 45.0) / 60.0))  # around 45N baseline
        temp = 0.55 * lat_factor + 0.45 * _fbm_noise(fx * 1.7, fy * 1.7, salt=11, octaves=5)

        # Moisture model: noise + proximity to pseudo water bands
        # 0=dry ... 1=wet
        # Coast/river bands via trigonometric curves for large-scale features
        band_y = 0.5 * (1.0 + math.sin(grid_y / 6.0))
        band_x = 0.5 * (1.0 + math.cos(grid_x / 9.0))
        coast_river = 1.0 if (band_y > 0.95 or band_x > 0.96) else 0.0
        moist = 0.75 * _fbm_noise(fx * 1.3, fy * 1.3, salt=22, octaves=5) + 0.25 * coast_river
        moist = max(0.0, min(1.0, moist))

        # Elevation hint from distance and ridge patterns
        dist = math.sqrt(grid_x**2 + grid_y**2)
        ridge = 0.5 * (1.0 + math.sin((grid_x + grid_y) / 8.0))
        elev_noise = _fbm_noise(fx * 0.9, fy * 0.9, salt=33, octaves=4)
        elev = 0.3 * (dist / 25.0) + 0.4 * ridge + 0.3 * elev_noise  # 0..~1
        elev = max(0.0, min(1.0, elev))

        # Neighborhood smoothing: average temp/moist with 8-neighbors (cheap blur)
        def _neighbor_avg(base_val, salt):
            acc = base_val
            for dx in (-0.5, 0.0, 0.5):
                for dy in (-0.5, 0.0, 0.5):
                    if dx == 0.0 and dy == 0.0:
                        continue
                    acc += _fbm_noise((fx + dx) * 1.2, (fy + dy) * 1.2, salt=salt, octaves=3)
            return acc / 9.0
        temp = 0.7 * temp + 0.3 * _neighbor_avg(temp, salt=14)
        moist = 0.7 * moist + 0.3 * _neighbor_avg(moist, salt=25)

        # Base biome grid from temp/moist
        biome = 'plains'
        if temp < 0.25:
            if moist < 0.35:
                biome = 'tundra'
            elif moist < 0.7:
                biome = 'taiga'
            else:
                biome = 'bog'
        elif temp < 0.6:
            if moist < 0.25:
                biome = 'steppe'
            elif moist < 0.7:
                biome = 'plains'
            else:
                biome = 'forest'
        else:
            if moist < 0.25:
                biome = 'desert'
            elif moist < 0.6:
                biome = 'savanna'
            else:
                biome = 'rainforest'

        # Elevation overrides
        if elev > 0.78:
            biome = 'mountain'
        
        # Extreme elevation: Volcano (very high + hot)
        if elev > 0.88 and temp > 0.7:
            biome = 'volcano'
        
        # Very high elevation + very cold: Glacier
        if elev > 0.85 and temp < 0.2:
            biome = 'glacier'

        # Pattern/OSM-like coastal/wetland hints
        if band_y > 0.96:
            biome = 'coast'
        if (band_x > 0.94 or band_y > 0.9) and moist > 0.6 and temp < 0.7:
            biome = 'wetland'
        
        # Coral reef: coastal + warm + specific pattern
        if band_y > 0.97 and temp > 0.65 and _fbm_noise(fx * 3.1, fy * 3.1, salt=88) > 0.6:
            biome = 'coral_reef'
        
        # Canyon: hot + very dry + specific elevation pattern
        if temp > 0.75 and moist < 0.2 and 0.4 < elev < 0.7 and _fbm_noise(fx * 2.7, fy * 2.7, salt=66) > 0.7:
            biome = 'canyon'
        
        # Jungle: very hot + very wet (more extreme than rainforest)
        if temp > 0.8 and moist > 0.85:
            biome = 'jungle'
        
        # Mushroom forest: moderate temp + high moisture + specific pattern
        if 0.4 < temp < 0.65 and moist > 0.75 and _fbm_noise(fx * 2.5, fy * 2.5, salt=55) > 0.75:
            biome = 'mushroom_forest'

        # Human areas
        if _fbm_noise(fx * 2.3, fy * 2.3, salt=77) > 0.8 and dist < 12:
            biome = 'urban'

        # Spawn bias: around origin, favor plains/forest
        if dist < 3:
            bias = _hash_noise(grid_x + 5, grid_y + 7, salt=99)
            if bias < 0.6:
                biome = 'plains'
            elif bias < 0.9:
                biome = 'forest'

        return biome
    except Exception as e:
        # Fallback to plains if anything goes wrong
        print(f"Error in get_biome_from_coordinates: {str(e)}, falling back to 'plains'")
        return 'plains'


def get_smart_resources(lat, lon, grid_x, grid_y, biome, osm_context=None):
    """
    Generate smart resource list based on biome and coordinates
    Returns a dict with material names and their quantities
    """
    # Use coordinates as seed for deterministic randomness
    seed = int((lat * 1000 + lon * 1000 + grid_x * 41 + grid_y * 83) * 100)
    random.seed(seed)

    # Base materials by biome with expanded variety from actual materials
    biome_resources = {
        'plains': {
            'common': ['Pierre', 'Bois', 'Herbe', 'Terre fertile'],
            'uncommon': ['Charbon', 'Baie', 'Pomme', 'Carotte', 'Salade', 'Viande', 'Argile'],
            'rare': ["Minerai de Fer", 'Tomate', 'Blé', 'Coton', 'Lin'],
        },
        'forest': {
            'common': ['Bois', 'Bois', 'Pierre'],  # High wood probability
            'uncommon': ['Baie', 'Champignon', 'Pomme', 'Viande', 'Cuir brut', 'Bois précieux', 'Liane'],
            'rare': ['Minerai de Fer', 'Charbon', 'Améthyste', 'Jaspe', 'Poussière de fée'],
        },
        'mountain': {
            'common': ['Pierre', 'Pierre', 'Minerai de Fer'],  # High stone/mineral probability
            'uncommon': ['Charbon', 'Minerai d\'Or', 'Minerai de Cuivre'],
            'rare': ['Diamant', 'Rubis', 'Saphir', 'Émeraude', 'Cristal de mana', 'Pierre de lune'],
        },
        'steppe': {
            'common': ['Pierre', 'Bois', 'Herbe'],
            'uncommon': ['Fibres Végétales', 'Baie', 'Viande', 'Coton'],
            'rare': ['Charbon', 'Blé'],
        },
        'desert': {
            'common': ['Pierre', 'Sable', 'Pierre de sel'],
            'uncommon': ['Argile sèche'],
            'rare': ["Minerai d'Or", 'Topaze', 'Pierre de soleil', 'Os de sable'],
        },
        'savanna': {
            'common': ['Bois', 'Pierre', 'Herbe'],
            'uncommon': ['Fibres Végétales', 'Viande', 'Baie', 'Orange'],
            'rare': ['Charbon', 'Minerai de Fer'],
        },
        'rainforest': {
            'common': ['Bois', 'Bois', 'Pierre'],
            'uncommon': ['Baie', 'Champignon', 'Fibres Végétales', 'Banane', 'Orange', 'Noix de coco'],
            'rare': ['Charbon', 'Minerai de Fer', 'Orchidée rare', 'Écorce enchantée', 'Caoutchouc'],
        },
        'wetland': {
            'common': ['Bois', 'Pierre', 'Eau stagnante'],
            'uncommon': ['Champignon', 'Baie', 'Poisson', 'Roseau', 'Nénuphar', 'Herbe des marais'],
            'rare': ['Minerai de Fer', 'Champignon phosphorescent'],
        },
        'coast': {
            'common': ['Bois', 'Pierre', 'Sable fin'],
            'uncommon': ['Poisson', 'Poisson', 'Charbon', 'Coquillage', 'Algue'],  # Double fish chance
            'rare': ["Minerai d'Or", 'Jade', 'Corail', 'Perle noire'],
        },
        'farmland': {
            'common': ['Bois', 'Pierre', 'Terre fertile'],
            'uncommon': ['Fibres Végétales', 'Baie', 'Pomme', 'Carotte', 'Tomate', 'Salade'],
            'rare': ['Charbon', 'Blé', 'Maïs', 'Poivron', 'Aubergine', 'Brocoli'],
        },
        'urban': {
            'common': ['Pierre', 'Pierre'],  # High stone probability in cities
            'uncommon': ['Charbon', 'Minerai de Fer', 'Minerai de Cuivre', 'Argile'],
            'rare': ["Minerai d'Or", 'Minerai d\'Étain'],
        },
        'tundra': {
            'common': ['Pierre', 'Glace éternelle'],
            'uncommon': ['Charbon', 'Baies congelées'],
            'rare': ['Minerai de Fer', 'Cristal de glace'],
        },
        'taiga': {
            'common': ['Bois', 'Pierre'],
            'uncommon': ['Champignon', 'Baie', 'Charbon', 'Éclat de glace'],
            'rare': ['Minerai de Fer', 'Cœur de glace'],
        },
        'bog': {
            'common': ['Bois', 'Pierre', 'Tourbe'],
            'uncommon': ['Champignon', 'Poisson', 'Bois pourri', 'Champignon vénéneux'],
            'rare': ['Minerai de Fer', 'Eau stagnante'],
        },
        'volcano': {
            'common': ['Pierre', 'Obsidienne', 'Soufre'],
            'uncommon': ['Minerai de Fer', 'Charbon', 'Cendre volcanique'],
            'rare': ['Rubis', 'Diamant', 'Cristal de feu', 'Lave solidifiée'],
        },
        'canyon': {
            'common': ['Pierre rouge', 'Sable', 'Pierre'],
            'uncommon': ['Minerai de Cuivre', 'Argile rouge', 'Cactus'],
            'rare': ['Turquoise', 'Fossile', "Minerai d'Or", 'Os ancien'],
        },
        'jungle': {
            'common': ['Bois exotique', 'Liane', 'Feuilles tropicales'],
            'uncommon': ['Banane', 'Noix de coco', 'Bambou', 'Fruit du dragon', 'Viande'],
            'rare': ['Orchidée rare', 'Plume rare', 'Jade', 'Caoutchouc', 'Épice rare'],
        },
        'glacier': {
            'common': ['Glace pure', 'Pierre', 'Neige compacte'],
            'uncommon': ['Cristal de glace', 'Fourrure blanche', 'Poisson arctique'],
            'rare': ['Diamant de glace', 'Perle de glace', 'Minerai de platine'],
        },
        'coral_reef': {
            'common': ['Corail', 'Poisson', 'Algue marine'],
            'uncommon': ['Coquillage', 'Étoile de mer', 'Poisson exotique', 'Perle'],
            'rare': ['Perle noire', 'Coquillage rare', 'Corail doré', 'Éponge magique'],
        },
        'mushroom_forest': {
            'common': ['Champignon géant', 'Spore', 'Mousse'],
            'uncommon': ['Champignon bleu', 'Champignon rouge', 'Truffe', 'Bois moisi'],
            'rare': ['Champignon lumineux', 'Truffe noire', 'Spore magique', 'Mycélium ancien'],
        },
        'water': {
            'common': ['Eau pure', 'Algue', 'Roseau'],
            'uncommon': ['Poisson', 'Poisson', 'Nénuphar', 'Coquillage'],
            'rare': ['Perle', 'Poisson rare', 'Cristal d\'eau', 'Algue marine'],
        },
    }

    resources = biome_resources.get(biome, biome_resources['plains'])
    materials = {}

    # Always add 2-3 common resources
    num_common = random.randint(2, 3)
    for _ in range(num_common):
        material = random.choice(resources['common'])
        if material not in materials:
            materials[material] = random.randint(20, 50)
        else:
            materials[material] += random.randint(10, 20)

    # Add basic gathering resources (branches, leaves) to all biomes - always available
    materials['Branches'] = materials.get('Branches', random.randint(15, 40))
    materials['Feuilles'] = materials.get('Feuilles', random.randint(10, 30))

    # Add primitive tools scattered around (always present in some cells)
    primitive_tools = ['Bâton', 'Silex', 'Pierre taillée']
    if random.random() < 0.4:  # 40% chance per cell for basic tools
        tool = random.choice(primitive_tools)
        if tool not in materials:
            materials[tool] = random.randint(1, 3)

    # Add 1-2 uncommon resources (70% chance)
    if random.random() < 0.7:
        num_uncommon = random.randint(1, 2)
        for _ in range(num_uncommon):
            material = random.choice(resources['uncommon'])
            if material not in materials:
                materials[material] = random.randint(10, 30)

    # Add 0-1 rare resource (30% chance)
    if random.random() < 0.3:
        material = random.choice(resources['rare'])
        if material not in materials:
            materials[material] = random.randint(5, 15)

    # Special zones based on grid position
    # Diamond zones (very rare, specific coordinates)
    if (grid_x % 7 == 0 and grid_y % 7 == 0) and distance_from_origin(grid_x, grid_y) > 5:
        materials['Diamant'] = random.randint(1, 5)

    # Gold zones (specific pattern)
    if (grid_x + grid_y) % 11 == 0:
        materials['Minerai d\'Or'] = random.randint(5, 15)

    # Food zones (specific pattern)
    if abs(grid_x - grid_y) % 4 == 0:
        food_items = ['Baie', 'Pomme', 'Champignon']
        food = random.choice(food_items)
        materials[food] = random.randint(15, 35)

    # Fishing zones (rivers/lakes approximation)
    if (grid_x % 4 == 1 or grid_y % 5 == 2):
        materials['Poisson'] = materials.get('Poisson', 0) + random.randint(10, 30)

    # Hunting zones (fauna clusters)
    if (grid_x + 2 * grid_y) % 6 == 0:
        materials['Viande'] = materials.get('Viande', 0) + random.randint(10, 25)
        if random.random() < 0.5:
            materials['Cuir brut'] = materials.get('Cuir brut', 0) + random.randint(5, 15)

    # Iron/Coal zones (industrial areas)
    if (grid_x % 3 == 0 or grid_y % 3 == 0) and biome == 'mountain':
        materials['Minerai de Fer'] = materials.get('Minerai de Fer', 0) + random.randint(5, 20)
        materials['Charbon'] = materials.get('Charbon', 0) + random.randint(5, 20)

    # Bush gathering zones - add extra branches and leaves
    if (grid_x + grid_y) % 8 == 0:
        materials['Branches'] = materials.get('Branches', 0) + random.randint(20, 50)
        materials['Feuilles'] = materials.get('Feuilles', 0) + random.randint(15, 40)

    # Primitive tool zones - scattered stone tools
    if (grid_x % 5 == 0 and grid_y % 5 == 0) and distance_from_origin(grid_x, grid_y) > 3:
        primitive_tools = ['Silex', 'Pierre taillée']
        for tool in primitive_tools:
            if tool not in materials:
                materials[tool] = random.randint(1, 5)

    # Spawn-friendly resources near origin to ease testing of tools
    if distance_from_origin(grid_x, grid_y) <= 2:
        materials['Bois'] = max(materials.get('Bois', 0), random.randint(40, 80))
        materials['Pierre'] = max(materials.get('Pierre', 0), random.randint(30, 60))
        # ensure at least some food/hunting and fishing nearby
        materials['Poisson'] = max(materials.get('Poisson', 0), random.randint(15, 30))
        materials['Viande'] = max(materials.get('Viande', 0), random.randint(10, 20))
        # Add basic gathering materials near spawn
        materials['Branches'] = max(materials.get('Branches', 0), random.randint(25, 50))
        materials['Feuilles'] = max(materials.get('Feuilles', 0), random.randint(20, 40))

    # OSM modifiers (optional): boost certain pools based on local hints
    if osm_context:
        if osm_context.get('has_water'):
            materials['Poisson'] = materials.get('Poisson', 0) + random.randint(10, 30)
            materials['Argile'] = max(materials.get('Argile', 0), random.randint(5, 20))
        if osm_context.get('has_forest'):
            materials['Bois'] = max(materials.get('Bois', 0), random.randint(40, 80))
            materials['Champignon'] = max(materials.get('Champignon', 0), random.randint(10, 25))
            materials['Viande'] = max(materials.get('Viande', 0), random.randint(10, 20))
        if osm_context.get('urban'):
            materials['Pierre'] = max(materials.get('Pierre', 0), random.randint(20, 50))
            materials['Charbon'] = max(materials.get('Charbon', 0), random.randint(10, 25))

    random.seed()  # Reset random seed
    return materials


def distance_from_origin(x, y):
    """Calculate distance from origin (0, 0)"""
    return math.sqrt(x**2 + y**2)


def get_location_description_smart(lat, lon, grid_x, grid_y, biome, materials):
    """
    Generate a description based on the materials and biome
    """
    descriptions = []

    # Biome description
    biome_names = {
        'plains': '🌾 Plaines',
        'forest': '🌲 Forêt',
        'mountain': '⛰️ Montagne',
        'steppe': '🌿 Steppe',
        'desert': '🏜️ Désert',
        'savanna': '🦒 Savane',
        'rainforest': '🌳 Forêt tropicale',
        'wetland': '🪵 Marais',
        'coast': '🌊 Côte',
        'farmland': '🚜 Terres agricoles',
        'urban': '🏘️ Zone urbaine',
        'tundra': '❄️ Toundra',
        'taiga': '🌲 Taïga',
        'bog': '🫧 Tourbière',
        'volcano': '🌋 Volcan',
        'canyon': '🏜️ Canyon',
        'jungle': '🦜 Jungle',
        'glacier': '🧊 Glacier',
        'coral_reef': '🪸 Récif corallien',
        'mushroom_forest': '🍄 Forêt de champignons',
        'water': '💧 Lac/Rivière',
    }
    descriptions.append(biome_names.get(biome, biome))

    # Special zones descriptions
    distance = distance_from_origin(grid_x, grid_y)

    if 'Diamant' in materials:
        descriptions.append('💎 Zone diamant')
    elif 'Minerai d\'Or' in materials and materials['Minerai d\'Or'] > 10:
        descriptions.append('✨ Zone aurifère')

    if materials.get('Minerai de Fer', 0) > 15 or materials.get('Charbon', 0) > 15:
        descriptions.append('⚙️ Zone industrielle')

    if sum(1 for m in ['Baie', 'Pomme', 'Champignon'] if m in materials) >= 2:
        descriptions.append('🍎 Zone fertile')

    if distance > 10:
        descriptions.append('🗺️ Terres lointaines')
    elif distance > 5:
        descriptions.append('🏞️ Terres explorées')

    return ' | '.join(descriptions) if descriptions else 'Zone standard'
