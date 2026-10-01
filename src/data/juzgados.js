// Catálogo Oficial de Juzgados y Tribunales del Poder Judicial de Yucatán
// Estructurado para búsqueda rápida, filtrado por materia y visualización limpia.

export const JUZGADOS_LIST = [
  {
    id: 'todos',
    nombre: 'Todos los Juzgados',
    label: 'Todos los Juzgados (Cualquier Tribunal)',
    shortName: 'Cualquier Juzgado',
    materia: 'General',
    sede: 'Estatal',
    keywords: ['todos', 'cualquiera', 'general', 'todo']
  },
  {
    id: 'tsj',
    nombre: 'Tribunal Superior de Justicia',
    label: 'NOTIFICACIONES DEL TRIBUNAL SUPERIOR DE JUSTICIA',
    shortName: 'Tribunal Superior de Justicia',
    materia: 'Segunda Instancia',
    sede: 'Mérida',
    keywords: ['tribunal superior', 'tsj', 'salas colegiadas', 'apelaciones', 'tocas']
  },
  {
    id: 'j1m',
    nombre: 'Juzgado Primero Mercantil',
    label: 'NOTIFICACIONES DEL JUZGADO PRIMERO MERCANTIL',
    shortName: 'Juzgado 1° Mercantil',
    materia: 'Mercantil',
    sede: 'Mérida',
    keywords: ['primero mercantil', '1 mercantil', 'ejecutivo mercantil']
  },
  {
    id: 'j2m',
    nombre: 'Juzgado Segundo Mercantil',
    label: 'NOTIFICACIONES DEL JUZGADO SEGUNDO MERCANTIL',
    shortName: 'Juzgado 2° Mercantil',
    materia: 'Mercantil',
    sede: 'Mérida',
    keywords: ['segundo mercantil', '2 mercantil', 'ejecutivo mercantil']
  },
  {
    id: 'j3m',
    nombre: 'Juzgado Tercero Mercantil',
    label: 'NOTIFICACIONES DEL JUZGADO TERCERO MERCANTIL',
    shortName: 'Juzgado 3° Mercantil',
    materia: 'Mercantil',
    sede: 'Mérida',
    keywords: ['tercero mercantil', '3 mercantil', 'ejecutivo mercantil']
  },
  {
    id: 'j4m',
    nombre: 'Juzgado Cuarto Mercantil',
    label: 'NOTIFICACIONES DEL JUZGADO CUARTO MERCANTIL',
    shortName: 'Juzgado 4° Mercantil',
    materia: 'Mercantil',
    sede: 'Mérida',
    keywords: ['cuarto mercantil', '4 mercantil', 'ejecutivo mercantil']
  },
  {
    id: 'j1om',
    nombre: 'Juzgado Primero de Oralidad Mercantil',
    label: 'NOTIFICACIONES DEL JUZGADO PRIMERO DE ORALIDAD MERCANTIL',
    shortName: 'Juzgado 1° Oralidad Mercantil',
    materia: 'Mercantil',
    sede: 'Mérida',
    keywords: ['oralidad mercantil', '1 oralidad mercantil', 'primero oralidad']
  },
  {
    id: 'j1c',
    nombre: 'Juzgado Primero Civil',
    label: 'NOTIFICACIONES DEL JUZGADO PRIMERO CIVIL',
    shortName: 'Juzgado 1° Civil',
    materia: 'Civil',
    sede: 'Mérida',
    keywords: ['primero civil', '1 civil', 'ordinario civil']
  },
  {
    id: 'j2c',
    nombre: 'Juzgado Segundo Civil',
    label: 'NOTIFICACIONES DEL JUZGADO SEGUNDO CIVIL',
    shortName: 'Juzgado 2° Civil',
    materia: 'Civil',
    sede: 'Mérida',
    keywords: ['segundo civil', '2 civil', 'hipotecario']
  },
  {
    id: 'j3c',
    nombre: 'Juzgado Tercero Civil',
    label: 'NOTIFICACIONES DEL JUZGADO TERCERO CIVIL',
    shortName: 'Juzgado 3° Civil',
    materia: 'Civil',
    sede: 'Mérida',
    keywords: ['tercero civil', '3 civil']
  },
  {
    id: 'j4c',
    nombre: 'Juzgado Cuarto Civil',
    label: 'NOTIFICACIONES DEL JUZGADO CUARTO CIVIL',
    shortName: 'Juzgado 4° Civil',
    materia: 'Civil',
    sede: 'Mérida',
    keywords: ['cuarto civil', '4 civil']
  },
  {
    id: 'j5c',
    nombre: 'Juzgado Quinto Civil',
    label: 'NOTIFICACIONES DEL JUZGADO QUINTO CIVIL',
    shortName: 'Juzgado 5° Civil',
    materia: 'Civil',
    sede: 'Mérida',
    keywords: ['quinto civil', '5 civil']
  },
  {
    id: 'j1f',
    nombre: 'Juzgado Primero de lo Familiar',
    label: 'NOTIFICACIONES DEL JUZGADO PRIMERO DE LO FAMILIAR',
    shortName: 'Juzgado 1° de lo Familiar',
    materia: 'Familiar',
    sede: 'Mérida',
    keywords: ['primero familiar', '1 familiar', 'tradicional familiar']
  },
  {
    id: 'j1of',
    nombre: 'Juzgado Primero de Oralidad Familiar',
    label: 'NOTIFICACIONES DEL JUZGADO PRIMERO DE ORALIDAD FAMILIAR',
    shortName: 'Juzgado 1° Oralidad Familiar',
    materia: 'Familiar',
    sede: 'Mérida',
    keywords: ['1 oralidad familiar', 'primero oralidad familiar']
  },
  {
    id: 'j2of',
    nombre: 'Juzgado Segundo de Oralidad Familiar',
    label: 'NOTIFICACIONES DEL JUZGADO SEGUNDO DE ORALIDAD FAMILIAR',
    shortName: 'Juzgado 2° Oralidad Familiar',
    materia: 'Familiar',
    sede: 'Mérida',
    keywords: ['2 oralidad familiar', 'segundo oralidad familiar']
  },
  {
    id: 'j3of',
    nombre: 'Juzgado Tercero de Oralidad Familiar',
    label: 'NOTIFICACIONES DEL JUZGADO TERCERO DE ORALIDAD FAMILIAR',
    shortName: 'Juzgado 3° Oralidad Familiar',
    materia: 'Familiar',
    sede: 'Mérida',
    keywords: ['3 oralidad familiar', 'tercero oralidad familiar']
  },
  {
    id: 'j4of',
    nombre: 'Juzgado Cuarto de Oralidad Familiar',
    label: 'NOTIFICACIONES DEL JUZGADO CUARTO DE ORALIDAD FAMILIAR',
    shortName: 'Juzgado 4° Oralidad Familiar',
    materia: 'Familiar',
    sede: 'Mérida',
    keywords: ['4 oralidad familiar', 'cuarto oralidad familiar']
  },
  {
    id: 'j5of',
    nombre: 'Juzgado Quinto de Oralidad Familiar',
    label: 'NOTIFICACIONES DEL JUZGADO QUINTO DE ORALIDAD FAMILIAR',
    shortName: 'Juzgado 5° Oralidad Familiar',
    materia: 'Familiar',
    sede: 'Mérida',
    keywords: ['5 oralidad familiar', 'quinto oralidad familiar']
  },
  {
    id: 'j6of',
    nombre: 'Juzgado Sexto en Materia de Oralidad Familiar',
    label: 'NOTIFICACIONES DEL JUZGADO SEXTO EN MATERIA DE ORALIDAD FAMILIAR',
    shortName: 'Juzgado 6° Oralidad Familiar',
    materia: 'Familiar',
    sede: 'Mérida',
    keywords: ['6 oralidad familiar', 'sexto oralidad familiar', 'sexto materia oralidad familiar']
  },
  {
    id: 'j7of',
    nombre: 'Juzgado Séptimo de Oralidad Familiar',
    label: 'NOTIFICACIONES DEL JUZGADO SÉPTIMO DE ORALIDAD FAMILIAR',
    shortName: 'Juzgado 7° Oralidad Familiar',
    materia: 'Familiar',
    sede: 'Mérida',
    keywords: ['7 oralidad familiar', 'septimo oralidad familiar']
  },
  {
    id: 'j8of',
    nombre: 'Juzgado Octavo de Oralidad Familiar',
    label: 'NOTIFICACIONES DEL JUZGADO OCTAVO DE ORALIDAD FAMILIAR',
    shortName: 'Juzgado 8° Oralidad Familiar',
    materia: 'Familiar',
    sede: 'Mérida',
    keywords: ['8 oralidad familiar', 'octavo oralidad familiar']
  },
  {
    id: 'j9of',
    nombre: 'Juzgado Noveno de Oralidad Familiar',
    label: 'NOTIFICACIONES DEL JUZGADO NOVENO DE ORALIDAD FAMILIAR',
    shortName: 'Juzgado 9° Oralidad Familiar',
    materia: 'Familiar',
    sede: 'Mérida',
    keywords: ['9 oralidad familiar', 'noveno oralidad familiar']
  },
  {
    id: 'j10of',
    nombre: 'Juzgado Décimo de Oralidad Familiar',
    label: 'NOTIFICACIONES DEL JUZGADO DÉCIMO DE ORALIDAD FAMILIAR',
    shortName: 'Juzgado 10° Oralidad Familiar',
    materia: 'Familiar',
    sede: 'Mérida',
    keywords: ['10 oralidad familiar', 'decimo oralidad familiar']
  },
  {
    id: 'j11of',
    nombre: 'Juzgado Décimoprimero de Oralidad Familiar',
    label: 'NOTIFICACIONES DEL JUZGADO DÉCIMOPRIMERO DE ORALIDAD FAMILIAR',
    shortName: 'Juzgado 11° Oralidad Familiar',
    materia: 'Familiar',
    sede: 'Mérida',
    keywords: ['11 oralidad familiar', 'decimoprimero oralidad familiar', 'once familiar']
  },
  {
    id: 'j12of',
    nombre: 'Juzgado Décimosegundo de Oralidad Familiar',
    label: 'NOTIFICACIONES DEL JUZGADO DÉCIMOSEGUNDO DE ORALIDAD FAMILIAR',
    shortName: 'Juzgado 12° Oralidad Familiar',
    materia: 'Familiar',
    sede: 'Mérida',
    keywords: ['12 oralidad familiar', 'decimosegundo oralidad familiar', 'doce familiar']
  },
  {
    id: 'j13of',
    nombre: 'Juzgado Décimotercero de Oralidad Familiar',
    label: 'NOTIFICACIONES DEL JUZGADO DÉCIMOTERCERO DE ORALIDAD FAMILIAR',
    shortName: 'Juzgado 13° Oralidad Familiar',
    materia: 'Familiar',
    sede: 'Mérida',
    keywords: ['13 oralidad familiar', 'decimotercero oralidad familiar', 'trece familiar']
  },
  {
    id: 'j1es',
    nombre: 'Juzgado Primero de Ejecución de Sentencia del Estado',
    label: 'NOTIFICACIONES DEL JUZGADO PRIMERO DE EJECUCIÓN DE SENTENCIA DEL ESTADO',
    shortName: 'Juzgado 1° Ejecución de Sentencia',
    materia: 'Ejecución de Sentencia',
    sede: 'Mérida',
    keywords: ['primero ejecucion', '1 ejecucion', 'sentencia penal']
  },
  {
    id: 'j2es',
    nombre: 'Juzgado Segundo de Ejecución de Sentencia del Estado',
    label: 'NOTIFICACIONES DEL JUZGADO SEGUNDO DE EJECUCIÓN DE SENTENCIA DEL ESTADO',
    shortName: 'Juzgado 2° Ejecución de Sentencia',
    materia: 'Ejecución de Sentencia',
    sede: 'Mérida',
    keywords: ['segundo ejecucion', '2 ejecucion', 'sentencia penal']
  },
  {
    id: 'j1mxt1',
    nombre: 'Juzgado Primero Mixto de lo Civil, Familiar y Mercantil del Primer Departamento Judicial del Estado',
    label: 'NOTIFICACIONES DEL JUZGADO PRIMERO MIXTO DE LO CIVIL, FAMILIAR Y MERCANTIL DEL PRIMER DEPARTAMENTO JUDICIAL DEL ESTADO',
    shortName: 'Juzgado 1° Mixto (Progreso)',
    materia: 'Mixto',
    sede: 'Progreso',
    keywords: ['progreso', 'primero mixto progreso', '1 mixto primer departamento']
  },
  {
    id: 'j2mxt1',
    nombre: 'Juzgado Segundo Mixto de lo Civil y Mercantil del Primer Departamento Judicial del Estado',
    label: 'NOTIFICACIONES DEL JUZGADO SEGUNDO MIXTO DE LO CIVIL Y MERCANTIL DEL PRIMER DEPARTAMENTO JUDICIAL DEL ESTADO',
    shortName: 'Juzgado 2° Mixto (Umán)',
    materia: 'Mixto',
    sede: 'Umán',
    keywords: ['uman', 'segundo mixto uman', '2 mixto primer departamento']
  },
  {
    id: 'j3mxt1',
    nombre: 'Juzgado Tercero Mixto de lo Civil, Familiar y Mercantil del Primer Departamento Judicial del Estado',
    label: 'NOTIFICACIONES DEL JUZGADO TERCERO MIXTO DE LO CIVIL, FAMILIAR Y MERCANTIL DEL PRIMER DEPARTAMENTO JUDICIAL DEL ESTADO',
    shortName: 'Juzgado 3° Mixto (Motul)',
    materia: 'Mixto',
    sede: 'Motul',
    keywords: ['motul', 'tercero mixto motul', '3 mixto primer departamento']
  },
  {
    id: 'j4mxt1',
    nombre: 'Juzgado Cuarto Mixto de lo Civil y Mercantil del Primer Departamento Judicial del Estado',
    label: 'NOTIFICACIONES DEL JUZGADO CUARTO MIXTO DE LO CIVIL Y MERCANTIL DEL PRIMER DEPARTAMENTO JUDICIAL DEL ESTADO',
    shortName: 'Juzgado 4° Mixto (Kanasín)',
    materia: 'Mixto',
    sede: 'Kanasín',
    keywords: ['kanasin', 'cuarto mixto kanasin', '4 mixto primer departamento']
  },
  {
    id: 'j5mxt1',
    nombre: 'Juzgado Quinto Mixto de lo Civil, Familiar y Mercantil del Primer Departamento Judicial del Estado',
    label: 'NOTIFICACIONES DEL JUZGADO QUINTO MIXTO DE LO CIVIL, FAMILIAR Y MERCANTIL DEL PRIMER DEPARTAMENTO JUDICIAL DEL ESTADO',
    shortName: 'Juzgado 5° Mixto (Izamal)',
    materia: 'Mixto',
    sede: 'Izamal',
    keywords: ['izamal', 'quinto mixto izamal', '5 mixto primer departamento']
  },
  {
    id: 'j1feo1',
    nombre: 'Juzgado Primero Familiar de Procedimientos Escritos y Orales del Primer Departamento Judicial del Estado',
    label: 'NOTIFICACIONES DEL JUZGADO PRIMERO FAMILIAR DE PROCEDIMIENTOS ESCRITOS Y ORALES DEL PRIMER DEPARTAMENTO JUDICIAL DEL ESTADO',
    shortName: 'Juzgado 1° Familiar Escrito y Oral (Umán)',
    materia: 'Familiar',
    sede: 'Umán',
    keywords: ['uman familiar', 'procedimientos escritos y orales uman', 'primero familiar uman']
  },
  {
    id: 'j2feo1',
    nombre: 'Juzgado Segundo Familiar de Procedimientos Escritos y Orales del Primer Departamento Judicial del Estado',
    label: 'NOTIFICACIONES DEL JUZGADO SEGUNDO FAMILIAR DE PROCEDIMIENTOS ESCRITOS Y ORALES DEL PRIMER DEPARTAMENTO JUDICIAL DEL ESTADO',
    shortName: 'Juzgado 2° Familiar Escrito y Oral (Kanasín)',
    materia: 'Familiar',
    sede: 'Kanasín',
    keywords: ['kanasin familiar', 'procedimientos escritos y orales kanasin', 'segundo familiar kanasin']
  },
  {
    id: 'j1mxt2',
    nombre: 'Juzgado Primero Mixto de lo Civil, Familiar y Mercantil del Segundo Departamento Judicial del Estado',
    label: 'NOTIFICACIONES DEL JUZGADO PRIMERO MIXTO DE LO CIVIL, FAMILIAR Y MERCANTIL DEL SEGUNDO DEPARTAMENTO JUDICIAL DEL ESTADO',
    shortName: 'Juzgado 1° Mixto (Tekax)',
    materia: 'Mixto',
    sede: 'Tekax',
    keywords: ['tekax', 'primero mixto tekax', 'segundo departamento tekax']
  },
  {
    id: 'j2mxt2',
    nombre: 'Juzgado Segundo Mixto de lo Civil, Familiar y Mercantil del Segundo Departamento Judicial del Estado',
    label: 'NOTIFICACIONES DEL JUZGADO SEGUNDO MIXTO DE LO CIVIL, FAMILIAR Y MERCANTIL DEL SEGUNDO DEPARTAMENTO JUDICIAL DEL ESTADO',
    shortName: 'Juzgado 2° Mixto (Ticul)',
    materia: 'Mixto',
    sede: 'Ticul',
    keywords: ['ticul', 'segundo mixto ticul', 'segundo departamento ticul']
  },
  {
    id: 'j1mxt3',
    nombre: 'Juzgado Primero Mixto de lo Civil, Familiar y Mercantil del Tercer Departamento Judicial del Estado',
    label: 'NOTIFICACIONES DEL JUZGADO PRIMERO MIXTO DE LO CIVIL, FAMILIAR Y MERCANTIL DEL TERCER DEPARTAMENTO JUDICIAL DEL ESTADO',
    shortName: 'Juzgado 1° Mixto (Valladolid)',
    materia: 'Mixto',
    sede: 'Valladolid',
    keywords: ['valladolid', 'primero mixto valladolid', 'tercer departamento valladolid']
  },
  {
    id: 'j2mxt3',
    nombre: 'Juzgado Segundo Mixto de lo Civil, Familiar y Mercantil del Tercer Departamento Judicial del Estado',
    label: 'NOTIFICACIONES DEL JUZGADO SEGUNDO MIXTO DE LO CIVIL, FAMILIAR Y MERCANTIL DEL TERCER DEPARTAMENTO JUDICIAL DEL ESTADO',
    shortName: 'Juzgado 2° Mixto (Tizimín)',
    materia: 'Mixto',
    sede: 'Tizimín',
    keywords: ['tizimin', 'segundo mixto tizimin', 'tercer departamento tizimin']
  }
];

export function getJuzgadoShortName(juzgadoName) {
  if (!juzgadoName || juzgadoName === 'Todos' || juzgadoName === 'Todos los Juzgados') {
    return 'Cualquier Juzgado';
  }
  const clean = juzgadoName.toLowerCase().replace('notificaciones del ', '').trim();
  const found = JUZGADOS_LIST.find(j => 
    j.nombre.toLowerCase().includes(clean) || 
    clean.includes(j.nombre.toLowerCase()) ||
    j.shortName.toLowerCase().includes(clean)
  );
  return found ? found.shortName : juzgadoName;
}
