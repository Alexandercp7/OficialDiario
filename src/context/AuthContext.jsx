import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getStoredToken, setStoredToken, removeStoredToken } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [authToken, setAuthToken] = useState(() => getStoredToken());
  const [currentUser, setCurrentUser] = useState(null);
  const [loadingAuth, setLoadingAuth] = useState(true);

  // Helper para peticiones autenticadas
  const authFetch = useCallback(async (url, options = {}) => {
    const token = getStoredToken();
    const headers = {
      ...(options.headers || {}),
      'Authorization': token ? `Bearer ${token}` : ''
    };
    const res = await fetch(url, { ...options, headers });
    if (res.status === 401) {
      // Sesión expirada o token inválido
      handleLogout();
      throw new Error('Tu sesión ha expirado. Por favor inicia sesión nuevamente.');
    }
    return res;
  }, []);

  const handleLogout = useCallback(async () => {
    try {
      await authFetch('/api/auth/logout', { method: 'POST' });
    } catch (e) {
      // Silencioso
    }
    removeStoredToken();
    setAuthToken('');
    setCurrentUser(null);
  }, [authFetch]);

  const handleLoginSuccess = useCallback((user, token) => {
    setStoredToken(token);
    setAuthToken(token);
    setCurrentUser(user);
  }, []);

  // Verificar sesión al inicio
  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      setLoadingAuth(false);
      return;
    }

    authFetch('/api/auth/me')
      .then(r => (r.ok ? r.json() : null))
      .then(data => {
        if (data && data.user) {
          setCurrentUser(data.user);
          setAuthToken(token);
        } else {
          removeStoredToken();
          setAuthToken('');
          setCurrentUser(null);
        }
      })
      .catch(() => {
        removeStoredToken();
        setAuthToken('');
        setCurrentUser(null);
      })
      .finally(() => {
        setLoadingAuth(false);
      });
  }, [authFetch]);

  const value = {
    authToken,
    currentUser,
    setCurrentUser,
    isAuthenticated: Boolean(currentUser && authToken),
    loadingAuth,
    login: handleLoginSuccess,
    logout: handleLogout,
    authFetch
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe ser utilizado dentro de un AuthProvider');
  }
  return context;
}
