// Slice pour l'état de l'UI
export const createUiSlice = (set) => ({
  currentTab: 0,
  recipeFlowOpen: false,
  dashboardOpen: false,
  skillsDialogOpen: false,
  restartDialogOpen: false,
  menuAnchorEl: null,

  // Loading states for async operations
  isLoading: {
    player: false,
    inventory: false,
    crafting: false,
    gathering: false,
    moving: false,
    consuming: false,
    skills: false,
  },

  // Persist expanded state for accordions
  inventoryExpandedCategories: (() => {
    try {
      const raw = typeof window !== 'undefined' ? localStorage.getItem('inventoryExpandedCategories') : null;
      const parsed = raw ? JSON.parse(raw) : null;
      if (parsed && typeof parsed === 'object') return parsed;
    } catch (_) {}
    return { nourriture: false, bois: false, minerais: false, gemmes: false, magie: false, divers: false };
  })(),
  craftingExpandedCategories: (() => {
    try {
      const raw = typeof window !== 'undefined' ? localStorage.getItem('craftingExpandedCategories') : null;
      const parsed = raw ? JSON.parse(raw) : null;
      if (parsed && typeof parsed === 'object') return parsed;
    } catch (_) {}
    return { nourriture: false, bois: false, minerais: false, gemmes: false, magie: false, divers: false };
  })(),

  setCurrentTab: (tab) => set({ currentTab: tab }),
  setRecipeFlowOpen: (open) => set({ recipeFlowOpen: open }),
  setDashboardOpen: (open) => set({ dashboardOpen: open }),
  setSkillsDialogOpen: (open) => set({ skillsDialogOpen: open }),
  setRestartDialogOpen: (open) => set({ restartDialogOpen: open }),
  setMenuAnchorEl: (anchorEl) => set({ menuAnchorEl: anchorEl }),

  // Loading state setters
  setLoading: (key, value) =>
    set((state) => ({
      isLoading: { ...state.isLoading, [key]: value },
    })),
  setLoadingMultiple: (updates) =>
    set((state) => ({
      isLoading: { ...state.isLoading, ...updates },
    })),

  toggleRecipeFlow: () =>
    set((state) => ({ recipeFlowOpen: !state.recipeFlowOpen })),
  
  toggleDashboard: () =>
    set((state) => ({ dashboardOpen: !state.dashboardOpen })),

  // Inventory accordions
  toggleInventoryCategory: (category) =>
    set((state) => {
      const next = {
        ...state.inventoryExpandedCategories,
        [category]: !state.inventoryExpandedCategories[category],
      };
      try { if (typeof window !== 'undefined') localStorage.setItem('inventoryExpandedCategories', JSON.stringify(next)); } catch (_) {}
      return { inventoryExpandedCategories: next };
    }),
  setInventoryCategoryExpanded: (category, expanded) =>
    set((state) => {
      const next = {
        ...state.inventoryExpandedCategories,
        [category]: expanded,
      };
      try { if (typeof window !== 'undefined') localStorage.setItem('inventoryExpandedCategories', JSON.stringify(next)); } catch (_) {}
      return { inventoryExpandedCategories: next };
    }),

  // Crafting accordions
  toggleCraftingCategory: (category) =>
    set((state) => {
      const next = {
        ...state.craftingExpandedCategories,
        [category]: !state.craftingExpandedCategories[category],
      };
      try { if (typeof window !== 'undefined') localStorage.setItem('craftingExpandedCategories', JSON.stringify(next)); } catch (_) {}
      return { craftingExpandedCategories: next };
    }),
  setCraftingCategoryExpanded: (category, expanded) =>
    set((state) => {
      const next = {
        ...state.craftingExpandedCategories,
        [category]: expanded,
      };
      try { if (typeof window !== 'undefined') localStorage.setItem('craftingExpandedCategories', JSON.stringify(next)); } catch (_) {}
      return { craftingExpandedCategories: next };
    }),
});
