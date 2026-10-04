import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({ baseURL });

export const uploadDataset = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then((res) => res.data);
};

export const runAudit = (payload) =>
  api.post('/audit/run', payload).then((res) => res.data);

export const runMitigation = (payload) =>
  api.post('/mitigate', payload).then((res) => res.data);

export const generateReport = (payload, auditRunId) =>
  api.post(`/report${auditRunId ? `?audit_run_id=${auditRunId}` : ''}`, payload)
    .then((res) => res.data);

export const getHistory = () =>
  api.get('/audit/history').then((res) => res.data);

export default api;