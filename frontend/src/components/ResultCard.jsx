import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Tabs,
  Tab,
  Box,
  Typography,
  IconButton,
  Chip,
  Collapse,
  Tooltip,
  Stack,
} from '@mui/material';
import {
  ContentCopy as CopyIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
  Download as DownloadIcon,
  PlayArrow as PlayIcon,
  SentimentVerySatisfied as PositiveIcon,
  SentimentNeutral as NeutralIcon,
  SentimentVeryDissatisfied as NegativeIcon,
} from '@mui/icons-material';
import toast from 'react-hot-toast';
import AudioWaveform from './AudioWaveform';

const sentimentConfig = {
  positive: { icon: PositiveIcon, color: 'success', label: 'Positive' },
  negative: { icon: NegativeIcon, color: 'error', label: 'Negative' },
  neutral: { icon: NeutralIcon, color: 'warning', label: 'Neutral' },
};

function TabPanel({ children, value, index }) {
  return value === index ? <Box sx={{ pt: 2 }}>{children}</Box> : null;
}

function ResultCard({
  originalText = '',
  summary = '',
  translation = '',
  sentiment = '',
  keywords = [],
  audioUrl,
  filename,
  onPlayAudio,
}) {
  const [tab, setTab] = useState(0);
  const [expanded, setExpanded] = useState(true);
  const [isPlaying, setIsPlaying] = useState(false);

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  const sentimentText = typeof sentiment === 'object' && sentiment !== null
    ? sentiment.classification || sentiment.label || ''
    : (sentiment || '');
  const sentConfig = sentimentConfig[sentimentText.toLowerCase()] || sentimentConfig.neutral;
  const SentIcon = sentConfig.icon;

  const handlePlay = () => {
    if (onPlayAudio) {
      setIsPlaying(!isPlaying);
      onPlayAudio();
    }
  };

  const sections = [
    { label: 'Original Text', content: originalText },
    { label: 'Summary', content: summary },
    { label: 'Translation', content: translation },
  ];

  return (
    <Card sx={{ borderRadius: 3 }} elevation={2}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="h6" fontWeight={600}>
              Results
            </Typography>
            {sentimentText && (
              <Chip
                icon={<SentIcon />}
                label={sentConfig.label}
                size="small"
                color={sentConfig.color}
                variant="filled"
              />
            )}
          </Box>
          <IconButton size="small" onClick={() => setExpanded(!expanded)}>
            {expanded ? <CollapseIcon /> : <ExpandIcon />}
          </IconButton>
        </Box>

        {keywords.length > 0 && (
          <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap sx={{ mb: 1 }}>
            {keywords.map((kw, i) => (
              <Chip key={i} label={kw} size="small" variant="outlined" sx={{ mb: 0.5 }} />
            ))}
          </Stack>
        )}

        {audioUrl && (
          <Box sx={{ mb: 2 }}>
            <AudioWaveform audioUrl={audioUrl} isPlaying={isPlaying} height={50} />
            <IconButton onClick={handlePlay} color="primary" size="small">
              <PlayIcon />
            </IconButton>
          </Box>
        )}

        <Collapse in={expanded}>
          <Tabs value={tab} onChange={(_, v) => setTab(v)} variant="scrollable" scrollButtons="auto">
            {sections.map((s, i) => (
              <Tab key={i} label={s.label} disabled={!s.content} />
            ))}
          </Tabs>

          {sections.map((section, i) => (
            <TabPanel key={i} value={tab} index={i}>
              <Box sx={{ position: 'relative' }}>
                <Typography
                  variant="body1"
                  sx={{
                    whiteSpace: 'pre-wrap',
                    pr: 4,
                    maxHeight: 300,
                    overflow: 'auto',
                  }}
                >
                  {section.content || 'No content available.'}
                </Typography>
                {section.content && (
                  <Tooltip title="Copy to clipboard">
                    <IconButton
                      size="small"
                      onClick={() => handleCopy(section.content)}
                      sx={{ position: 'absolute', top: 0, right: 0 }}
                    >
                      <CopyIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                )}
              </Box>
            </TabPanel>
          ))}
        </Collapse>
      </CardContent>
    </Card>
  );
}

export default ResultCard;
