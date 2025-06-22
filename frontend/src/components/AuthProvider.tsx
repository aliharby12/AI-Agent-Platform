import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authApi } from '../services/api';

interface AuthContextType {
  isAuthenticated: boolean;
  user: any | null;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already authenticated on app load
    const token = localStorage.getItem('authToken');
    if (token) {
      setIsAuthenticated(true);
      // You could also fetch user details here if needed
      const username = localStorage.getItem('username');
      if (username) {
        setUser({ username });
      }
    }
    setLoading(false);
  }, []);

  const login = async (username: string, password: string) => {
    try {
      const response = await authApi.login({ username, password });
      localStorage.setItem('authToken', response.access_token);
      localStorage.setItem('refreshToken', response.refresh_token);
      localStorage.setItem('username', username);
      setIsAuthenticated(true);
      setUser({ username });
    } catch (error) {
      throw error;
    }
  };

  const register = async (username: string, password: string) => {
    try {
      const response = await authApi.register({ username, password });
      setUser(response);
      // After registration, automatically log in
      await login(username, password);
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    authApi.logout();
    localStorage.removeItem('username');
    setIsAuthenticated(false);
    setUser(null);
  };

  const value: AuthContextType = {
    isAuthenticated,
    user,
    login,
    register,
    logout,
    loading,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 