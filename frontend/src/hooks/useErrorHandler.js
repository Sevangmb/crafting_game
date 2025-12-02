import { useCallback } from 'react';
import { useGameStore } from '../stores/useGameStore';
import logger from '../utils/logger';

/**
 * Hook personnalisé pour la gestion standardisée des erreurs
 * Combine le logging et les notifications utilisateur
 */
export const useErrorHandler = () => {
    const showNotification = useGameStore((state) => state.showNotification);

    /**
     * Gère une erreur en la loggant et en affichant une notification
     * @param {Error} error - L'erreur à gérer
     * @param {string} userMessage - Message à afficher à l'utilisateur
     * @param {object} context - Contexte additionnel pour le debug
     */
    const handleError = useCallback((error, userMessage, context = {}) => {
        // Log l'erreur complète pour le debug
        logger.error('Error occurred:', {
            message: error?.message || error,
            context,
            stack: error?.stack,
            response: error?.response?.data
        });

        // Affiche une notification à l'utilisateur
        const displayMessage = userMessage ||
            error?.response?.data?.error ||
            error?.message ||
            'Une erreur est survenue';

        showNotification(displayMessage, 'error');
    }, [showNotification]);

    /**
     * Gère une erreur 401 (non autorisé)
     */
    const handle401Error = useCallback(() => {
        logger.warn('401 Unauthorized - Resetting player session');
        const resetPlayer = useGameStore.getState().resetPlayer;
        resetPlayer();
    }, []);

    return {
        handleError,
        handle401Error
    };
};

export default useErrorHandler;
