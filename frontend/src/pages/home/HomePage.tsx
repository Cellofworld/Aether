import { useEffect, useState } from 'react';
import { homeAPI } from '@/services/api';
import type { MediaItem } from '@/types';

interface ContinueWatchingItem {
  id: number;
  media_id: number;
  media_type: 'movie' | 'episode';
  title: string;
  poster_url?: string;
  progress: number;
  duration: number;
  episode_title?: string;
}

export function HomePage() {
  const [continueWatching, setContinueWatching] = useState<ContinueWatchingItem[]>([]);
  const [recentlyAdded, setRecentlyAdded] = useState<MediaItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [focusedIndex, setFocusedIndex] = useState(0);

  useEffect(() => {
    loadHomeData();
  }, []);

  const loadHomeData = async () => {
    try {
      const data = await homeAPI.getHomeData();
      setContinueWatching(data.continueWatching || []);
      setRecentlyAdded(data.recentlyAdded || []);
    } catch (error) {
      console.error('Failed to load home data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    const cards = document.querySelectorAll('[data-media-card]');
    if (!cards.length) return;

    switch (e.key) {
      case 'ArrowRight':
        e.preventDefault();
        setFocusedIndex((prev) => Math.min(prev + 1, cards.length - 1));
        break;
      case 'ArrowLeft':
        e.preventDefault();
        setFocusedIndex((prev) => Math.max(prev - 1, 0));
        break;
      case 'Enter':
        e.preventDefault();
        (cards[focusedIndex] as HTMLElement)?.click();
        break;
    }
  };

  useEffect(() => {
    const cards = document.querySelectorAll('[data-media-card]');
    cards.forEach((card, index) => {
      card.classList.remove('ring-4', 'ring-blue-500', 'scale-105');
      card.classList.add('scale-100');
      if (index === focusedIndex) {
        card.classList.add('ring-4', 'ring-blue-500', 'scale-105');
        card.classList.remove('scale-100');
        (card as HTMLElement).focus();
      }
    });
  }, [focusedIndex]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-blue-500 text-xl">Загрузка...</div>
      </div>
    );
  }

  return (
    <div 
      className="min-h-screen bg-gray-950 text-white"
      onKeyDown={handleKeyDown}
      tabIndex={0}
    >
      {/* Hero Section */}
      {recentlyAdded.length > 0 && (
        <section className="relative h-[70vh] w-full overflow-hidden">
          <div 
            className="absolute inset-0 bg-cover bg-center"
            style={{ backgroundImage: `url(${recentlyAdded[0]?.backdrop_url || recentlyAdded[0]?.poster_url})` }}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-gray-950 via-gray-950/50 to-transparent" />
          <div className="absolute bottom-0 left-0 right-0 p-8 md:p-12 max-w-[1920px] mx-auto">
            <h1 className="text-4xl md:text-6xl font-bold mb-4 drop-shadow-lg">
              {recentlyAdded[0]?.title}
            </h1>
            <p className="text-gray-300 text-lg md:text-xl max-w-2xl mb-6 line-clamp-3">
              {recentlyAdded[0]?.overview || 'Описание недоступно'}
            </p>
            <div className="flex gap-4">
              <a
                href={`/player/${recentlyAdded[0]?.id}`}
                className="px-8 py-3 bg-blue-600 hover:bg-blue-500 rounded font-semibold transition-colors flex items-center gap-2"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8 5v14l11-7z"/>
                </svg>
                Смотреть
              </a>
              <a
                href={`/movie/${recentlyAdded[0]?.id}`}
                className="px-8 py-3 bg-gray-700/80 hover:bg-gray-600/80 rounded font-semibold transition-colors flex items-center gap-2"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10" strokeWidth="2"/>
                  <path strokeLinecap="round" strokeWidth="2" d="M12 16v-4m0-4h.01"/>
                </svg>
                Подробнее
              </a>
            </div>
          </div>
        </section>
      )}

      <div className="px-6 py-8 max-w-[1920px] mx-auto">
        {/* Continue Watching */}
        {continueWatching.length > 0 && (
          <section className="mb-12">
            <h2 className="text-2xl font-semibold mb-4 text-gray-100">Продолжить просмотр</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-4">
              {continueWatching.map((item) => (
                <a
                  key={item.id}
                  href={`/player/${item.media_id}`}
                  data-media-card
                  className="group relative aspect-[2/3] rounded-lg overflow-hidden bg-gray-800 transition-all duration-200 hover:scale-105 outline-none ring-2 ring-transparent hover:ring-blue-500 focus:ring-4 focus:ring-blue-500"
                  tabIndex={0}
                >
                  {item.poster_url ? (
                    <img src={item.poster_url} alt={item.title} className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center bg-gray-700 text-gray-500">
                      <svg className="w-12 h-12" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-4z"/>
                      </svg>
                    </div>
                  )}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent" />
                  <div className="absolute bottom-0 left-0 right-0 p-3">
                    <p className="text-sm font-medium truncate">{item.title}</p>
                    {item.episode_title && (
                      <p className="text-xs text-gray-400 truncate">{item.episode_title}</p>
                    )}
                    <div className="mt-2 h-1 bg-gray-700 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-blue-500 rounded-full"
                        style={{ width: `${(item.progress / item.duration) * 100}%` }}
                      />
                    </div>
                  </div>
                </a>
              ))}
            </div>
          </section>
        )}

        {/* Recently Added */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4 text-gray-100">Недавно добавленные</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-4">
            {recentlyAdded.map((item) => (
              <a
                key={item.id}
                href={item.media_type === 'movie' ? `/movie/${item.id}` : `/series/${item.id}`}
                data-media-card
                className="group relative aspect-[2/3] rounded-lg overflow-hidden bg-gray-800 transition-all duration-200 hover:scale-105 outline-none ring-2 ring-transparent hover:ring-blue-500 focus:ring-4 focus:ring-blue-500"
                tabIndex={0}
              >
                {item.poster_url ? (
                  <img src={item.poster_url} alt={item.title} className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center bg-gray-700 text-gray-500">
                    <svg className="w-12 h-12" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-4z"/>
                    </svg>
                  </div>
                )}
                <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent" />
                <div className="absolute bottom-0 left-0 right-0 p-3">
                  <p className="text-sm font-medium truncate">{item.title}</p>
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-xs text-gray-400">{item.year}</span>
                    {item.rating && (
                      <span className="text-xs bg-yellow-600/80 px-1.5 py-0.5 rounded">{item.rating.toFixed(1)}</span>
                    )}
                  </div>
                  {item.resolution && (
                    <span className="absolute top-2 right-2 text-xs bg-blue-600/90 px-2 py-0.5 rounded font-medium">
                      {item.resolution}
                    </span>
                  )}
                </div>
              </a>
            ))}
          </div>
        </section>

        {/* Movies */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4 text-gray-100">Фильмы</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-4">
            {recentlyAdded.filter(i => i.media_type === 'movie').slice(0, 8).map((item) => (
              <a
                key={item.id}
                href={`/movie/${item.id}`}
                data-media-card
                className="group relative aspect-[2/3] rounded-lg overflow-hidden bg-gray-800 transition-all duration-200 hover:scale-105 outline-none ring-2 ring-transparent hover:ring-blue-500 focus:ring-4 focus:ring-blue-500"
                tabIndex={0}
              >
                {item.poster_url ? (
                  <img src={item.poster_url} alt={item.title} className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center bg-gray-700 text-gray-500">
                    <svg className="w-12 h-12" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-4z"/>
                    </svg>
                  </div>
                )}
                <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent" />
                <div className="absolute bottom-0 left-0 right-0 p-3">
                  <p className="text-sm font-medium truncate">{item.title}</p>
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-xs text-gray-400">{item.year}</span>
                    {item.rating && (
                      <span className="text-xs bg-yellow-600/80 px-1.5 py-0.5 rounded">{item.rating.toFixed(1)}</span>
                    )}
                  </div>
                </div>
              </a>
            ))}
          </div>
        </section>

        {/* Series */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4 text-gray-100">Сериалы</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-4">
            {recentlyAdded.filter(i => i.media_type === 'series').slice(0, 8).map((item) => (
              <a
                key={item.id}
                href={`/series/${item.id}`}
                data-media-card
                className="group relative aspect-[2/3] rounded-lg overflow-hidden bg-gray-800 transition-all duration-200 hover:scale-105 outline-none ring-2 ring-transparent hover:ring-blue-500 focus:ring-4 focus:ring-blue-500"
                tabIndex={0}
              >
                {item.poster_url ? (
                  <img src={item.poster_url} alt={item.title} className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center bg-gray-700 text-gray-500">
                    <svg className="w-12 h-12" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-4z"/>
                    </svg>
                  </div>
                )}
                <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent" />
                <div className="absolute bottom-0 left-0 right-0 p-3">
                  <p className="text-sm font-medium truncate">{item.title}</p>
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-xs text-gray-400">{item.year}</span>
                    {item.seasons_count && (
                      <span className="text-xs text-gray-400">{item.seasons_count} сез.</span>
                    )}
                  </div>
                </div>
              </a>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
