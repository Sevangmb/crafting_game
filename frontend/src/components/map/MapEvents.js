import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  Alert,
} from '@mui/material';
import {
  CardGiftcard as TreasureIcon,
  Storefront as MerchantIcon,
  Spa as ResourceIcon,
  Cloud as WeatherIcon,
  EmojiEvents as RewardIcon,
} from '@mui/icons-material';
import { eventsAPI } from '../../services/api';

const MapEvents = ({ playerGridX, playerGridY }) => {
  const [nearbyEvents, setNearbyEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadNearbyEvents();
    // Refresh events every 30 seconds
    const interval = setInterval(loadNearbyEvents, 30000);
    return () => clearInterval(interval);
  }, [playerGridX, playerGridY]);

  const loadNearbyEvents = async () => {
    try {
      const response = await eventsAPI.getNearby(10);
      setNearbyEvents(response.data);
    } catch (err) {
      console.error('Erreur chargement événements:', err);
    }
  };

  const handleParticipate = async (eventId) => {
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      const response = await eventsAPI.participate(eventId);
      setSuccess(response.data.message || 'Participation réussie!');
      setSelectedEvent(null);
      loadNearbyEvents();
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur lors de la participation');
    } finally {
      setLoading(false);
    }
  };

  const getEventIcon = (type) => {
    switch (type) {
      case 'treasure': return <TreasureIcon />;
      case 'merchant': return <MerchantIcon />;
      case 'resource': return <ResourceIcon />;
      case 'weather': return <WeatherIcon />;
      default: return <RewardIcon />;
    }
  };

  const getEventColor = (type) => {
    switch (type) {
      case 'treasure': return '#ffd700';
      case 'merchant': return '#4caf50';
      case 'resource': return '#8bc34a';
      case 'weather': return '#2196f3';
      default: return '#757575';
    }
  };

  const calculateDistance = (eventX, eventY) => {
    return Math.abs(eventX - playerGridX) + Math.abs(eventY - playerGridY);
  };

  const isAtEventLocation = (event) => {
    return event.cell_info.grid_x === playerGridX && event.cell_info.grid_y === playerGridY;
  };

  if (nearbyEvents.length === 0) {
    return null;
  }

  return (
    <Box sx={{ position: 'absolute', top: 10, right: 10, zIndex: 1000, maxWidth: 300 }}>
      {/* Alert messages */}
      {error && (
        <Alert severity="error" onClose={() => setError('')} sx={{ mb: 1 }}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" onClose={() => setSuccess('')} sx={{ mb: 1 }}>
          {success}
        </Alert>
      )}

      {/* Events List */}
      <Card sx={{ bgcolor: 'rgba(255, 255, 255, 0.95)' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            ✨ Événements à proximité
          </Typography>

          <List dense>
            {nearbyEvents.slice(0, 5).map((event) => {
              const distance = calculateDistance(event.cell_info.grid_x, event.cell_info.grid_y);
              const atLocation = isAtEventLocation(event);

              return (
                <ListItem
                  key={event.id}
                  sx={{
                    border: `2px solid ${getEventColor(event.event_type)}`,
                    borderRadius: 1,
                    mb: 1,
                    bgcolor: atLocation ? `${getEventColor(event.event_type)}20` : 'transparent',
                  }}
                  button
                  onClick={() => setSelectedEvent(event)}
                >
                  <Box sx={{ width: '100%' }}>
                    <Box display="flex" alignItems="center" justifyContent="space-between">
                      <Box display="flex" alignItems="center" gap={1}>
                        {getEventIcon(event.event_type)}
                        <Typography variant="body2" fontWeight="bold">
                          {event.icon} {event.name}
                        </Typography>
                      </Box>
                      <Chip
                        label={atLocation ? 'ICI' : `${distance} cellules`}
                        size="small"
                        color={atLocation ? 'success' : 'default'}
                      />
                    </Box>
                    <Typography variant="caption" color="text.secondary">
                      Position: ({event.cell_info.grid_x}, {event.cell_info.grid_y})
                    </Typography>
                  </Box>
                </ListItem>
              );
            })}
          </List>

          {nearbyEvents.length > 5 && (
            <Typography variant="caption" color="text.secondary">
              + {nearbyEvents.length - 5} autres événements...
            </Typography>
          )}
        </CardContent>
      </Card>

      {/* Event Details Dialog */}
      {selectedEvent && (
        <Dialog
          open={Boolean(selectedEvent)}
          onClose={() => setSelectedEvent(null)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>
            {selectedEvent.icon} {selectedEvent.name}
          </DialogTitle>
          <DialogContent>
            <Box mb={2}>
              <Chip
                label={selectedEvent.type_display}
                size="small"
                sx={{ bgcolor: getEventColor(selectedEvent.event_type), color: 'white' }}
              />
              <Chip
                label={`${selectedEvent.participant_count || 0} / ${selectedEvent.max_participants || '∞'} participants`}
                size="small"
                sx={{ ml: 1 }}
              />
            </Box>

            <Typography variant="body1" paragraph>
              {selectedEvent.description}
            </Typography>

            <Box mb={2}>
              <Typography variant="body2" color="text.secondary">
                📍 Position: ({selectedEvent.cell_info.grid_x}, {selectedEvent.cell_info.grid_y})
              </Typography>
              <Typography variant="body2" color="text.secondary">
                🌍 Biome: {selectedEvent.cell_info.biome}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                ⏱️ Expire: {new Date(selectedEvent.expires_at).toLocaleString()}
              </Typography>
            </Box>

            {selectedEvent.rewards && (
              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  <RewardIcon fontSize="small" sx={{ verticalAlign: 'middle', mr: 0.5 }} />
                  Récompenses potentielles:
                </Typography>
                <List dense>
                  {Object.entries(selectedEvent.rewards).map(([key, value]) => (
                    <ListItem key={key}>
                      <ListItemText
                        primary={`${key}: ${JSON.stringify(value)}`}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}

            {!isAtEventLocation(selectedEvent) && (
              <Alert severity="info" sx={{ mt: 2 }}>
                Vous devez vous déplacer à la position de l'événement pour y participer.
              </Alert>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setSelectedEvent(null)}>
              Fermer
            </Button>
            {isAtEventLocation(selectedEvent) && (
              <Button
                variant="contained"
                onClick={() => handleParticipate(selectedEvent.id)}
                disabled={loading || selectedEvent.is_expired}
              >
                Participer
              </Button>
            )}
          </DialogActions>
        </Dialog>
      )}
    </Box>
  );
};

export default MapEvents;
