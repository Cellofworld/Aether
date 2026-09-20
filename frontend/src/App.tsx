import { Routes, Route, Navigate } from 'react-router-dom';
import { MainLayout } from '@/layouts';
import { LoginPage } from '@/pages/login';
import { HomePage } from '@/pages/home';

// Заглушки для страниц, которые будут созданы позже
const MoviePage = () => <div className="p-8 text-white">Страница фильма (в разработке)</div>;
const SeriesPage = () => <div className="p-8 text-white">Страница сериала (в разработке)</div>;
const PlayerPage = () => <div className="p-8 text-white">Видеоплеер (в разработке)</div>;
const SearchPage = () => <div className="p-8 text-white">Поиск (в разработке)</div>;
const AdminPage = () => <div className="p-8 text-white">Админ-панель (в разработке)</div>;

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      
      <Route path="/" element={<MainLayout />}>
        <Route index element={<HomePage />} />
        <Route path="movie/:id" element={<MoviePage />} />
        <Route path="series/:id" element={<SeriesPage />} />
        <Route path="player/:id" element={<PlayerPage />} />
        <Route path="search" element={<SearchPage />} />
        <Route path="admin" element={<AdminPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
