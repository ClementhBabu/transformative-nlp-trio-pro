import React, { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Stack,
  IconButton,
} from '@mui/material';
import {
  Mic as MicIcon,
  Summarize as SummarizeIcon,
  Translate as TranslateIcon,
  RecordVoiceOver as VoiceIcon,
  ArrowForward as ArrowIcon,
  CloudUpload,
  Psychology,
  GTranslate,
  Audiotrack,
  Speed,
  Security,
  AutoAwesome,
} from '@mui/icons-material';
import { useAuth } from '../hooks/useAuth';

const features = [
  { icon: MicIcon, title: 'Speech Recognition', desc: 'Convert speech to text with state-of-the-art accuracy across 50+ languages.' },
  { icon: SummarizeIcon, title: 'AI Summarization', desc: 'Generate concise summaries with multiple modes: short, medium, detailed, or bullet points.' },
  { icon: TranslateIcon, title: 'Neural Translation', desc: 'Translate text between any supported language pair with context-aware neural models.' },
  { icon: VoiceIcon, title: 'Voice Output', desc: 'Convert translated text back to natural-sounding speech with multiple voice options.' },
];

const steps = [
  { icon: CloudUpload, title: 'Upload Audio', desc: 'Record or upload your audio file in any supported format.' },
  { icon: Psychology, title: 'AI Processing', desc: 'Our models transcribe, summarize, and analyze your content.' },
  { icon: GTranslate, title: 'Translate', desc: 'Get accurate translations in your target language.' },
  { icon: Audiotrack, title: 'Listen', desc: 'Download or stream the generated voice output.' },
];

const stats = [
  { value: '50+', label: 'Languages' },
  { value: '99%', label: 'Accuracy' },
  { value: '10K+', label: 'Users' },
  { value: '1M+', label: 'Processed' },
];

