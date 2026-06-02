import React, { useState, useCallback } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Paper,
  Stack,
  IconButton,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Download as DownloadIcon,
  Description as PdfIcon,
} from '@mui/icons-material';
import toast from 'react-hot-toast';
import AudioRecorder from '../components/AudioRecorder';
import ProcessingPipeline from '../components/ProcessingPipeline';
import ResultCard from '../components/ResultCard';
import QAWidget from '../components/QAWidget';
import LanguageSelector from '../components/LanguageSelector';
import { pipelineAPI, reportAPI, sentimentAPI, keywordsAPI, ttsAPI } from '../services/api';

const summaryModes = [
  { value: 'short', label: 'Short (2-3 sentences)' },
  { value: 'medium', label: 'Medium (1 paragraph)' },
  { value: 'detailed', label: 'Detailed (multiple paragraphs)' },
  { value: 'bullets', label: 'Bullet Points' },
];

function AudioProcessingPage() {
  const [audioFile, setAudioFile] = useState(null);
  const [targetLang, setTargetLang] = useState('es');
  const [summaryMode, setSummaryMode] = useState('medium');
  const [processing, setProcessing] = useState(false);
  const [pipelineState, setPipelineState] = useState({});
  const [results, setResults] = useState({});
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioElement, setAudioElement] = useState(null);

  const handleAudioReady = useCallback((data) => {
    setAudioFile(data);
    setPipelineState({});
    setResults({});
  }, []);

  const handleFileUpload = useCallback((file) => {
    setAudioFile({ blob: file, url: URL.createObjectURL(file) });
  }, []);

  const updateStep = (key, status, resultData) => {
    setPipelineState((prev) => ({ ...prev, [key]: status }));
    if (resultData !== undefined) {
      setResults((prev) => ({ ...prev, [key]: resultData }));
    }
  };

  const handleProcess = async () => {
    if (!audioFile) {
      toast.error('Please provide an audio file first.');
      return;
    }

    setProcessing(true);
    setPipelineState({
      upload: 'completed',
      recognize: 'processing',
      summarize: 'pending',
      translate: 'pending',
      tts: 'pending',
    });
    setResults({});

    try {
      const formData = new FormData();
      formData.append('file', audioFile.blob);
      formData.append('target_language', targetLang);
      formData.append('summary_mode', summaryMode);

      const response = await pipelineAPI.process(formData);
      const data = response.data;

      updateStep('upload', 'completed');
      updateStep('recognize', 'completed', data.transcript || data.text || 'Speech recognized successfully.');
      updateStep('summarize', 'completed', data.summary || 'Summary generated.');
      updateStep('translate', 'completed', data.translation || 'Translation completed.');
      updateStep('tts', 'completed');

      if (data.sentiment) {
        setResults((prev) => ({ ...prev, sentiment: data.sentiment }));
      }
      if (data.keywords) {
        setResults((prev) => ({ ...prev, keywords: Array.isArray(data.keywords) ? data.keywords : [] }));
      }

      toast.success('Processing pipeline completed!');
    } catch (error) {
      const msg = error.response?.data?.detail || 'Processing failed';
      toast.error(msg);
      const currentStep = Object.entries(pipelineState).find(([, v]) => v === 'processing')?.[0] || 'recognize';
      updateStep(currentStep, 'error', `${currentStep}_error: ${msg}`);
    } finally {
      setProcessing(false);
    }
  };

  const handleRetry = async (stepKey) => {
    toast.success('Retrying...');
    handleProcess();
  };

  const handleGenerateReport = async () => {
    try {
      const historyId = results.history_id || results.id;
      if (!historyId) {
        toast.error('No history record available for report generation.');
        return;
      }
      const response = await reportAPI.generate(historyId);
      const filename = response.data.filename || response.data.report_filename;
      if (filename) {
        window.open(reportAPI.download(filename), '_blank');
        toast.success('Report downloaded!');
      }
    } catch {
      toast.error('Failed to generate report.');
    }
  };

  const handlePlayAudio = () => {
    if (results.tts_audio_url || results.audio_url) {
      if (isPlaying) {
        audioElement?.pause();
      } else {
        const audio = new Audio(results.tts_audio_url || results.audio_url);
        audio.play();
        setAudioElement(audio);
        audio.onended = () => setIsPlaying(false);
      }
      setIsPlaying(!isPlaying);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Audio Processing
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Record or upload audio, then let AI transcribe, summarize, translate and generate voice output.
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={5}>
          <AudioRecorder
            onAudioReady={handleAudioReady}
            onFileUpload={handleFileUpload}
          />

          <Paper sx={{ p: 3, mt: 3, borderRadius: 3 }} elevation={2}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Processing Options
            </Typography>

            <Stack spacing={2.5}>
              <FormControl fullWidth>
                <InputLabel>Summary Mode</InputLabel>
                <Select
                  value={summaryMode}
                  onChange={(e) => setSummaryMode(e.target.value)}
                  label="Summary Mode"
                >
                  {summaryModes.map((mode) => (
                    <MenuItem key={mode.value} value={mode.value}>
                      {mode.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <LanguageSelector
                value={targetLang}
                onChange={setTargetLang}
                label="Target Language"
              />

              <Button
                variant="contained"
                size="large"
                onClick={handleProcess}
                disabled={processing || !audioFile}
                startIcon={processing ? <CircularProgress size={20} color="inherit" /> : <PlayIcon />}
                fullWidth
                sx={{ py: 1.5, fontSize: '1rem' }}
              >
                {processing ? 'Processing...' : 'Start Processing'}
              </Button>
            </Stack>
          </Paper>
        </Grid>

        <Grid item xs={12} md={7}>
          {(Object.keys(pipelineState).length > 0) && (
            <ProcessingPipeline
              pipelineState={pipelineState}
              onRetry={handleRetry}
              results={results}
            />
          )}

          {(results.recognize || results.summarize || results.translate) && (
            <Box sx={{ mt: 3 }}>
              <ResultCard
                originalText={results.recognize}
                summary={results.summarize}
                translation={results.translate}
                sentiment={results.sentiment}
                keywords={results.keywords || []}
                audioUrl={results.tts_audio_url || results.audio_url}
                onPlayAudio={handlePlayAudio}
              />

              <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Button
                  variant="outlined"
                  startIcon={<PdfIcon />}
                  onClick={handleGenerateReport}
                  disabled={processing}
                >
                  Download Report
                </Button>
                {results.translate && (
                  <Button
                    variant="outlined"
                    startIcon={<DownloadIcon />}
                    onClick={() => {
                      const blob = new Blob([results.translate], { type: 'text/plain' });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = 'translation.txt';
                      a.click();
                      URL.revokeObjectURL(url);
                    }}
                  >
                    Download Translation
                  </Button>
                )}
              </Box>
            </Box>
          )}

          {results.recognize && (
            <Box sx={{ mt: 3 }}>
              <QAWidget context={results.recognize} />
            </Box>
          )}
        </Grid>
      </Grid>
    </Container>
  );
}

export default AudioProcessingPage;
