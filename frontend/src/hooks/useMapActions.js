import { useState, useCallback } from 'react';
import { playerAPI, mapAPI } from '../services/api';
import { useGameStore } from '../stores/useGameStore';
import { useAchievements } from './useAchievements';
import logger from '../utils/logger';

export const useMapActions = (onPlayerUpdate, onCellUpdate, onGather) => {
    const [loading, setLoading] = useState(false);
    const showNotification = useGameStore((state) => state.showNotification);
    const { handleAchievements } = useAchievements();

    const move = useCallback(async (playerId, direction, energy) => {
        if (energy < 1) {
            showNotification('Pas assez d\'énergie pour se déplacer!', 'warning');
            return { success: false };
        }

        setLoading(true);
        try {
            const response = await playerAPI.move(playerId, direction);
            onPlayerUpdate(response.data);

            // Handle achievements
            handleAchievements(response);

            showNotification('Déplacement réussi', 'success');

            // Return encounter data if present
            return {
                success: true,
                encounter: response.data.encounter || null
            };
        } catch (error) {
            logger.error('Failed to move:', error);
            const errorMsg = error.response?.data?.error || 'Échec du déplacement';
            showNotification(errorMsg, 'error');
            return { success: false };
        } finally {
            setLoading(false);
        }
    }, [onPlayerUpdate, showNotification, handleAchievements]);

    const gather = useCallback(async (cellId, materialId, fetchCurrentCell) => {
        setLoading(true);
        try {
            const response = await mapAPI.gather(cellId, materialId);

            // Handle achievements
            handleAchievements(response);

            showNotification(response.data.message, 'success');

            // Refresh data
            if (fetchCurrentCell) await fetchCurrentCell();
            if (onGather) onGather();

            return true;
        } catch (error) {
            const msg = error.response?.data?.error || 'Échec de la récolte';

            // Tool advice logic
            if (typeof msg === 'string') {
                if (msg.includes('pioche')) {
                    showNotification('Outil requis: Pioche. Fabrique une Pioche ou Pioche en Bronze.', 'warning');
                } else if (msg.includes('hache')) {
                    showNotification('Outil requis: Hache. Hache en Pierre (départ) ou Hache en Fer (meilleure).', 'warning');
                } else if (msg.includes('canne à pêche') || msg.includes('pêcher')) {
                    showNotification('Outil requis: Canne à Pêche.', 'warning');
                } else if (msg.includes('arc') || msg.includes('chasser')) {
                    showNotification('Outil requis: Arc.', 'warning');
                } else if (msg.includes('énergie')) {
                    showNotification('Pas assez d\'énergie. Les bons outils réduisent le coût!', 'warning');
                } else {
                    showNotification(msg, 'error');
                }
            } else {
                showNotification(msg, 'error');
            }

            // Resync on 400 error
            try {
                if (fetchCurrentCell) await fetchCurrentCell();
                const me = await playerAPI.getMe();
                onPlayerUpdate(me.data);
            } catch (_) { }

            return false;
        } finally {
            setLoading(false);
        }
    }, [onGather, onPlayerUpdate, showNotification, handleAchievements]);

    return {
        move,
        gather,
        loading
    };
};
