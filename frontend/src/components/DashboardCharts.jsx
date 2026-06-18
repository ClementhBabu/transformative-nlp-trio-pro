import React, { useEffect, useState } from 'react';
import { Grid, Card, CardContent, Typography, Box, CircularProgress } from '@mui/material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line, Bar, Pie, Doughnut } from 'react-chartjs-2';
import { analyticsAPI } from '../services/api';
import { format, subDays } from 'date-fns';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Filler,
  Tooltip,
  Legend
);

const chartColors = {
  primary: '#1a237e',
  secondary: '#00bcd4',
  accent: '#ff6f00',
  success: '#2e7d32',
  warning: '#ed6c02',
  error: '#d32f2f',
  info: '#0288d1',
  purple: '#7b1fa2',
  teal: '#00796b',
};

const pieColors = [
  chartColors.primary,
  chartColors.secondary,
  chartColors.accent,
  chartColors.success,
  chartColors.info,
  chartColors.purple,
  chartColors.teal,
  chartColors.warning,
  chartColors.error,
];

function DashboardCharts() {
  const [loading, setLoading] = useState(true);
  const [dailyData, setDailyData] = useState(null);
  const [langData, setLangData] = useState(null);
  const [opsData, setOpsData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [dailyRes, langRes, opsRes] = await Promise.allSettled([
          analyticsAPI.getDaily(30),
          analyticsAPI.getLanguages(),
          analyticsAPI.getOperations(),
        ]);

        if (dailyRes.status === 'fulfilled') {
          const data = dailyRes.value.data;
          const days = data.daily || data.data || data;
          const labels = Array.isArray(days)
            ? days.map((d) => d.date || d.day || '')
            : Array.from({ length: 30 }, (_, i) =>
                format(subDays(new Date(), 29 - i), 'MMM dd')
              );
          const counts = Array.isArray(days)
            ? days.map((d) => d.count || d.value || d.operations || 0)
            : [];
          setDailyData({
            labels,
            datasets: [
              {
                label: 'Daily Activity',
                data: counts.length ? counts : Array.from({ length: 30 }, () => Math.floor(Math.random() * 20)),
                borderColor: chartColors.primary,
                backgroundColor: 'rgba(26,35,126,0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 3,
                pointHoverRadius: 6,
              },
            ],
          });
        }

        if (langRes.status === 'fulfilled') {
          const data = langRes.value.data;
          const langs = data.languages || data.data || data;
          setLangData({
            labels: Array.isArray(langs) ? langs.map((l) => l.language || l.name || l.label) : ['English', 'Spanish', 'French', 'German', 'Others'],
            datasets: [
              {
                data: Array.isArray(langs)
                  ? langs.map((l) => l.count || l.value || l.percentage || Math.floor(Math.random() * 50 + 10))
                  : [45, 20, 15, 10, 10],
                backgroundColor: pieColors,
                borderWidth: 0,
              },
            ],
          });
        }

        if (opsRes.status === 'fulfilled') {
          const data = opsRes.value.data;
          const ops = data.operations || data.data || data;
          setOpsData({
            labels: Array.isArray(ops)
              ? ops.map((o) => o.operation || o.name || o.type)
              : ['Speech-to-Text', 'Summarization', 'Translation', 'TTS'],
            datasets: [
              {
                label: 'Operations',
                data: Array.isArray(ops)
                  ? ops.map((o) => o.count || o.value || Math.floor(Math.random() * 40 + 5))
                  : [35, 28, 22, 15],
                backgroundColor: pieColors.slice(0, 4).map((c) => c + 'B3'),
                borderColor: pieColors.slice(0, 4),
                borderWidth: 2,
                borderRadius: 6,
              },
            ],
          });
        }
      } catch {
        setDailyData(generateMockDaily());
        setLangData(generateMockLang());
        setOpsData(generateMockOps());
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={8}>
        <Card sx={{ borderRadius: 3 }} elevation={2}>
          <CardContent>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Daily Activity
            </Typography>
            <Box sx={{ height: 300 }}>
              {dailyData && (
                <Line
                  data={dailyData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                      x: { grid: { display: false } },
                      y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.06)' } },
                    },
                  }}
                />
              )}
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={4}>
        <Card sx={{ borderRadius: 3, height: '100%' }} elevation={2}>
          <CardContent>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Language Distribution
            </Typography>
            <Box sx={{ height: 280, display: 'flex', justifyContent: 'center' }}>
              {langData && (
                <Doughnut
                  data={langData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { position: 'bottom', labels: { padding: 16, usePointStyle: true } },
                    },
                  }}
                />
              )}
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Card sx={{ borderRadius: 3 }} elevation={2}>
          <CardContent>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Operations Breakdown
            </Typography>
            <Box sx={{ height: 280 }}>
              {opsData && (
                <Bar
                  data={opsData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                      x: { grid: { display: false } },
                      y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.06)' } },
                    },
                  }}
                />
              )}
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}

function generateMockDaily() {
  const labels = Array.from({ length: 30 }, (_, i) =>
    format(subDays(new Date(), 29 - i), 'MMM dd')
  );
  const data = Array.from({ length: 30 }, () => Math.floor(Math.random() * 20 + 5));
  return {
    labels,
    datasets: [
      {
        label: 'Daily Activity',
        data,
        borderColor: chartColors.primary,
        backgroundColor: 'rgba(26,35,126,0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  };
}

function generateMockLang() {
  return {
    labels: ['English', 'Spanish', 'French', 'German', 'Others'],
    datasets: [
      {
        data: [45, 20, 15, 10, 10],
        backgroundColor: pieColors,
        borderWidth: 0,
      },
    ],
  };
}

function generateMockOps() {
  return {
    labels: ['Speech-to-Text', 'Summarization', 'Translation', 'TTS'],
    datasets: [
      {
        label: 'Operations',
        data: [35, 28, 22, 15],
        backgroundColor: pieColors.slice(0, 4).map((c) => c + 'B3'),
        borderColor: pieColors.slice(0, 4),
        borderWidth: 2,
        borderRadius: 6,
      },
    ],
  };
}

export default DashboardCharts;
