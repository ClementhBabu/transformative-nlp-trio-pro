import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  CardActionArea,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Button,
  CircularProgress,
  IconButton,
} from '@mui/material';
import {
  Mic as MicIcon,
  History as HistoryIcon,
  ArrowForward as ArrowIcon,
  Translate as TranslateIcon,
  Summarize as SummarizeIcon,
  RecordVoiceOver as TtsIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { useAuth } from '../hooks/useAuth';
import { historyAPI, analyticsAPI } from '../services/api';
import DashboardStats from '../components/DashboardStats';
import DashboardCharts from '../components/DashboardCharts';
import toast from 'react-hot-toast';

function Dashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [recentItems, setRecentItems] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [historyRes, analyticsRes] = await Promise.allSettled([
        historyAPI.getRecent(),
        analyticsAPI.getUserAnalytics(),
      ]);

      if (historyRes.status === 'fulfilled') {
        setRecentItems(historyRes.value.data.items || historyRes.value.data || []);
      } else {
        setRecentItems([]);
      }

      if (analyticsRes.status === 'fulfilled') {
        setStats(analyticsRes.value.data);
      } else {
        setStats({});
      }
    } catch {
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const getOperationIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'translation': return <TranslateIcon />;
      case 'summary': return <SummarizeIcon />;
      case 'tts': return <TtsIcon />;
      default: return <MicIcon />;
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress size={48} />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Welcome back, {user?.name || 'User'}
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Here&apos;s your NLP activity overview.
        </Typography>
      </Box>

      <DashboardStats stats={stats} />

      <Box sx={{ my: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <Button
            variant="contained"
            startIcon={<MicIcon />}
            onClick={() => navigate('/process')}
            size="large"
          >
            New Processing
          </Button>
          <Button
            variant="outlined"
            startIcon={<HistoryIcon />}
            onClick={() => navigate('/history')}
            size="large"
          >
            View History
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <DashboardCharts />
        </Grid>

        <Grid item xs={12}>
          <Card sx={{ borderRadius: 3 }} elevation={2}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" fontWeight={600}>
                  Recent Activity
                </Typography>
                <IconButton size="small" onClick={fetchData}>
                  <RefreshIcon />
                </IconButton>
              </Box>

              {recentItems.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body1" color="text.secondary" gutterBottom>
                    No recent activity yet.
                  </Typography>
                  <Button variant="contained" onClick={() => navigate('/process')}>
                    Start Your First Processing
                  </Button>
                </Box>
              ) : (
                <List disablePadding>
                  {recentItems.slice(0, 5).map((item, i) => (
                    <ListItem
                      key={item.id || i}
                      divider={i < recentItems.slice(0, 5).length - 1}
                      secondaryAction={
                        <IconButton edge="end" onClick={() => navigate('/history')}>
                          <ArrowIcon />
                        </IconButton>
                      }
                    >
                      <ListItemIcon>{getOperationIcon(item.operation || item.type)}</ListItemIcon>
                      <ListItemText
                        primary={
                          <Typography variant="body2" fontWeight={500} noWrap>
                            {(item.text || item.original_text || 'Audio Processing').substring(0, 80)}
                          </Typography>
                        }
                        secondary={
                          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', mt: 0.5 }}>
                            <Typography variant="caption" color="text.secondary">
                              {item.created_at
                                ? format(new Date(item.created_at), 'MMM dd, yyyy HH:mm')
                                : 'Unknown date'}
                            </Typography>
                            {item.language && (
                              <Chip label={item.language} size="small" variant="outlined" sx={{ height: 20 }} />
                            )}
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
}

export default Dashboard;
