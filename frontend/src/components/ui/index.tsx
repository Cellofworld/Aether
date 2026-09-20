import React from 'react';
import { cn } from '@/utils';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg' | 'tv';
  children: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', children, ...props }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center font-medium transition-colors focus:outline-none focusable rounded-button';
    
    const variants = {
      primary: 'bg-primary text-white hover:bg-primary-hover',
      secondary: 'bg-surface-light text-white hover:bg-secondary',
      outline: 'border border-border-color text-white hover:bg-surface-light',
      ghost: 'text-white hover:bg-surface-light',
    };
    
    const sizes = {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-4 py-2 text-base',
      lg: 'px-6 py-3 text-lg',
      tv: 'px-8 py-4 text-tv-base',
    };
    
    return (
      <button
        ref={ref}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  tabIndex?: number;
}

export const Card: React.FC<CardProps> = ({ children, className, onClick, tabIndex = 0 }) => {
  return (
    <div
      className={cn('bg-surface rounded-card overflow-hidden card-hover cursor-pointer', className)}
      onClick={onClick}
      tabIndex={tabIndex}
    >
      {children}
    </div>
  );
};

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'accent' | 'warning';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'default', className }) => {
  const variants = {
    default: 'bg-secondary text-white',
    accent: 'bg-accent text-black',
    warning: 'bg-yellow-500 text-black',
  };
  
  return (
    <span className={cn('px-2 py-0.5 text-xs font-medium rounded', variants[variant], className)}>
      {children}
    </span>
  );
};

interface ProgressBarProps {
  progress: number;
  className?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ progress, className }) => {
  return (
    <div className={cn('progress-bar', className)}>
      <div 
        className="progress-bar-fill" 
        style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
      />
    </div>
  );
};

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-text-muted mb-1">
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={cn(
            'w-full px-3 py-2 bg-surface-light border border-border-color rounded-button text-white',
            'focus:outline-none focus:border-primary focusable',
            error && 'border-red-500',
            className
          )}
          {...props}
        />
        {error && (
          <p className="mt-1 text-sm text-red-500">{error}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
