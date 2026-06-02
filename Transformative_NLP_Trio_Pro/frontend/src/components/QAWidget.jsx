import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  IconButton,
  Typography,
  Paper,
  CircularProgress,
  Chip,
  Stack,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  Lightbulb as SuggestIcon,
} from '@mui/icons-material';
import { qaAPI } from '../services/api';
import toast from 'react-hot-toast';

function QAWidget({ context = '', onResult }) {
  const [question, setQuestion] = useState('');
  const [qaHistory, setQaHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [suggestedQuestions, setSuggestedQuestions] = useState([]);
  const [generatingSuggestions, setGeneratingSuggestions] = useState(false);

  useEffect(() => {
    if (context && context.length > 50) {
      generateSuggestions();
    }
  }, [context]);

  const generateSuggestions = async () => {
    setGeneratingSuggestions(true);
    try {
      const response = await qaAPI.generateQuestions(context);
      setSuggestedQuestions(response.data.questions || response.data || []);
    } catch {
      setSuggestedQuestions([
        'What is the main topic?',
        'What are the key points?',
        'Can you provide more details?',
      ]);
    } finally {
      setGeneratingSuggestions(false);
    }
  };

  const handleAsk = async () => {
    if (!question.trim()) return;
    const q = question.trim();
    setQaHistory((prev) => [...prev, { type: 'question', text: q }]);
    setQuestion('');
    setLoading(true);

    try {
      const response = await qaAPI.ask(context, q);
      const answer = response.data.answer || response.data.result || 'No answer found.';
      setQaHistory((prev) => [...prev, { type: 'answer', text: answer }]);
      if (onResult) onResult({ question: q, answer });
    } catch (error) {
      const msg = error.response?.data?.detail || 'Failed to get answer';
      toast.error(msg);
      setQaHistory((prev) => [...prev, { type: 'answer', text: 'Sorry, unable to answer that question.', error: true }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAsk();
    }
  };

  return (
    <Paper sx={{ p: 3, borderRadius: 3 }} elevation={2}>
      <Typography variant="h6" fontWeight={600} gutterBottom>
        Ask About This Text
      </Typography>

      {suggestedQuestions.length > 0 && qaHistory.length === 0 && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
            <SuggestIcon fontSize="small" /> Suggested Questions
          </Typography>
          <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap>
            {suggestedQuestions.map((sq, i) => (
              <Chip
                key={i}
                label={sq}
                size="small"
                onClick={() => setQuestion(sq)}
                clickable
                variant="outlined"
                sx={{ mb: 0.5 }}
              />
            ))}
          </Stack>
        </Box>
      )}

      <Box
        sx={{
          maxHeight: 300,
          overflow: 'auto',
          mb: 2,
          display: 'flex',
          flexDirection: 'column',
          gap: 1.5,
        }}
      >
        {qaHistory.map((item, index) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              gap: 1,
              justifyContent: item.type === 'question' ? 'flex-end' : 'flex-start',
            }}
          >
            {item.type === 'answer' && (
              <BotIcon fontSize="small" color="primary" sx={{ mt: 0.3 }} />
            )}
            <Paper
              variant="outlined"
              sx={{
                p: 1.5,
                maxWidth: '85%',
                borderRadius: 2,
                bgcolor:
                  item.type === 'question'
                    ? 'primary.main'
                    : item.error
                    ? 'error.dark'
                    : 'background.paper',
                color: item.type === 'question' ? 'white' : 'text.primary',
              }}
            >
              <Typography variant="body2">{item.text}</Typography>
            </Paper>
            {item.type === 'question' && (
              <PersonIcon fontSize="small" color="primary" sx={{ mt: 0.3 }} />
            )}
          </Box>
        ))}
        {loading && (
          <Box sx={{ display: 'flex', gap: 1 }}>
            <BotIcon fontSize="small" color="primary" />
            <CircularProgress size={20} />
          </Box>
        )}
      </Box>

      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          size="small"
          placeholder="Ask a question about the text..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading || !context}
          multiline
          maxRows={3}
        />
        <IconButton
          onClick={handleAsk}
          disabled={loading || !question.trim()}
          color="primary"
          sx={{ alignSelf: 'flex-end' }}
        >
          <SendIcon />
        </IconButton>
      </Box>
    </Paper>
  );
}

export default QAWidget;
