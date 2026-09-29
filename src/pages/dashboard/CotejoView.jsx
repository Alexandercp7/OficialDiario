import React, { useState, useEffect } from 'react';
import { 
  Calendar, 
  Play, 
  RefreshCw, 
  FileSearch, 
  AlertTriangle, 
  CheckCircle2, 
  FileText, 
  ExternalLink 
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useData } from '../../context/DataContext';

export default function CotejoView() {
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

  useEffect(() => {
    if (selectedReport) {
      setScanResult(selectedReport);
      if (selectedReport.fecha) {
        setSelectedDate(selectedReport.fecha);
      }
    }
  }, [selectedReport]);

  const startScan = async () => {
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
    <div className="animate-in fade-in duration-300">
      <div className="mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">Cotejo Automatizado</h2>
          <p className="text-slate-600 mt-1 text-sm md:text-base">
            Descarga y análisis del Diario Oficial del Estado de Yucatán con notificación personalizada.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2 bg-white px-3 py-2 rounded-xl border border-slate-300 shadow-sm">
            <Calendar className="w-4 h-4 text-slate-400 shrink-0" />
            <input 
              type="date" 
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="text-xs sm:text-sm font-medium text-slate-700 bg-transparent focus:outline-none"
              disabled={isScanning}
            />
          </div>

          <button 
            onClick={startScan}
            disabled={isScanning}
            className={`flex items-center gap-2 px-6 py-2.5 rounded-xl font-bold text-sm text-white shadow-md transition-all ${
              isScanning 
                ? 'bg-slate-400 cursor-not-allowed' 
                : 'bg-blue-600 hover:bg-blue-500 hover:shadow-blue-600/30 active:scale-95'
            }`}
          >
            {isScanning ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Play className="w-4 h-4 fill-current" />
            )}
            <span>{isScanning ? 'Procesando PDF...' : 'Escanear Diario'}</span>
          </button>
        </div>
      </div>

      {isScanning && (
        <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200/90 mb-8 text-center animate-in fade-in">
          <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4 animate-bounce">
            <FileSearch className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-bold text-slate-900 mb-1">Analizando Diario Oficial</h3>
          <p className="text-xs sm:text-sm text-slate-500 mb-6 max-w-md mx-auto">
            Descargando ejemplar oficial y cotejando acuerdos con las tablas de expedientes de los usuarios.
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

      {errorMessage && (
        <div className="flex items-start gap-3 bg-red-50 text-red-800 p-4 rounded-xl border border-red-200 mb-6">
          <AlertTriangle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
          <div>
            <p className="font-bold text-sm">Aviso de Cotejo</p>
            <p className="text-xs text-red-700 mt-0.5">{errorMessage}</p>
          </div>
        </div>
      )}

      {scanResult && !isScanning && (
        <div className="space-y-6">
          <div className={`flex items-center gap-3 p-4 rounded-xl border ${
            matches.length > 0 
              ? 'bg-emerald-50 text-emerald-900 border-emerald-200' 
              : 'bg-slate-100 text-slate-800 border-slate-200'
          }`}>
            <CheckCircle2 className={`w-5 h-5 shrink-0 ${matches.length > 0 ? 'text-emerald-600' : 'text-slate-500'}`} />
            <div>
              <p className="font-bold text-sm">
                {matches.length > 0 
                  ? 'Análisis Completado Exitosamente' 
                  : 'Análisis Completado — Sin Coincidencias para tus Criterios'}
              </p>
              <p className="text-xs text-slate-600 mt-0.5">
                Edición: <strong className="font-semibold">{scanResult.fecha}</strong> &bull; Se detectaron <strong>{matches.length}</strong> publicación(es) para tus expedientes.
              </p>
            </div>
          </div>

          {matches.map((item, idx) => {
            const termino = item.termino || 'Expediente';
            return (
              <div key={idx} className="bg-white rounded-2xl shadow-sm border border-slate-200/90 overflow-hidden hover:border-blue-400/80 transition-colors">
                <div className="bg-slate-50/90 border-b border-slate-200/80 px-6 py-4 flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="bg-blue-100 text-blue-800 font-mono text-xs sm:text-sm font-bold px-3 py-1 rounded-md border border-blue-200">
                      {termino.includes('/') ? `Exp. ${termino}` : termino}
                    </div>
                    <span className="text-xs sm:text-sm font-semibold text-slate-700">
                      Poder Judicial de Yucatán
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
              <p className="font-semibold text-slate-700 mb-1">Sin acuerdos en la edición consultada</p>
              <p className="text-xs text-slate-400">
                Ninguno de los expedientes registrados bajo tu cuenta apareció publicado en la edición del {scanResult.fecha}.
              </p>
            </div>
          )}
        </div>
      )}

      {!isScanning && !scanResult && !errorMessage && (
        <div className="bg-white border border-slate-200/90 rounded-2xl p-12 text-center flex flex-col items-center justify-center min-h-[380px]">
          <div className="w-20 h-20 bg-slate-50 text-slate-300 rounded-full flex items-center justify-center mb-4 border border-slate-100">
            <FileSearch className="w-10 h-10" />
          </div>
          <h3 className="text-xl font-bold text-slate-400 mb-2">Listo para escanear</h3>
          <p className="text-slate-500 max-w-md text-sm">
            Haz clic en el botón superior para iniciar el cotejo del Diario Oficial del Estado de Yucatán con tus criterios actuales.
          </p>
        </div>
      )}
    </div>
  );
}
