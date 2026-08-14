import { apiClient } from './api';
import { DashboardMetrics, AgentesEstado, HealthResponse, DetailedHealthResponse } from '@/types/api';

/**
 * Dashboard Service - Endpoints for dashboard metrics and agent status
 */

export const dashboardService = {
  /**
   * Get main dashboard metrics
   */
  async getMetrics(): Promise<DashboardMetrics> {
    const response = await apiClient.get('/dashboard/metrics');
    return response.data;
  },

  /**
   * Get agent swarm status
   */
  async getAgentesEstado(): Promise<AgentesEstado> {
    const response = await apiClient.get('/dashboard/agentes/estado');
    return response.data;
  },

  /**
   * Basic health check
   */
  async getHealth(): Promise<HealthResponse> {
    const response = await apiClient.get('/health');
    return response.data;
  },

  /**
   * Detailed health check with component status
   */
  async getDetailedHealth(): Promise<DetailedHealthResponse> {
    const response = await apiClient.get('/health/detailed');
    return response.data;
  },
};

export default dashboardService;
