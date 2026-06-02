import React from 'react';
import { Box, Typography, IconButton, Link as MuiLink } from '@mui/material';
import { GitHub, LinkedIn, Language } from '@mui/icons-material';
import { useThemeContext } from '../hooks/useTheme';

function Footer() {
  const { isDark } = useThemeContext();

  return (
    <Box
      component="footer"
      sx={{
        py: 3,
        px: 2,
        mt: 'auto',
        textAlign: 'center',
        borderTop: `1px solid ${isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)'}`,
        background: isDark ? 'rgba(26,31,61,0.5)' : 'rgba(245,247,250,0.8)',
      }}
    >
      <Typography variant="body2" color="text.secondary" gutterBottom>
        &copy; {new Date().getFullYear()} <strong>NLP Trio Pro</strong> — Transform Speech to Action
      </Typography>
      <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
        Built with FastAPI &amp; React
      </Typography>
      <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, mt: 1 }}>
        <IconButton size="small" component={MuiLink} href="https://github.com" target="_blank" color="inherit">
          <GitHub fontSize="small" />
        </IconButton>
        <IconButton size="small" color="inherit">
          <LinkedIn fontSize="small" />
        </IconButton>
        <IconButton size="small" color="inherit">
          <Language fontSize="small" />
        </IconButton>
      </Box>
    </Box>
  );
}

export default Footer;
