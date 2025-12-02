import { createTheme } from '@mui/material/styles';

// Define color palette
const colors = {
    // Primary colors
    primary: {
        main: '#4a9eff',
        light: '#6bb3ff',
        dark: '#3380d6',
    },
    // SCUM-inspired orange accent
    accent: {
        main: '#ff9800',
        light: '#ffb74d',
        dark: '#f57c00',
    },
    // Status colors
    success: {
        main: '#66bb6a',
        light: '#81c784',
        dark: '#4caf50',
    },
    warning: {
        main: '#ffa726',
        light: '#ffb74d',
        dark: '#f57c00',
    },
    error: {
        main: '#ef5350',
        light: '#e57373',
        dark: '#d32f2f',
    },
    // Background & surfaces
    background: {
        default: '#0a0a0a',      // Very dark background
        paper: '#1a1a1a',        // Dark paper
        elevated: '#252525',     // Slightly elevated surfaces
        input: '#2a2a2a',        // Input backgrounds
    },
    // Text colors
    text: {
        primary: '#e0e0e0',
        secondary: '#a0a0a0',
        disabled: '#666666',
        hint: '#888888',
    },
    // Borders & dividers
    border: {
        main: '#333333',
        light: '#444444',
        dark: '#222222',
    },
};

const theme = createTheme({
    palette: {
        mode: 'dark',
        primary: colors.primary,
        secondary: colors.accent,
        success: colors.success,
        warning: colors.warning,
        error: colors.error,
        background: {
            default: colors.background.default,
            paper: colors.background.paper,
        },
        text: colors.text,
        divider: colors.border.main,
    },
    typography: {
        fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
        h1: {
            fontWeight: 700,
            letterSpacing: '-0.02em',
            fontSize: '2.5rem',
        },
        h2: {
            fontWeight: 700,
            letterSpacing: '-0.02em',
            fontSize: '2rem',
        },
        h3: {
            fontWeight: 700,
            letterSpacing: '-0.01em',
            fontSize: '1.75rem',
        },
        h4: {
            fontWeight: 700,
            letterSpacing: '-0.01em',
            fontSize: '1.5rem',
        },
        h5: {
            fontWeight: 600,
            fontSize: '1.25rem',
        },
        h6: {
            fontWeight: 600,
            fontSize: '1rem',
        },
        subtitle1: {
            fontWeight: 500,
            fontSize: '1rem',
        },
        subtitle2: {
            fontWeight: 500,
            fontSize: '0.875rem',
        },
        body1: {
            fontSize: '1rem',
        },
        body2: {
            fontSize: '0.875rem',
        },
        button: {
            fontWeight: 600,
            textTransform: 'none',
        },
        caption: {
            fontSize: '0.75rem',
            color: colors.text.secondary,
        },
        overline: {
            fontSize: '0.75rem',
            fontWeight: 600,
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
        },
    },
    shape: {
        borderRadius: 4,
    },
    components: {
        MuiCssBaseline: {
            styleOverrides: {
                body: {
                    scrollbarWidth: 'thin',
                    scrollbarColor: `${colors.border.light} ${colors.background.default}`,
                    '&::-webkit-scrollbar': {
                        width: '8px',
                        height: '8px',
                    },
                    '&::-webkit-scrollbar-track': {
                        background: colors.background.default,
                    },
                    '&::-webkit-scrollbar-thumb': {
                        background: colors.border.light,
                        borderRadius: '4px',
                        '&:hover': {
                            background: colors.border.main,
                        },
                    },
                },
            },
        },
        MuiButton: {
            styleOverrides: {
                root: {
                    textTransform: 'none',
                    fontWeight: 600,
                    borderRadius: 4,
                    boxShadow: 'none',
                    padding: '8px 16px',
                    '&:hover': {
                        boxShadow: 'none',
                    },
                },
                contained: {
                    backgroundColor: colors.background.input,
                    color: colors.text.primary,
                    '&:hover': {
                        backgroundColor: colors.background.elevated,
                    },
                },
                containedPrimary: {
                    backgroundColor: colors.primary.main,
                    '&:hover': {
                        backgroundColor: colors.primary.dark,
                    },
                },
                containedSecondary: {
                    backgroundColor: colors.accent.main,
                    '&:hover': {
                        backgroundColor: colors.accent.dark,
                    },
                },
                outlined: {
                    borderColor: colors.border.main,
                    '&:hover': {
                        borderColor: colors.border.light,
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    },
                },
            },
        },
        MuiPaper: {
            styleOverrides: {
                root: {
                    backgroundImage: 'none',
                    backgroundColor: colors.background.paper,
                    border: `1px solid ${colors.border.main}`,
                },
                elevation1: {
                    boxShadow: '0 2px 4px rgba(0,0,0,0.3)',
                },
                elevation2: {
                    boxShadow: '0 4px 8px rgba(0,0,0,0.4)',
                },
                elevation3: {
                    boxShadow: '0 8px 16px rgba(0,0,0,0.5)',
                },
            },
        },
        MuiCard: {
            styleOverrides: {
                root: {
                    backgroundImage: 'none',
                    backgroundColor: colors.background.paper,
                    border: `1px solid ${colors.border.main}`,
                },
            },
        },
        MuiChip: {
            styleOverrides: {
                root: {
                    borderRadius: 4,
                    fontSize: '0.75rem',
                    height: 24,
                    backgroundColor: colors.background.elevated,
                    border: `1px solid ${colors.border.main}`,
                },
                filled: {
                    backgroundColor: colors.background.elevated,
                },
                outlined: {
                    borderColor: colors.border.main,
                },
            },
        },
        MuiTab: {
            styleOverrides: {
                root: {
                    textTransform: 'none',
                    fontWeight: 500,
                    fontSize: '0.875rem',
                    minHeight: 48,
                    color: colors.text.secondary,
                    '&.Mui-selected': {
                        color: colors.primary.main,
                    },
                    '&:hover': {
                        color: colors.text.primary,
                    },
                },
            },
        },
        MuiTabs: {
            styleOverrides: {
                root: {
                    minHeight: 48,
                    backgroundColor: colors.background.paper,
                    borderBottom: `1px solid ${colors.border.main}`,
                },
                indicator: {
                    backgroundColor: colors.primary.main,
                    height: 3,
                },
            },
        },
        MuiTextField: {
            styleOverrides: {
                root: {
                    '& .MuiOutlinedInput-root': {
                        backgroundColor: colors.background.input,
                        '& fieldset': {
                            borderColor: colors.border.main,
                        },
                        '&:hover fieldset': {
                            borderColor: colors.border.light,
                        },
                        '&.Mui-focused fieldset': {
                            borderColor: colors.primary.main,
                        },
                    },
                },
            },
        },
        MuiOutlinedInput: {
            styleOverrides: {
                root: {
                    backgroundColor: colors.background.input,
                    '& .MuiOutlinedInput-notchedOutline': {
                        borderColor: colors.border.main,
                    },
                    '&:hover .MuiOutlinedInput-notchedOutline': {
                        borderColor: colors.border.light,
                    },
                    '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                        borderColor: colors.primary.main,
                    },
                },
            },
        },
        MuiSelect: {
            styleOverrides: {
                select: {
                    backgroundColor: colors.background.input,
                },
            },
        },
        MuiDialog: {
            styleOverrides: {
                paper: {
                    backgroundColor: colors.background.paper,
                    backgroundImage: 'none',
                },
            },
        },
        MuiDialogTitle: {
            styleOverrides: {
                root: {
                    backgroundColor: colors.background.elevated,
                    borderBottom: `1px solid ${colors.border.main}`,
                    fontWeight: 600,
                },
            },
        },
        MuiDialogContent: {
            styleOverrides: {
                root: {
                    backgroundColor: colors.background.paper,
                },
            },
        },
        MuiDialogActions: {
            styleOverrides: {
                root: {
                    backgroundColor: colors.background.elevated,
                    borderTop: `1px solid ${colors.border.main}`,
                    padding: '16px',
                },
            },
        },
        MuiTableCell: {
            styleOverrides: {
                root: {
                    borderColor: colors.border.main,
                },
                head: {
                    backgroundColor: colors.background.elevated,
                    fontWeight: 600,
                    color: colors.text.primary,
                },
            },
        },
        MuiTableRow: {
            styleOverrides: {
                root: {
                    '&:hover': {
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    },
                },
            },
        },
        MuiLinearProgress: {
            styleOverrides: {
                root: {
                    backgroundColor: colors.background.input,
                    borderRadius: 4,
                },
            },
        },
        MuiTooltip: {
            styleOverrides: {
                tooltip: {
                    backgroundColor: colors.background.elevated,
                    border: `1px solid ${colors.border.main}`,
                    color: colors.text.primary,
                    fontSize: '0.75rem',
                },
                arrow: {
                    color: colors.background.elevated,
                },
            },
        },
        MuiAlert: {
            styleOverrides: {
                root: {
                    borderRadius: 4,
                },
                standardSuccess: {
                    backgroundColor: 'rgba(102, 187, 106, 0.15)',
                    border: `1px solid ${colors.success.main}`,
                },
                standardError: {
                    backgroundColor: 'rgba(239, 83, 80, 0.15)',
                    border: `1px solid ${colors.error.main}`,
                },
                standardWarning: {
                    backgroundColor: 'rgba(255, 167, 38, 0.15)',
                    border: `1px solid ${colors.warning.main}`,
                },
                standardInfo: {
                    backgroundColor: 'rgba(74, 158, 255, 0.15)',
                    border: `1px solid ${colors.primary.main}`,
                },
            },
        },
        MuiDivider: {
            styleOverrides: {
                root: {
                    borderColor: colors.border.main,
                },
            },
        },
        MuiListItemButton: {
            styleOverrides: {
                root: {
                    '&:hover': {
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    },
                    '&.Mui-selected': {
                        backgroundColor: 'rgba(74, 158, 255, 0.15)',
                        '&:hover': {
                            backgroundColor: 'rgba(74, 158, 255, 0.2)',
                        },
                    },
                },
            },
        },
    },
});

export default theme;
