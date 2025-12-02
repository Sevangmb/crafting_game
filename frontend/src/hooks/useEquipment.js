import { useCallback } from 'react';
import { useGameStore } from '../stores/useGameStore';
import { useNotifications } from './useNotifications';
import { useGameData } from './useGameData';
import axios from 'axios';

export const useEquipment = () => {
    const player = useGameStore((state) => state.player);
    const { success, error } = useNotifications();
    const { fetchPlayerData } = useGameData();

    const equipItem = useCallback(async (materialId, slot) => {
        try {
            await axios.post('/api/equipment/equip/', {
                material_id: materialId,
                slot: slot
            });
            success('Objet équipé avec succès');
            await fetchPlayerData();
        } catch (err) {
            error(err.response?.data?.error || 'Impossible d\'équiper l\'objet');
        }
    }, [success, error, fetchPlayerData]);

    const unequipItem = useCallback(async (slot) => {
        try {
            await axios.post('/api/equipment/unequip/', {
                slot: slot
            });
            success('Objet déséquipé');
            await fetchPlayerData();
        } catch (err) {
            error(err.response?.data?.error || 'Impossible de déséquiper l\'objet');
        }
    }, [success, error, fetchPlayerData]);

    const getEquippedItem = useCallback((slot) => {
        if (!player || !player.equipped_items) return null;
        return player.equipped_items.find(item => item.slot === slot);
    }, [player]);

    return {
        equipItem,
        unequipItem,
        getEquippedItem,
        equippedItems: player?.equipped_items || []
    };
};
