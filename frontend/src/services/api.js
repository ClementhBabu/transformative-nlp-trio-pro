import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data) => api.post('/api/auth/register', data),
  login: (data) => api.post('/api/auth/login', data),
  forgotPassword: (email) => api.post('/api/auth/forgot-password', { email }),
  resetPassword: (token, newPassword) =>
    api.post('/api/auth/reset-password', { token, new_password: newPassword }),
  getProfile: () => api.get('/api/auth/me'),
  updateProfile: (data) => api.put('/api/auth/profile', data),
};

export const speechAPI = {
  uploadAudio: (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/speech/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (onProgress) onProgress(Math.round((e.loaded * 100) / e.total));
      },
    });
  },
  speechToText: (filePath, language) => {
    const formData = new FormData();
    formData.append('file_path', filePath);
    if (language) formData.append('language', language);
    return api.post('/api/speech/speech-to-text', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  detectLanguage: (filePath) => {
    const formData = new FormData();
    formData.append('file_path', filePath);
    return api.post('/api/speech/detect-language', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getStatus: (taskId) => api.get(`/api/speech/status/${taskId}`),
};

export const summarizeAPI = {
  summarize: (text, mode = 'medium') =>
    api.post('/api/summarize/', { text, mode }),
  batchSummarize: (texts, mode = 'medium') =>
    api.post('/api/summarize/batch', { texts, mode }),
  getModes: () => api.get('/api/summarize/modes'),
};

export const translateAPI = {
  translate: (text, sourceLang, targetLang) =>
    api.post('/api/translate/', { text, source_lang: sourceLang, target_lang: targetLang }),
  getLanguages: () => api.get('/api/translate/languages'),
  detectLanguage: (text) => api.post('/api/translate/detect', { text }),
};

export const ttsAPI = {
  generate: (text, language = 'en', gender = 'female') =>
    api.post('/api/tts/generate', { text, language, gender }),
  getVoices: () => api.get('/api/tts/voices'),
  getDownloadUrl: (filename) => `${API_BASE_URL}/api/tts/download/${filename}`,
  getStreamUrl: (filename) => `${API_BASE_URL}/api/tts/stream/${filename}`,
};

export const pipelineAPI = {
  process: (formData, onProgress) =>
    api.post('/api/pipeline/process', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (onProgress) onProgress(Math.round((e.loaded * 100) / e.total));
      },
    }),
  getStatus: (pipelineId) => api.get(`/api/pipeline/status/${pipelineId}`),
};

export const historyAPI = {
  getAll: (page = 1, limit = 10) =>
    api.get('/api/history/', { params: { page, limit } }),
  getById: (id) => api.get(`/api/history/${id}`),
  deleteRecord: (id) => api.delete(`/api/history/${id}`),
  search: (query) => api.get('/api/history/search', { params: { q: query } }),
  getRecent: () => api.get('/api/history/recent'),
};

export const analyticsAPI = {
  getUserAnalytics: () => api.get('/api/analytics/user'),
  getAdminAnalytics: () => api.get('/api/analytics/admin'),
  getDaily: (days = 30) => api.get('/api/analytics/daily', { params: { days } }),
  getLanguages: () => api.get('/api/analytics/languages'),
  getOperations: () => api.get('/api/analytics/operations'),
};

export const reportAPI = {
  generate: (historyId) => api.post('/api/report/generate', { history_id: historyId }),
  download: (filename) => `${API_BASE_URL}/api/report/download/${filename}`,
  list: () => api.get('/api/report/list'),
  deleteReport: (id) => api.delete(`/api/report/${id}`),
};

export const sentimentAPI = {
  analyze: (text) => api.post('/api/sentiment/analyze', { text }),
  batchAnalyze: (texts) => api.post('/api/sentiment/batch', { texts }),
};

export const keywordsAPI = {
  extract: (text, numKeywords = 10) =>
    api.post('/api/keywords/extract', { text, num_keywords: numKeywords }),
  extractKeyphrases: (text) => api.post('/api/keywords/keyphrases', { text }),
};

export const qaAPI = {
  ask: (context, question) => api.post('/api/qa/ask', { text: context, question }),
  generateQuestions: (context, numQuestions = 5) =>
    api.post('/api/qa/generate-questions', { text: context, num_questions: numQuestions }),
};

export const meetingAPI = {
  generate: (text) => api.post('/api/meeting/generate', { text }),
  fromAudio: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/meeting/from-audio', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getById: (id) => api.get(`/api/meeting/${id}`),
};

export default api;
