import React from 'react';
import { HashRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import ProtectedRoute from '../components/common/ProtectedRoute';

// Páginas
import LandingPage from '../pages/LandingPage';
import AuthPage from '../pages/AuthPage';
import DashboardLayout from '../pages/DashboardLayout';

// Vistas del Dashboard
import ConsultaView from '../pages/dashboard/ConsultaView';
import HistorialView from '../pages/dashboard/HistorialView';
import ConfiguracionView from '../pages/dashboard/ConfiguracionView';

// Redirección para /auth cuando ya hay sesión activa
function AuthGuard({ children }) {
  const { isAuthenticated } = useAuth();
  if (isAuthenticated) {
    return <Navigate to="/dashboard/consulta" replace />;
  }
  return children;
}

export default function AppRoutes() {
  const { isAuthenticated } = useAuth();

  return (
    <HashRouter>
      <Routes>
        {/* Raíz: Si está logueado va al dashboard, si no muestra la landing */}
        <Route
          path="/"
          element={
            isAuthenticated ? (
              <Navigate to="/dashboard/consulta" replace />
            ) : (
              <LandingPage />
            )
          }
        />

        {/* Ruta explícita para la página de presentación / bienvenida */}
        <Route path="/landing" element={<LandingPage />} />

        {/* Autenticación: Login y Registro */}
        <Route
          path="/auth"
          element={
            <AuthGuard>
              <AuthPage />
            </AuthGuard>
          }
        />

        {/* Rutas protegidas del Dashboard */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          {/* Redirección por defecto */}
          <Route index element={<Navigate to="consulta" replace />} />
          
          <Route path="consulta" element={<ConsultaView />} />
          {/* Compatibilidad hacia atrás */}
          <Route path="criterios" element={<Navigate to="/dashboard/consulta" replace />} />
          <Route path="cotejo" element={<Navigate to="/dashboard/consulta" replace />} />
          <Route path="historial" element={<HistorialView />} />
          <Route path="configuracion" element={<ConfiguracionView />} />
        </Route>

        {/* Cualquier ruta desconocida redirige al inicio */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </HashRouter>
  );
}
