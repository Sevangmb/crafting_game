import { useEffect, useCallback } from 'react';
import { useGameStore } from '../stores/useGameStore';
import { useGameData } from './useGameData';

export const useAuth = () => {
    const setIsAuthenticated = useGameStore((state) => state.setIsAuthenticated);
    const isAuthenticated = useGameStore((state) => state.isAuthenticated);
    const { fetchPlayerData } = useGameData();

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            setIsAuthenticated(true);
            fetchPlayerData();
        }
    }, [setIsAuthenticated, fetchPlayerData]);

    const login = useCallback(() => {
        setIsAuthenticated(true);
        fetchPlayerData();
    }, [setIsAuthenticated, fetchPlayerData]);

    const logout = useCallback(() => {
        localStorage.removeItem('token');
        useGameStore.getState().resetPlayer();
        setIsAuthenticated(false); // Ensure state is updated
    }, [setIsAuthenticated]);

    return {
        isAuthenticated,
        login,
        logout
    };
};
