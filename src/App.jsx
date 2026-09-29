import React from 'react';
import { AuthProvider } from './context/AuthContext';
import { DataProvider } from './context/DataContext';
import AppRoutes from './routes/AppRoutes';

export default function App() {
  return (
    <AuthProvider>
      <DataProvider>
        <div className="min-h-screen font-sans text-slate-800 selection:bg-amber-500 selection:text-white bg-slate-50">
          <AppRoutes />
        </div>
      </DataProvider>
    </AuthProvider>
  );
}
