import { createTheme } from '@mui/material/styles';

/**
 * Thème principal du jeu - Style SCUM/Survival
 * Harmonise toute l'interface avec des couleurs cohérentes
 */
const gameTheme = createTheme({
  palette: {
    mode: 'dark',

    // Couleurs principales
    primary: {
      main: '#ff9800', // Orange - Actions principales
      light: '#ffb74d',
      dark: '#f57c00',
      contrastText: '#fff',
    },

    secondary: {
      main: '#4caf50', // Vert - Succès, santé
      light: '#81c784',
      dark: '#388e3c',
      contrastText: '#fff',
    },

    // Couleurs de statut
    error: {
      main: '#f44336', // Rouge - Danger, santé critique
      light: '#e57373',
      dark: '#d32f2f',
    },

    warning: {
      main: '#ffeb3b', // Jaune - Attention
      light: '#fff176',
      dark: '#fbc02d',
    },

    info: {
      main: '#2196f3', // Bleu - Information, eau
      light: '#64b5f6',
      dark: '#1976d2',
    },

    success: {
      main: '#4caf50', // Vert - Succès
      light: '#81c784',
      dark: '#388e3c',
    },

    // Couleurs de fond
    background: {
      default: '#0a0a0a', // Noir très foncé
      paper: '#1a1a1a', // Noir foncé pour les panels
      elevated: '#252525', // Noir moins foncé pour les éléments surélevés
    },

    // Couleurs de texte
    text: {
      primary: '#ffffff', // Blanc
      secondary: '#888888', // Gris moyen
      disabled: '#555555', // Gris foncé
      hint: '#666666',
    },

    // Séparateurs et bordures
    divider: 'rgba(255, 255, 255, 0.1)',

    // Couleurs personnalisées pour le jeu
    game: {
      // Stats vitales
      health: '#e91e63', // Rose/Rouge pour santé
      energy: '#ffc107', // Jaune pour énergie
      hunger: '#ff9800', // Orange pour faim
      thirst: '#2196f3', // Bleu pour soif
      stamina: '#9c27b0', // Violet pour endurance

      // Système SCUM
      heartbeat: '#ff6b6b',
      blood: '#4488ff',
      oxygen: '#44ff44',
      temperature: '#ffaa44',

      // Métabolisme
      calories: '#44ff44',
      water: '#4488ff',
      protein: '#ff8844',
      carbs: '#ffdd44',
      fat: '#44ff88',

      // Niveaux (vert -> jaune -> orange -> rouge)
      excellent: '#4caf50',
      good: '#8bc34a',
      moderate: '#ffeb3b',
      low: '#ff9800',
      critical: '#f44336',

      // UI
      panel: '#1a1a1a',
      panelBorder: '#333333',
      overlay: 'rgba(0, 0, 0, 0.85)',
      highlight: '#ff9800',
    },
  },

  // Typographie harmonisée
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',

    // Famille monospace pour les éléments techniques
    fontFamilyMonospace: '"Courier New", "Consolas", monospace',

    // Headers
    h1: {
      fontFamily: 'monospace',
      fontWeight: 700,
      fontSize: '3rem',
      letterSpacing: 2,
      color: '#ff9800',
    },
    h2: {
      fontFamily: 'monospace',
      fontWeight: 700,
      fontSize: '2.5rem',
      letterSpacing: 2,
      color: '#ff9800',
    },
    h3: {
      fontFamily: 'monospace',
      fontWeight: 700,
      fontSize: '2rem',
      letterSpacing: 1.5,
      color: '#ff9800',
    },
    h4: {
      fontFamily: 'monospace',
      fontWeight: 700,
      fontSize: '1.75rem',
      letterSpacing: 1.5,
      color: '#ff9800',
    },
    h5: {
      fontFamily: 'monospace',
      fontWeight: 600,
      fontSize: '1.5rem',
      letterSpacing: 1,
    },
    h6: {
      fontFamily: 'monospace',
      fontWeight: 600,
      fontSize: '1.25rem',
      letterSpacing: 1,
    },

    // Corps de texte
    body1: {
      fontSize: '1rem',
    },
    body2: {
      fontSize: '0.875rem',
    },

    // Texte technique (pour stats, valeurs)
    caption: {
      fontFamily: 'monospace',
      fontSize: '0.75rem',
      color: '#888888',
    },

    // Boutons
    button: {
      fontWeight: 600,
      letterSpacing: 0.5,
      textTransform: 'uppercase',
    },
  },

  // Espacements et dimensions
  spacing: 8, // Base de 8px

  // Bordures arrondies
  shape: {
    borderRadius: 4,
  },

  // Ombres personnalisées (plus subtiles pour style gaming)
  shadows: [
    'none',
    '0px 2px 4px rgba(0,0,0,0.5)',
    '0px 4px 8px rgba(0,0,0,0.5)',
    '0px 6px 12px rgba(0,0,0,0.6)',
    '0px 8px 16px rgba(0,0,0,0.6)',
    '0px 10px 20px rgba(0,0,0,0.7)',
    '0px 12px 24px rgba(0,0,0,0.7)',
    '0px 14px 28px rgba(0,0,0,0.8)',
    '0px 16px 32px rgba(0,0,0,0.8)',
    '0px 18px 36px rgba(0,0,0,0.9)',
    // ... rest of shadows
    ...Array(15).fill('0px 20px 40px rgba(0,0,0,0.9)'),
  ],

  // Personnalisation des composants
  components: {
    // Paper (panels, cards)
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: '#1a1a1a',
          border: '1px solid #333333',
        },
        elevation1: {
          boxShadow: '0px 2px 4px rgba(0,0,0,0.5)',
        },
        elevation2: {
          boxShadow: '0px 4px 8px rgba(0,0,0,0.5)',
          border: '1px solid rgba(255, 152, 0, 0.2)',
        },
        elevation3: {
          boxShadow: '0px 6px 12px rgba(0,0,0,0.6)',
          border: '1px solid rgba(255, 152, 0, 0.3)',
        },
      },
    },

    // Boutons
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          padding: '8px 16px',
          fontWeight: 600,
          transition: 'all 0.2s',
        },
        contained: {
          boxShadow: '0px 2px 4px rgba(0,0,0,0.5)',
          '&:hover': {
            boxShadow: '0px 4px 8px rgba(0,0,0,0.6)',
            transform: 'translateY(-1px)',
          },
        },
        outlined: {
          borderWidth: 2,
          '&:hover': {
            borderWidth: 2,
            backgroundColor: 'rgba(255, 152, 0, 0.08)',
          },
        },
      },
    },

    // Chips
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 600,
          borderRadius: 4,
        },
        filled: {
          backgroundColor: 'rgba(255, 152, 0, 0.2)',
          color: '#ff9800',
          border: '1px solid rgba(255, 152, 0, 0.4)',
        },
      },
    },

    // Barres de progression
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          backgroundColor: 'rgba(255, 255, 255, 0.1)',
        },
        bar: {
          borderRadius: 4,
        },
      },
    },

    // Tabs
    MuiTabs: {
      styleOverrides: {
        root: {
          borderBottom: '1px solid #333',
        },
        indicator: {
          backgroundColor: '#ff9800',
          height: 3,
        },
      },
    },

    MuiTab: {
      styleOverrides: {
        root: {
          fontFamily: 'monospace',
          fontWeight: 600,
          fontSize: '1rem',
          color: '#888888',
          '&.Mui-selected': {
            color: '#ff9800',
          },
          '&:hover': {
            color: '#ffb74d',
          },
        },
      },
    },

    // Cards
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: '#1a1a1a',
          border: '1px solid #333',
        },
      },
    },

    // Dialogs
    MuiDialog: {
      styleOverrides: {
        paper: {
          backgroundImage: 'none',
          backgroundColor: '#1a1a1a',
          border: '1px solid #333',
        },
      },
    },

    // Tooltips
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.95)',
          border: '1px solid #333',
          fontSize: '0.75rem',
          fontFamily: 'monospace',
        },
      },
    },

    // Tables
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderBottom: '1px solid #333',
        },
        head: {
          fontWeight: 700,
          fontFamily: 'monospace',
          color: '#ff9800',
          backgroundColor: 'rgba(26, 26, 26, 0.8)',
        },
      },
    },

    // Inputs
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            '& fieldset': {
              borderColor: '#333',
            },
            '&:hover fieldset': {
              borderColor: '#555',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#ff9800',
            },
          },
        },
      },
    },

    // Alerts
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          fontFamily: 'monospace',
        },
        standardError: {
          backgroundColor: 'rgba(244, 67, 54, 0.1)',
          border: '1px solid rgba(244, 67, 54, 0.4)',
        },
        standardWarning: {
          backgroundColor: 'rgba(255, 235, 59, 0.1)',
          border: '1px solid rgba(255, 235, 59, 0.4)',
        },
        standardInfo: {
          backgroundColor: 'rgba(33, 150, 243, 0.1)',
          border: '1px solid rgba(33, 150, 243, 0.4)',
        },
        standardSuccess: {
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          border: '1px solid rgba(76, 175, 80, 0.4)',
        },
      },
    },
  },

  // Breakpoints (responsive)
  breakpoints: {
    values: {
      xs: 0,
      sm: 600,
      md: 960,
      lg: 1280,
      xl: 1920,
    },
  },

  // Transitions
  transitions: {
    duration: {
      shortest: 150,
      shorter: 200,
      short: 250,
      standard: 300,
      complex: 375,
      enteringScreen: 225,
      leavingScreen: 195,
    },
    easing: {
      easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
      easeOut: 'cubic-bezier(0.0, 0, 0.2, 1)',
      easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
      sharp: 'cubic-bezier(0.4, 0, 0.6, 1)',
    },
  },
});

export default gameTheme;
