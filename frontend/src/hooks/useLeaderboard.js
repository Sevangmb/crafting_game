import { useState, useCallback } from 'react';
import { leaderboardAPI } from '../services/api';
import { useGameStore } from '../stores/useGameStore';

export function useLeaderboard() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const showNotification = useGameStore((state) => state.showNotification);

  const fetchLeaderboard = useCallback(async (category, limit = 100) => {
    setLoading(true);
    setError(null);
    try {
      const response = await leaderboardAPI.getAll(category, limit);
      return response.data;
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Erreur lors du chargement du classement';
      setError(errorMsg);
      showNotification(errorMsg, 'error');
      return [];
    } finally {
      setLoading(false);
    }
  }, [showNotification]);

  const fetchMyRanks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await leaderboardAPI.getMyRanks();
      return response.data;
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Erreur lors du chargement de vos rangs';
      setError(errorMsg);
      console.error('Failed to fetch my ranks:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchTopPlayers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await leaderboardAPI.getTopPlayers();
      return response.data;
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Erreur lors du chargement des top joueurs';
      setError(errorMsg);
      showNotification(errorMsg, 'error');
      return null;
    } finally {
      setLoading(false);
    }
  }, [showNotification]);

  const updateLeaderboards = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await leaderboardAPI.updateAll();
      showNotification(response.data.message || 'Classements mis à jour', 'success');
      return { success: true, data: response.data };
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Erreur lors de la mise à jour';
      setError(errorMsg);
      showNotification(errorMsg, 'error');
      return { success: false, error: errorMsg };
    } finally {
      setLoading(false);
    }
  }, [showNotification]);

  return {
    loading,
    error,
    fetchLeaderboard,
    fetchMyRanks,
    fetchTopPlayers,
    updateLeaderboards,
  };
}

export default useLeaderboard;
