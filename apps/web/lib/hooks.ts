import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  api, 
  HealthStatus, 
  Workflow, 
  Log, 
  Memory,
  ExecutionResult 
} from './api';

export function useHealth() {
  return useQuery<HealthStatus>({
    queryKey: ['health'],
    queryFn: api.getHealth,
    refetchInterval: 30000,
    retry: 1,
  });
}

export function useConfig() {
  return useQuery({
    queryKey: ['config'],
    queryFn: api.getConfig,
    staleTime: 60000,
  });
}

export function useWorkflows() {
  return useQuery<Workflow[]>({
    queryKey: ['workflows'],
    queryFn: api.getWorkflows,
    staleTime: 30000,
  });
}

export function useWorkflow(id: string) {
  return useQuery<Workflow>({
    queryKey: ['workflow', id],
    queryFn: () => api.getWorkflow(id),
    enabled: !!id,
  });
}

export function useRunWorkflow() {
  const queryClient = useQueryClient();
  
  return useMutation<ExecutionResult, Error, string>({
    mutationFn: api.runWorkflow,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflows'] });
    },
  });
}

export function useSaveWorkflow() {
  const queryClient = useQueryClient();
  
  return useMutation<Workflow, Error, Workflow>({
    mutationFn: api.saveWorkflow,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflows'] });
    },
  });
}

export function useLogs() {
  return useQuery<Log[]>({
    queryKey: ['logs'],
    queryFn: api.getLogs,
    refetchInterval: 10000,
  });
}

export function useMemory() {
  return useQuery<Memory[]>({
    queryKey: ['memory'],
    queryFn: api.getMemory,
    staleTime: 30000,
  });
}