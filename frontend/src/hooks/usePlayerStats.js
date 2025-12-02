import { useMemo } from 'react';
import { useGameStore, selectPlayer } from '../stores/useGameStore';

/**
 * Hook pour centraliser les calculs des statistiques du joueur
 * Évite la duplication de logique entre PlayerStats et PlayerStatsCompact
 */
export const usePlayerStats = () => {
    const player = useGameStore(selectPlayer);

    const stats = useMemo(() => {
        if (!player) return null;

        // Calcul des pourcentages
        const energyPercent = (player.energy / player.max_energy) * 100;
        const healthPercent = (player.health / player.max_health) * 100;
        const hungerPercent = (player.hunger / player.max_hunger) * 100;
        const thirstPercent = (player.thirst / player.max_thirst) * 100;
        const radiationPercent = (player.radiation / 100) * 100;
        const weightPercent = (player.current_carry_weight / player.effective_carry_capacity) * 100;
        const xpForNextLevel = player.level * 100;
        const xpPercent = (player.experience / xpForNextLevel) * 100;

        // Fonction pour déterminer la couleur de la barre
        const getBarColor = (percent, inverted = false) => {
            if (inverted) {
                // Pour radiation - low is good, high is bad
                if (percent < 30) return 'success.main';
                if (percent < 60) return 'warning.main';
                return 'error.main';
            } else {
                // Pour health/hunger/thirst - high is good, low is bad
                if (percent > 50) return 'success.main';
                if (percent > 20) return 'warning.main';
                return 'error.main';
            }
        };

        // États dérivés
        const isLowEnergy = energyPercent < 30;
        const isLowHealth = healthPercent < 30;
        const isLowHunger = hungerPercent < 30;
        const isLowThirst = thirstPercent < 30;
        const isHighRadiation = radiationPercent > 60;

        return {
            // Données brutes
            player,

            // Pourcentages
            energyPercent,
            healthPercent,
            hungerPercent,
            thirstPercent,
            radiationPercent,
            weightPercent,
            xpPercent,
            xpForNextLevel,

            // Couleurs
            energyColor: getBarColor(energyPercent),
            healthColor: getBarColor(healthPercent),
            hungerColor: getBarColor(hungerPercent),
            thirstColor: getBarColor(thirstPercent),
            radiationColor: getBarColor(radiationPercent, true),
            weightColor: player.is_overencumbered ? 'error' : weightPercent > 80 ? 'warning' : 'default',

            // États booléens
            isLowEnergy,
            isLowHealth,
            isLowHunger,
            isLowThirst,
            isHighRadiation,

            // Fonction utilitaire
            getBarColor
        };
    }, [player]);

    return stats;
};

export default usePlayerStats;
