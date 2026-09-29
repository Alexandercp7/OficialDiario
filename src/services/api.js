// Helper de almacenamiento y configuración para peticiones al backend

export const TOKEN_STORAGE_KEY = 'lexmonitor_token';

export const getStoredToken = () => {
  return localStorage.getItem(TOKEN_STORAGE_KEY) || '';
};

export const setStoredToken = (token) => {
  if (token) {
    localStorage.setItem(TOKEN_STORAGE_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
  }
};

export const removeStoredToken = () => {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
};

export const createAuthHeaders = (token) => {
  const currentToken = token || getStoredToken();
  return currentToken ? { Authorization: `Bearer ${currentToken}` } : {};
};
