import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Box,
  Avatar,
  Menu,
  MenuItem,
  ListItemIcon,
  Divider,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Tooltip,
  useMediaQuery,
  useTheme as useMuiTheme,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Mic as MicIcon,
  History as HistoryIcon,
  Analytics as AnalyticsIcon,
  Person as PersonIcon,
  Logout as LogoutIcon,
  LightMode as LightModeIcon,
  DarkMode as DarkModeIcon,
  SmartToy as SmartToyIcon,
} from '@mui/icons-material';
import { useAuth } from '../hooks/useAuth';
import { useThemeContext } from '../hooks/useTheme';

const navLinks = [
  { to: '/dashboard', label: 'Dashboard', icon: <DashboardIcon /> },
  { to: '/process', label: 'Process', icon: <MicIcon /> },
  { to: '/history', label: 'History', icon: <HistoryIcon /> },
  { to: '/analytics', label: 'Analytics', icon: <AnalyticsIcon /> },
];

function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, user, logout } = useAuth();
  const { mode, toggleTheme, isDark } = useThemeContext();
  const muiTheme = useMuiTheme();
  const isMobile = useMediaQuery(muiTheme.breakpoints.down('md'));

  const [anchorEl, setAnchorEl] = useState(null);
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleMenuOpen = (e) => setAnchorEl(e.currentTarget);
  const handleMenuClose = () => setAnchorEl(null);
  const handleMobileToggle = () => setMobileOpen(!mobileOpen);

  const handleLogout = () => {
    handleMenuClose();
    logout();
  };

  const handleNavigate = (to) => {
    navigate(to);
    setMobileOpen(false);
  };

  const isLanding = location.pathname === '/';

  const drawer = (
    <Box sx={{ width: 260, pt: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, px: 2, mb: 2 }}>
        <SmartToyIcon color="primary" sx={{ fontSize: 32 }} />
        <Typography variant="h6" fontWeight={700} color="primary">
          NLP Trio Pro
        </Typography>
      </Box>
      <Divider />
      <List>
        {navLinks.map((link) => (
          <ListItem key={link.to} disablePadding>
            <ListItemButton
              selected={location.pathname === link.to}
              onClick={() => handleNavigate(link.to)}
              sx={{ mx: 1, borderRadius: 2 }}
            >
              <ListItemIcon>{link.icon}</ListItemIcon>
              <ListItemText primary={link.label} />
            </ListItemButton>
          </ListItem>
        ))}
        {isAuthenticated && (
          <>
            <Divider sx={{ my: 1 }} />
            <ListItem disablePadding>
              <ListItemButton
                selected={location.pathname === '/profile'}
                onClick={() => handleNavigate('/profile')}
                sx={{ mx: 1, borderRadius: 2 }}
              >
                <ListItemIcon><PersonIcon /></ListItemIcon>
                <ListItemText primary="Profile" />
              </ListItemButton>
            </ListItem>
            <ListItem disablePadding>
              <ListItemButton onClick={handleLogout} sx={{ mx: 1, borderRadius: 2 }}>
                <ListItemIcon><LogoutIcon /></ListItemIcon>
                <ListItemText primary="Logout" />
              </ListItemButton>
            </ListItem>
          </>
        )}
      </List>
    </Box>
  );

  return (
    <>
      <AppBar
        position="sticky"
        color={isLanding ? 'transparent' : 'default'}
        sx={{
          backdropFilter: 'blur(10px)',
          background: isLanding
            ? 'rgba(26,35,126,0.85)'
            : undefined,
        }}
      >
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {isAuthenticated && isMobile && (
              <IconButton color="inherit" edge="start" onClick={handleMobileToggle}>
                <MenuIcon />
              </IconButton>
            )}
            <SmartToyIcon
              sx={{ fontSize: 32, color: isLanding ? 'white' : 'primary.main', cursor: 'pointer' }}
              onClick={() => navigate('/')}
            />
            <Typography
              variant="h6"
              fontWeight={700}
              sx={{
                cursor: 'pointer',
                color: isLanding ? 'white' : 'primary.main',
                display: { xs: 'none', sm: 'block' },
              }}
              onClick={() => navigate('/')}
            >
              NLP Trio Pro
            </Typography>
          </Box>

          {isAuthenticated && !isMobile && (
            <Box sx={{ display: 'flex', gap: 1 }}>
              {navLinks.map((link) => (
                <Button
                  key={link.to}
                  startIcon={link.icon}
                  onClick={() => navigate(link.to)}
                  sx={{
                    color: isLanding ? 'white' : 'text.primary',
                    opacity: location.pathname === link.to ? 1 : 0.7,
                    '&:hover': { opacity: 1 },
                  }}
                >
                  {link.label}
                </Button>
              ))}
            </Box>
          )}

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Tooltip title={isDark ? 'Light mode' : 'Dark mode'}>
              <IconButton
                onClick={toggleTheme}
                sx={{ color: isLanding ? 'white' : 'text.primary' }}
              >
                {isDark ? <LightModeIcon /> : <DarkModeIcon />}
              </IconButton>
            </Tooltip>

            {isAuthenticated ? (
              <>
                <Tooltip title={user?.name || user?.email || 'User'}>
                  <IconButton onClick={handleMenuOpen}>
                    <Avatar
                      src={user?.avatar_url}
                      sx={{
                        width: 36,
                        height: 36,
                        bgcolor: isLanding ? 'rgba(255,255,255,0.3)' : 'primary.main',
                        color: 'white',
                        fontWeight: 600,
                        fontSize: '0.9rem',
                      }}
                    >
                      {(user?.name || user?.email || 'U')[0].toUpperCase()}
                    </Avatar>
                  </IconButton>
                </Tooltip>
                <Menu
                  anchorEl={anchorEl}
                  open={Boolean(anchorEl)}
                  onClose={handleMenuClose}
                  transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                  anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
                  PaperProps={{ sx: { mt: 1, minWidth: 200 } }}
                >
                  <MenuItem onClick={() => { handleMenuClose(); navigate('/profile'); }}>
                    <ListItemIcon><PersonIcon fontSize="small" /></ListItemIcon>
                    Profile
                  </MenuItem>
                  <Divider />
                  <MenuItem onClick={handleLogout}>
                    <ListItemIcon><LogoutIcon fontSize="small" /></ListItemIcon>
                    Logout
                  </MenuItem>
                </Menu>
              </>
            ) : (
              !isLanding && (
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button variant="outlined" onClick={() => navigate('/login')}>
                    Login
                  </Button>
                  <Button variant="contained" onClick={() => navigate('/register')}>
                    Register
                  </Button>
                </Box>
              )
            )}
          </Box>
        </Toolbar>
      </AppBar>

      {isAuthenticated && isMobile && (
        <Drawer anchor="left" open={mobileOpen} onClose={handleMobileToggle}>
          {drawer}
        </Drawer>
      )}
    </>
  );
}

export default Navbar;
