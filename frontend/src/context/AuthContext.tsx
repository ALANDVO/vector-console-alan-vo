import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { AuthUser } from '../types/api';
import { api } from '../api/client';

interface AuthContextType {
  user: AuthUser | null;
  isLoading: boolean;
  error: string | null;
  switchRole: (role: 'viewer' | 'analyst' | 'admin') => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const refreshUser = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const currentUser = await api.getCurrentUser();
      setUser(currentUser);
      if (currentUser.csrf_token) {
        api.setCsrfToken(currentUser.csrf_token);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Auth error';
      setError(msg);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refreshUser();
  }, []);

  const switchRole = async (role: 'viewer' | 'analyst' | 'admin') => {
    try {
      setError(null);
      await api.switchDemoRole(role);
      await refreshUser();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to switch role';
      setError(msg);
    }
  };

  const logout = async () => {
    try {
      await api.logout();
      setUser(null);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Logout error';
      setError(msg);
    }
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, error, switchRole, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
