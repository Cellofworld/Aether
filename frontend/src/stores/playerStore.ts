import { create } from 'zustand';
import type { MediaItem, Movie, Series, ContinueWatchingItem } from '@/types';

interface PlayerState {
  currentMedia: MediaItem | null;
  isPlaying: boolean;
  position: number;
  duration: number;
  volume: number;
  isMuted: boolean;
  playbackRate: number;
  audioTrackId: number | null;
  subtitleTrackId: number | null;
  isFullscreen: boolean;
  
  setMedia: (media: MediaItem) => void;
  play: () => void;
  pause: () => void;
  seek: (position: number) => void;
  setDuration: (duration: number) => void;
  setVolume: (volume: number) => void;
  toggleMute: () => void;
  setPlaybackRate: (rate: number) => void;
  setAudioTrack: (trackId: number | null) => void;
  setSubtitleTrack: (trackId: number | null) => void;
  toggleFullscreen: () => void;
  reset: () => void;
}

export const usePlayerStore = create<PlayerState>((set) => ({
  currentMedia: null,
  isPlaying: false,
  position: 0,
  duration: 0,
  volume: 1,
  isMuted: false,
  playbackRate: 1,
  audioTrackId: null,
  subtitleTrackId: null,
  isFullscreen: false,

  setMedia: (media: MediaItem) => {
    set({ 
      currentMedia: media, 
      position: 0, 
      duration: 0,
      isPlaying: true 
    });
  },

  play: () => set({ isPlaying: true }),
  
  pause: () => set({ isPlaying: false }),
  
  seek: (position: number) => set({ position }),
  
  setDuration: (duration: number) => set({ duration }),
  
  setVolume: (volume: number) => set({ volume, isMuted: volume === 0 }),
  
  toggleMute: () => set((state) => ({ isMuted: !state.isMuted })),
  
  setPlaybackRate: (rate: number) => set({ playbackRate: rate }),
  
  setAudioTrack: (trackId: number | null) => set({ audioTrackId: trackId }),
  
  setSubtitleTrack: (trackId: number | null) => set({ subtitleTrackId: trackId }),
  
  toggleFullscreen: () => set((state) => ({ isFullscreen: !state.isFullscreen })),
  
  reset: () => set({
    currentMedia: null,
    isPlaying: false,
    position: 0,
    duration: 0,
    audioTrackId: null,
    subtitleTrackId: null,
    isFullscreen: false,
  }),
}));
