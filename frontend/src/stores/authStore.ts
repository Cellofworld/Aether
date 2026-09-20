import { create } from 'zustand';
import { authAPI } from '../services/api';
import type { User, LoginResponse } from '../types';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  checkAuth: () => Promise<void>;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  setUser: (user: User | null) => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: localStorage.getItem('access_token'),
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,

  checkAuth: async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      set({ user: null, isAuthenticated: false });
      return;
    }
    
    try {
      const response = await authAPI.getCurrentUser();
      set({ 
        user: response.data, 
        isAuthenticated: true,
        isLoading: false 
      });
    } catch (error) {
      localStorage.removeItem('access_token');
      set({ user: null, token: null, isAuthenticated: false });
    }
  },

  login: async (username: string, password: string) => {
    set({ isLoading: true });
    try {
      const response = await authAPI.login(username, password);
      const data = response.data as LoginResponse;
      
      localStorage.setItem('access_token', data.access_token);
      if (data.refresh_token) {
        localStorage.setItem('refresh_token', data.refresh_token);
      }
      
      set({ 
        user: data.user, 
        token: data.access_token, 
        isAuthenticated: true,
        isLoading: false 
      });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({ user: null, token: null, isAuthenticated: false });
  },

  setUser: (user: User | null) => {
    set({ user });
  },
}));
