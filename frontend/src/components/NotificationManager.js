import React from 'react';
import { Snackbar, Alert, Slide, Box, Typography } from '@mui/material';
import {
  CheckCircle,
  Error,
  Warning,
  Info,
  EmojiEvents,
} from '@mui/icons-material';
import { useGameStore } from '../stores/useGameStore';

function SlideTransition(props) {
  return <Slide {...props} direction="up" />;
}

const iconMapping = {
  success: <CheckCircle fontSize="inherit" />,
  error: <Error fontSize="inherit" />,
  warning: <Warning fontSize="inherit" />,
  info: <Info fontSize="inherit" />,
};

function NotificationManager() {
  const notifications = useGameStore((state) => state.notifications || []);
  const removeNotification = useGameStore((state) => state.removeNotification);

  return (
    <>
      {notifications.map((notification, index) => {
        // Achievement notifications have special styling
        const isAchievement = notification.isAchievement;
        const achievement = notification.achievement;

        return (
          <Snackbar
            key={notification.id}
            open={notification.open}
            autoHideDuration={isAchievement ? 6000 : 4000}
            onClose={() => removeNotification(notification.id)}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            TransitionComponent={SlideTransition}
            sx={{ bottom: `${24 + index * (isAchievement ? 100 : 70)}px !important` }}
          >
            <Alert
              onClose={() => removeNotification(notification.id)}
              severity={notification.severity}
              variant="filled"
              icon={isAchievement ? <EmojiEvents sx={{ fontSize: 32 }} /> : iconMapping[notification.severity]}
              sx={{
                width: '100%',
                minWidth: isAchievement ? '350px' : '300px',
                borderRadius: 2,
                boxShadow: isAchievement
                  ? '0 12px 24px rgba(255, 215, 0, 0.4)'
                  : '0 8px 16px rgba(0,0,0,0.3)',
                animation: isAchievement
                  ? 'achievementPulse 0.6s ease-in-out'
                  : 'fadeIn 0.3s ease-in-out',
                background: isAchievement
                  ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                  : undefined,
                '& .MuiAlert-icon': {
                  fontSize: isAchievement ? 36 : 28,
                },
                '@keyframes achievementPulse': {
                  '0%': { transform: 'scale(0.9)', opacity: 0 },
                  '50%': { transform: 'scale(1.05)' },
                  '100%': { transform: 'scale(1)', opacity: 1 },
                },
              }}
            >
              {isAchievement ? (
                <Box>
                  <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 0.5 }}>
                    🏆 Achievement débloqué !
                  </Typography>
                  <Typography variant="body1" sx={{ fontWeight: 600 }}>
                    {notification.message}
                  </Typography>
                  {achievement?.description && (
                    <Typography variant="caption" sx={{ opacity: 0.9, display: 'block', mt: 0.5 }}>
                      {achievement.description}
                    </Typography>
                  )}
                  {achievement?.reward_xp > 0 && (
                    <Typography variant="caption" sx={{ opacity: 0.9, display: 'block', mt: 0.5, fontWeight: 600 }}>
                      +{achievement.reward_xp} XP
                    </Typography>
                  )}
                </Box>
              ) : (
                notification.message
              )}
            </Alert>
          </Snackbar>
        );
      })}
    </>
  );
}

export default NotificationManager;
