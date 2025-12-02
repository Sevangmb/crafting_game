import { useEffect, useState } from 'react';
import { mapAPI } from '../services/api';

// Simple hook to poll /map/world_state/ periodically
export function useWorldState(pollIntervalMs = 60000) {
  const [state, setState] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;
    let timer = null;

    const fetchState = async () => {
      setLoading(true);
      try {
        const res = await mapAPI.getWorldState();
        if (isMounted) {
          setState(res.data || null);
          setError(null);
        }
      } catch (e) {
        if (isMounted) {
          setError(e);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    // initial load
    fetchState();

    if (pollIntervalMs > 0) {
      timer = setInterval(fetchState, pollIntervalMs);
    }

    return () => {
      isMounted = false;
      if (timer) clearInterval(timer);
    };
  }, [pollIntervalMs]);

  return { worldState: state, loading, error };
}
