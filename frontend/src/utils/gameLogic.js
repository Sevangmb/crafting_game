// Constantes et utilitaires pour la logique de jeu
// Centralise les calculs de biomes, raretés, catégories, etc.
import useConfigStore from '../stores/useConfigStore';

const getConfigs = () => useConfigStore.getState();

// Icônes pour les catégories
export const CATEGORY_ICONS = {
  nourriture: getConfigs().categoryIcons?.nourriture || '🍎',
  bois: getConfigs().categoryIcons?.bois || '🪵',
  minerais: getConfigs().categoryIcons?.minerais || '⛏️',
  gemmes: getConfigs().categoryIcons?.gemmes || '💎',
  magie: getConfigs().categoryIcons?.magie || '✨',
  divers: getConfigs().categoryIcons?.divers || '📦',
};

// Noms affichés pour les catégories
export const CATEGORY_NAMES = {
  nourriture: getConfigs().categoryNames?.nourriture || 'Nourriture',
  bois: getConfigs().categoryNames?.bois || 'Bois & Matériaux',
  minerais: getConfigs().categoryNames?.minerais || 'Minerais & Pierres',
  gemmes: getConfigs().categoryNames?.gemmes || 'Gemmes Précieuses',
  magie: getConfigs().categoryNames?.magie || 'Objets Magiques',
  divers: getConfigs().categoryNames?.divers || 'Divers',
};

// Couleurs pour les raretés
export const RARITY_COLORS = getConfigs().rarityColors || {
  common: '#9e9e9e',
  uncommon: '#4caf50',
  rare: '#2196f3',
  epic: '#9c27b0',
  legendary: '#ff9800',
  mythic: '#e91e63',
};

// Couleurs MUI pour les raretés (pour les Chips)
export const RARITY_CHIP_COLORS = getConfigs().rarityChipColors || {
  legendary: 'error',
  epic: 'secondary',
  rare: 'warning',
  uncommon: 'info',
  common: 'default',
  mythic: 'default',
};

// Configurations des biomes
export const BIOME_CONFIG = getConfigs().biomeConfig || {
  forest: {
    color: '#228B22',
    name: 'Forêt 🌲',
  },
  water: {
    color: '#4169E1',
    name: 'Eau 💧',
  },
  mountain: {
    color: '#8B7355',
    name: 'Montagne ⛰️',
  },
  plains: {
    color: '#9ACD32',
    name: 'Plaines 🌾',
  },
  steppe: {
    color: '#C2B280',
    name: 'Steppe 🌿',
  },
  desert: {
    color: '#EDC9AF',
    name: 'Désert 🏜️',
  },
  savanna: {
    color: '#D4A76A',
    name: 'Savane 🦒',
  },
  rainforest: {
    color: '#0B6623',
    name: 'Forêt tropicale 🌳',
  },
  wetland: {
    color: '#4A7C59',
    name: 'Marais 🪵',
  },
  coast: {
    color: '#5F9EA0',
    name: 'Côte 🌊',
  },
  farmland: {
    color: '#8B4513',
    name: 'Terres agricoles 🚜',
  },
  urban: {
    color: '#696969',
    name: 'Zone urbaine 🏘️',
  },
  tundra: {
    color: '#E0E0E0',
    name: 'Toundra ❄️',
  },
  taiga: {
    color: '#2F4F4F',
    name: 'Taïga 🌲',
  },
  bog: {
    color: '#556B2F',
    name: 'Tourbière 🫧',
  },
  volcano: {
    color: '#DC143C',
    name: 'Volcan 🌋',
  },
  canyon: {
    color: '#CD853F',
    name: 'Canyon 🏜️',
  },
  jungle: {
    color: '#006400',
    name: 'Jungle 🦜',
  },
  glacier: {
    color: '#B0E0E6',
    name: 'Glacier 🧊',
  },
  coral_reef: {
    color: '#FF7F50',
    name: 'Récif corallien 🪸',
  },
  mushroom_forest: {
    color: '#8B4789',
    name: 'Forêt de champignons 🍄',
  },
  water: {
    color: '#1E90FF',
    name: 'Lac/Rivière 💧',
  },
};

