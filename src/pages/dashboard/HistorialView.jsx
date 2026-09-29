import React from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle2, AlertTriangle } from 'lucide-react';
import { useData } from '../../context/DataContext';

export default function HistorialView() {
  const navigate = useNavigate();
  const { appData, setSelectedReport } = useData();
  const history = appData?.history || [];

  const handleViewReport = (item) => {
    setSelectedReport(item);
    navigate('/dashboard/cotejo');
  };

  return (
    <div className="animate-in fade-in duration-300">
      <div className="mb-8">
        <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">Libro de Consultas Previas</h2>
        <p className="text-slate-600 mt-1 text-sm md:text-base">
          Historial de cotejos y coincidencias encontradas para tu cuenta.
        </p>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-200/90 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200 text-xs">
              <tr>
                <th className="px-6 py-4">Fecha de Edición</th>
                <th className="px-6 py-4">Hora de Escaneo</th>
                <th className="px-6 py-4">Estado</th>
                <th className="px-6 py-4">Tus Coincidencias</th>
                <th className="px-6 py-4 text-right">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {history.map((item, idx) => {
                const totalCoincidencias = item.total_coincidencias !== undefined 
                  ? item.total_coincidencias 
                  : (item.coincidencias ? item.coincidencias.length : 0);

                const esCompletado = item.estado === 'completado';
                const horaTxt = item.timestamp ? item.timestamp.split(' ')[1] : '--:--';

                return (
                  <tr key={idx} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-6 py-4 font-semibold text-slate-900 font-mono text-xs sm:text-sm">
                      {item.fecha}
                    </td>
                    <td className="px-6 py-4 text-slate-500 text-xs sm:text-sm">
                      {horaTxt}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${
                        esCompletado ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'
                      }`}>
                        {esCompletado ? <CheckCircle2 className="w-3.5 h-3.5" /> : <AlertTriangle className="w-3.5 h-3.5" />}
                        {esCompletado ? 'Completado' : 'Error'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      {totalCoincidencias > 0 ? (
                        <span className="bg-amber-100 text-amber-900 font-bold px-2.5 py-1 rounded-md text-xs border border-amber-200/60">
                          {totalCoincidencias} encontrada{totalCoincidencias > 1 ? 's' : ''}
                        </span>
                      ) : (
                        <span className="text-slate-400 text-xs">Ninguna</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button 
                        disabled={!esCompletado}
                        onClick={() => handleViewReport(item)}
                        className="text-blue-600 hover:text-blue-900 font-semibold text-xs disabled:opacity-30 disabled:cursor-not-allowed hover:underline"
                      >
                        Ver Reporte
                      </button>
                    </td>
                  </tr>
                );
              })}

              {history.length === 0 && (
                <tr>
                  <td colSpan="5" className="px-6 py-10 text-center text-slate-400 text-sm">
                    Aún no se han ejecutado escaneos. Realiza uno en la pestaña Cotejo Automatizado.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
