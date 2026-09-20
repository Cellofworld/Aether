import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosError } from 'axios';

const API_BASE_URL = '/api';

// Создание экземпляра axios
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерцептор для добавления токена
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Интерцептор для обработки ошибок авторизации
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Токен истек или невалиден
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      
      // Перенаправление на страницу входа
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (username: string, password: string) => 
    apiClient.post('/auth/login', { username, password }),
  
  logout: () => apiClient.post('/auth/logout'),
  
  getCurrentUser: () => apiClient.get('/auth/me'),
};

// Libraries API
export const librariesAPI = {
  getAll: () => apiClient.get('/libraries'),
  getById: (id: number) => apiClient.get(`/libraries/${id}`),
  getItems: (libraryId: number, params?: Record<string, any>) => 
    apiClient.get(`/libraries/${libraryId}/items`, { params }),
};

// Media API
export const mediaAPI = {
  getMovie: (id: number) => apiClient.get(`/movies/${id}`),
  getSeries: (id: number) => apiClient.get(`/series/${id}`),
  getSeasons: (seriesId: number) => apiClient.get(`/series/${seriesId}/seasons`),
  getEpisodes: (seasonId: number) => apiClient.get(`/seasons/${seasonId}/episodes`),
  getRecent: (limit = 20) => apiClient.get('/media/recent', { params: { limit } }),
};

// Playback API
export const playbackAPI = {
  getContinueWatching: () => apiClient.get('/playback/continue'),
  updateProgress: (mediaId: number, position: number, duration: number) => 
    apiClient.post('/playback/progress', { media_id: mediaId, position, duration }),
  markAsWatched: (mediaId: number) => apiClient.post(`/playback/${mediaId}/watched`),
};

// Search API
export const searchAPI = {
  search: (query: string) => apiClient.get('/search', { params: { q: query } }),
};

// Admin API
export const adminAPI = {
  getStats: () => apiClient.get('/admin/stats'),
  startScan: (libraryId?: number) => apiClient.post('/admin/scan', { library_id: libraryId }),
  getJobStatus: (jobId: string) => apiClient.get(`/admin/jobs/${jobId}`),
  getJobs: () => apiClient.get('/admin/jobs'),
};

// Home API - агрегирует данные для главной страницы
export const homeAPI = {
  getHomeData: async () => {
    const [continueWatching, recentlyAdded] = await Promise.all([
      playbackAPI.getContinueWatching().catch(() => ({ items: [] })),
      mediaAPI.getRecent(12),
    ]);
    return { continueWatching: continueWatching.items || [], recentlyAdded: recentlyAdded.items || [] };
  },
};

export default apiClient;
