import axios from 'axios';
import {
  Video,
  DashboardSummary,
  ProcessVideoParams,
  SessionStatus,
  SessionAnalytics,
  CrossingEvent,
  Alert,
  SystemSettings
} from '../types';

const client = axios.create({
  baseURL: '/api',
  timeout: 60000,
});

export const api = {
  // Health
  getHealth: async () => {
    const res = await client.get('/health');
    return res.data;
  },

  // Dashboard
  getDashboardSummary: async (): Promise<DashboardSummary> => {
    const res = await client.get('/dashboard/summary');
    return res.data;
  },

  getAlerts: async (sessionId?: string): Promise<Alert[]> => {
    const res = await client.get('/dashboard/alerts', {
      params: sessionId ? { session_id: sessionId } : {}
    });
    return res.data;
  },

  // Videos
  getVideos: async (): Promise<Video[]> => {
    const res = await client.get('/videos');
    return res.data;
  },

  getVideo: async (videoId: string): Promise<Video> => {
    const res = await client.get(`/videos/${videoId}`);
    return res.data;
  },

  uploadVideo: async (
    file: File,
    onProgress?: (percent: number) => void
  ): Promise<Video> => {
    const formData = new FormData();
    formData.append('file', file);

    const res = await client.post('/videos/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percent);
        }
      },
    });
    return res.data;
  },

  getVideoPreview: async (
    videoId: string,
    frameNumber: number = 0
  ): Promise<{ video_id: string; frame_number: number; preview_url: string; width: number; height: number }> => {
    const res = await client.get(`/videos/${videoId}/preview`, {
      params: { frame_number: frameNumber }
    });
    return res.data;
  },

  deleteVideo: async (videoId: string): Promise<{ status: string; message: string }> => {
    const res = await client.delete(`/videos/${videoId}`);
    return res.data;
  },

  // Processing
  startProcessing: async (videoId: string, params: ProcessVideoParams): Promise<SessionStatus> => {
    const res = await client.post(`/process/${videoId}`, params);
    return res.data;
  },

  getSessionStatus: async (sessionId: string): Promise<SessionStatus> => {
    const res = await client.get(`/process/${sessionId}/status`);
    return res.data;
  },

  cancelSession: async (sessionId: string): Promise<{ session_id: string; status: string }> => {
    const res = await client.post(`/process/${sessionId}/cancel`);
    return res.data;
  },

  getSessionResults: async (sessionId: string): Promise<SessionAnalytics> => {
    const res = await client.get(`/process/${sessionId}/results`);
    return res.data;
  },

  getSessionEvents: async (sessionId: string, limit = 200, offset = 0): Promise<CrossingEvent[]> => {
    const res = await client.get(`/process/${sessionId}/events`, {
      params: { limit, offset }
    });
    return res.data;
  },

  // Settings
  getSettings: async (): Promise<SystemSettings> => {
    const res = await client.get('/settings');
    return res.data;
  },

  updateSettings: async (settingsData: Partial<SystemSettings>): Promise<{ status: string; message: string }> => {
    const res = await client.post('/settings', settingsData);
    return res.data;
  }
};