// Outils requis pour les matériaux
export const TOOL_REQUIREMENTS = {
  // Outils de minage
  pickaxe: ['minerai', 'diamant', 'rubis', 'émeraude', 'saphir', 'or', 'argent', 'cuivre', 'fer'],
  // Outils de coupe
  axe: ['bois', 'tronc'],
  // Outils de pêche
  fishing_rod: ['poisson', 'poissons'],
  // Outils de chasse
  bow: ['viande', 'cuir'],
};

// Fonction pour obtenir la couleur d'un biome
export const getBiomeColor = (biome) => {
  const { biomeConfig } = getConfigs();
  const fallback = biomeConfig?.plains?.color || '#9ACD32';
  return biomeConfig?.[biome]?.color || fallback;
};

// Fonction pour obtenir le nom d'un biome
export const getBiomeName = (biome) => {
  const { biomeConfig } = getConfigs();
  const fallback = biomeConfig?.plains?.name || 'Plaines';
  return biomeConfig?.[biome]?.name || fallback;
};

// Fonction pour obtenir la couleur de rareté avec opacité
export const getRarityColor = (rarity, opacity = 1) => {
  const { rarityColors } = getConfigs();
  const baseColor = rarityColors?.[rarity?.toLowerCase()] || rarityColors?.common || '#9e9e9e';
  if (opacity === 1) return baseColor;

  // Convertir hex vers rgba
  const hex = baseColor.replace('#', '');
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);
  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
};

// Fonction pour obtenir la couleur Chip MUI pour une rareté
export const getRarityChipColor = (rarity) => {
  const { rarityChipColors } = getConfigs();
  return rarityChipColors?.[rarity?.toLowerCase()] || rarityChipColors?.common || 'default';
};

// Fonction pour classifier un matériau selon sa catégorie
export const classifyMaterial = (material) => {
  if (!material || !material.name) return 'divers';

  const name = material.name.toLowerCase();

  if (material.is_food) return 'nourriture';

  if (name.includes('bois') || name.includes('planche') || name.includes('bâton')) {
    return 'bois';
  }

  if (name.includes('pierre') || name.includes('minerai') || name.includes('fer') ||
    name.includes('cuivre') || name.includes('or') || name.includes('argent')) {
    return 'minerais';
  }

  if (name.includes('rubis') || name.includes('émeraude') || name.includes('diamant') ||
    name.includes('saphir') || name.includes('améthyste') || name.includes('jaspe') ||
    name.includes('jade') || name.includes('agate')) {
    return 'gemmes';
  }

  if (name.includes('rune') || name.includes('poussière') || name.includes('essence') ||
    name.includes('cristal') || name.includes('amulette') || name.includes('parchemin')) {
    return 'magie';
  }

  return 'divers';
};

// Fonction pour classifier une recette selon sa catégorie
export const classifyRecipe = (recipe) => {
  if (!recipe || !recipe.result_material) return 'divers';
  return classifyMaterial(recipe.result_material);
};

// Fonction pour regrouper les recettes par catégories
export const groupRecipesByCategory = (recipes) => {
  const categories = {
    nourriture: [],
    bois: [],
    minerais: [],
    gemmes: [],
    magie: [],
    divers: [],
  };

  recipes.forEach((recipe) => {
    const category = classifyRecipe(recipe);
    categories[category].push(recipe);
  });

  return categories;
};

// Fonction pour regrouper l'inventaire par catégories
export const groupInventoryByCategory = (inventory) => {
  // Si l'inventaire est déjà groupé par catégorie (format de l'API)
  if (inventory && typeof inventory === 'object' && !Array.isArray(inventory)) {
    return {
      nourriture: inventory.nourriture || [],
      bois: inventory.bois || [],
      minerais: inventory.minerais || [],
      gemmes: inventory.gemmes || [],
      magie: inventory.magie || [],
      divers: inventory.divers || []
    };
  }

  // Sinon, créer le regroupement à partir d'un tableau plat
  const safe = Array.isArray(inventory) ? inventory : [];

  const categories = {
    nourriture: [],
    bois: [],
    minerais: [],
    gemmes: [],
    magie: [],
    divers: []
  };

  safe.forEach((item) => {
    const category = classifyMaterial(item.material);
    categories[category].push(item);
  });

  return categories;
};

