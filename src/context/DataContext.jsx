import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useAuth } from './AuthContext';

const DataContext = createContext(null);

export function DataProvider({ children }) {
  const { authToken, authFetch, isAuthenticated, setCurrentUser } = useAuth();

  const [appData, setAppData] = useState({
    keywords: [],
    criteria: [],
    notifications: {
      channel: 'email',
      email: {
        sender_email: '',
        sender_password: '',
        recipient_email: '',
        smtp_host: 'smtp.gmail.com',
        smtp_port: 465,
        use_ssl: true
      }
    },
    history: []
  });

  const [loadingData, setLoadingData] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);

  const loadUserData = useCallback(async () => {
    if (!authToken || !isAuthenticated) return;

    setLoadingData(true);
    try {
      const res = await authFetch('/api/data');
      if (res.ok) {
        const data = await res.json();
        setAppData(data);
        if (data.user) {
          setCurrentUser(data.user);
        }
      }
    } catch (e) {
      console.error('Error cargando datos de usuario:', e);
    } finally {
      setLoadingData(false);
    }
  }, [authToken, isAuthenticated, authFetch, setCurrentUser]);

  useEffect(() => {
    if (isAuthenticated) {
      loadUserData();
    } else {
      setAppData({
        keywords: [],
        criteria: [],
        notifications: { channel: 'email', email: {} },
        history: []
      });
      setSelectedReport(null);
    }
  }, [isAuthenticated, loadUserData]);

  const value = {
    appData,
    setAppData,
    loadingData,
    refreshData: loadUserData,
    selectedReport,
    setSelectedReport
  };

  return <DataContext.Provider value={value}>{children}</DataContext.Provider>;
}

export function useData() {
  const context = useContext(DataContext);
  if (!context) {
    throw new Error('useData debe ser utilizado dentro de un DataProvider');
  }
  return context;
}
