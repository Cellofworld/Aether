import { Outlet, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/stores';

export function MainLayout() {
  const { isAuthenticated } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <header className="fixed top-0 left-0 right-0 z-50 bg-gradient-to-b from-gray-950/90 to-transparent px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-8">
            <a href="/" className="text-2xl font-bold text-blue-500 hover:text-blue-400 transition-colors">
              AETHER
            </a>
            <nav className="hidden md:flex items-center gap-6">
              <a href="/" className="text-gray-300 hover:text-white transition-colors">Главная</a>
              <a href="/movies" className="text-gray-300 hover:text-white transition-colors">Фильмы</a>
              <a href="/series" className="text-gray-300 hover:text-white transition-colors">Сериалы</a>
              <a href="/anime" className="text-gray-300 hover:text-white transition-colors">Аниме</a>
              <a href="/search" className="text-gray-300 hover:text-white transition-colors">Поиск</a>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <a href="/admin" className="text-gray-300 hover:text-white transition-colors text-sm">
              Админка
            </a>
            <button 
              onClick={() => {}}
              className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-semibold hover:bg-blue-500 transition-colors"
            >
              A
            </button>
          </div>
        </div>
      </header>
      <main className="pt-20">
        <Outlet />
      </main>
    </div>
  );
}
