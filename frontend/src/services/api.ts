import type {
  StartSessionRequest,
  StartSessionResponse,
  NextTurnRequest,
  NextTurnResponse,
  SessionHistoryResponse,
  SessionStatusResponse,
  SessionListResponse,
} from '../types/api.types';
import { mockApiClient } from './mockApi';

const APP_ENV = (import.meta.env.VITE_APP_ENV || import.meta.env.MODE || 'development').toLowerCase();

const resolveApiBaseUrl = (): string => {
  const explicit = import.meta.env.VITE_API_BASE_URL?.trim();
  if (explicit) {
    return explicit.replace(/\/+$/, '');
  }

  if (APP_ENV === 'production') {
    if (typeof window !== 'undefined' && window.location?.origin) {
      return window.location.origin;
    }
    return 'http://api:8000';
  }

  return 'http://localhost:8000';
};

const API_BASE_URL = resolveApiBaseUrl();

// Check if we're in mock mode (stored in localStorage)
const isMockMode = () => {
  if (typeof window === 'undefined') return false;
  const stored = localStorage.getItem('api_mode') as 'mock' | 'real' | null;
  const defaultMode: 'mock' | 'real' = APP_ENV === 'production' ? 'real' : 'mock';
  return (stored || defaultMode) === 'mock';
};

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = `${baseUrl}/api`;
  }

  async startSession(request: StartSessionRequest): Promise<StartSessionResponse> {
    if (isMockMode()) {
      return mockApiClient.startSession(request);
    }

    const response = await fetch(`${this.baseUrl}/start-session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Failed to start session: ${response.statusText}`);
    }
    return response.json();
  }

  async nextTurn(request: NextTurnRequest): Promise<NextTurnResponse> {
    if (isMockMode()) {
      return mockApiClient.nextTurn(request);
    }

    const response = await fetch(`${this.baseUrl}/next-turn`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Failed to execute turn: ${response.statusText}`);
    }
    return response.json();
  }

  async getSessionHistory(sessionId: string): Promise<SessionHistoryResponse> {
    if (isMockMode()) {
      return mockApiClient.getSessionHistory(sessionId);
    }

    const response = await fetch(`${this.baseUrl}/session/${sessionId}/history`);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Failed to fetch history: ${response.statusText}`);
    }
    return response.json();
  }

  async getSessionStatus(sessionId: string): Promise<SessionStatusResponse> {
    if (isMockMode()) {
      return mockApiClient.getSessionStatus(sessionId);
    }

    const response = await fetch(`${this.baseUrl}/session/${sessionId}/status`);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Failed to fetch status: ${response.statusText}`);
    }
    return response.json();
  }

  async listSessions(): Promise<SessionListResponse> {
    if (isMockMode()) {
      return mockApiClient.listSessions();
    }

    const response = await fetch(`${this.baseUrl}/sessions`);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Failed to fetch sessions: ${response.statusText}`);
    }
    return response.json();
  }

  async healthCheck(): Promise<{ status: string }> {
    if (isMockMode()) {
      return mockApiClient.healthCheck();
    }

    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) {
      throw new Error('Health check failed');
    }
    return response.json();
  }
}

export const apiClient = new ApiClient(API_BASE_URL);

// Export mode toggle functions
export const setApiMode = (mode: 'mock' | 'real') => {
  localStorage.setItem('api_mode', mode);
  // No reload needed - components will re-check mode on next API call
};

export const getApiMode = (): 'mock' | 'real' => {
  const stored = localStorage.getItem('api_mode') as 'mock' | 'real' | null;
  const defaultMode: 'mock' | 'real' = APP_ENV === 'production' ? 'real' : 'mock';
  return stored || defaultMode;
};
