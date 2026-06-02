import React, { useState, useCallback, useRef, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  IconButton,
  Typography,
  Button,
  Chip,
  LinearProgress,
  Paper,
  Stack,
} from '@mui/material';
import {
  Mic as MicIcon,
  Stop as StopIcon,
  Pause as PauseIcon,
  PlayArrow as PlayIcon,
  Delete as DeleteIcon,
  CloudUpload as UploadIcon,
  Audiotrack as AudioIcon,
} from '@mui/icons-material';
import { useAudioRecorder } from '../hooks/useAudioRecorder';
import { useThemeContext } from '../hooks/useTheme';

function AudioRecorder({ onAudioReady, onFileUpload }) {
  const {
    recording,
    paused,
    audioBlob,
    audioUrl,
    formattedDuration,
    error: recorderError,
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
    resetRecording,
  } = useAudioRecorder();

  const { isDark } = useThemeContext();
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef(null);
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const analyserRef = useRef(null);

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      setUploadedFile(file);
      if (onFileUpload) onFileUpload(file);
      if (onAudioReady) {
        const url = URL.createObjectURL(file);
        onAudioReady({ blob: file, url });
      }
    }
  }, [onAudioReady, onFileUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'audio/*': ['.mp3', '.wav', '.webm', '.ogg', '.m4a', '.flac'] },
    maxFiles: 1,
    maxSize: 100 * 1024 * 1024,
  });

  useEffect(() => {
    if (audioBlob && onAudioReady) {
      onAudioReady({ blob: audioBlob, url: audioUrl });
    }
  }, [audioBlob, audioUrl, onAudioReady]);

  useEffect(() => {
    if (!canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    const bars = 40;

    const draw = () => {
      ctx.clearRect(0, 0, width, height);
      const barWidth = (width / bars) - 2;

      for (let i = 0; i < bars; i++) {
        let barHeight;
        if (recording && !paused) {
          barHeight = Math.random() * height * 0.8 + 4;
        } else if (isPlaying || (audioUrl && !recording)) {
          const phase = (Date.now() / 200 + i * 0.3) % (Math.PI * 2);
          barHeight = (Math.sin(phase) * 0.5 + 0.5) * height * 0.6 + 4;
        } else {
          barHeight = 4;
        }
        const x = i * (barWidth + 2);
        const y = height - barHeight;
        const gradient = ctx.createLinearGradient(x, y, x, height);
        if (recording && !paused) {
          gradient.addColorStop(0, '#ef5350');
          gradient.addColorStop(1, '#d32f2f');
        } else {
          gradient.addColorStop(0, isDark ? '#7986cb' : '#534bae');
          gradient.addColorStop(1, isDark ? '#49599a' : '#1a237e');
        }
        ctx.fillStyle = gradient;
        ctx.fillRect(x, y, barWidth, barHeight);
      }
      animationRef.current = requestAnimationFrame(draw);
    };

    draw();
    return () => {
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
  }, [recording, paused, isPlaying, audioUrl, isDark]);

  const handlePlayPause = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleAudioEnded = () => setIsPlaying(false);

  const handleStopRecording = () => {
    stopRecording();
  };

  return (
    <Paper sx={{ p: 3, borderRadius: 3 }} elevation={2}>
      <Typography variant="h6" gutterBottom fontWeight={600}>
        Audio Input
      </Typography>

      <canvas
        ref={canvasRef}
        width={500}
        height={80}
        style={{
          width: '100%',
          height: 80,
          borderRadius: 8,
          marginBottom: 16,
          background: isDark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.02)',
        }}
      />

      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 2, mb: 2 }}>
        {!recording && !audioBlob && (
          <IconButton
            onClick={startRecording}
            sx={{
              width: 72,
              height: 72,
              bgcolor: 'error.main',
              color: 'white',
              '&:hover': { bgcolor: 'error.dark' },
            }}
          >
            <MicIcon sx={{ fontSize: 36 }} />
          </IconButton>
        )}

        {recording && (
          <>
            <IconButton
              onClick={paused ? resumeRecording : pauseRecording}
              sx={{ width: 56, height: 56, bgcolor: 'warning.main', color: 'white' }}
            >
              {paused ? <PlayIcon fontSize="large" /> : <PauseIcon fontSize="large" />}
            </IconButton>
            <Box className={!paused ? 'recording-pulse' : ''}>
              <IconButton
                onClick={handleStopRecording}
                sx={{ width: 72, height: 72, bgcolor: 'error.main', color: 'white' }}
              >
                <StopIcon sx={{ fontSize: 36 }} />
              </IconButton>
            </Box>
          </>
        )}

        {(audioUrl || uploadedFile) && !recording && (
          <Stack direction="row" spacing={1} alignItems="center">
            <IconButton
              onClick={handlePlayPause}
              sx={{ width: 56, height: 56, bgcolor: 'primary.main', color: 'white' }}
            >
              {isPlaying ? <PauseIcon /> : <PlayIcon />}
            </IconButton>
            <IconButton onClick={resetRecording} color="error" sx={{ width: 48, height: 48 }}>
              <DeleteIcon />
            </IconButton>
            {audioUrl && <audio ref={audioRef} src={audioUrl} onEnded={handleAudioEnded} />}
          </Stack>
        )}
      </Box>

      {recording && (
        <Typography
          align="center"
          variant="h4"
          fontWeight={700}
          color="error.main"
          sx={{ mb: 1 }}
        >
          {formattedDuration}
          {paused && <Typography component="span" variant="body2" sx={{ ml: 1 }}>(Paused)</Typography>}
        </Typography>
      )}

      {recorderError && (
        <Typography color="error" align="center" variant="body2" sx={{ mb: 1 }}>
          {recorderError}
        </Typography>
      )}

      {uploadProgress > 0 && uploadProgress < 100 && (
        <Box sx={{ mt: 2 }}>
          <LinearProgress variant="determinate" value={uploadProgress} />
        </Box>
      )}

      <Paper
        {...getRootProps()}
        variant="outlined"
        sx={{
          p: 3,
          mt: 2,
          textAlign: 'center',
          cursor: 'pointer',
          borderStyle: 'dashed',
          borderColor: isDragActive ? 'primary.main' : isDark ? 'rgba(255,255,255,0.15)' : 'divider',
          bgcolor: isDragActive ? (isDark ? 'rgba(121,134,203,0.1)' : 'rgba(26,35,126,0.04)') : 'transparent',
          transition: 'all 0.2s ease',
        }}
      >
        <input {...getInputProps()} />
        <UploadIcon sx={{ fontSize: 40, color: 'text.secondary', mb: 1 }} />
        <Typography variant="body2" color="text.secondary">
          {isDragActive
            ? 'Drop audio file here...'
            : 'Drag & drop an audio file, or click to browse'}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Supports MP3, WAV, WebM, OGG, M4A, FLAC (max 100MB)
        </Typography>
        {uploadedFile && !audioBlob && (
          <Chip
            icon={<AudioIcon />}
            label={uploadedFile.name}
            onDelete={() => setUploadedFile(null)}
            sx={{ mt: 1 }}
            color="primary"
          />
        )}
      </Paper>
    </Paper>
  );
}

export default AudioRecorder;
