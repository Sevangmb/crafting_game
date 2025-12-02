import { useGameStore } from '../stores/useGameStore';

/**
 * Hook pour gérer les achievements débloqués dans les réponses API
 */
export const useAchievements = () => {
  const showAchievementNotification = useGameStore(
    (state) => state.showAchievementNotification
  );

  /**
   * Vérifie si la réponse API contient des achievements débloqués
   * et affiche les notifications appropriées
   *
   * @param {Object} response - Réponse de l'API (axios response)
   */
  const handleAchievements = (response) => {
    if (response?.data?.achievements_unlocked) {
      const achievements = response.data.achievements_unlocked;

      // Afficher une notification pour chaque achievement débloqué
      achievements.forEach((achievement, index) => {
        // Décalage pour que les notifications n'apparaissent pas toutes en même temps
        setTimeout(() => {
          showAchievementNotification(achievement);
        }, index * 300); // 300ms de décalage entre chaque
      });

      return achievements;
    }

    return [];
  };

  return {
    handleAchievements,
  };
};
