import React, { useEffect, useRef, useState } from 'react';
import { Grid, Card, CardContent, Typography, Box } from '@mui/material';
import {
  Translate as TranslateIcon,
  Summarize as SummarizeIcon,
  Language as LanguageIcon,
  Schedule as ScheduleIcon,
  TrendingUp as TrendingIcon,
} from '@mui/icons-material';

function AnimatedCounter({ value, duration = 1000 }) {
  const [count, setCount] = useState(0);
  const startTime = useRef(null);
  const raf = useRef(null);

  useEffect(() => {
    const animate = (timestamp) => {
      if (!startTime.current) startTime.current = timestamp;
      const progress = Math.min((timestamp - startTime.current) / duration, 1);
      setCount(Math.floor(progress * value));
      if (progress < 1) {
        raf.current = requestAnimationFrame(animate);
      }
    };
    raf.current = requestAnimationFrame(animate);
    return () => {
      if (raf.current) cancelAnimationFrame(raf.current);
      startTime.current = null;
    };
  }, [value, duration]);

  return <span>{count.toLocaleString()}</span>;
}

function StatCard({ title, value, icon: Icon, color, subtitle }) {
  return (
    <Card
      sx={{
        borderRadius: 3,
        background: `linear-gradient(135deg, ${color}15 0%, ${color}05 100%)`,
        borderTop: `3px solid ${color}`,
        transition: 'transform 0.2s ease, box-shadow 0.2s ease',
        '&:hover': { transform: 'translateY(-2px)', boxShadow: 4 },
      }}
      elevation={2}
    >
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography variant="body2" color="text.secondary" fontWeight={500}>
              {title}
            </Typography>
            <Typography variant="h4" fontWeight={700} sx={{ mt: 0.5 }}>
              <AnimatedCounter value={value} />
            </Typography>
            {subtitle && (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                {subtitle}
              </Typography>
            )}
          </Box>
          <Box
            sx={{
              width: 48,
              height: 48,
              borderRadius: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              bgcolor: `${color}20`,
              color,
            }}
          >
            <Icon />
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}

function DashboardStats({ stats = {} }) {
  const {
    totalTranslations = 0,
    totalSummaries = 0,
    mostUsedLanguage = 'N/A',
    lastActivity = 'N/A',
    totalOperations = 0,
  } = stats;

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} sm={6} md={4} lg={3}>
        <StatCard
          title="Total Translations"
          value={totalTranslations}
          icon={TranslateIcon}
          color="#00bcd4"
        />
      </Grid>
      <Grid item xs={12} sm={6} md={4} lg={3}>
        <StatCard
          title="Total Summaries"
          value={totalSummaries}
          icon={SummarizeIcon}
          color="#1a237e"
        />
      </Grid>
      <Grid item xs={12} sm={6} md={4} lg={3}>
        <StatCard
          title="Total Operations"
          value={totalOperations || totalTranslations + totalSummaries}
          icon={TrendingIcon}
          color="#ed6c02"
        />
      </Grid>
      <Grid item xs={12} sm={6} md={4} lg={3}>
        <StatCard
          title="Top Language"
          value={0}
          icon={LanguageIcon}
          color="#2e7d32"
          subtitle={mostUsedLanguage}
        />
      </Grid>
      <Grid item xs={12} sm={12}>
        <Card sx={{ borderRadius: 3 }} elevation={1}>
          <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <ScheduleIcon color="action" />
            <Box>
              <Typography variant="body2" color="text.secondary">
                Last Activity
              </Typography>
              <Typography variant="body1" fontWeight={500}>
                {lastActivity}
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}

export default DashboardStats;
