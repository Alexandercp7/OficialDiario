import re
import unicodedata

LISTA_JUZGADOS_YUCATAN = [
    {"id": "todos", "nombre": "Todos los Juzgados", "label": "Todos los Juzgados (Cualquier Tribunal)", "shortName": "Cualquier Juzgado", "materia": "General", "sede": "Estatal"},
    {"id": "tsj", "nombre": "Tribunal Superior de Justicia", "label": "NOTIFICACIONES DEL TRIBUNAL SUPERIOR DE JUSTICIA", "shortName": "Tribunal Superior de Justicia", "materia": "Segunda Instancia", "sede": "Mérida"},
    {"id": "j1m", "nombre": "Juzgado Primero Mercantil", "label": "NOTIFICACIONES DEL JUZGADO PRIMERO MERCANTIL", "shortName": "Juzgado 1° Mercantil", "materia": "Mercantil", "sede": "Mérida"},
    {"id": "j2m", "nombre": "Juzgado Segundo Mercantil", "label": "NOTIFICACIONES DEL JUZGADO SEGUNDO MERCANTIL", "shortName": "Juzgado 2° Mercantil", "materia": "Mercantil", "sede": "Mérida"},
    {"id": "j3m", "nombre": "Juzgado Tercero Mercantil", "label": "NOTIFICACIONES DEL JUZGADO TERCERO MERCANTIL", "shortName": "Juzgado 3° Mercantil", "materia": "Mercantil", "sede": "Mérida"},
    {"id": "j4m", "nombre": "Juzgado Cuarto Mercantil", "label": "NOTIFICACIONES DEL JUZGADO CUARTO MERCANTIL", "shortName": "Juzgado 4° Mercantil", "materia": "Mercantil", "sede": "Mérida"},
    {"id": "j1om", "nombre": "Juzgado Primero de Oralidad Mercantil", "label": "NOTIFICACIONES DEL JUZGADO PRIMERO DE ORALIDAD MERCANTIL", "shortName": "Juzgado 1° Oralidad Mercantil", "materia": "Mercantil", "sede": "Mérida"},
    {"id": "j1c", "nombre": "Juzgado Primero Civil", "label": "NOTIFICACIONES DEL JUZGADO PRIMERO CIVIL", "shortName": "Juzgado 1° Civil", "materia": "Civil", "sede": "Mérida"},
    {"id": "j2c", "nombre": "Juzgado Segundo Civil", "label": "NOTIFICACIONES DEL JUZGADO SEGUNDO CIVIL", "shortName": "Juzgado 2° Civil", "materia": "Civil", "sede": "Mérida"},
    {"id": "j3c", "nombre": "Juzgado Tercero Civil", "label": "NOTIFICACIONES DEL JUZGADO TERCERO CIVIL", "shortName": "Juzgado 3° Civil", "materia": "Civil", "sede": "Mérida"},
    {"id": "j4c", "nombre": "Juzgado Cuarto Civil", "label": "NOTIFICACIONES DEL JUZGADO CUARTO CIVIL", "shortName": "Juzgado 4° Civil", "materia": "Civil", "sede": "Mérida"},
    {"id": "j5c", "nombre": "Juzgado Quinto Civil", "label": "NOTIFICACIONES DEL JUZGADO QUINTO CIVIL", "shortName": "Juzgado 5° Civil", "materia": "Civil", "sede": "Mérida"},
    {"id": "j1f", "nombre": "Juzgado Primero de lo Familiar", "label": "NOTIFICACIONES DEL JUZGADO PRIMERO DE LO FAMILIAR", "shortName": "Juzgado 1° de lo Familiar", "materia": "Familiar", "sede": "Mérida"},
    {"id": "j1of", "nombre": "Juzgado Primero de Oralidad Familiar", "label": "NOTIFICACIONES DEL JUZGADO PRIMERO DE ORALIDAD FAMILIAR", "shortName": "Juzgado 1° Oralidad Familiar", "materia": "Familiar", "sede": "Mérida"},
    {"id": "j2of", "nombre": "Juzgado Segundo de Oralidad Familiar", "label": "NOTIFICACIONES DEL JUZGADO SEGUNDO DE ORALIDAD FAMILIAR", "shortName": "Juzgado 2° Oralidad Familiar", "materia": "Familiar", "sede": "Mérida"},
    {"id": "j3of", "nombre": "Juzgado Tercero de Oralidad Familiar", "label": "NOTIFICACIONES DEL JUZGADO TERCERO DE ORALIDAD FAMILIAR", "shortName": "Juzgado 3° Oralidad Familiar", "materia": "Familiar", "sede": "Mérida"},
    {"id": "j4of", "nombre": "Juzgado Cuarto de Oralidad Familiar", "label": "NOTIFICACIONES DEL JUZGADO CUARTO DE ORALIDAD FAMILIAR", "shortName": "Juzgado 4° Oralidad Familiar", "materia": "Familiar", "sede": "Mérida"},
    {"id": "j5of", "nombre": "Juzgado Quinto de Oralidad Familiar", "label": "NOTIFICACIONES DEL JUZGADO QUINTO DE ORALIDAD FAMILIAR", "shortName": "Juzgado 5° Oralidad Familiar", "materia": "Familiar", "sede": "Mérida"},
    {"id": "j6of", "nombre": "Juzgado Sexto en Materia de Oralidad Familiar", "label": "NOTIFICACIONES DEL JUZGADO SEXTO EN MATERIA DE ORALIDAD FAMILIAR", "shortName": "Juzgado 6° Oralidad Familiar", "materia": "Familiar", "sede": "Mérida"},
    {"id": "j7of", "nombre": "Juzgado Séptimo de Oralidad Familiar", "label": "NOTIFICACIONES DEL JUZGADO SÉPTIMO DE ORALIDAD FAMILIAR", "shortName": "Juzgado 7° Oralidad Familiar", "materia": "Familiar", "sede": "Mérida"},
    {"id": "j8of", "nombre": "Juzgado Octavo de Oralidad Familiar", "label": "NOTIFICACIONES DEL JUZGADO OCTAVO DE ORALIDAD FAMILIAR", "shortName": "Juzgado 8° Oralidad Familiar", "materia": "Familiar", "sede": "Mérida"},
    {"id": "j9of", "nombre": "Juzgado Noveno de Oralidad Familiar", "label": "NOTIFICACIONES DEL JUZGADO NOVENO DE ORALIDAD FAMILIAR", "shortName": "Juzgado 9° Oralidad Familiar", "materia": "Familiar", "sede": "Mérida"},
    {"id": "j10of", "nombre": "Juzgado Décimo de Oralidad Familiar", "label": "NOTIFICACIONES DEL JUZGADO DÉCIMO DE ORALIDAD FAMILIAR", "shortName": "Juzgado 10° Oralidad Familiar", "materia": "Familiar", "sede": "Mérida"},
    {"id": "j11of", "nombre": "Juzgado Décimoprimero de Oralidad Familiar", "label": "NOTIFICACIONES DEL JUZGADO DÉCIMOPRIMERO DE ORALIDAD FAMILIAR", "shortName": "Juzgado 11° Oralidad Familiar", "materia": "Familiar", "sede": "Mérida"},
    {"id": "j12of", "nombre": "Juzgado Décimosegundo de Oralidad Familiar", "label": "NOTIFICACIONES DEL JUZGADO DÉCIMOSEGUNDO DE ORALIDAD FAMILIAR", "shortName": "Juzgado 12° Oralidad Familiar", "materia": "Familiar", "sede": "Mérida"},
    {"id": "j13of", "nombre": "Juzgado Décimotercero de Oralidad Familiar", "label": "NOTIFICACIONES DEL JUZGADO DÉCIMOTERCERO DE ORALIDAD FAMILIAR", "shortName": "Juzgado 13° Oralidad Familiar", "materia": "Familiar", "sede": "Mérida"},
    {"id": "j1es", "nombre": "Juzgado Primero de Ejecución de Sentencia del Estado", "label": "NOTIFICACIONES DEL JUZGADO PRIMERO DE EJECUCIÓN DE SENTENCIA DEL ESTADO", "shortName": "Juzgado 1° Ejecución de Sentencia", "materia": "Ejecución de Sentencia", "sede": "Mérida"},
    {"id": "j2es", "nombre": "Juzgado Segundo de Ejecución de Sentencia del Estado", "label": "NOTIFICACIONES DEL JUZGADO SEGUNDO DE EJECUCIÓN DE SENTENCIA DEL ESTADO", "shortName": "Juzgado 2° Ejecución de Sentencia", "materia": "Ejecución de Sentencia", "sede": "Mérida"},
    {"id": "j1mxt1", "nombre": "Juzgado Primero Mixto de lo Civil, Familiar y Mercantil del Primer Departamento Judicial del Estado", "label": "NOTIFICACIONES DEL JUZGADO PRIMERO MIXTO DE LO CIVIL, FAMILIAR Y MERCANTIL DEL PRIMER DEPARTAMENTO JUDICIAL DEL ESTADO", "shortName": "Juzgado 1° Mixto (Progreso)", "materia": "Mixto", "sede": "Progreso"},
    {"id": "j2mxt1", "nombre": "Juzgado Segundo Mixto de lo Civil y Mercantil del Primer Departamento Judicial del Estado", "label": "NOTIFICACIONES DEL JUZGADO SEGUNDO MIXTO DE LO CIVIL Y MERCANTIL DEL PRIMER DEPARTAMENTO JUDICIAL DEL ESTADO", "shortName": "Juzgado 2° Mixto (Umán)", "materia": "Mixto", "sede": "Umán"},
    {"id": "j3mxt1", "nombre": "Juzgado Tercero Mixto de lo Civil, Familiar y Mercantil del Primer Departamento Judicial del Estado", "label": "NOTIFICACIONES DEL JUZGADO TERCERO MIXTO DE LO CIVIL, FAMILIAR Y MERCANTIL DEL PRIMER DEPARTAMENTO JUDICIAL DEL ESTADO", "shortName": "Juzgado 3° Mixto (Motul)", "materia": "Mixto", "sede": "Motul"},
    {"id": "j4mxt1", "nombre": "Juzgado Cuarto Mixto de lo Civil y Mercantil del Primer Departamento Judicial del Estado", "label": "NOTIFICACIONES DEL JUZGADO CUARTO MIXTO DE LO CIVIL Y MERCANTIL DEL PRIMER DEPARTAMENTO JUDICIAL DEL ESTADO", "shortName": "Juzgado 4° Mixto (Kanasín)", "materia": "Mixto", "sede": "Kanasín"},
    {"id": "j5mxt1", "nombre": "Juzgado Quinto Mixto de lo Civil, Familiar y Mercantil del Primer Departamento Judicial del Estado", "label": "NOTIFICACIONES DEL JUZGADO QUINTO MIXTO DE LO CIVIL, FAMILIAR Y MERCANTIL DEL PRIMER DEPARTAMENTO JUDICIAL DEL ESTADO", "shortName": "Juzgado 5° Mixto (Izamal)", "materia": "Mixto", "sede": "Izamal"},
    {"id": "j1feo1", "nombre": "Juzgado Primero Familiar de Procedimientos Escritos y Orales del Primer Departamento Judicial del Estado", "label": "NOTIFICACIONES DEL JUZGADO PRIMERO FAMILIAR DE PROCEDIMIENTOS ESCRITOS Y ORALES DEL PRIMER DEPARTAMENTO JUDICIAL DEL ESTADO", "shortName": "Juzgado 1° Familiar Escrito y Oral (Umán)", "materia": "Familiar", "sede": "Umán"},
    {"id": "j2feo1", "nombre": "Juzgado Segundo Familiar de Procedimientos Escritos y Orales del Primer Departamento Judicial del Estado", "label": "NOTIFICACIONES DEL JUZGADO SEGUNDO FAMILIAR DE PROCEDIMIENTOS ESCRITOS Y ORALES DEL PRIMER DEPARTAMENTO JUDICIAL DEL ESTADO", "shortName": "Juzgado 2° Familiar Escrito y Oral (Kanasín)", "materia": "Familiar", "sede": "Kanasín"},
    {"id": "j1mxt2", "nombre": "Juzgado Primero Mixto de lo Civil, Familiar y Mercantil del Segundo Departamento Judicial del Estado", "label": "NOTIFICACIONES DEL JUZGADO PRIMERO MIXTO DE LO CIVIL, FAMILIAR Y MERCANTIL DEL SEGUNDO DEPARTAMENTO JUDICIAL DEL ESTADO", "shortName": "Juzgado 1° Mixto (Tekax)", "materia": "Mixto", "sede": "Tekax"},
    {"id": "j2mxt2", "nombre": "Juzgado Segundo Mixto de lo Civil, Familiar y Mercantil del Segundo Departamento Judicial del Estado", "label": "NOTIFICACIONES DEL JUZGADO SEGUNDO MIXTO DE LO CIVIL, FAMILIAR Y MERCANTIL DEL SEGUNDO DEPARTAMENTO JUDICIAL DEL ESTADO", "shortName": "Juzgado 2° Mixto (Ticul)", "materia": "Mixto", "sede": "Ticul"},
    {"id": "j1mxt3", "nombre": "Juzgado Primero Mixto de lo Civil, Familiar y Mercantil del Tercer Departamento Judicial del Estado", "label": "NOTIFICACIONES DEL JUZGADO PRIMERO MIXTO DE LO CIVIL, FAMILIAR Y MERCANTIL DEL TERCER DEPARTAMENTO JUDICIAL DEL ESTADO", "shortName": "Juzgado 1° Mixto (Valladolid)", "materia": "Mixto", "sede": "Valladolid"},
    {"id": "j2mxt3", "nombre": "Juzgado Segundo Mixto de lo Civil, Familiar y Mercantil del Tercer Departamento Judicial del Estado", "label": "NOTIFICACIONES DEL JUZGADO SEGUNDO MIXTO DE LO CIVIL, FAMILIAR Y MERCANTIL DEL TERCER DEPARTAMENTO JUDICIAL DEL ESTADO", "shortName": "Juzgado 2° Mixto (Tizimín)", "materia": "Mixto", "sede": "Tizimín"},
]

def normalize_court_name(name):
    """
    Normaliza el nombre de un juzgado eliminando acentos, caracteres especiales
    y prefijos como 'NOTIFICACIONES DE'.
    """
    if not name:
        return ""
    n = unicodedata.normalize('NFKD', str(name))
    n = ''.join(c for c in n if not unicodedata.combining(c))
    n = re.sub(r'[^a-zA-Z0-9\s]', ' ', n).upper()
    n = re.sub(r'\bNOTIFICACIONES\s+DEL?\s+', '', n)
    return ' '.join(n.split())

def court_matches(current_court, target_court):
    """
    Verifica si un juzgado detectado coincide con el juzgado objetivo de búsqueda/criterio.
    Si el objetivo es 'Todos' o 'Cualquier Juzgado', coincide siempre.
    """
    if not target_court or target_court in ("Todos", "Todos los Juzgados", "Cualquier Juzgado"):
        return True
    if not current_court:
        return False
    c_norm = normalize_court_name(current_court)
    t_norm = normalize_court_name(target_court)
    if not t_norm or not c_norm:
        return True
    return (t_norm in c_norm) or (c_norm in t_norm) or (t_norm[:20] == c_norm[:20])
