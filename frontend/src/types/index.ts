export interface User {
  id: number;
  username: string;
  email?: string;
  role: 'admin' | 'user';
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  user: User;
}

export interface MediaItem {
  id: number;
  title: string;
  original_title?: string;
  overview?: string;
  year?: number;
  rating?: number;
  poster_url?: string;
  backdrop_url?: string;
  media_type: 'movie' | 'series' | 'episode';
  resolution?: string;
  seasons_count?: number;
  runtime?: number;
  genres?: string[];
}

export interface Movie extends MediaItem {
  media_type: 'movie';
}

export interface Series extends MediaItem {
  media_type: 'series';
  seasons_count: number;
}

export interface Season {
  id: number;
  series_id: number;
  season_number: number;
  title: string;
  overview?: string;
  poster_url?: string;
  episodes_count: number;
}

export interface Episode {
  id: number;
  season_id: number;
  episode_number: number;
  title: string;
  overview?: string;
  poster_url?: string;
  duration: number;
  air_date?: string;
}

export interface Library {
  id: number;
  name: string;
  type: 'movies' | 'series' | 'anime' | 'cartoons' | 'documentaries';
  paths: string[];
  created_at: string;
  updated_at: string;
}

export interface ContinueWatchingItem {
  id: number;
  media_id: number;
  media_type: 'movie' | 'episode';
  title: string;
  poster_url?: string;
  progress: number;
  duration: number;
  episode_title?: string;
  season_number?: number;
  episode_number?: number;
}

export interface SearchResults {
  movies: MediaItem[];
  series: MediaItem[];
  episodes: Episode[];
  people: Person[];
}

export interface Person {
  id: number;
  name: string;
  role: 'actor' | 'director';
  character?: string;
  profile_url?: string;
}

export interface DashboardStats {
  movies_count: number;
  series_count: number;
  episodes_count: number;
  storage_used: number;
  last_scan?: string;
  active_streams: number;
  transcoding_sessions: number;
}

export interface ScanJob {
  id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  current_file?: string;
  added: number;
  updated: number;
  removed: number;
  errors: number;
  started_at?: string;
  completed_at?: string;
}
