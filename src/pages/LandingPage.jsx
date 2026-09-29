import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Scale, Clock, ShieldCheck, Zap, Search, ChevronRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function LandingPage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const handleAccess = () => {
    if (isAuthenticated) {
      navigate('/dashboard/criterios');
    } else {
      navigate('/auth');
    }
  };

  const todayFormatted = new Date().toLocaleDateString('es-MX', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  });

  return (
    <div className="flex flex-col min-h-screen bg-white">
      {/* Barra de Navegación */}
      <nav className="sticky top-0 z-50 bg-slate-900/95 backdrop-blur-md border-b border-slate-800 shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-20 items-center">
            <div className="flex items-center gap-3 cursor-pointer" onClick={handleAccess}>
              <div className="bg-amber-500 p-2.5 rounded-xl shadow-lg shadow-amber-500/20">
                <Scale className="h-6 w-6 text-slate-950" />
              </div>
              <div>
                <span className="font-extrabold text-2xl tracking-tight text-white block">
                  LexMonitor <span className="text-amber-500 font-semibold">Yucatán</span>
                </span>
                <span className="text-[10px] tracking-wider uppercase text-slate-400 font-medium block">
                  Vigilancia Jurídica con Base Relacional
                </span>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <button 
                onClick={handleAccess}
                className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2.5 rounded-xl text-sm font-semibold transition-all shadow-lg shadow-blue-900/40 hover:shadow-blue-600/30 flex items-center gap-2 border border-blue-500 active:scale-95"
              >
                <span>{isAuthenticated ? 'Ir al Panel' : 'Acceder al Sistema'}</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Sección Hero */}
      <section className="relative pt-20 pb-28 md:pt-24 md:pb-36 overflow-hidden bg-slate-900 flex-grow">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-slate-800 via-slate-900 to-slate-950 pointer-events-none"></div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
            <div className="max-w-2xl">
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-800/90 border border-slate-700/80 text-amber-400 text-sm font-medium mb-6 shadow-inner">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
                </span>
                Vigilancia Personalizada por Abogado
              </div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold text-white leading-[1.15] mb-6">
                Sistema de Vigilancia Jurídica y <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-amber-500 to-amber-600">Notificaciones</span>
              </h1>
              <p className="text-lg md:text-xl text-slate-300 mb-8 leading-relaxed font-normal">
                Cada usuario o despacho cuenta con su propio padrón de expedientes y recibe alertas personalizadas por Correo o Telegram en tiempo real.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <button 
                  onClick={handleAccess}
                  className="bg-amber-500 hover:bg-amber-400 text-slate-950 px-8 py-4 rounded-xl text-base font-bold transition-all shadow-xl shadow-amber-500/20 hover:shadow-amber-500/30 flex items-center justify-center gap-2 active:scale-95"
                >
                  <span>{isAuthenticated ? 'Ir al Panel de Vigilancia' : 'Acceder al Sistema'}</span>
                  <ChevronRight className="w-5 h-5 stroke-[2.5]" />
                </button>
              </div>
            </div>
            
            {/* Gráfico Hero */}
            <div className="relative mx-auto w-full max-w-lg lg:max-w-none">
              <div className="absolute inset-0 bg-gradient-to-tr from-amber-500/20 via-blue-500/15 to-amber-400/20 rounded-3xl transform rotate-2 scale-105 blur-2xl"></div>
              <div className="relative bg-slate-800/90 backdrop-blur-xl p-6 sm:p-8 rounded-3xl shadow-2xl border border-slate-700/80 flex flex-col gap-4">
                <div className="flex items-center justify-between border-b border-slate-700/80 pb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-slate-700/80 rounded-xl flex items-center justify-center shadow-inner">
                      <Search className="w-5 h-5 text-amber-400" />
                    </div>
                    <div>
                      <div className="text-sm font-bold text-white flex items-center gap-2">
                        Escaneo Multi-Usuario Activo
                      </div>
                      <div className="text-xs text-slate-400">Diario Oficial — {todayFormatted}</div>
                    </div>
                  </div>
                  <div className="animate-pulse bg-emerald-950/70 text-emerald-400 border border-emerald-800/60 text-xs font-bold px-2.5 py-1 rounded-md">
                    Tablas SQLite
                  </div>
                </div>
                
                {[
                  { exp: '800/2026', nombre: 'Eduardo Alexander Canto', pag: '26' },
                  { exp: '1250/2025', nombre: 'Constructora Maya S.A.', pag: '42' }
                ].map((item, idx) => (
                  <div key={idx} className="bg-slate-900/70 p-4 rounded-xl border border-slate-700/70 flex flex-col gap-2 relative overflow-hidden group hover:border-slate-600 transition-colors">
                    <div className="flex justify-between items-start">
                      <div className="font-mono text-xs font-semibold text-amber-400 bg-amber-400/10 px-2.5 py-0.5 rounded-md border border-amber-400/20">
                        Exp. {item.exp}
                      </div>
                      <div className="text-xs text-slate-500 font-mono">Pág. {item.pag}</div>
                    </div>
                    <div className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                      ... se notifica en los estrados al C. <span className="bg-amber-500/20 text-amber-300 px-1.5 py-0.5 font-medium rounded border border-amber-500/30">{item.nombre}</span> sobre el acuerdo dictado...
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Características */}
      <section className="py-24 bg-slate-50/80 border-t border-slate-200/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-extrabold text-slate-900 mb-4 tracking-tight">¿Qué problema resuelve?</h2>
            <p className="text-lg text-slate-600">Optimizamos tu flujo de trabajo diario, eliminando tareas repetitivas y mitigando riesgos legales procesales.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white rounded-2xl p-8 shadow-sm hover:shadow-md transition-shadow border border-slate-200/80 flex flex-col">
              <div className="w-14 h-14 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center mb-6">
                <Clock className="w-7 h-7" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-3">Ahorro de Tiempo</h3>
              <p className="text-slate-600 leading-relaxed text-sm md:text-base">
                Evita descargar y leer manualmente documentos de más de 100 páginas todos los días para encontrar una sola publicación.
              </p>
            </div>

            <div className="bg-white rounded-2xl p-8 shadow-sm hover:shadow-md transition-shadow border border-slate-200/80 flex flex-col">
              <div className="w-14 h-14 bg-amber-50 text-amber-600 rounded-2xl flex items-center justify-center mb-6">
                <ShieldCheck className="w-7 h-7" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-3">Cero Error Humano</h3>
              <p className="text-slate-600 leading-relaxed text-sm md:text-base">
                Evita que un acuerdo pase desapercibido por cansancio visual y corran los términos legales de impugnación o contestación.
              </p>
            </div>

            <div className="bg-white rounded-2xl p-8 shadow-sm hover:shadow-md transition-shadow border border-slate-200/80 flex flex-col">
              <div className="w-14 h-14 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center mb-6">
                <Zap className="w-7 h-7" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-3">Inmediatez Personalizada</h3>
              <p className="text-slate-600 leading-relaxed text-sm md:text-base">
                Coteja la edición en segundos y alerta a cada abogado exclusivamente con los expedientes que tiene asignados.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
