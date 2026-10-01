import React, { useState, useEffect } from 'react';
import { 
  Calendar, 
  Search, 
  RefreshCw, 
  FileSearch, 
  AlertTriangle, 
  CheckCircle2, 
  FileText, 
  ExternalLink,
  Plus,
  Trash2,
  SlidersHorizontal,
  Bookmark
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useData } from '../../context/DataContext';
import JuzgadoSelector from '../../components/ui/JuzgadoSelector';

export default function ConsultaView() {
  const { authFetch } = useAuth();
  const { appData, refreshData, selectedReport, setSelectedReport } = useData();

  // Obtener fecha actual en zona horaria oficial de Mérida, Yucatán (UTC-6)
  const getTodayMerida = () => {
    try {
      return new Date().toLocaleDateString('en-CA', { timeZone: 'America/Merida' });
    } catch (e) {
      const d = new Date(Date.now() - 6 * 3600 * 1000);
      return d.toISOString().split('T')[0];
    }
  };

  const todayStr = getTodayMerida();
  const [selectedDate, setSelectedDate] = useState(todayStr);
  const [isScanning, setIsScanning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [scanResult, setScanResult] = useState(selectedReport || null);
  const [errorMessage, setErrorMessage] = useState('');

  // Estados para gestión de criterios con selección de juzgado
  const [nuevoJuzgado, setNuevoJuzgado] = useState('Todos los Juzgados');
  const [nuevoValor, setNuevoValor] = useState('');
  const [submittingCriteria, setSubmittingCriteria] = useState(false);
  const [criteriaError, setCriteriaError] = useState('');
  const [showCriteriaPanel, setShowCriteriaPanel] = useState(true);

  useEffect(() => {
    if (selectedReport) {
      setScanResult(selectedReport);
      if (selectedReport.fecha) {
        setSelectedDate(selectedReport.fecha);
      }
    }
  }, [selectedReport]);

  // Lista de criterios
  const criteriaList = appData?.criteria && appData.criteria.length > 0 
    ? appData.criteria 
    : (appData?.keywords || []).map((k, i) => ({ 
        id: i, 
        valor: k, 
        juzgado: 'Todos los Juzgados',
        tipo: k.includes('/') ? 'Expediente' : 'Nombre' 
      }));

  // Agregar criterio
  const handleAddCriteria = async (e) => {
    e.preventDefault();
    const valorLimpio = nuevoValor.trim();
    if (!valorLimpio) return;

    setSubmittingCriteria(true);
    setCriteriaError('');

    try {
      const res = await authFetch('/api/keywords', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          keyword: valorLimpio, 
          juzgado: nuevoJuzgado || 'Todos los Juzgados'
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Error al guardar criterio');
      
      setNuevoValor('');
      await refreshData();
    } catch (err) {
      setCriteriaError(err.message);
    } finally {
      setSubmittingCriteria(false);
    }
  };

  // Eliminar criterio
  const handleRemoveCriteria = async (kw, id) => {
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

  // Ejecutar Cotejo / Búsqueda
  const startScan = async () => {
    if (criteriaList.length === 0) {
      setErrorMessage('Agrega al menos un criterio (expediente o nombre) antes de iniciar la búsqueda.');
      return;
    }

    setIsScanning(true);
    setProgress(5);
    setScanResult(null);
    setErrorMessage('');
    if (setSelectedReport) setSelectedReport(null);

    let p = 5;
    const progressTimer = setInterval(() => {
      p += Math.floor(Math.random() * 8) + 3;
      if (p >= 92) {
        clearInterval(progressTimer);
      } else {
        setProgress(p);
      }
    }, 280);

    try {
      const res = await authFetch('/api/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ date: selectedDate })
      });
      const data = await res.json();
      
      clearInterval(progressTimer);
      setProgress(100);

      setTimeout(() => {
        setIsScanning(false);
        if (data.estado === 'error' || data.estado === 'no_disponible') {
          setErrorMessage(data.mensaje || 'La edición para esta fecha aún no está publicada o disponible.');
        } else {
          setScanResult(data);
        }
        refreshData();
      }, 400);

    } catch (err) {
      clearInterval(progressTimer);
      setIsScanning(false);
      setErrorMessage(`Fallo de conexión con el servidor: ${err.message}`);
    }
  };

  const renderHighlightedSnippet = (contexto, highlights = []) => {
    if (!contexto) return null;
    let termsToHighlight = highlights;
    if (!termsToHighlight || termsToHighlight.length === 0) {
      termsToHighlight = appData?.keywords || [];
    }

    if (termsToHighlight.length === 0) {
      return <span>{contexto}</span>;
    }

    const escaped = termsToHighlight
      .filter(t => Boolean(t && t.trim()))
      .map(t => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
      .join('|');

    if (!escaped) return <span>{contexto}</span>;

    const regex = new RegExp(`(${escaped})`, 'gi');
    const parts = contexto.split(regex);

    return (
      <span>
        {parts.map((part, i) => 
          regex.test(part) ? (
            <mark key={i} className="bg-amber-200 text-amber-950 font-semibold px-1 rounded mx-0.5">
              {part}
            </mark>
          ) : (
            <span key={i}>{part}</span>
          )
        )}
      </span>
    );
  };

  const getPdfUrl = (fecha) => {
    const f = fecha || selectedDate;
    const year = f.split('-')[0];
    return `https://www.yucatan.gob.mx/docs/diario_oficial/diarios/${year}/${f}_1.pdf`;
  };

  const matches = scanResult?.coincidencias || [];

  return (
    <div className="animate-in fade-in duration-300 space-y-6">
      {/* Encabezado y Acción de Búsqueda */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200/90 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">Consulta Inmediata</h2>
            <span className="text-xs bg-amber-100 text-amber-800 font-bold px-2 py-0.5 rounded-full border border-amber-200">
              En Vivo
            </span>
          </div>
          <p className="text-slate-600 mt-1 text-sm">
            Gestiona tus criterios y coteja acuerdos en el Diario Oficial de Yucatán al instante.
          </p>
        </div>

        {/* Barra de Búsqueda: Fecha y Botón de Acción */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2 bg-slate-50 px-3.5 py-2.5 rounded-xl border border-slate-300 shadow-inner focus-within:ring-2 focus-within:ring-blue-500 focus-within:bg-white transition-all">
            <Calendar className="w-4 h-4 text-slate-500 shrink-0" />
            <input 
              type="date" 
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="text-xs sm:text-sm font-semibold text-slate-700 bg-transparent focus:outline-none"
              disabled={isScanning}
            />
          </div>

          <button 
            onClick={startScan}
            disabled={isScanning}
            className={`flex items-center gap-2 px-6 py-2.5 rounded-xl font-bold text-sm text-white shadow-md transition-all active:scale-95 ${
              isScanning 
                ? 'bg-slate-400 cursor-not-allowed' 
                : 'bg-blue-600 hover:bg-blue-500 hover:shadow-blue-600/30'
            }`}
          >
            {isScanning ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Search className="w-4 h-4" />
            )}
            <span>{isScanning ? 'Procesando PDF...' : 'Buscar Ahora'}</span>
          </button>
        </div>
      </div>

      {/* Sección Integrada: Gestión de Criterios */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200/90 overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200/80 bg-slate-50/80 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <SlidersHorizontal className="w-4 h-4 text-slate-600" />
            <h3 className="font-bold text-slate-900 text-sm sm:text-base">
              Criterios en Vigilancia
            </h3>
            <span className="text-xs font-semibold bg-slate-200 text-slate-700 px-2 py-0.5 rounded-full">
              {criteriaList.length}
            </span>
          </div>

          <button
            type="button"
            onClick={() => setShowCriteriaPanel(!showCriteriaPanel)}
            className="text-xs font-semibold text-blue-600 hover:text-blue-800 transition-colors"
          >
            {showCriteriaPanel ? 'Ocultar Criterios' : 'Mostrar Criterios'}
          </button>
        </div>

        {showCriteriaPanel && (
          <div className="p-6">
            {/* Formulario rápido para añadir criterio con selección de Juzgado */}
            <form onSubmit={handleAddCriteria} className="flex flex-col sm:flex-row gap-3 mb-5">
              <JuzgadoSelector 
                value={nuevoJuzgado}
                onChange={setNuevoJuzgado}
                className="w-full sm:w-80 md:w-96 shrink-0"
              />

              <input 
                type="text" 
                placeholder="Número de expediente o frase exacta (ej. 69/2026)"
                value={nuevoValor}
                onChange={(e) => setNuevoValor(e.target.value)}
                className="flex-1 px-4 py-2.5 rounded-xl border border-slate-300 text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all shadow-sm"
                disabled={submittingCriteria}
              />

              <button 
                type="submit"
                disabled={submittingCriteria || !nuevoValor.trim()}
                className="bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white px-5 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition-all flex items-center justify-center gap-1.5 shadow-sm active:scale-95 shrink-0"
              >
                <Plus className="w-4 h-4" />
                <span>{submittingCriteria ? 'Guardando...' : 'Agregar'}</span>
              </button>
            </form>

            {criteriaError && (
              <div className="mb-4 text-xs text-red-600 bg-red-50 p-2.5 rounded-lg border border-red-200">
                {criteriaError}
              </div>
            )}

            {/* Listado de Criterios en formato de Chips / Cards */}
            {criteriaList.length > 0 ? (
              <div className="flex flex-wrap gap-2.5 pt-1">
                {criteriaList.map((c, index) => {
                  const juzgadoLabel = c.juzgado && c.juzgado !== 'Todos' && c.juzgado !== 'Todos los Juzgados'
                    ? c.juzgado
                    : 'Cualquier Juzgado';
                  const isEspecifico = juzgadoLabel !== 'Cualquier Juzgado';

                  return (
                    <div 
                      key={c.id || index}
                      className="group flex items-center gap-2 bg-slate-50 hover:bg-slate-100/80 border border-slate-200/90 rounded-xl px-3 py-1.5 transition-all shadow-2xs"
                    >
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md tracking-wider flex items-center gap-1 ${
                        isEspecifico 
                          ? 'bg-blue-100 text-blue-900 border border-blue-200/70' 
                          : 'bg-slate-200 text-slate-700'
                      }`}>
                        <span>🏛️</span>
                        <span className="max-w-[180px] truncate">{juzgadoLabel}</span>
                      </span>

                      <span className="font-mono text-xs font-bold text-slate-900">
                        {c.valor}
                      </span>

                      <button 
                        type="button"
                        onClick={() => handleRemoveCriteria(c.valor, c.id)}
                        className="text-slate-400 hover:text-red-500 p-0.5 rounded transition-colors ml-1"
                        title={`Eliminar ${c.valor}`}
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-6 border border-dashed border-slate-200 rounded-xl bg-slate-50/50">
                <Bookmark className="w-6 h-6 text-slate-300 mx-auto mb-1" />
                <p className="text-xs text-slate-500 font-medium">
                  Aún no tienes criterios registrados. Selecciona el juzgado y escribe el expediente a vigilar arriba.
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Estado: Escaneando / Progreso */}
      {isScanning && (
        <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200/90 text-center animate-in fade-in">
          <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4 animate-bounce">
            <FileSearch className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-bold text-slate-900 mb-1">Analizando Diario Oficial</h3>
          <p className="text-xs sm:text-sm text-slate-500 mb-6 max-w-md mx-auto">
            Descargando ejemplar oficial de Mérida y cotejando acuerdos con tus criterios registrados.
          </p>
          
          <div className="w-full max-w-md mx-auto bg-slate-100 rounded-full h-3 mb-2 overflow-hidden shadow-inner">
            <div 
              className="bg-blue-600 h-3 rounded-full transition-all duration-300 ease-out relative"
              style={{ width: `${progress}%` }}
            >
              <div className="absolute inset-0 bg-white/20 w-full h-full animate-[shimmer_1s_infinite] bg-gradient-to-r from-transparent via-white/40 to-transparent"></div>
            </div>
          </div>
          <p className="text-xs font-bold text-blue-600">{Math.round(progress)}%</p>
        </div>
      )}

      {/* Estado: Error / No disponible */}
      {errorMessage && (
        <div className="flex items-start gap-3 bg-red-50 text-red-800 p-4 rounded-xl border border-red-200">
          <AlertTriangle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
          <div>
            <p className="font-bold text-sm">Aviso de Cotejo</p>
            <p className="text-xs text-red-700 mt-0.5">{errorMessage}</p>
          </div>
        </div>
      )}

      {/* Estado: Resultados de Búsqueda */}
      {scanResult && !isScanning && (
        <div className="space-y-4">
          <div className={`flex items-center gap-3 p-4 rounded-xl border ${
            matches.length > 0 
              ? 'bg-emerald-50 text-emerald-900 border-emerald-200' 
              : 'bg-slate-100 text-slate-800 border-slate-200'
          }`}>
            <CheckCircle2 className={`w-5 h-5 shrink-0 ${matches.length > 0 ? 'text-emerald-600' : 'text-slate-500'}`} />
            <div>
              <p className="font-bold text-sm">
                {matches.length > 0 
                  ? 'Consulta Finalizada Exitosamente' 
                  : 'Consulta Finalizada — Sin Coincidencias en esta Edición'}
              </p>
              <p className="text-xs text-slate-600 mt-0.5">
                Edición Oficial: <strong className="font-semibold">{scanResult.fecha}</strong> &bull; Se detectaron <strong>{matches.length}</strong> publicación(es) para tus criterios.
              </p>
            </div>
          </div>

          {matches.map((item, idx) => {
            const termino = item.termino || 'Expediente';
            return (
              <div key={idx} className="bg-white rounded-2xl shadow-sm border border-slate-200/90 overflow-hidden hover:border-blue-400 transition-colors">
                <div className="bg-slate-50/90 border-b border-slate-200/80 px-6 py-3.5 flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="bg-blue-100 text-blue-800 font-mono text-xs sm:text-sm font-bold px-3 py-1 rounded-md border border-blue-200">
                      {termino.includes('/') ? `Exp. ${termino}` : termino}
                    </div>
                    <span className="text-xs sm:text-sm font-semibold text-slate-700 bg-slate-100 px-2.5 py-1 rounded-md border border-slate-200 flex items-center gap-1.5">
                      <span>🏛️</span>
                      <span className="truncate max-w-[240px] sm:max-w-md" title={item.juzgado || 'Poder Judicial de Yucatán'}>
                        {item.juzgado || 'Poder Judicial de Yucatán'}
                      </span>
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-slate-500 text-xs sm:text-sm font-medium">
                    <FileText className="w-4 h-4 text-slate-400" />
                    Página {item.pagina}
                  </div>
                </div>

                <div className="p-6">
                  <p className="text-slate-700 leading-relaxed text-sm md:text-base font-normal">
                    {renderHighlightedSnippet(item.contexto, [termino])}
                  </p>
                </div>

                <div className="bg-slate-50/80 px-6 py-3 border-t border-slate-100 flex justify-end">
                  <a 
                    href={getPdfUrl(scanResult.fecha)} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 text-xs sm:text-sm font-semibold flex items-center gap-1.5 transition-colors"
                  >
                    Ver PDF Original <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>
              </div>
            );
          })}

          {matches.length === 0 && (
            <div className="bg-white border border-slate-200 rounded-2xl p-10 text-center text-slate-500">
              <p className="font-semibold text-slate-700 mb-1">Sin publicaciones en la edición consultada</p>
              <p className="text-xs text-slate-400">
                Ninguno de los expedientes o nombres vigilados apareció publicado en la edición del {scanResult.fecha}.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Estado Inicial: Esperando acción */}
      {!isScanning && !scanResult && !errorMessage && (
        <div className="bg-white border border-slate-200/90 rounded-2xl p-12 text-center flex flex-col items-center justify-center min-h-[320px]">
          <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mb-4 border border-blue-100">
            <Search className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-bold text-slate-700 mb-1">Listo para consultar</h3>
          <p className="text-slate-500 max-w-md text-xs sm:text-sm">
            Selecciona la fecha arriba y pulsa <strong>"Buscar Ahora"</strong> para descargar y cotejar en vivo los acuerdos del Diario Oficial de Yucatán con tus criterios.
          </p>
        </div>
      )}
    </div>
  );
}
