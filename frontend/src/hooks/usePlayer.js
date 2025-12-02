import { useGameStore } from '../stores/useGameStore';

/**
 * Hook personnalisé pour accéder facilement aux données du joueur
 */
export const usePlayer = () => {
  const player = useGameStore((state) => state.player);
  const setPlayer = useGameStore((state) => state.setPlayer);
  const updatePlayer = useGameStore((state) => state.updatePlayer);
  const currentCell = useGameStore((state) => state.currentCell);
  const setCurrentCell = useGameStore((state) => state.setCurrentCell);

  return {
    player,
    setPlayer,
    updatePlayer,
    currentCell,
    setCurrentCell,
    // Helpers calculés
    hasEnergy: (amount) => player?.energy >= amount,
    energyPercent: player ? (player.energy / player.max_energy) * 100 : 0,
    isLowEnergy: player ? player.energy < 20 : false,
  };
};
