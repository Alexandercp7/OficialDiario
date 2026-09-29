import React from 'react';
import { Scale, User, Search, FileSearch, History, Settings, LogOut } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useData } from '../../context/DataContext';
import NavItem from './NavItem';

export default function Sidebar() {
  const { currentUser, logout } = useAuth();
  const { appData } = useData();

  const userName = currentUser?.name || 'Usuario';
  const userEmail = currentUser?.email || '';

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col hidden md:flex border-r border-slate-800">
      {/* Brand Header */}
      <div className="h-20 flex items-center px-6 border-b border-slate-800 bg-slate-950">
        <div className="bg-amber-500 p-2 rounded-lg mr-3 shadow-md shadow-amber-500/20">
          <Scale className="h-5 w-5 text-slate-950" />
        </div>
        <div>
          <span className="font-bold text-lg text-white block leading-tight">LexMonitor</span>
          <span className="text-[10px] uppercase tracking-wider text-amber-500 font-semibold block">Yucatán</span>
        </div>
      </div>

      {/* Perfil del Usuario Autenticado */}
      <div className="p-5 border-b border-slate-800 bg-slate-900/60">
        <div className="flex items-center gap-3">
          <div className="bg-slate-800 border border-slate-700 p-2 rounded-xl text-slate-300 shadow-sm shrink-0">
            <User className="w-5 h-5 text-amber-400" />
          </div>
          <div className="overflow-hidden">
            <p className="text-xs font-bold text-white truncate" title={userName}>
              {userName}
            </p>
            <p className="text-[11px] text-slate-400 truncate" title={userEmail}>
              {userEmail}
            </p>
          </div>
        </div>
      </div>

      {/* Menú de Navegación */}
      <nav className="flex-1 py-6 px-3 space-y-1.5">
        <NavItem
          to="/dashboard/criterios"
          icon={<Search />}
          label="Gestión de Criterios"
          badge={appData?.criteria?.length ?? appData?.keywords?.length}
        />
        <NavItem
          to="/dashboard/cotejo"
          icon={<FileSearch />}
          label="Cotejo Automatizado"
        />
        <NavItem
          to="/dashboard/historial"
          icon={<History />}
          label="Historial"
          badge={appData?.history?.length}
        />
        <NavItem
          to="/dashboard/configuracion"
          icon={<Settings />}
          label="Configuración"
        />
      </nav>

      {/* Botón Salir */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/40">
        <button
          onClick={logout}
          className="flex items-center gap-2.5 text-xs font-medium text-slate-400 hover:text-white w-full px-3 py-2.5 rounded-lg hover:bg-slate-800/80 transition-colors"
        >
          <LogOut className="w-4 h-4" />
          Cerrar Sesión
        </button>
      </div>
    </aside>
  );
}
