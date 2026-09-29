import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from '../components/layout/Sidebar';
import MobileHeader from '../components/layout/MobileHeader';

export default function DashboardLayout() {
  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      {/* Barra Lateral Desktop */}
      <Sidebar />

      {/* Área Principal */}
      <main className="flex-1 flex flex-col h-screen overflow-y-auto">
        {/* Cabecera y Navegación Móvil */}
        <MobileHeader />

        {/* Contenido Dinámico de la Ruta */}
        <div className="p-6 md:p-10 max-w-5xl mx-auto w-full flex-1">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
