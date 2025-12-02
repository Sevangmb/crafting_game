// Slice pour les notifications (Snackbar)
export const createNotificationSlice = (set, get) => ({
  notifications: [],

  showNotification: (message, severity = 'info', options = {}) => {
    const id = Date.now() + Math.random();
    set((state) => ({
      notifications: [
        ...state.notifications,
        { id, message, severity, open: true, ...options },
      ],
    }));

    // Auto-fermeture après durée spécifiée ou 4 secondes
    const duration = options.duration || 4000;
    setTimeout(() => {
      get().hideNotification(id);
    }, duration);
  },

  // Notification spéciale pour les achievements
  showAchievementNotification: (achievement) => {
    const id = Date.now() + Math.random();
    set((state) => ({
      notifications: [
        ...state.notifications,
        {
          id,
          message: `${achievement.icon} ${achievement.name}`,
          severity: 'success',
          open: true,
          isAchievement: true,
          achievement,
        },
      ],
    }));

    // Achievement notifications durent plus longtemps (6 secondes)
    setTimeout(() => {
      get().hideNotification(id);
    }, 6000);
  },

  hideNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.map((notif) =>
        notif.id === id ? { ...notif, open: false } : notif
      ),
    })),

  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((notif) => notif.id !== id),
    })),
});
