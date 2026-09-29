import React from 'react';
import { NavLink } from 'react-router-dom';
import { Scale, LogOut } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useData } from '../../context/DataContext';

export default function MobileHeader() {
  const { logout } = useAuth();
  const { appData } = useData();

  const criteriaCount = appData?.criteria?.length ?? appData?.keywords?.length ?? 0;
  const historyCount = appData?.history?.length ?? 0;

  return (
    <>
      {/* Cabecera Móvil */}
      <header className="md:hidden bg-slate-900 h-16 flex items-center justify-between px-4 border-b border-slate-800 shrink-0 sticky top-0 z-40">
        <div className="flex items-center gap-2">
          <div className="bg-amber-500 p-1.5 rounded-lg">
            <Scale className="h-4 w-4 text-slate-900" />
          </div>
          <span className="font-bold text-base text-white">LexMonitor</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={logout}
            className="text-slate-400 hover:text-white p-2 rounded-lg hover:bg-slate-800 transition-colors"
            title="Cerrar sesión"
          >
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </header>

      {/* Barra de Navegación Móvil */}
      <div className="md:hidden bg-slate-900/90 border-b border-slate-800 px-2 py-1.5 flex gap-1 overflow-x-auto shrink-0 sticky top-16 z-30">
        <NavLink
          to="/dashboard/criterios"
          className={({ isActive }) =>
            `px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
              isActive ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200'
            }`
          }
        >
          Criterios ({criteriaCount})
        </NavLink>
        <NavLink
          to="/dashboard/cotejo"
          className={({ isActive }) =>
            `px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
              isActive ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200'
            }`
          }
        >
          Cotejo
        </NavLink>
        <NavLink
          to="/dashboard/historial"
          className={({ isActive }) =>
            `px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
              isActive ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200'
            }`
          }
        >
          Historial ({historyCount})
        </NavLink>
        <NavLink
          to="/dashboard/configuracion"
          className={({ isActive }) =>
            `px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
              isActive ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200'
            }`
          }
        >
          Configuración
        </NavLink>
      </div>
    </>
  );
}
