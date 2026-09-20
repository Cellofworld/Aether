import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores';
import { authAPI } from '@/services/api';

export function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { login, isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login(username, password);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка входа. Проверьте логин и пароль.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-blue-500 mb-2">AETHER</h1>
          <p className="text-gray-400">Домашний медиасервер</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-gray-900 rounded-lg p-8 shadow-xl">
          <h2 className="text-2xl font-semibold mb-6 text-white">Вход</h2>

          {error && (
            <div className="mb-6 p-4 bg-red-900/50 border border-red-700 rounded text-red-200 text-sm">
              {error}
            </div>
          )}

          <div className="mb-6">
            <label htmlFor="username" className="block text-gray-300 mb-2 text-sm font-medium">
              Имя пользователя
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded focus:outline-none focus:border-blue-500 text-white placeholder-gray-500 transition-colors"
              placeholder="admin"
              disabled={isLoading}
              autoFocus
            />
          </div>

          <div className="mb-6">
            <label htmlFor="password" className="block text-gray-300 mb-2 text-sm font-medium">
              Пароль
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded focus:outline-none focus:border-blue-500 text-white placeholder-gray-500 transition-colors"
              placeholder="••••••••"
              disabled={isLoading}
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 disabled:cursor-not-allowed rounded font-semibold text-white transition-colors"
          >
            {isLoading ? 'Вход...' : 'Войти'}
          </button>

          <p className="mt-6 text-center text-gray-500 text-sm">
            По умолчанию: admin / admin123
          </p>
        </form>
      </div>
    </div>
  );
}
