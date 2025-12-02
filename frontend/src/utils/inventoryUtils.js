export const groupInventory = (inventory) => {
  // If API returns already grouped object
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

  const safe = Array.isArray(inventory) ? inventory : [];
  if (!safe.length) {
    return {
      nourriture: [],
      bois: [],
      minerais: [],
      gemmes: [],
      magie: [],
      divers: []
    };
  }

  const categories = {
    nourriture: [],
    bois: [],
    minerais: [],
    gemmes: [],
    magie: [],
    divers: []
  };

  safe.forEach(item => {
    let category = 'divers';
    const name = item.material?.name?.toLowerCase() || '';

    if (item.material?.is_food) {
      category = 'nourriture';
    } else if (name.includes('bois') || name.includes('planche') || name.includes('bâton')) {
      category = 'bois';
    } else if (name.includes('pierre') || name.includes('minerai') || name.includes('fer') ||
              name.includes('cuivre') || name.includes('or') || name.includes('argent')) {
      category = 'minerais';
    } else if (name.includes('rubis') || name.includes('émeraude') || name.includes('diamant') ||
              name.includes('saphir') || name.includes('améthyste') || name.includes('jaspe') ||
              name.includes('jade') || name.includes('agate')) {
      category = 'gemmes';
    } else if (name.includes('poussière') || name.includes('cristal') ||
              name.includes('pierre de lune') || name.includes('perle')) {
      category = 'magie';
    }

    if (categories[category]) {
      categories[category].push(item);
    } else {
      categories.divers.push(item);
    }
  });

  return categories;
};
