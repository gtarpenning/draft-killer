/**
 * Authentication hook.
 * 
 * Provides authentication state and functions for login, register, and logout.
 */

'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import type { User, LoginRequest, RegisterRequest } from '@/types';
import {
  login as apiLogin,
  register as apiRegister,
  getCurrentUser,
  setToken,
  removeToken,
  ApiErrorClass,
} from '@/lib/api';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  
  // Load user on mount
  useEffect(() => {
    loadUser();
  }, []);
  
  async function loadUser() {
    try {
      const userData = await getCurrentUser();
      setUser(userData);
    } catch (err) {
      // Token might be invalid or expired
      removeToken();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }
  
  async function login(data: LoginRequest) {
    try {
      setLoading(true);
      setError(null);
      
      const tokens = await apiLogin(data);
      setToken(tokens.access_token);
      
      const userData = await getCurrentUser();
      setUser(userData);
      
      router.push('/');
    } catch (err) {
      if (err instanceof ApiErrorClass) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred');
      }
      throw err;
    } finally {
      setLoading(false);
    }
  }
  
  async function register(data: RegisterRequest) {
    try {
      setLoading(true);
      setError(null);
      
      const tokens = await apiRegister(data);
      setToken(tokens.access_token);
      
      const userData = await getCurrentUser();
      setUser(userData);
      
      router.push('/');
    } catch (err) {
      if (err instanceof ApiErrorClass) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred');
      }
      throw err;
    } finally {
      setLoading(false);
    }
  }
  
  function logout() {
    removeToken();
    setUser(null);
    router.push('/login');
  }
  
  function clearError() {
    setError(null);
  }
  
  return (
    <AuthContext.Provider
      value={{ user, loading, error, login, register, logout, clearError }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

