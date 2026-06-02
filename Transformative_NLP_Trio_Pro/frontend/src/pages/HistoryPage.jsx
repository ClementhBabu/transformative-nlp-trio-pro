import React, { useState, useEffect, useCallback } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  TextField,
  InputAdornment,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Pagination,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  CircularProgress,
  Stack,
  Collapse,
  Tooltip,
} from '@mui/material';
import {
  Search as SearchIcon,
  Delete as DeleteIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Translate as TranslateIcon,
  Summarize as SummarizeIcon,
  RecordVoiceOver as TtsIcon,
  Mic as MicIcon,
  ContentCopy as CopyIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import toast from 'react-hot-toast';
import { historyAPI, reportAPI } from '../services/api';

function HistoryPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('date');
  const [languageFilter, setLanguageFilter] = useState('all');
  const [expandedId, setExpandedId] = useState(null);
  const [deleteDialog, setDeleteDialog] = useState({ open: false, id: null });
  const [languages, setLanguages] = useState([]);

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    try {
      const params = { page, limit: 10 };
      if (sortBy) params.sort = sortBy;
      if (languageFilter !== 'all') params.language = languageFilter;

      let response;
      if (search.trim()) {
        response = await historyAPI.search(search);
      } else {
        response = await historyAPI.getAll(page, 10);
      }

      const data = response.data;
      const itemsList = data.items || data.data || data;
      setItems(Array.isArray(itemsList) ? itemsList : []);
      setTotalPages(data.pages || data.total_pages || Math.ceil((data.total || itemsList.length) / 10) || 1);

      const langs = new Set();
      (Array.isArray(itemsList) ? itemsList : []).forEach((item) => {
        if (item.language) langs.add(item.language);
        if (item.source_language) langs.add(item.source_language);
        if (item.target_language) langs.add(item.target_language);
      });
      setLanguages(Array.from(langs));
    } catch {
      toast.error('Failed to load history.');
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [page, search, sortBy, languageFilter]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const handleDelete = async () => {
    try {
      await historyAPI.deleteRecord(deleteDialog.id);
      toast.success('Record deleted.');
      setDeleteDialog({ open: false, id: null });
      fetchHistory();
    } catch {
      toast.error('Failed to delete record.');
    }
  };

  const handleDownloadReport = async (historyId) => {
    try {
      const response = await reportAPI.generate(historyId);
      const filename = response.data.filename;
      if (filename) {
        window.open(reportAPI.download(filename), '_blank');
        toast.success('Report downloaded.');
      }
    } catch {
      toast.error('Failed to generate report.');
    }
  };

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied!');
  };

  const getOperationIcon = (op) => {
    switch (op?.toLowerCase()) {
      case 'translation': return <TranslateIcon />;
      case 'summary': return <SummarizeIcon />;
      case 'tts': return <TtsIcon />;
      default: return <MicIcon />;
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Processing History
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        View and manage your past processing records.
      </Typography>

      <Card sx={{ borderRadius: 3, mb: 3, p: 2 }} elevation={2}>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="center">
          <TextField
            placeholder="Search history..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            size="small"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            sx={{ minWidth: 240 }}
          />

          <FormControl size="small" sx={{ minWidth: 140 }}>
            <InputLabel>Sort By</InputLabel>
            <Select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              label="Sort By"
            >
              <MenuItem value="date">Date (Newest)</MenuItem>
              <MenuItem value="date_asc">Date (Oldest)</MenuItem>
              <MenuItem value="language">Language</MenuItem>
              <MenuItem value="type">Type</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 140 }}>
            <InputLabel>Language</InputLabel>
            <Select
              value={languageFilter}
              onChange={(e) => setLanguageFilter(e.target.value)}
              label="Language"
            >
              <MenuItem value="all">All Languages</MenuItem>
              {languages.map((lang) => (
                <MenuItem key={lang} value={lang}>{lang}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Stack>
      </Card>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
          <CircularProgress />
        </Box>
      ) : items.length === 0 ? (
        <Card sx={{ borderRadius: 3, p: 6, textAlign: 'center' }} elevation={2}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No records found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Process some audio to see your history here.
          </Typography>
        </Card>
      ) : (
        <>
          <Grid container spacing={2}>
            {items.map((item, i) => {
              const isExpanded = expandedId === (item.id || i);
              return (
                <Grid item xs={12} key={item.id || i}>
                  <Card sx={{ borderRadius: 3 }} elevation={1}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <Box sx={{ flex: 1, minWidth: 0 }}>
                          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', mb: 1, flexWrap: 'wrap' }}>
                            {getOperationIcon(item.operation || item.type)}
                            <Typography variant="body2" color="text.secondary">
                              {item.created_at
                                ? format(new Date(item.created_at), 'MMM dd, yyyy HH:mm')
                                : 'Unknown date'}
                            </Typography>
                            {item.language && (
                              <Chip label={item.language} size="small" variant="outlined" />
                            )}
                            {item.operation && (
                              <Chip label={item.operation} size="small" color="primary" variant="outlined" />
                            )}
                          </Box>
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            noWrap
                            sx={{ maxWidth: '80%' }}
                          >
                            {(item.text || item.original_text || item.transcript || 'Audio processing').substring(0, 150)}
                          </Typography>
                        </Box>

                        <Box sx={{ display: 'flex', gap: 0.5, flexShrink: 0 }}>
                          <Tooltip title="Copy text">
                            <IconButton
                              size="small"
                              onClick={() => handleCopy(
                                item.text || item.original_text || item.transcript || ''
                              )}
                            >
                              <CopyIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Download Report">
                            <IconButton
                              size="small"
                              onClick={() => handleDownloadReport(item.id)}
                            >
                              <DownloadIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title={isExpanded ? 'Collapse' : 'Expand'}>
                            <IconButton
                              size="small"
                              onClick={() => setExpandedId(isExpanded ? null : (item.id || i))}
                            >
                              {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => setDeleteDialog({ open: true, id: item.id })}
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </Box>

                      <Collapse in={isExpanded}>
                        <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
                          {item.original_text && (
                            <Box sx={{ mb: 2 }}>
                              <Typography variant="subtitle2" fontWeight={600}>Original Text</Typography>
                              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', mt: 0.5 }}>
                                {item.original_text}
                              </Typography>
                            </Box>
                          )}
                          {item.summary && (
                            <Box sx={{ mb: 2 }}>
                              <Typography variant="subtitle2" fontWeight={600}>Summary</Typography>
                              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', mt: 0.5 }}>
                                {item.summary}
                              </Typography>
                            </Box>
                          )}
                          {item.translation && (
                            <Box sx={{ mb: 2 }}>
                              <Typography variant="subtitle2" fontWeight={600}>Translation</Typography>
                              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', mt: 0.5 }}>
                                {item.translation}
                              </Typography>
                            </Box>
                          )}
                          {item.text && !item.original_text && (
                            <Box sx={{ mb: 2 }}>
                              <Typography variant="subtitle2" fontWeight={600}>Text</Typography>
                              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', mt: 0.5 }}>
                                {item.text}
                              </Typography>
                            </Box>
                          )}
                        </Box>
                      </Collapse>
                    </CardContent>
                  </Card>
                </Grid>
              );
            })}
          </Grid>

          {totalPages > 1 && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
              <Pagination
                count={totalPages}
                page={page}
                onChange={(_, p) => setPage(p)}
                color="primary"
                size="large"
              />
            </Box>
          )}
        </>
      )}

      <Dialog open={deleteDialog.open} onClose={() => setDeleteDialog({ open: false, id: null })}>
        <DialogTitle>Delete Record</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this record? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog({ open: false, id: null })}>Cancel</Button>
          <Button onClick={handleDelete} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

export default HistoryPage;
