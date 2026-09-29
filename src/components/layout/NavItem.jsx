import React from 'react';
import { NavLink } from 'react-router-dom';

export default function NavItem({ to, icon, label, badge }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs sm:text-sm font-medium transition-all duration-200 ${
          isActive
            ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 shadow-sm'
            : 'text-slate-300 hover:bg-slate-800 hover:text-white border border-transparent'
        }`
      }
    >
      {({ isActive }) => (
        <>
          <div className="flex items-center gap-3">
            {React.cloneElement(icon, { className: 'w-4 h-4 sm:w-5 sm:h-5 shrink-0' })}
            <span>{label}</span>
          </div>
          {badge !== undefined && badge > 0 && (
            <span
              className={`text-[11px] font-mono px-2 py-0.5 rounded-full ${
                isActive ? 'bg-blue-500/20 text-blue-300' : 'bg-slate-800 text-slate-400'
              }`}
            >
              {badge}
            </span>
          )}
        </>
      )}
    </NavLink>
  );
}
