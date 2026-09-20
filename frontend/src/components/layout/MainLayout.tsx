import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Film, Tv, Search, Home, User, Settings, LogOut, FolderOpen } from 'lucide-react';
import { cn } from '@/utils';
import { useAuthStore } from '@/stores/authStore';

interface MainLayoutProps {
  children: React.ReactNode;
}

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [isSearchOpen, setIsSearchOpen] = React.useState(false);
  const [searchQuery, setSearchQuery] = React.useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
      setIsSearchOpen(false);
      setSearchQuery('');
    }
  };

  const navItems = [
    { icon: Home, label: 'Главная', path: '/' },
    { icon: Film, label: 'Фильмы', path: '/movies' },
    { icon: Tv, label: 'Сериалы', path: '/series' },
    { icon: FolderOpen, label: 'Библиотеки', path: '/libraries' },
  ];

  return (
    <div className="min-h-screen bg-background flex">
      {/* Sidebar Navigation */}
      <aside className="w-16 md:w-64 bg-surface border-r border-border-color flex-shrink-0">
        <div className="h-full flex flex-col">
          {/* Logo */}
          <div className="p-4 border-b border-border-color">
            <h1 className="text-xl font-bold text-primary hidden md:block">AETHER</h1>
            <div className="md:hidden text-primary font-bold text-center">A</div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 py-4">
            <ul className="space-y-1 px-2">
              {navItems.map((item) => (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    className={cn(
                      'flex items-center gap-3 px-3 py-3 rounded-button transition-colors focus:outline-none focusable',
                      'text-text-muted hover:text-white hover:bg-surface-light',
                      location.pathname === item.path && 'text-white bg-surface-light'
                    )}
                    tabIndex={0}
                  >
                    <item.icon size={20} />
                    <span className="hidden md:block">{item.label}</span>
                  </Link>
                </li>
              ))}
            </ul>
          </nav>

          {/* User section */}
          <div className="p-4 border-t border-border-color">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-white font-medium">
                {user?.username?.[0]?.toUpperCase() || 'U'}
              </div>
              <div className="hidden md:block overflow-hidden">
                <p className="text-sm font-medium text-white truncate">{user?.username}</p>
                <p className="text-xs text-text-muted capitalize">{user?.role}</p>
              </div>
            </div>

            <div className="space-y-1">
              {user?.role === 'admin' && (
                <Link
                  to="/admin"
                  className={cn(
                    'flex items-center gap-3 px-3 py-2 rounded-button transition-colors focus:outline-none focusable',
                    'text-text-muted hover:text-white hover:bg-surface-light'
                  )}
                  tabIndex={0}
                >
                  <Settings size={20} />
                  <span className="hidden md:block">Админка</span>
                </Link>
              )}

              <button
                onClick={logout}
                className={cn(
                  'w-full flex items-center gap-3 px-3 py-2 rounded-button transition-colors focus:outline-none focusable',
                  'text-text-muted hover:text-red-500 hover:bg-surface-light'
                )}
                tabIndex={0}
              >
                <LogOut size={20} />
                <span className="hidden md:block">Выйти</span>
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 min-w-0 overflow-auto">
        {/* Top bar */}
        <header className="sticky top-0 z-40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80 border-b border-border-color">
          <div className="flex items-center justify-between px-4 md:px-8 py-4">
            {/* Search */}
            {isSearchOpen ? (
              <form onSubmit={handleSearch} className="flex-1 max-w-md">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Поиск..."
                  className="w-full px-4 py-2 bg-surface-light border border-border-color rounded-button text-white focus:outline-none focus:border-primary"
                  autoFocus
                  onBlur={() => !searchQuery && setIsSearchOpen(false)}
                />
              </form>
            ) : (
              <button
                onClick={() => setIsSearchOpen(true)}
                className="p-2 text-text-muted hover:text-white transition-colors focus:outline-none focusable"
                tabIndex={0}
              >
                <Search size={24} />
              </button>
            )}

            {/* Right actions */}
            <div className="flex items-center gap-4">
              {/* Additional actions can go here */}
            </div>
          </div>
        </header>

        {/* Page content */}
        <div className="pb-16">
          {children}
        </div>
      </main>
    </div>
  );
};
