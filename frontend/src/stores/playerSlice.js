// Slice pour le state du joueur
export const createPlayerSlice = (set, get) => ({
  player: null,
  isAuthenticated: false,
  currentCell: null,

  setPlayer: (player) => set({ player }),
  setIsAuthenticated: (isAuthenticated) => set({ isAuthenticated }),
  setCurrentCell: (currentCell) => set({ currentCell }),

  updatePlayer: (updates) =>
    set((state) => ({
      player: state.player ? { ...state.player, ...updates } : null,
    })),

  resetPlayer: () =>
    set({
      player: null,
      isAuthenticated: false,
      currentCell: null,
    }),
});
