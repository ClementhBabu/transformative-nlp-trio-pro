import { createTheme } from '@mui/material/styles';

const baseTypography = {
  fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  h1: { fontWeight: 800, fontSize: '2.5rem', letterSpacing: '-0.02em' },
  h2: { fontWeight: 700, fontSize: '2rem', letterSpacing: '-0.01em' },
  h3: { fontWeight: 700, fontSize: '1.5rem' },
  h4: { fontWeight: 600, fontSize: '1.25rem' },
  h5: { fontWeight: 600, fontSize: '1.1rem' },
  h6: { fontWeight: 600, fontSize: '1rem' },
  subtitle1: { fontWeight: 500, fontSize: '0.95rem' },
  body1: { fontSize: '0.95rem', lineHeight: 1.7 },
  body2: { fontSize: '0.85rem', lineHeight: 1.6 },
  button: { fontWeight: 600, textTransform: 'none', letterSpacing: '0.01em' },
};

const baseComponents = {
  MuiButton: {
    styleOverrides: {
      root: { borderRadius: 10, padding: '10px 24px', fontSize: '0.9rem' },
      containedPrimary: {
        background: 'linear-gradient(135deg, #1a237e 0%, #534bae 100%)',
        boxShadow: '0 4px 14px 0 rgba(26,35,126,0.4)',
        '&:hover': {
          boxShadow: '0 6px 20px 0 rgba(26,35,126,0.5)',
          background: 'linear-gradient(135deg, #283593 0%, #5c6bc0 100%)',
        },
      },
      containedSecondary: {
        background: 'linear-gradient(135deg, #00bcd4 0%, #00acc1 100%)',
        '&:hover': { background: 'linear-gradient(135deg, #00acc1 0%, #0097a7 100%)' },
      },
      outlined: { borderWidth: 2, '&:hover': { borderWidth: 2 } },
    },
  },
  MuiCard: {
    styleOverrides: {
      root: { borderRadius: 16, transition: 'all 0.3s ease' },
    },
  },
  MuiTextField: {
    styleOverrides: {
      root: {
        '& .MuiOutlinedInput-root': { borderRadius: 10 },
      },
    },
  },
  MuiChip: {
    styleOverrides: {
      root: { borderRadius: 8, fontWeight: 500 },
    },
  },
  MuiPaper: {
    styleOverrides: {
      rounded: { borderRadius: 16 },
    },
  },
  MuiAppBar: {
    styleOverrides: {
      root: {
        boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
      },
    },
  },
};

export const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#1a237e', light: '#534bae', dark: '#000051' },
    secondary: { main: '#00bcd4', light: '#62efff', dark: '#008ba3' },
    background: { default: '#f5f7fa', paper: '#ffffff' },
    text: { primary: '#1a1a2e', secondary: '#546e7a' },
    divider: '#e0e0e0',
    success: { main: '#2e7d32' },
    warning: { main: '#ed6c02' },
    error: { main: '#d32f2f' },
    info: { main: '#0288d1' },
  },
  typography: baseTypography,
  components: baseComponents,
  shape: { borderRadius: 10 },
});

export const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#7986cb', light: '#aab6fe', dark: '#49599a' },
    secondary: { main: '#4dd0e1', light: '#88ffff', dark: '#00acc1' },
    background: { default: '#0a0e27', paper: '#1a1f3d' },
    text: { primary: '#e8eaf6', secondary: '#9e9e9e' },
    divider: '#333366',
    success: { main: '#66bb6a' },
    warning: { main: '#ffa726' },
    error: { main: '#ef5350' },
    info: { main: '#29b6f6' },
  },
  typography: baseTypography,
  components: {
    ...baseComponents,
    MuiButton: {
      styleOverrides: {
        ...baseComponents.MuiButton.styleOverrides,
        containedPrimary: {
          background: 'linear-gradient(135deg, #49599a 0%, #7986cb 100%)',
          boxShadow: '0 4px 14px 0 rgba(121,134,203,0.3)',
          '&:hover': {
            boxShadow: '0 6px 20px 0 rgba(121,134,203,0.4)',
            background: 'linear-gradient(135deg, #5c6bc0 0%, #9fa8da 100%)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(145deg, #1a1f3d 0%, #232855 100%)',
          border: '1px solid rgba(255,255,255,0.05)',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 12px rgba(0,0,0,0.3)',
        },
      },
    },
  },
  shape: { borderRadius: 10 },
});

export const getTheme = (mode) => (mode === 'dark' ? darkTheme : lightTheme);
