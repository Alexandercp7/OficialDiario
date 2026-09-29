import React, { useState } from 'react';
import { Plus, Trash2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useData } from '../../context/DataContext';

export default function CriteriosView() {
  const { authFetch } = useAuth();
  const { appData, refreshData } = useData();

  const [nuevoTipo, setNuevoTipo] = useState('Expediente');
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
        body: JSON.stringify({ keyword: valorLimpio, tipo: nuevoTipo })
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

  const handleRemove = async (kw) => {
    try {
      const res = await authFetch('/api/keywords', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keyword: kw })
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
    : (appData?.keywords || []).map((k, i) => ({ id: i, valor: k, tipo: k.includes('/') ? 'Expediente' : 'Nombre' }));

  return (
    <div className="animate-in fade-in duration-300">
      <div className="mb-8">
        <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">Gestión de Criterios en Vigilancia</h2>
        <p className="text-slate-600 mt-1 text-sm md:text-base">
          Estos expedientes y nombres corresponden a <strong>tu cuenta personal</strong>. Solamente tú recibirás alertas de estas coincidencias.
        </p>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-200/90 overflow-hidden mb-8">
        <div className="p-6 border-b border-slate-200/80 bg-slate-50/70">
          <form onSubmit={handleAdd} className="flex flex-col sm:flex-row gap-3">
            <select 
              value={nuevoTipo}
              onChange={(e) => setNuevoTipo(e.target.value)}
              className="px-4 py-2.5 rounded-xl border border-slate-300 bg-white text-slate-700 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all shadow-sm"
            >
              <option value="Expediente">Expediente</option>
              <option value="Nombre">Nombre</option>
              <option value="Empresa">Empresa</option>
            </select>
            <input 
              type="text" 
              placeholder={
                nuevoTipo === 'Expediente' ? 'Ej. 800/2026 o 1250/2025' :
                nuevoTipo === 'Nombre' ? 'Ej. Eduardo Alexander Canto' :
                'Ej. Constructora Maya S.A.'
              }
              value={nuevoValor}
              onChange={(e) => setNuevoValor(e.target.value)}
              className="flex-1 px-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all shadow-sm"
              disabled={submitting}
            />
            <button 
              type="submit"
              disabled={submitting || !nuevoValor.trim()}
              className="bg-blue-900 hover:bg-blue-800 disabled:opacity-50 text-white px-6 py-2.5 rounded-xl text-sm font-semibold transition-all flex items-center justify-center gap-2 shadow-md shadow-blue-950/20 active:scale-95"
            >
              <Plus className="w-4 h-4" />
              <span>{submitting ? 'Agregando...' : 'Agregar'}</span>
            </button>
          </form>

          {errorMsg && (
            <div className="mt-3 text-xs text-red-600 bg-red-50 p-2.5 rounded-lg border border-red-200">
              {errorMsg}
            </div>
          )}
        </div>

        <ul className="divide-y divide-slate-100">
          {criteriaList.map((c, index) => {
            const tipo = c.tipo || (c.valor && c.valor.includes('/') ? 'Expediente' : 'Nombre');
            return (
              <li key={c.id || index} className="p-4 sm:px-6 flex items-center justify-between hover:bg-slate-50/80 transition-colors">
                <div className="flex items-center gap-3 sm:gap-4 overflow-hidden">
                  <span className={`text-xs font-bold px-2.5 py-1 rounded-full shrink-0 ${
                    tipo === 'Expediente' ? 'bg-indigo-100 text-indigo-700 border border-indigo-200/50' :
                    tipo === 'Nombre' ? 'bg-emerald-100 text-emerald-700 border border-emerald-200/50' :
                    'bg-orange-100 text-orange-700 border border-orange-200/50'
                  }`}>
                    {tipo}
                  </span>
                  <span className="font-semibold text-slate-800 text-sm truncate font-mono">
                    {c.valor}
                  </span>
                </div>
                <button 
                  onClick={() => handleRemove(c.valor)}
                  className="text-slate-400 hover:text-red-500 p-2 rounded-lg hover:bg-red-50 transition-colors"
                  title="Eliminar criterio"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </li>
            );
          })}

          {criteriaList.length === 0 && (
            <li className="p-10 text-center text-slate-500 text-sm">
              No tienes criterios registrados todavía. Agrega el número de expediente o nombre que deseas monitorear.
            </li>
          )}
        </ul>
      </div>
    </div>
  );
}
