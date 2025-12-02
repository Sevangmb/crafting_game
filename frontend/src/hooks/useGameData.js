import { useCallback, useEffect } from 'react';
import { playerAPI, inventoryAPI } from '../services/api';
import { useGameStore } from '../stores/useGameStore';
import logger from '../utils/logger';

export const useGameData = () => {
    const setPlayer = useGameStore((state) => state.setPlayer);
    const setInventory = useGameStore((state) => state.setInventory);
    const resetPlayer = useGameStore((state) => state.resetPlayer);
    const setIsAuthenticated = useGameStore((state) => state.setIsAuthenticated);
    const showNotification = useGameStore((state) => state.showNotification);
    const isAuthenticated = useGameStore((state) => state.isAuthenticated);

    const fetchPlayerData = useCallback(async () => {
        logger.debug('useGameData', 'fetchPlayerData called');
        try {
            logger.debug('useGameData', 'Fetching player data...');
            const [playerResponse, inventoryResponse] = await Promise.all([
                playerAPI.getMe(),
                inventoryAPI.getAll(),
            ]);
            logger.debug('useGameData', 'Player data received:', playerResponse.data);

            // Check if energy was regenerated
            if (playerResponse.data.energy_regenerated > 0) {
                const minutes = playerResponse.data.minutes_offline;
                const energy = playerResponse.data.energy_regenerated;
                showNotification(
                    `⚡ +${energy} énergie régénérée (${minutes} min offline)`,
                    'success'
                );
            }

            setPlayer(playerResponse.data);
            setInventory(inventoryResponse.data);
        } catch (error) {
            logger.error('Failed to fetch player data:', error);
            if (error.response?.status === 401) {
                logger.warn('401 Unauthorized - resetting player session');
                resetPlayer();
                setIsAuthenticated(false);
            }
        }
    }, [setPlayer, setInventory, resetPlayer, setIsAuthenticated, showNotification]);

    const refreshInventory = useCallback(async () => {
        try {
            const response = await inventoryAPI.getAll();
            setInventory(response.data);
            const playerResponse = await playerAPI.getMe();
            setPlayer(playerResponse.data);
        } catch (error) {
            logger.error('Failed to refresh inventory:', error);
        }
    }, [setInventory, setPlayer]);

    // Auto-save: Periodically fetch player data to keep game state synchronized
    useEffect(() => {
        if (!isAuthenticated) {
            return;
        }

        // Initial fetch
        fetchPlayerData();

        // Set up auto-save interval (every 2 minutes)
        const AUTO_SAVE_INTERVAL = 2 * 60 * 1000; // 2 minutes in milliseconds
        const intervalId = setInterval(() => {
            logger.debug('useGameData', 'Auto-save: fetching player data');
            fetchPlayerData();
        }, AUTO_SAVE_INTERVAL);

        // Cleanup interval on unmount
        return () => {
            clearInterval(intervalId);
        };
    }, [isAuthenticated, fetchPlayerData]);

    return {
        fetchPlayerData,
        refreshInventory
    };
};
