import { useState, useCallback } from 'react';
import { questsAPI } from '../services/api';
import { useGameStore } from '../stores/useGameStore';

export function useQuests() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const showNotification = useGameStore((state) => state.showNotification);

  const fetchAvailable = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await questsAPI.getAvailable();
      return response.data;
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Erreur lors du chargement des quêtes';
      setError(errorMsg);
      showNotification(errorMsg, 'error');
      return [];
    } finally {
      setLoading(false);
    }
  }, [showNotification]);

  const fetchActive = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await questsAPI.getActive();
      return response.data;
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Erreur lors du chargement des quêtes actives';
      setError(errorMsg);
      showNotification(errorMsg, 'error');
      return [];
    } finally {
      setLoading(false);
    }
  }, [showNotification]);

  const acceptQuest = useCallback(async (questId) => {
    setLoading(true);
    setError(null);
    try {
      const response = await questsAPI.accept(questId);
      showNotification(response.data.message || 'Quête acceptée!', 'success');
      return { success: true, data: response.data };
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Erreur lors de l\'acceptation';
      setError(errorMsg);
      showNotification(errorMsg, 'error');
      return { success: false, error: errorMsg };
    } finally {
      setLoading(false);
    }
  }, [showNotification]);

  const abandonQuest = useCallback(async (questId) => {
    setLoading(true);
    setError(null);
    try {
      const response = await questsAPI.abandon(questId);
      showNotification(response.data.message || 'Quête abandonnée', 'info');
      return { success: true, data: response.data };
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Erreur lors de l\'abandon';
      setError(errorMsg);
      showNotification(errorMsg, 'error');
      return { success: false, error: errorMsg };
    } finally {
      setLoading(false);
    }
  }, [showNotification]);

  const getQuestStats = useCallback(async () => {
    try {
      const response = await questsAPI.getStats();
      return response.data;
    } catch (err) {
      console.error('Failed to fetch quest stats:', err);
      return null;
    }
  }, []);

  return {
    loading,
    error,
    fetchAvailable,
    fetchActive,
    acceptQuest,
    abandonQuest,
    getQuestStats,
  };
}

export default useQuests;
