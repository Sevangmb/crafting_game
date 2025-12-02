import { useCallback } from 'react';
import { useGameStore } from '../stores/useGameStore';
import { playerAPI } from '../services/api';
import { useNotifications } from './useNotifications';
import { useGameData } from './useGameData';
import logger from '../utils/logger';

export const useGameActions = () => {
    const setRestartDialogOpen = useGameStore((state) => state.setRestartDialogOpen);
    const restartDialogOpen = useGameStore((state) => state.restartDialogOpen);
    const { success, error } = useNotifications();
    const { fetchPlayerData } = useGameData();

    const openRestartDialog = useCallback(() => {
        setRestartDialogOpen(true);
    }, [setRestartDialogOpen]);

    const closeRestartDialog = useCallback(() => {
        setRestartDialogOpen(false);
    }, [setRestartDialogOpen]);

    const restartGame = useCallback(async () => {
        try {
            await playerAPI.restart();
            setRestartDialogOpen(false);
            await fetchPlayerData();
            success('Partie recommencée avec succès!');
        } catch (err) {
            logger.error('Failed to restart game:', err);
            error('Échec du recommencement de la partie');
        }
    }, [setRestartDialogOpen, fetchPlayerData, success, error]);

    return {
        restartDialogOpen,
        openRestartDialog,
        closeRestartDialog,
        restartGame
    };
};
