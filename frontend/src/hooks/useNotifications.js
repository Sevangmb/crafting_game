import { useGameStore } from '../stores/useGameStore';

/**
 * Hook personnalisé pour gérer les notifications
 */
export const useNotifications = () => {
  const showNotification = useGameStore((state) => state.showNotification);

  return {
    success: (message) => showNotification(message, 'success'),
    error: (message) => showNotification(message, 'error'),
    warning: (message) => showNotification(message, 'warning'),
    info: (message) => showNotification(message, 'info'),
    // Méthode générique
    show: showNotification,
  };
};
