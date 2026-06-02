import React, { useState, useEffect, useMemo } from 'react';
import {
  Autocomplete,
  TextField,
  Box,
  Typography,
  Chip,
  CircularProgress,
} from '@mui/material';
import { translateAPI } from '../services/api';

function LanguageSelector({ value, onChange, label = 'Select Language', showDetect = false, sx }) {
  const [languages, setLanguages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [recent, setRecent] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('recentLanguages') || '[]');
    } catch {
      return [];
    }
  });

  useEffect(() => {
    const fetchLanguages = async () => {
      try {
        const response = await translateAPI.getLanguages();
        setLanguages(response.data.languages || response.data || []);
      } catch {
        setLanguages([
          { code: 'en', name: 'English' },
          { code: 'es', name: 'Spanish' },
          { code: 'fr', name: 'French' },
          { code: 'de', name: 'German' },
          { code: 'it', name: 'Italian' },
          { code: 'pt', name: 'Portuguese' },
          { code: 'ru', name: 'Russian' },
          { code: 'ja', name: 'Japanese' },
          { code: 'zh', name: 'Chinese' },
          { code: 'ko', name: 'Korean' },
          { code: 'ar', name: 'Arabic' },
          { code: 'hi', name: 'Hindi' },
          { code: 'nl', name: 'Dutch' },
          { code: 'pl', name: 'Polish' },
          { code: 'tr', name: 'Turkish' },
          { code: 'sv', name: 'Swedish' },
        ]);
      } finally {
        setLoading(false);
      }
    };
    fetchLanguages();
  }, []);

  const options = useMemo(() => {
    const opts = [...languages];
    if (showDetect) {
      opts.unshift({ code: 'auto', name: 'Auto-detect' });
    }
    const recents = recent.filter(
      (r) => !opts.find((o) => o.code === r.code)
    );
    return [...recents, ...opts];
  }, [languages, recent, showDetect]);

  const selectedOption = options.find((o) => o.code === value) || null;

  const handleChange = (_, newValue) => {
    const code = newValue?.code || '';
    onChange(code);
    if (code && code !== 'auto') {
      const updated = [newValue, ...recent.filter((r) => r.code !== newValue.code)].slice(0, 4);
      setRecent(updated);
      localStorage.setItem('recentLanguages', JSON.stringify(updated));
    }
  };

  return (
    <Autocomplete
      value={selectedOption}
      onChange={handleChange}
      options={options}
      loading={loading}
      getOptionLabel={(option) => `${option.name} (${option.code})`}
      isOptionEqualToValue={(option, val) => option.code === val?.code}
      groupBy={(option) => {
        if (recent.find((r) => r.code === option.code)) return 'Recently Used';
        if (option.code === 'auto') return '';
        return 'All Languages';
      }}
      renderInput={(params) => (
        <TextField
          {...params}
          label={label}
          InputProps={{
            ...params.InputProps,
            endAdornment: (
              <>
                {loading && <CircularProgress color="inherit" size={20} />}
                {params.InputProps.endAdornment}
              </>
            ),
          }}
        />
      )}
      renderOption={(props, option) => (
        <Box component="li" {...props} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="body2">{option.name}</Typography>
          <Chip label={option.code} size="small" variant="outlined" />
        </Box>
      )}
      sx={sx}
      fullWidth
    />
  );
}

export default LanguageSelector;
