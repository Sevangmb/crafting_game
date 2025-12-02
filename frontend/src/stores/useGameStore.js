import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { createPlayerSlice } from './playerSlice';
import { createInventorySlice } from './inventorySlice';
import { createRecipesSlice } from './recipesSlice';
import { createUiSlice } from './uiSlice';
import { createNotificationSlice } from './notificationSlice';
import { createSkillsSlice } from './skillsSlice';

// Store principal qui combine tous les slices
export const useGameStore = create(
  devtools(
    (set, get) => ({
      ...createPlayerSlice(set, get),
      ...createInventorySlice(set, get),
      ...createRecipesSlice(set, get),
      ...createUiSlice(set, get),
      ...createNotificationSlice(set, get),
      ...createSkillsSlice(set, get),

      // Action globale pour reset tout le store
      resetAll: () => {
        const state = get();
        state.resetPlayer();
        state.clearInventory();
        state.clearCraftingHistory();
        set({
          currentTab: 0,
          recipeFlowOpen: false,
          dashboardOpen: false,
          restartDialogOpen: false,
          menuAnchorEl: null,
        });
      },
    }),
    { name: 'GameStore' }
  )
);

// Selectors pour optimiser les re-renders
export const selectPlayer = (state) => state.player;
export const selectInventory = (state) => state.inventory;
export const selectRecipes = (state) => state.recipes;
export const selectIsAuthenticated = (state) => state.isAuthenticated;
export const selectCurrentTab = (state) => state.currentTab;
export const selectCurrentCell = (state) => state.currentCell;
export const selectSkills = (state) => state.skills;
export const selectTalents = (state) => state.talents;
export const selectIsLoading = (state) => state.isLoading;
export const selectIsLoadingKey = (key) => (state) => state.isLoading[key];
