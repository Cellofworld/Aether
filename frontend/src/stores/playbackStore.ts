import { create } from 'zustand';

interface PlaybackState {
  currentMediaId: number | null;
  isPlaying: boolean;
  position: number;
  duration: number;
  volume: number;
  isMuted: boolean;
  playbackRate: number;
  activeAudioTrack: string | null;
  activeSubtitleTrack: string | null;
  isFullscreen: boolean;
  setCurrentMedia: (mediaId: number) => void;
  setPlaying: (playing: boolean) => void;
  setPosition: (position: number) => void;
  setDuration: (duration: number) => void;
  setVolume: (volume: number) => void;
  toggleMute: () => void;
  setPlaybackRate: (rate: number) => void;
  setAudioTrack: (track: string | null) => void;
  setSubtitleTrack: (track: string | null) => void;
  setFullscreen: (fullscreen: boolean) => void;
  reset: () => void;
}

export const usePlaybackStore = create<PlaybackState>((set) => ({
  currentMediaId: null,
  isPlaying: false,
  position: 0,
  duration: 0,
  volume: 1,
  isMuted: false,
  playbackRate: 1,
  activeAudioTrack: null,
  activeSubtitleTrack: null,
  isFullscreen: false,

  setCurrentMedia: (mediaId: number) => set({ currentMediaId: mediaId, position: 0, isPlaying: false }),
  
  setPlaying: (playing: boolean) => set({ isPlaying: playing }),
  
  setPosition: (position: number) => set({ position }),
  
  setDuration: (duration: number) => set({ duration }),
  
  setVolume: (volume: number) => set({ volume, isMuted: volume === 0 }),
  
  toggleMute: () => set((state) => ({ isMuted: !state.isMuted })),
  
  setPlaybackRate: (rate: number) => set({ playbackRate: rate }),
  
  setAudioTrack: (track: string | null) => set({ activeAudioTrack: track }),
  
  setSubtitleTrack: (track: string | null) => set({ activeSubtitleTrack: track }),
  
  setFullscreen: (fullscreen: boolean) => set({ isFullscreen: fullscreen }),
  
  reset: () => set({
    currentMediaId: null,
    isPlaying: false,
    position: 0,
    duration: 0,
    activeAudioTrack: null,
    activeSubtitleTrack: null,
    isFullscreen: false,
  }),
}));
