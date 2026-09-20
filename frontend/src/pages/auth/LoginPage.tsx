import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { Input, Button } from '@/components/ui';
import { authApi } from '@/services';
import { useAuthStore } from '@/stores/authStore';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login, checkAuth } = useAuthStore();
  const [username, setUsername] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [error, setError] = React.useState('');
  const [isLoading, setIsLoading] = React.useState(false);

  // Проверка авторизации при загрузке
  React.useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      checkAuth().then(() => {
        const user = useAuthStore.getState().user;
        if (user) {
          navigate('/');
        }
      });
    }
  }, []);

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
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-primary mb-2">AETHER</h1>
          <p className="text-text-muted">Домашний медиасервер</p>
        </div>

        {/* Login form */}
        <div className="bg-surface rounded-card p-8 shadow-xl">
          <h2 className="text-2xl font-bold text-white mb-6 text-center">Вход</h2>

          <form onSubmit={handleSubmit} className="space-y-6">
            <Input
              label="Логин"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Введите логин"
              required
              disabled={isLoading}
              autoFocus
            />

            <Input
              label="Пароль"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Введите пароль"
              required
              disabled={isLoading}
            />

            {error && (
              <div className="p-3 bg-red-500/10 border border-red-500 rounded text-red-500 text-sm">
                {error}
              </div>
            )}

            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full"
              disabled={isLoading}
            >
              {isLoading ? 'Вход...' : 'Войти'}
            </Button>
          </form>

          {/* Default credentials hint */}
          <div className="mt-6 p-4 bg-surface-light rounded text-sm text-text-muted">
            <p className="font-medium mb-2">Тестовые учетные данные:</p>
            <p>Логин: <code className="bg-background px-2 py-0.5 rounded">admin</code></p>
            <p>Пароль: <code className="bg-background px-2 py-0.5 rounded">admin123</code></p>
          </div>
        </div>
      </div>
    </div>
  );
};
