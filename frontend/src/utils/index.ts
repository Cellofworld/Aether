export function cn(...inputs: unknown[]): string {
  return inputs.filter(Boolean).join(' ');
}

export function formatDuration(seconds: number): string {
  if (!seconds || seconds <= 0) return '0:00';
  
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

export function getPosterUrl(posterPath?: string, size: 'small' | 'medium' | 'large' = 'medium'): string {
  if (!posterPath) {
    return '/placeholder-poster.png';
  }
  
  // Если это полный URL (например, с TMDB)
  if (posterPath.startsWith('http')) {
    return posterPath;
  }
  
  // Локальный путь к изображению
  const sizeMap = {
    small: 'w185',
    medium: 'w342',
    large: 'w500',
  };
  
  return `/images/${sizeMap[size]}${posterPath}`;
}

export function getBackdropUrl(backdropPath?: string, size: 'small' | 'medium' | 'large' = 'large'): string {
  if (!backdropPath) {
    return '/placeholder-backdrop.png';
  }
  
  if (backdropPath.startsWith('http')) {
    return backdropPath;
  }
  
  const sizeMap = {
    small: 'w300',
    medium: 'w780',
    large: 'w1280',
  };
  
  return `/images/${sizeMap[size]}${backdropPath}`;
}

export function formatYear(dateString?: string): number | undefined {
  if (!dateString) return undefined;
  return new Date(dateString).getFullYear();
}

export function formatRating(rating?: number): string {
  if (!rating) return 'N/A';
  return rating.toFixed(1);
}
