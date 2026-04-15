import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const extractErrorMessage = (error, fallback) => {
  const detail = error?.response?.data?.detail;
  if (Array.isArray(detail)) {
    return detail.map((d) => d?.msg).filter(Boolean).join(', ') || fallback;
  }
  if (typeof detail === 'string' && detail.trim()) {
    return detail;
  }
  return error?.message || fallback;
};

export const predictReview = async (text) => {
  try {
    const response = await apiClient.post('/predict', { text });
    return response.data;
  } catch (error) {
    throw new Error(extractErrorMessage(error, 'Failed to analyze review.'));
  }
};

export const uploadCSV = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data?.results || [];
  } catch (error) {
    throw new Error(extractErrorMessage(error, 'Failed to upload CSV.'));
  }
};

export const getModerationData = async () => {
  try {
    const response = await apiClient.get('/moderation', {
      params: { risk_level: 'High Risk', limit: 100 },
    });
    return response.data?.items || [];
  } catch (error) {
    throw new Error(extractErrorMessage(error, 'Failed to fetch moderation queue.'));
  }
};

export const getDashboardStats = async () => {
  try {
    const response = await apiClient.get('/moderation', {
      params: { risk_level: 'all', limit: 10000 },
    });
    const { total, items } = response.data;
    
    if (!items || items.length === 0) {
      return null; // Use defaults if no data
    }
    
    const avgTrust = Math.round(
      items.reduce((sum, item) => sum + item.trust_score, 0) / items.length
    );
    
    const fakePercent = (
      (items.filter(i => i.risk_level === 'High Risk').length / total) * 100
    ).toFixed(1);
    
    const highRisk = items.filter(i => i.risk_level === 'High Risk').length;
    
    return {
      total,
      avgTrust,
      fakePercent: parseFloat(fakePercent),
      highRisk
    };
  } catch (error) {
    console.error('Failed to fetch dashboard stats:', error);
    return null; // Will fall back to defaults
  }
};
