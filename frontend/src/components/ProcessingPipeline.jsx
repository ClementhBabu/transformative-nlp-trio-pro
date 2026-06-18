import React from 'react';
import {
  Box,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Typography,
  LinearProgress,
  Paper,
  Chip,
  IconButton,
  Collapse,
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  HourglassEmpty as PendingIcon,
  Replay as RetryIcon,
  CloudUpload,
  Hearing,
  Summarize,
  Translate,
  RecordVoiceOver,
} from '@mui/icons-material';

const steps = [
  { key: 'upload', label: 'Upload Audio', icon: CloudUpload },
  { key: 'recognize', label: 'Speech Recognition', icon: Hearing },
  { key: 'summarize', label: 'AI Summarization', icon: Summarize },
  { key: 'translate', label: 'Translation', icon: Translate },
  { key: 'tts', label: 'Voice Generation', icon: RecordVoiceOver },
];

const statusConfig = {
  pending: { icon: PendingIcon, color: 'default', label: 'Pending' },
  processing: { icon: null, color: 'primary', label: 'Processing' },
  completed: { icon: CheckIcon, color: 'success', label: 'Completed' },
  error: { icon: ErrorIcon, color: 'error', label: 'Failed' },
};

function ProcessingPipeline({
  pipelineState = {},
  onRetry,
  results = {},
}) {
  const getStatus = (key) => pipelineState[key] || 'pending';

  return (
    <Paper sx={{ p: 3, borderRadius: 3 }} elevation={2}>
      <Typography variant="h6" fontWeight={600} gutterBottom>
        Processing Pipeline
      </Typography>

      <Box sx={{ mt: 2 }}>
        {steps.map((step, index) => {
          const status = getStatus(step.key);
          const config = statusConfig[status] || statusConfig.pending;
          const StepIcon = step.icon;
          const StatusIcon = config.icon;

          return (
            <Box
              key={step.key}
              sx={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: 2,
                py: 1.5,
                position: 'relative',
              }}
            >
              {index < steps.length - 1 && (
                <Box
                  sx={{
                    position: 'absolute',
                    left: 19,
                    top: 48,
                    bottom: 0,
                    width: 2,
                    bgcolor:
                      status === 'completed'
                        ? 'success.main'
                        : status === 'processing'
                        ? 'primary.main'
                        : 'divider',
                  }}
                />
              )}

              <Box
                sx={{
                  width: 40,
                  height: 40,
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  bgcolor:
                    status === 'completed'
                      ? 'success.main'
                      : status === 'error'
                      ? 'error.main'
                      : status === 'processing'
                      ? 'primary.main'
                      : 'grey.400',
                  color: 'white',
                  animation: status === 'processing' ? 'pulse 1.5s ease-in-out infinite' : 'none',
                }}
              >
                {StatusIcon ? <StatusIcon /> : <StepIcon />}
              </Box>

              <Box sx={{ flex: 1, minWidth: 0 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="subtitle2" fontWeight={600}>
                    {step.label}
                  </Typography>
                  <Chip
                    label={config.label}
                    size="small"
                    color={config.color}
                    variant="outlined"
                    sx={{ height: 20, fontSize: '0.7rem' }}
                  />
                  {status === 'error' && (
                    <IconButton size="small" color="error" onClick={() => onRetry?.(step.key)}>
                      <RetryIcon fontSize="small" />
                    </IconButton>
                  )}
                </Box>

                {status === 'processing' && (
                  <LinearProgress sx={{ mt: 0.5, borderRadius: 4, height: 4 }} />
                )}

                {status === 'completed' && results[step.key] && (
                  <Collapse in>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{
                        mt: 0.5,
                        maxHeight: 60,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                      }}
                    >
                      {typeof results[step.key] === 'string'
                        ? results[step.key].substring(0, 120) + '...'
                        : JSON.stringify(results[step.key]).substring(0, 120) + '...'}
                    </Typography>
                  </Collapse>
                )}

                {status === 'error' && (
                  <Typography variant="body2" color="error.main" sx={{ mt: 0.5 }}>
                    {results[`${step.key}_error`] || 'An error occurred. Please retry.'}
                  </Typography>
                )}
              </Box>
            </Box>
          );
        })}
      </Box>
    </Paper>
  );
}

export default ProcessingPipeline;
