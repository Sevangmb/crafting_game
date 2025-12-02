// Slice pour l'inventaire et les items
export const createInventorySlice = (set, get) => ({
  inventory: [],
  materials: [],
  loading: false,

  setInventory: (inventory) => set({ inventory }),
  setMaterials: (materials) => set({ materials }),
  setLoading: (loading) => set({ loading }),

  addInventoryItem: (item) =>
    set((state) => {
      const existingIndex = state.inventory.findIndex(
        (i) => i.material.id === item.material.id
      );
      if (existingIndex >= 0) {
        const newInventory = [...state.inventory];
        newInventory[existingIndex] = {
          ...newInventory[existingIndex],
          quantity: newInventory[existingIndex].quantity + item.quantity,
        };
        return { inventory: newInventory };
      }
      return { inventory: [...state.inventory, item] };
    }),

  updateInventoryItem: (itemId, updates) =>
    set((state) => ({
      inventory: state.inventory.map((item) =>
        item.id === itemId ? { ...item, ...updates } : item
      ),
    })),

  removeInventoryItem: (itemId) =>
    set((state) => ({
      inventory: state.inventory.filter((item) => item.id !== itemId),
    })),

  clearInventory: () => set({ inventory: [] }),

  // Statistiques calculées
  getInventoryStats: () => {
    const state = get();
    const flat = Array.isArray(state.inventory)
      ? state.inventory
      : state.inventory && typeof state.inventory === 'object'
        ? Object.values(state.inventory).flat()
        : [];
    const total = flat.length;
    const foodCount = flat.filter((i) => i.material.is_food).length;
    const rarityCount = flat.reduce((acc, item) => {
      const rarity = item.material.rarity;
      acc[rarity] = (acc[rarity] || 0) + 1;
      return acc;
    }, {});

    return {
      total,
      foodCount,
      materialCount: total - foodCount,
      rarityCount,
    };
  },
});