// Fonction pour déterminer l'outil requis pour un matériau
export const getRequiredTool = (materialName) => {
  if (!materialName) return null;

  const name = materialName.toLowerCase();

  if (TOOL_REQUIREMENTS.pickaxe.some(keyword => name.includes(keyword))) {
    return 'Pioche';
  }
  if (TOOL_REQUIREMENTS.axe.some(keyword => name.includes(keyword))) {
    return 'Hache';
  }
  if (TOOL_REQUIREMENTS.fishing_rod.some(keyword => name.includes(keyword))) {
    return 'Canne à Pêche';
  }
  if (TOOL_REQUIREMENTS.bow.some(keyword => name.includes(keyword))) {
    return 'Arc';
  }

  return null;
};

// Fonction pour vérifier si le joueur a l'outil requis
export const hasRequiredTool = (requiredTool, inventory) => {
  if (!requiredTool || !inventory) return true;

  const flatInventory = Array.isArray(inventory)
    ? inventory
    : Object.values(inventory).flat();

  const toolPrefixes = {
    'Pioche': ['pioche'],
    'Hache': ['hache'],
    'Canne à Pêche': ['canne à pêche'],
    'Arc': ['arc'],
  };

  const prefixes = toolPrefixes[requiredTool] || [];
  return prefixes.some(prefix =>
    flatInventory.some(item =>
      item.material?.name?.toLowerCase().startsWith(prefix.toLowerCase()) &&
      item.quantity > 0
    )
  );
};

// Fonction pour vérifier si un matériau est une station de travail
export const isWorkstationMaterial = (name) => {
  if (!name) return false;
  const n = name.toLowerCase();
  return ['établi', 'étau', 'banc de menuisier', "banc d'archer"].some(k => n === k);
};

// Fonction pour vérifier si un matériau est crafted (fabriqué)
export const isCraftedMaterial = (name) => {
  if (!name) return false;
  return name.match(/Planches|Bâton|Barre|Pioche|Épée|Hache|Pioche|Pelle/) !== null;
};

// Fonction pour calculer les statistiques d'inventaire
export const calculateInventoryStats = (inventory) => {
  const flat = Array.isArray(inventory)
    ? inventory
    : Object.values(inventory || {}).flat();

  const total = flat.length;
  const totalQuantity = flat.reduce((sum, item) => sum + (item.quantity || 0), 0);
  const foodCount = flat.filter((i) => i.material?.is_food).length;

  // Compter par rareté
  const rarityCount = flat.reduce((acc, item) => {
    const rarity = item.material?.rarity || 'common';
    acc[rarity] = (acc[rarity] || 0) + 1;
    return acc;
  }, {});

  // Top 5 des items par quantité
  const topItems = [...flat]
    .sort((a, b) => (b.quantity || 0) - (a.quantity || 0))
    .slice(0, 5);

  return {
    total,
    totalQuantity,
    foodCount,
    rarityCount,
    topItems,
  };
};

// Fonction pour calculer les statistiques de crafting
export const calculateCraftingStats = (craftingHistory) => {
  const totalCrafts = craftingHistory.length;

  // Compter les crafts par recette
  const craftsByRecipe = craftingHistory.reduce((acc, craft) => {
    const recipeName = craft.recipeName || 'Unknown';
    acc[recipeName] = (acc[recipeName] || 0) + (craft.quantity || 1);
    return acc;
  }, {});

  // Top 5 des recettes les plus craftées
  const topRecipes = Object.entries(craftsByRecipe)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5)
    .map(([name, count]) => ({ name, count }));

  return {
    totalCrafts,
    craftsByRecipe,
    topRecipes,
  };
};