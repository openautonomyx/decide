'use client';

import { useHealth, useWorkflows, useLogs, useMemory } from '@/lib/hooks';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Activity,
  GitBranch,
  Database,
  FileText,
  CheckCircle,
  XCircle,
  AlertCircle,
} from 'lucide-react';

export default function DashboardPage() {
  const { data: health, isLoading: healthLoading } = useHealth();
  const { data: workflows, isLoading: workflowsLoading } = useWorkflows();
  const { data: logs, isLoading: logsLoading } = useLogs();
  const { data: memory, isLoading: memoryLoading } = useMemory();

  const activeWorkflows = workflows?.filter((w) => w.status === 'active').length || 0;
  const errorLogs = logs?.filter((l) => l.level === 'error').length || 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          System overview and health status
        </p>
      </div>

      {/* Health Status */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">API Health</CardTitle>
            {healthLoading ? (
              <Activity className="h-4 w-4 animate-pulse text-muted-foreground" />
            ) : health?.status === 'healthy' ? (
              <CheckCircle className="h-4 w-4 text-green-500" />
            ) : health?.status === 'degraded' ? (
              <AlertCircle className="h-4 w-4 text-yellow-500" />
            ) : (
              <XCircle className="h-4 w-4 text-destructive" />
            )}
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {healthLoading ? 'Checking...' : health?.status || 'Unknown'}
            </div>
            <p className="text-xs text-muted-foreground">
              {health?.version ? `Version ${health.version}` : 'No version info'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Workflows</CardTitle>
            <GitBranch className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {workflowsLoading ? '-' : `${activeWorkflows}/${workflows?.length || 0}`}
            </div>
            <p className="text-xs text-muted-foreground">
              {workflowsLoading ? 'Loading...' : `${workflows?.length || 0} total workflows`}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Memory Items</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {memoryLoading ? '-' : memory?.length || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              {memoryLoading ? 'Loading...' : 'Stored memories'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Error Logs</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{errorLogs}</div>
            <p className="text-xs text-muted-foreground">
              {logsLoading ? 'Loading...' : `${logs?.length || 0} total logs`}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* System Info */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>System Status</CardTitle>
            <CardDescription>Current system configuration</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Status</span>
              <Badge variant={health?.status === 'healthy' ? 'success' : 'warning'}>
                {health?.status || 'unknown'}
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Version</span>
              <span className="text-sm font-medium">{health?.version || 'N/A'}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">API Endpoint</span>
              <span className="text-sm font-medium">http://localhost:18000</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Environment</span>
              <span className="text-sm font-medium">development</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest system events</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {logsLoading ? (
                <p className="text-sm text-muted-foreground">Loading...</p>
              ) : logs && logs.length > 0 ? (
                logs.slice(0, 5).map((log) => (
                  <div key={log.id} className="flex items-start gap-3">
                    <div
                      className={`mt-0.5 h-2 w-2 rounded-full ${
                        log.level === 'error'
                          ? 'bg-destructive'
                          : log.level === 'warning'
                          ? 'bg-yellow-500'
                          : 'bg-green-500'
                      }`}
                    />
                    <div className="flex-1 space-y-1">
                      <p className="text-sm font-medium leading-none">
                        {log.message}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(log.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">No recent activity</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}