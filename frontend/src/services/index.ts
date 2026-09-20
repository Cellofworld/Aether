import apiClient from './api';
import type { 
  User, 
  AuthTokens, 
  LoginRequest, 
  Library, 
  MediaItem, 
  Movie, 
  Series, 
  Season,
  Episode,
  ContinueWatchingItem,
  SearchResult,
  ScanJob,
  DashboardStats 
} from '@/types';

// Auth API
export const authApi = {
  login: async (data: LoginRequest): Promise<AuthTokens> => {
    const response = await apiClient.post<AuthTokens>('/auth/login', data);
    return response.data;
  },

  register: async (data: { username: string; password: string; email: string }): Promise<User> => {
    const response = await apiClient.post<User>('/auth/register', data);
    return response.data;
  },

  getMe: async (): Promise<User> => {
    const response = await apiClient.get<User>('/users/me');
    return response.data;
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/auth/logout');
  },
};

// Libraries API
export const librariesApi = {
  getAll: async (): Promise<Library[]> => {
    const response = await apiClient.get<Library[]>('/libraries');
    return response.data;
  },

  getById: async (id: number): Promise<Library> => {
    const response = await apiClient.get<Library>(`/libraries/${id}`);
    return response.data;
  },

  create: async (data: { name: string; type: string; paths: string[] }): Promise<Library> => {
    const response = await apiClient.post<Library>('/libraries', data);
    return response.data;
  },

  update: async (id: number, data: Partial<Library>): Promise<Library> => {
    const response = await apiClient.put<Library>(`/libraries/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/libraries/${id}`);
  },

  getItems: async (libraryId: number, page = 1, limit = 20): Promise<{ items: MediaItem[]; total: number }> => {
    const response = await apiClient.get<{ items: MediaItem[]; total: number }>(
      `/libraries/${libraryId}/items`,
      { params: { page, limit } }
    );
    return response.data;
  },
};

// Media API
export const mediaApi = {
  getMovies: async (page = 1, limit = 20): Promise<{ items: Movie[]; total: number }> => {
    const response = await apiClient.get<{ items: Movie[]; total: number }>('/media/movies', {
      params: { page, limit },
    });
    return response.data;
  },

  getSeries: async (page = 1, limit = 20): Promise<{ items: Series[]; total: number }> => {
    const response = await apiClient.get<{ items: Series[]; total: number }>('/media/series', {
      params: { page, limit },
    });
    return response.data;
  },

  getMovie: async (id: number): Promise<Movie> => {
    const response = await apiClient.get<Movie>(`/media/movies/${id}`);
    return response.data;
  },

  getSeries: async (id: number): Promise<Series> => {
    const response = await apiClient.get<Series>(`/media/series/${id}`);
    return response.data;
  },

  getSeason: async (id: number): Promise<Season> => {
    const response = await apiClient.get<Season>(`/media/seasons/${id}`);
    return response.data;
  },

  getEpisodes: async (seasonId: number): Promise<Episode[]> => {
    const response = await apiClient.get<Episode[]>(`/media/seasons/${seasonId}/episodes`);
    return response.data;
  },
};

// Search API
export const searchApi = {
  search: async (query: string): Promise<SearchResult> => {
    const response = await apiClient.get<SearchResult>('/search', {
      params: { q: query },
    });
    return response.data;
  },
};

// Playback API
export const playbackApi = {
  getContinueWatching: async (): Promise<ContinueWatchingItem[]> => {
    const response = await apiClient.get<ContinueWatchingItem[]>('/playback/continue-watching');
    return response.data;
  },

  updateProgress: async (data: { 
    media_id: number; 
    position: number; 
    duration: number; 
    episode_id?: number 
  }): Promise<void> => {
    await apiClient.post('/playback/progress', data);
  },

  markAsWatched: async (mediaId: number, episodeId?: number): Promise<void> => {
    await apiClient.post(`/playback/watched/${mediaId}`, episodeId ? { episode_id: episodeId } : {});
  },
};

// Admin API
export const adminApi = {
  getDashboardStats: async (): Promise<DashboardStats> => {
    const response = await apiClient.get<DashboardStats>('/admin/dashboard');
    return response.data;
  },

  startScan: async (libraryId?: number): Promise<ScanJob> => {
    const response = await apiClient.post<ScanJob>('/admin/scan', libraryId ? { library_id: libraryId } : {});
    return response.data;
  },

  getScanJobs: async (): Promise<ScanJob[]> => {
    const response = await apiClient.get<ScanJob[]>('/admin/jobs');
    return response.data;
  },

  getScanJob: async (jobId: number): Promise<ScanJob> => {
    const response = await apiClient.get<ScanJob>(`/admin/jobs/${jobId}`);
    return response.data;
  },
};
