import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
          const response = await api.post('/auth/refresh', {}, {
            headers: { Authorization: `Bearer ${refreshToken}` }
          });
          
          localStorage.setItem('authToken', response.data.access_token);
          localStorage.setItem('refreshToken', response.data.refresh_token);
          
          originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('authToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/';
      }
    }
    
    return Promise.reject(error);
  }
);

// Auth types
export interface AuthCredentials {
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserResponse {
  id: number;
  username: string;
  created_at: string;
}

// Auth API functions
export const authApi = {
  // Register a new user
  register: async (credentials: AuthCredentials): Promise<UserResponse> => {
    const response = await api.post('/auth/register', credentials);
    return response.data;
  },

  // Login user
  login: async (credentials: AuthCredentials): Promise<AuthResponse> => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },

  // Refresh token
  refresh: async (): Promise<AuthResponse> => {
    const response = await api.post('/auth/refresh');
    return response.data;
  },

  // Logout (client-side)
  logout: () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('refreshToken');
  },
};

// Agent types
export interface Agent {
  id: number;
  name: string;
  prompt: string;
  created_at: string;
}

export interface AgentCreate {
  name: string;
  prompt: string;
}

export interface AgentUpdate {
  name?: string;
  prompt?: string;
}

// Agent API functions
export const agentApi = {
  // Get all agents
  getAgents: async (): Promise<Agent[]> => {
    const response = await api.get('/agents/');
    return response.data;
  },

  // Get a single agent by ID
  getAgent: async (id: number): Promise<Agent> => {
    const response = await api.get(`/agents/${id}`);
    return response.data;
  },

  // Create a new agent
  createAgent: async (agent: AgentCreate): Promise<Agent> => {
    const response = await api.post('/agents/', agent);
    return response.data;
  },

  // Update an agent
  updateAgent: async (id: number, agent: AgentUpdate): Promise<Agent> => {
    const response = await api.patch(`/agents/${id}`, agent);
    return response.data;
  },

  // Delete an agent
  deleteAgent: async (id: number): Promise<Agent> => {
    const response = await api.delete(`/agents/${id}`);
    return response.data;
  },
};

export default api; 