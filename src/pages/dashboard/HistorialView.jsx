import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle2, AlertTriangle, Clock, X, Info, HelpCircle } from 'lucide-react';
import { useData } from '../../context/DataContext';

export default function HistorialView() {
  const navigate = useNavigate();
  const { appData, setSelectedReport } = useData();
  const history = appData?.history || [];
  const [selectedError, setSelectedError] = useState(null);

  const handleViewReport = (item) => {
    setSelectedReport(item);
    navigate('/dashboard/consulta');
  };

  return (
    <div className="animate-in fade-in duration-300">
      <div className="mb-8">
        <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">Libro de Consultas Previas</h2>
        <p className="text-slate-600 mt-1 text-sm md:text-base">
          Historial de cotejos y alertas generadas para tu cuenta (Horario oficial de Mérida, Yucatán UTC-6).
        </p>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-200/90 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200 text-xs">
              <tr>
                <th className="px-6 py-4">Fecha de Edición</th>
                <th className="px-6 py-4">Hora de Escaneo (Mérida)</th>
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
                const esNoDisponible = item.estado === 'no_disponible' || item.estado === 'no_publicado';
                const horaTxt = item.hora || (item.timestamp ? item.timestamp.split(' ')[1] : '--:--');

                return (
                  <tr key={idx} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-6 py-4 font-semibold text-slate-900 font-mono text-xs sm:text-sm">
                      {item.fecha}
                    </td>
                    <td className="px-6 py-4 text-slate-600 font-mono text-xs sm:text-sm">
                      <span className="inline-flex items-center gap-1.5 bg-slate-100 px-2 py-0.5 rounded text-slate-700 text-xs">
                        <Clock className="w-3 h-3 text-slate-400" />
                        {horaTxt}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      {esCompletado && (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-700">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          Completado
                        </span>
                      )}
                      {esNoDisponible && (
                        <button
                          type="button"
                          onClick={() => setSelectedError(item)}
                          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 hover:bg-amber-200 transition-colors cursor-pointer border border-amber-200/60 active:scale-95 group"
                          title="Clic para ver detalles de por qué no está disponible"
                        >
                          <Clock className="w-3.5 h-3.5 text-amber-600 group-hover:scale-110 transition-transform" />
                          <span>No publicada aún</span>
                          <span className="text-[10px] bg-amber-200/80 text-amber-900 font-bold px-1 rounded">¿Por qué?</span>
                        </button>
                      )}
                      {!esCompletado && !esNoDisponible && (
                        <button
                          type="button"
                          onClick={() => setSelectedError(item)}
                          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-700 hover:bg-red-200 hover:text-red-800 transition-colors cursor-pointer border border-red-200/60 active:scale-95 group"
                          title="Clic para ver por qué falló"
                        >
                          <AlertTriangle className="w-3.5 h-3.5 text-red-600 group-hover:scale-110 transition-transform" />
                          <span>Error</span>
                          <span className="text-[10px] bg-red-200/80 text-red-900 font-bold px-1 rounded">¿Por qué?</span>
                        </button>
                      )}
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
                      {esCompletado ? (
                        <button 
                          onClick={() => handleViewReport(item)}
                          className="text-blue-600 hover:text-blue-900 font-semibold text-xs hover:underline cursor-pointer"
                        >
                          Ver Reporte
                        </button>
                      ) : (
                        <button 
                          onClick={() => setSelectedError(item)}
                          className="text-red-600 hover:text-red-800 font-semibold text-xs hover:underline cursor-pointer inline-flex items-center gap-1"
                        >
                          <span>Ver Motivo</span>
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}

              {history.length === 0 && (
                <tr>
                  <td colSpan="5" className="px-6 py-10 text-center text-slate-400 text-sm">
                    Aún no se han ejecutado escaneos. Realiza uno en la pestaña Consulta Inmediata.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal de Detalle de Error / Estado */}
      {selectedError && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200"
          onClick={() => setSelectedError(null)}
        >
          <div 
            className="bg-white rounded-2xl shadow-2xl max-w-lg w-full border border-slate-200 overflow-hidden transform transition-all animate-in zoom-in-95 duration-200"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header del Modal */}
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/80">
              <div className="flex items-center gap-3">
                <div className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 ${
                  selectedError.estado === 'no_disponible' 
                    ? 'bg-amber-100 text-amber-700' 
                    : 'bg-red-100 text-red-700'
                }`}>
                  {selectedError.estado === 'no_disponible' ? (
                    <Clock className="w-5 h-5" />
                  ) : (
                    <AlertTriangle className="w-5 h-5" />
                  )}
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-900">
                    {selectedError.estado === 'no_disponible' 
                      ? 'Edición No Disponible' 
                      : 'Motivo del Error en Cotejo'}
                  </h3>
                  <span className="text-xs text-slate-500">
                    Edición: <strong className="font-mono text-slate-700">{selectedError.fecha}</strong> • {selectedError.hora || (selectedError.timestamp ? selectedError.timestamp.split(' ')[1] : '')} (Mérida)
                  </span>
                </div>
              </div>
              <button
                onClick={() => setSelectedError(null)}
                className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100 transition-colors"
                title="Cerrar ventana"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Contenido del Modal */}
            <div className="p-6 space-y-4">
              <div>
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1.5">
                  Respuesta del servidor:
                </span>
                <div className={`p-4 rounded-xl border text-xs sm:text-sm font-mono leading-relaxed break-words ${
                  selectedError.estado === 'no_disponible'
                    ? 'bg-amber-50 text-amber-950 border-amber-200'
                    : 'bg-red-50 text-red-950 border-red-200'
                }`}>
                  {selectedError.mensaje || 'No se registró un mensaje detallado para este evento.'}
                </div>
              </div>

              {/* Explicación amigable */}
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-xs text-slate-600 space-y-1.5">
                <span className="font-bold text-slate-800 flex items-center gap-1.5">
                  <Info className="w-4 h-4 text-blue-500 shrink-0" />
                  ¿Por qué ocurre esto?
                </span>
                {String(selectedError.mensaje || '').includes('404') ? (
                  <p className="leading-relaxed">
                    El portal oficial del Gobierno del Estado de Yucatán (<strong>yucatan.gob.mx</strong>) aún no había publicado el boletín del Diario Oficial para esa fecha en el momento en que se ejecutó el escaneo, o se trata de un sábado, domingo o día inhábil.
                  </p>
                ) : String(selectedError.mensaje || '').toLowerCase().includes('conexión') || String(selectedError.mensaje || '').toLowerCase().includes('timeout') ? (
                  <p className="leading-relaxed">
                    Hubo un retraso o corte de red al intentar descargar el archivo PDF desde los servidores oficiales del Gobierno del Estado.
                  </p>
                ) : (
                  <p className="leading-relaxed">
                    Ocurrió una interrupción durante la descarga o análisis del documento oficial. Puedes reintentar la consulta en la pestaña <strong>Consulta Inmediata</strong>.
                  </p>
                )}
              </div>
            </div>

            {/* Pie del Modal */}
            <div className="px-6 py-3.5 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
              <span className="text-[11px] text-slate-400">
                ID de escaneo: #{selectedError.id}
              </span>
              <button
                type="button"
                onClick={() => setSelectedError(null)}
                className="bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs px-4 py-2 rounded-xl transition-colors shadow-sm"
              >
                Entendido, cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

