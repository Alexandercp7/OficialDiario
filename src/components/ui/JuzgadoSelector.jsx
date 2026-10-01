import React, { useState, useRef, useEffect, useMemo } from 'react';
import { 
  Building2, 
  Search, 
  ChevronDown, 
  Check, 
  X, 
  Scale, 
  Gavel, 
  MapPin 
} from 'lucide-react';
import { JUZGADOS_LIST } from '../../data/juzgados';

export default function JuzgadoSelector({ 
  value = 'Todos los Juzgados', 
  onChange, 
  className = '',
  placeholder = 'Selecciona el juzgado o tribunal...'
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedMateria, setSelectedMateria] = useState('Todas');
  const [highlightedIndex, setHighlightedIndex] = useState(0);

  const containerRef = useRef(null);
  const searchInputRef = useRef(null);
  const listRef = useRef(null);

  // Normalizar para comparación y búsqueda insensible a acentos
  const normalize = (text) => {
    if (!text) return '';
    return text
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase()
      .trim();
  };

  // Encontrar el juzgado actualmente seleccionado
  const currentSelection = useMemo(() => {
    if (!value || value === 'Todos' || value === 'Todos los Juzgados') {
      return JUZGADOS_LIST[0];
    }
    const valNorm = normalize(value).replace('notificaciones del ', '');
    return JUZGADOS_LIST.find(j => {
      const jNorm = normalize(j.nombre);
      const sNorm = normalize(j.shortName);
      return jNorm === valNorm || jNorm.includes(valNorm) || valNorm.includes(jNorm) || sNorm === valNorm;
    }) || { nombre: value, shortName: value, materia: 'General', sede: 'Yucatán' };
  }, [value]);

  // Lista de materias únicas para las pestañas de filtro rápido
  const materias = ['Todas', 'Mercantil', 'Civil', 'Familiar', 'Mixto', 'Ejecución de Sentencia'];

  // Filtrado de juzgados por texto y materia
  const filteredJuzgados = useMemo(() => {
    const q = normalize(searchQuery);
    return JUZGADOS_LIST.filter(item => {
      // Filtro de materia
      if (selectedMateria !== 'Todas') {
        if (item.id !== 'todos' && item.materia !== selectedMateria) {
          return false;
        }
      }
      // Filtro de texto
      if (!q) return true;
      const matchName = normalize(item.nombre).includes(q);
      const matchLabel = normalize(item.label).includes(q);
      const matchShort = normalize(item.shortName).includes(q);
      const matchSede = normalize(item.sede || '').includes(q);
      const matchMateria = normalize(item.materia || '').includes(q);
      const matchKw = (item.keywords || []).some(k => normalize(k).includes(q));

      return matchName || matchLabel || matchShort || matchSede || matchMateria || matchKw;
    });
  }, [searchQuery, selectedMateria]);

  // Cerrar al hacer clic fuera
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Autofoco al abrir
  useEffect(() => {
    if (isOpen) {
      setHighlightedIndex(0);
      setTimeout(() => {
        if (searchInputRef.current) {
          searchInputRef.current.focus();
        }
      }, 50);
    } else {
      setSearchQuery('');
      setSelectedMateria('Todas');
    }
  }, [isOpen]);

  // Manejo de teclado
  const handleKeyDown = (e) => {
    if (!isOpen) {
      if (e.key === 'Enter' || e.key === 'ArrowDown' || e.key === ' ') {
        e.preventDefault();
        setIsOpen(true);
      }
      return;
    }

    if (e.key === 'Escape') {
      e.preventDefault();
      setIsOpen(false);
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      setHighlightedIndex(prev => (prev + 1) % Math.max(filteredJuzgados.length, 1));
      scrollHighlightedIntoView((highlightedIndex + 1) % filteredJuzgados.length);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setHighlightedIndex(prev => (prev - 1 + filteredJuzgados.length) % Math.max(filteredJuzgados.length, 1));
      scrollHighlightedIntoView((highlightedIndex - 1 + filteredJuzgados.length) % filteredJuzgados.length);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (filteredJuzgados[highlightedIndex]) {
        selectOption(filteredJuzgados[highlightedIndex]);
      }
    }
  };

  const scrollHighlightedIntoView = (index) => {
    if (listRef.current) {
      const items = listRef.current.children;
      if (items && items[index]) {
        items[index].scrollIntoView({ block: 'nearest' });
      }
    }
  };

  const selectOption = (item) => {
    if (onChange) {
      // Si selecciona "todos", guardamos "Todos los Juzgados"
      onChange(item.id === 'todos' ? 'Todos los Juzgados' : item.nombre);
    }
    setIsOpen(false);
  };

  const getMateriaBadgeColor = (materia) => {
    switch (materia) {
      case 'Mercantil':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'Civil':
        return 'bg-amber-100 text-amber-800 border-amber-200';
      case 'Familiar':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'Mixto':
        return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'Ejecución de Sentencia':
        return 'bg-rose-100 text-rose-800 border-rose-200';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  const isAllSelected = !value || value === 'Todos' || value === 'Todos los Juzgados';

  return (
    <div className={`relative ${className}`} ref={containerRef} onKeyDown={handleKeyDown}>
      {/* Botón Selector Principal */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={`w-full flex items-center justify-between gap-2.5 px-3.5 py-2.5 rounded-xl border text-left text-xs sm:text-sm transition-all shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
          isOpen 
            ? 'border-blue-500 bg-white ring-2 ring-blue-500/20' 
            : 'border-slate-300 bg-white hover:bg-slate-50/80 text-slate-800'
        }`}
      >
        <div className="flex items-center gap-2.5 min-w-0 flex-1">
          <div className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 ${
            isAllSelected ? 'bg-slate-100 text-slate-600' : 'bg-blue-100 text-blue-700 font-bold'
          }`}>
            {isAllSelected ? <Scale className="w-4 h-4" /> : <Gavel className="w-4 h-4" />}
          </div>
          
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className="font-semibold text-slate-900 truncate">
                {currentSelection.nombre}
              </span>
              {currentSelection.materia && currentSelection.id !== 'todos' && (
                <span className={`text-[10px] font-bold px-1.5 py-0.2 rounded border shrink-0 ${getMateriaBadgeColor(currentSelection.materia)}`}>
                  {currentSelection.materia}
                </span>
              )}
              {currentSelection.sede && currentSelection.sede !== 'Estatal' && currentSelection.sede !== 'Mérida' && (
                <span className="text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 px-1.5 py-0.2 rounded shrink-0 flex items-center gap-0.5">
                  <MapPin className="w-2.5 h-2.5" />
                  {currentSelection.sede}
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-1 shrink-0 text-slate-400">
          {!isAllSelected && (
            <span
              role="button"
              tabIndex={0}
              onClick={(e) => {
                e.stopPropagation();
                if (onChange) onChange('Todos los Juzgados');
              }}
              title="Restablecer a todos los juzgados"
              className="p-1 hover:text-slate-600 rounded-md hover:bg-slate-100 transition-colors"
            >
              <X className="w-3.5 h-3.5" />
            </span>
          )}
          <ChevronDown className={`w-4 h-4 transition-transform duration-200 ${isOpen ? 'rotate-180 text-blue-600' : ''}`} />
        </div>
      </button>

      {/* Menú Desplegable con Filtro de Búsqueda */}
      {isOpen && (
        <div className="absolute left-0 right-0 top-full mt-1.5 z-50 bg-white rounded-2xl border border-slate-200 shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150 sm:min-w-[420px] max-w-full">
          {/* Cabecera y Barra de Búsqueda en el Desplegable */}
          <div className="p-3 border-b border-slate-100 bg-slate-50/70">
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                ref={searchInputRef}
                type="text"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setHighlightedIndex(0);
                }}
                placeholder="Escribe juzgado, materia o municipio..."
                className="w-full pl-9 pr-8 py-2 text-xs sm:text-sm bg-white rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all shadow-inner"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => setSearchQuery('')}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 p-0.5"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            {/* Pestañas de filtro rápido por materia */}
            <div className="flex items-center gap-1.5 mt-2.5 overflow-x-auto pb-1 scrollbar-none text-[11px]">
              {materias.map(mat => (
                <button
                  key={mat}
                  type="button"
                  onClick={() => {
                    setSelectedMateria(mat);
                    setHighlightedIndex(0);
                  }}
                  className={`px-2.5 py-1 rounded-lg font-semibold shrink-0 transition-all ${
                    selectedMateria === mat
                      ? 'bg-blue-600 text-white shadow-xs'
                      : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-100'
                  }`}
                >
                  {mat}
                </button>
              ))}
            </div>
          </div>

          {/* Lista de Juzgados */}
          <div 
            ref={listRef}
            className="max-h-[300px] overflow-y-auto divide-y divide-slate-100/80 p-1.5 focus:outline-none"
          >
            {filteredJuzgados.map((item, idx) => {
              const isSelected = item.id === 'todos' 
                ? isAllSelected 
                : normalize(item.nombre) === normalize(value) || normalize(item.shortName) === normalize(value);
              const isHighlighted = idx === highlightedIndex;

              return (
                <div
                  key={item.id}
                  onClick={() => selectOption(item)}
                  onMouseEnter={() => setHighlightedIndex(idx)}
                  className={`px-3 py-2.5 rounded-xl cursor-pointer transition-all flex items-center justify-between gap-3 ${
                    isSelected 
                      ? 'bg-blue-50/90 text-blue-950 font-bold' 
                      : isHighlighted 
                        ? 'bg-slate-100/90 text-slate-900' 
                        : 'text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <span className="text-xs sm:text-sm">
                        {item.nombre}
                      </span>
                      {item.materia && item.id !== 'todos' && (
                        <span className={`text-[10px] font-bold px-1.5 py-0.2 rounded border shrink-0 ${getMateriaBadgeColor(item.materia)}`}>
                          {item.materia}
                        </span>
                      )}
                      {item.sede && item.sede !== 'Estatal' && item.sede !== 'Mérida' && (
                        <span className="text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 px-1.5 py-0.2 rounded shrink-0 flex items-center gap-0.5">
                          <MapPin className="w-2.5 h-2.5" />
                          {item.sede}
                        </span>
                      )}
                    </div>
                    {item.shortName && item.shortName !== item.nombre && (
                      <p className="text-[11px] text-slate-400 mt-0.5 font-normal">
                        {item.shortName}
                      </p>
                    )}
                  </div>

                  {isSelected && (
                    <div className="w-5 h-5 rounded-full bg-blue-600 text-white flex items-center justify-center shrink-0">
                      <Check className="w-3 h-3 stroke-[3]" />
                    </div>
                  )}
                </div>
              );
            })}

            {filteredJuzgados.length === 0 && (
              <div className="p-8 text-center text-slate-500">
                <Building2 className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                <p className="text-xs font-semibold text-slate-700">No se encontró ningún juzgado coincidente</p>
                <p className="text-[11px] text-slate-400 mt-1">Prueba con otro término o selecciona "Todas" en materias.</p>
              </div>
            )}
          </div>

          {/* Pie del desplegable */}
          <div className="px-3.5 py-2 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
            <span>{filteredJuzgados.length} juzgado(s) disponible(s)</span>
            <span className="text-slate-400">Poder Judicial de Yucatán</span>
          </div>
        </div>
      )}
    </div>
  );
}