function LandingPage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  return (
    <Box>
      {/* Hero Section */}
      <Box
        className="hero-gradient"
        sx={{
          minHeight: '92vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'relative',
          overflow: 'hidden',
          px: 2,
          py: 10,
        }}
      >
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            opacity: 0.06,
            background: 'radial-gradient(circle at 20% 50%, #fff 0%, transparent 50%), radial-gradient(circle at 80% 20%, #fff 0%, transparent 50%)',
          }}
        />
        <Container maxWidth="lg">
          <Grid container spacing={6} alignItems="center">
            <Grid item xs={12} md={7}>
              <Box sx={{ color: 'white', position: 'relative', zIndex: 1 }}>
                <Box
                  sx={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 1,
                    bgcolor: 'rgba(255,255,255,0.15)',
                    borderRadius: 6,
                    px: 2,
                    py: 0.75,
                    mb: 3,
                  }}
                >
                  <AutoAwesome sx={{ fontSize: 18 }} />
                  <Typography variant="body2" fontWeight={500}>
                    AI-Powered NLP Platform
                  </Typography>
                </Box>
                <Typography
                  variant="h1"
                  fontWeight={800}
                  sx={{ fontSize: { xs: '2.2rem', sm: '3rem', md: '3.8rem' }, lineHeight: 1.1, mb: 2 }}
                >
                  Transform Speech to Action
                </Typography>
                <Typography variant="h5" fontWeight={400} sx={{ mb: 4, opacity: 0.9, maxWidth: 600 }}>
                  Record, transcribe, summarize, translate, and generate voice output — all in one seamless pipeline powered by cutting-edge AI.
                </Typography>
                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                  <Button
                    variant="contained"
                    size="large"
                    onClick={() => navigate(isAuthenticated ? '/dashboard' : '/register')}
                    sx={{
                      bgcolor: 'white',
                      color: 'primary.main',
                      px: 5,
                      py: 1.5,
                      fontSize: '1.05rem',
                      '&:hover': { bgcolor: 'rgba(255,255,255,0.9)' },
                    }}
                    endIcon={<ArrowIcon />}
                  >
                    Get Started Free
                  </Button>
                  <Button
                    variant="outlined"
                    size="large"
                    onClick={() => navigate(isAuthenticated ? '/dashboard' : '/login')}
                    sx={{
                      borderColor: 'rgba(255,255,255,0.5)',
                      color: 'white',
                      px: 5,
                      py: 1.5,
                      fontSize: '1.05rem',
                      '&:hover': { borderColor: 'white', bgcolor: 'rgba(255,255,255,0.1)' },
                    }}
                  >
                    {isAuthenticated ? 'Go to Dashboard' : 'Login'}
                  </Button>
                </Stack>
              </Box>
            </Grid>
            <Grid item xs={12} md={5} sx={{ display: { xs: 'none', md: 'block' } }}>
              <Box
                sx={{
                  bgcolor: 'rgba(255,255,255,0.08)',
                  borderRadius: 4,
                  p: 4,
                  backdropFilter: 'blur(12px)',
                  border: '1px solid rgba(255,255,255,0.12)',
                }}
              >
                <Typography variant="h5" fontWeight={700} sx={{ color: 'white', mb: 3 }}>
                  Pipeline Demo
                </Typography>
                {steps.map((step, i) => (
                  <Box key={i} sx={{ display: 'flex', gap: 2, mb: 2.5, opacity: 0.9 }}>
                    <Box
                      sx={{
                        width: 42,
                        height: 42,
                        borderRadius: 2,
                        bgcolor: 'rgba(255,255,255,0.15)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                        color: 'white',
                      }}
                    >
                      <step.icon />
                    </Box>
                    <Box>
                      <Typography variant="subtitle2" fontWeight={600} color="white">
                        {step.title}
                      </Typography>
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                        {step.desc}
                      </Typography>
                    </Box>
                  </Box>
                ))}
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ py: 10 }}>
        <Box sx={{ textAlign: 'center', mb: 6 }}>
          <Typography variant="h2" fontWeight={700} gutterBottom>
            Powerful Features
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ maxWidth: 600, mx: 'auto' }}>
            Everything you need to process audio content from end to end.
          </Typography>
        </Box>
        <Grid container spacing={3}>
          {features.map((feature, i) => (
            <Grid item xs={12} sm={6} md={3} key={i}>
              <Card
                sx={{
                  height: '100%',
                  borderRadius: 3,
                  textAlign: 'center',
                  p: 2,
                  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                  '&:hover': { transform: 'translateY(-6px)', boxShadow: 6 },
                }}
                elevation={2}
              >
                <CardContent>
                  <Box
                    sx={{
                      width: 64,
                      height: 64,
                      borderRadius: 3,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mx: 'auto',
                      mb: 2,
                      bgcolor: 'primary.main',
                      color: 'white',
                    }}
                  >
                    <feature.icon sx={{ fontSize: 32 }} />
                  </Box>
                  <Typography variant="h6" fontWeight={600} gutterBottom>
                    {feature.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {feature.desc}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* How It Works */}
      <Box sx={{ bgcolor: 'background.default', py: 10 }}>
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center', mb: 6 }}>
            <Typography variant="h2" fontWeight={700} gutterBottom>
              How It Works
            </Typography>
            <Typography variant="h6" color="text.secondary" sx={{ maxWidth: 600, mx: 'auto' }}>
              Four simple steps from audio input to voice output.
            </Typography>
          </Box>
          <Grid container spacing={3} alignItems="stretch">
            {steps.map((step, i) => (
              <Grid item xs={12} sm={6} md={3} key={i}>
                <Box sx={{ textAlign: 'center', position: 'relative' }}>
                  <Box
                    sx={{
                      width: 80,
                      height: 80,
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mx: 'auto',
                      mb: 2,
                      bgcolor: 'primary.main',
                      color: 'white',
                      position: 'relative',
                      zIndex: 1,
                    }}
                  >
                    <step.icon sx={{ fontSize: 36 }} />
                  </Box>
                  {i < steps.length - 1 && (
                    <Box
                      sx={{
                        display: { xs: 'none', md: 'block' },
                        position: 'absolute',
                        top: 40,
                        right: -20,
                        width: 40,
                        height: 2,
                        bgcolor: 'divider',
                      }}
                    />
                  )}
                  <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                    {step.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {step.desc}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* Stats */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Grid container spacing={3}>
          {stats.map((stat, i) => (
            <Grid item xs={6} md={3} key={i}>
              <Box sx={{ textAlign: 'center', p: 3 }}>
                <Typography variant="h3" fontWeight={800} color="primary.main">
                  {stat.value}
                </Typography>
                <Typography variant="body1" color="text.secondary" fontWeight={500}>
                  {stat.label}
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* CTA */}
      <Box className="hero-gradient" sx={{ py: 10, textAlign: 'center' }}>
        <Container maxWidth="sm">
          <Typography variant="h3" fontWeight={700} color="white" gutterBottom>
            Ready to Get Started?
          </Typography>
          <Typography variant="h6" color="rgba(255,255,255,0.85)" sx={{ mb: 4 }}>
            Join thousands of users transforming speech into action with AI.
          </Typography>
          <Button
            variant="contained"
            size="large"
            onClick={() => navigate(isAuthenticated ? '/dashboard' : '/register')}
            sx={{
              bgcolor: 'white',
              color: 'primary.main',
              px: 6,
              py: 1.5,
              fontSize: '1.1rem',
              '&:hover': { bgcolor: 'rgba(255,255,255,0.9)' },
            }}
          >
            Start Free Now
          </Button>
        </Container>
      </Box>
    </Box>
  );
}

export default LandingPage;
