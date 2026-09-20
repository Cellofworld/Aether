import { useEffect, useState } from 'react';

interface UseKeyboardNavigationOptions {
  onFocusChange?: (direction: 'up' | 'down' | 'left' | 'right') => void;
  onSelect?: () => void;
  onBack?: () => void;
  onPlayPause?: () => void;
  onSeekForward?: () => void;
  onSeekBackward?: () => void;
}

export function useKeyboardNavigation({
  onFocusChange,
  onSelect,
  onBack,
  onPlayPause,
  onSeekForward,
  onSeekBackward,
}: UseKeyboardNavigationOptions) {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      switch (event.key) {
        case 'ArrowUp':
          event.preventDefault();
          onFocusChange?.('up');
          break;
        case 'ArrowDown':
          event.preventDefault();
          onFocusChange?.('down');
          break;
        case 'ArrowLeft':
          event.preventDefault();
          onFocusChange?.('left');
          break;
        case 'ArrowRight':
          event.preventDefault();
          onFocusChange?.('right');
          break;
        case 'Enter':
        case ' ':
          event.preventDefault();
          onSelect?.();
          break;
        case 'Escape':
        case 'Backspace':
          event.preventDefault();
          onBack?.();
          break;
        case 'p':
        case 'P':
          if (event.shiftKey || event.ctrlKey) {
            event.preventDefault();
            onPlayPause?.();
          }
          break;
        case 'ArrowRight':
          if (event.shiftKey) {
            event.preventDefault();
            onSeekForward?.();
          }
          break;
        case 'ArrowLeft':
          if (event.shiftKey) {
            event.preventDefault();
            onSeekBackward?.();
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onFocusChange, onSelect, onBack, onPlayPause, onSeekForward, onSeekBackward]);
}
