import React, { useState } from 'react';
import { Paper, TextField, Button, Typography, Box, Alert } from '@mui/material';
import { authAPI } from '../services/api';
import logger from '../utils/logger';

function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    logger.debug('Login', 'Attempting login with:', username);

    try {
      const response = await authAPI.login(username, password);
      logger.debug('Login', 'Login response:', response.data);
      localStorage.setItem('token', response.data.token);
      logger.debug('Login', 'Token stored successfully');
      onLogin();
    } catch (err) {
      logger.error('Login failed:', err);
      const errorData = err.response?.data;
      let errorMessage = 'Échec de la connexion';
      
      if (errorData) {
        if (errorData.error) errorMessage = errorData.error;
        else if (errorData.non_field_errors) errorMessage = errorData.non_field_errors[0];
        else if (errorData.detail) errorMessage = errorData.detail;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        bgcolor: 'background.default',
      }}
    >
      <Paper sx={{ p: 4, maxWidth: 400, width: '100%' }}>
        <Typography variant="h4" gutterBottom align="center">
          Jeu de Craft
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom align="center" sx={{ mb: 3 }}>
          Connectez-vous pour commencer à jouer
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          <TextField
            label="Nom d'utilisateur"
            fullWidth
            margin="normal"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <TextField
            label="Mot de passe"
            type="password"
            fullWidth
            margin="normal"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <Button
            type="submit"
            variant="contained"
            fullWidth
            sx={{ mt: 2 }}
            disabled={loading}
          >
            {loading ? 'Connexion...' : 'Se connecter'}
          </Button>
        </form>

        <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block', textAlign: 'center' }}>
          Utilisateur de test : test / test123
        </Typography>
      </Paper>
    </Box>
  );
}

export default Login;
