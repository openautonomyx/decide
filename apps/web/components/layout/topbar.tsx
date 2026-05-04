'use client';

import { useHealth } from '@/lib/hooks';
import { Activity, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

export function Topbar() {
  const { data: health, isLoading, isError } = useHealth();

  return (
    <header className="flex h-16 items-center justify-between border-b bg-background px-6">
      <div className="flex items-center gap-4">
        <span className="text-sm text-muted-foreground">
          API:{' '}
          {isLoading ? (
            <span className="inline-flex items-center gap-1">
              <Activity className="h-3 w-3 animate-pulse" />
              Checking...
            </span>
          ) : isError ? (
            <span className="inline-flex items-center gap-1 text-destructive">
              <XCircle className="h-3 w-3" />
              Unavailable
            </span>
          ) : health?.status === 'healthy' ? (
            <span className="inline-flex items-center gap-1 text-green-600">
              <CheckCircle className="h-3 w-3" />
              Healthy
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 text-yellow-600">
              <AlertCircle className="h-3 w-3" />
              {health?.status || 'Unknown'}
            </span>
          )}
        </span>
        {health?.version && (
          <span className="text-xs text-muted-foreground">
            v{health.version}
          </span>
        )}
      </div>

      <div className="flex items-center gap-4">
        <EnvironmentBadge />
        <div className="h-8 w-8 rounded-full bg-primary/10" />
      </div>
    </header>
  );
}

function EnvironmentBadge() {
  const env = process.env.NEXT_PUBLIC_ENV || 'development';
  
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        env === 'production'
          ? 'bg-red-100 text-red-800'
          : env === 'staging'
          ? 'bg-yellow-100 text-yellow-800'
          : 'bg-green-100 text-green-800'
      )}
    >
      {env}
    </span>
  );
}