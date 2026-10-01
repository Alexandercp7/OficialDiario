import React, { useState } from 'react';
import { Plus, Trash2, Building2, Search } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useData } from '../../context/DataContext';
import JuzgadoSelector from '../../components/ui/JuzgadoSelector';

export default function CriteriosView() {
  const { authFetch } = useAuth();
  const { appData, refreshData } = useData();

  const [nuevoJuzgado, setNuevoJuzgado] = useState('Todos');
  const [nuevoValor, setNuevoValor] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleAdd = async (e) => {
    e.preventDefault();
    const valorLimpio = nuevoValor.trim();
    if (!valorLimpio) return;

    setSubmitting(true);
    setErrorMsg('');

    try {
      const res = await authFetch('/api/keywords', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keyword: valorLimpio,
          tipo: valorLimpio.includes('/') ? 'Expediente' : 'Nombre',
          juzgado: nuevoJuzgado || 'Todos'
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Error al guardar criterio');
      
      setNuevoValor('');
      await refreshData();
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleRemove = async (kw, id) => {
    try {
      const res = await authFetch('/api/keywords', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keyword: kw, id })
      });
      if (res.ok) {
        await refreshData();
      }
    } catch (err) {
      console.error('Error eliminando criterio:', err);
    }
  };

  const criteriaList = appData?.criteria && appData.criteria.length > 0 
    ? appData.criteria 
    : (appData?.keywords || []).map((k, i) => ({ 
        id: i, 
        valor: k, 
        juzgado: 'Todos',
        tipo: k.includes('/') ? 'Expediente' : 'Nombre' 
      }));

  return (
    <div className="animate-in fade-in duration-300">
      <div className="mb-8">
        <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">Gestión de Criterios en Vigilancia</h2>
        <p className="text-slate-600 mt-1 text-sm md:text-base">
          Configura tus expedientes y términos asociados a su juzgado específico. Recibirás alertas inmediatas por correo y Telegram cuando se publiquen acuerdos.
        </p>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-200/90 overflow-hidden mb-8">
        <div className="p-6 border-b border-slate-200/80 bg-slate-50/70">
          <form onSubmit={handleAdd} className="space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-12 gap-3 items-start">
              {/* Input 1: Juzgado Selector */}
              <div className="md:col-span-6">
                <label className="block text-xs font-bold text-slate-600 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                  <Building2 className="w-3.5 h-3.5 text-blue-600" />
                  1. Juzgado o Tribunal
                </label>
                <JuzgadoSelector
                  value={nuevoJuzgado}
                  onChange={setNuevoJuzgado}
                  disabled={submitting}
                />
              </div>

              {/* Input 2: Frase o Expediente exacto */}
              <div className="md:col-span-4">
                <label className="block text-xs font-bold text-slate-600 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                  <Search className="w-3.5 h-3.5 text-blue-600" />
                  2. Frase o Expediente exacto
                </label>
                <input 
                  type="text" 
                  placeholder="Ej. 69/2026, 800/2025 o Nombre"
                  value={nuevoValor}
                  onChange={(e) => setNuevoValor(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all shadow-sm font-medium"
                  disabled={submitting}
                />
              </div>

              {/* Botón Agregar */}
              <div className="md:col-span-2 md:pt-6">
                <button 
                  type="submit"
                  disabled={submitting || !nuevoValor.trim()}
                  className="w-full bg-blue-900 hover:bg-blue-800 disabled:opacity-50 text-white px-4 py-2.5 rounded-xl text-sm font-semibold transition-all flex items-center justify-center gap-2 shadow-md shadow-blue-950/20 active:scale-95"
                >
                  <Plus className="w-4 h-4 shrink-0" />
                  <span>{submitting ? 'Agregando...' : 'Vigilar'}</span>
                </button>
              </div>
            </div>
          </form>

          {errorMsg && (
            <div className="mt-3 text-xs text-red-600 bg-red-50 p-2.5 rounded-lg border border-red-200">
              {errorMsg}
            </div>
          )}
        </div>

        <ul className="divide-y divide-slate-100">
          {criteriaList.map((c, index) => {
            const juzgadoName = c.juzgado && c.juzgado !== 'Todos' ? c.juzgado : 'Todos los Juzgados';
            const isAll = !c.juzgado || c.juzgado === 'Todos';

            return (
              <li key={c.id || index} className="p-4 sm:px-6 flex items-center justify-between hover:bg-slate-50/80 transition-colors">
                <div className="flex flex-wrap items-center gap-2.5 sm:gap-3">
                  <div className="bg-blue-100 text-blue-800 font-mono text-xs sm:text-sm font-bold px-3 py-1 rounded-md border border-blue-200">
                    {c.valor}
                  </div>
                  <span className={`text-xs font-semibold px-2.5 py-1 rounded-full border flex items-center gap-1.5 ${
                    isAll 
                      ? 'bg-slate-100 text-slate-700 border-slate-200' 
                      : 'bg-emerald-50 text-emerald-800 border-emerald-200'
                  }`}>
                    <span>🏛️</span>
                    <span className="truncate max-w-[280px] sm:max-w-md" title={juzgadoName}>
                      {juzgadoName}
                    </span>
                  </span>
                </div>
                <button 
                  onClick={() => handleRemove(c.valor, c.id)}
                  className="text-slate-400 hover:text-red-500 p-2 rounded-lg hover:bg-red-50 transition-colors"
                  title="Eliminar de vigilancia"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </li>
            );
          })}

          {criteriaList.length === 0 && (
            <li className="p-10 text-center text-slate-500 text-sm">
              No tienes criterios en vigilancia todavía. Selecciona un juzgado e ingresa el expediente o nombre que deseas monitorear.
            </li>
          )}
        </ul>
      </div>
    </div>
  );
}
