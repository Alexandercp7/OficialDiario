import os
import re
import requests
import pymupdf
from backend.juzgados import LISTA_JUZGADOS_YUCATAN, normalize_court_name, court_matches

def descargar_diario(fecha, ruta_destino):
    """
    Descarga el PDF del Diario Oficial de Yucatán.
    Formato fecha: YYYY-MM-DD
    """
    año = fecha.split("-")[0]
    url = f"https://www.yucatan.gob.mx/docs/diario_oficial/diarios/{año}/{fecha}_1.pdf"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        if response.status_code == 200:
            with open(ruta_destino, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True, "Descargado con éxito"
        elif response.status_code == 404:
            return False, "La edición del diario para esta fecha aún no está publicada o no existe (Error 404)."
        else:
            return False, f"Servidor respondió con código HTTP {response.status_code}"
    except Exception as e:
        return False, f"Error de conexión: {str(e)}"

def build_pdf_court_map(doc):
    """
    Lee las páginas del sumario (índice del Diario Oficial) y construye el mapa
    de inicio de cada juzgado o tribunal y el final de la sección judicial.
    """
    sumario_text = ''
    for pno in range(1, min(6, len(doc))):
        sumario_text += doc[pno].get_text('text') + '\n'

    pj_match = re.search(r'PODER\s+JUDICIAL\s*(.*?)\s*(?:GOBIERNO\s+MUNICIPAL|PODER\s+LEGISLATIVO|$)', sumario_text, re.S | re.I)
    court_list = []
    if pj_match:
        entries = re.findall(r'NOTIFICACIONES\s+(?:DEL?\s+)?(.+?)\s*\.{3,}\s*(\d+)', pj_match.group(1), re.S)
        for name, page_str in entries:
            clean_name = ' '.join(name.split())
            court_list.append({
                'nombre': clean_name,
                'norm': normalize_court_name(clean_name),
                'short_norm': normalize_court_name(clean_name).replace('JUZGADO ', ''),
                'page': int(page_str)
            })

    if not court_list:
        for item in LISTA_JUZGADOS_YUCATAN[1:]:
            court_list.append({
                'nombre': item['nombre'],
                'norm': normalize_court_name(item['nombre']),
                'short_norm': normalize_court_name(item['nombre']).replace('JUZGADO ', ''),
                'page': 6
            })

    end_pj_page = len(doc)
    gm_match = re.search(r'GOBIERNO\s+MUNICIPAL\s*.*?\.{3,}\s*(\d+)', sumario_text, re.S | re.I)
    if gm_match:
        end_pj_page = int(gm_match.group(1))

    return court_list, end_pj_page

def get_block_court(doc, pno, block_idx, courts, end_page):
    """
    Determina con exactitud a qué juzgado o tribunal pertenece un bloque de texto en una página dada.
    """
    page_num = pno + 1
    if not courts or page_num < courts[0]['page'] or page_num >= end_page:
        return None

    active = [c for c in courts if c['page'] <= page_num]
    if not active:
        return None

    courts_on_this_page = [c for c in courts if c['page'] == page_num]
    if not courts_on_this_page:
        return active[-1]['nombre']

    blocks = doc[pno].get_text('blocks')
    court_block_indices = []
    for c in courts_on_this_page:
        for i, b in enumerate(blocks):
            bn = normalize_court_name(b[4])
            if c['norm'][:20] in bn or c['short_norm'][:20] in bn:
                court_block_indices.append((i, c['nombre']))
                break
    court_block_indices.sort(key=lambda x: x[0])

    if not court_block_indices:
        return active[-1]['nombre']

    # Si el bloque está antes del primer encabezado de juzgado en esta página
    if block_idx < court_block_indices[0][0]:
        idx_prev = len(active) - len(courts_on_this_page) - 1
        return active[idx_prev]['nombre'] if idx_prev >= 0 else court_block_indices[0][1]

    curr = court_block_indices[0][1]
    for idx_header, cname in court_block_indices:
        if block_idx >= idx_header:
            curr = cname
    return curr

def buscar_terminos_en_pdf(ruta_pdf, criteria_or_keywords):
    """
    Busca términos o expedientes en los párrafos/bloques del PDF, diferenciando
    con total precisión el juzgado o tribunal correspondiente.
    Soporta lista de strings o lista de dicts de criterios (con 'valor' y 'juzgado').
    """
    coincidencias = []
    if not os.path.exists(ruta_pdf):
        return coincidencias

    try:
        documento = pymupdf.open(ruta_pdf)
        courts, end_page = build_pdf_court_map(documento)

        parsed_criteria = []
        for item in criteria_or_keywords:
            if isinstance(item, str):
                val = item.strip()
                tgt = "Todos"
            elif isinstance(item, dict):
                val = str(item.get("valor", "")).strip()
                tgt = str(item.get("juzgado", "Todos") or "Todos").strip()
            else:
                continue

            if not val:
                continue

            # Detectar si es número de expediente (ej. 69/2026, 00093/2025)
            m_exp = re.match(r'^0*(\d+)/(\d{4})$', val)
            if m_exp:
                exp_regex = re.compile(rf'(?<!\d)0*{int(m_exp.group(1))}/{m_exp.group(2)}(?!\d)', re.I)
            else:
                exp_regex = None

            parsed_criteria.append({
                "valor": val,
                "target_juzgado": tgt,
                "exp_regex": exp_regex
            })

        for num_pag in range(len(documento)):
            page_num = num_pag + 1
            if courts and (page_num < courts[0]["page"] or page_num >= end_page):
                continue

            pagina = documento.load_page(num_pag)
            bloques = pagina.get_text("blocks")

            for bidx, bloque in enumerate(bloques):
                texto_raw = bloque[4].strip()
                if not texto_raw:
                    continue
                texto_limpio = " ".join(texto_raw.split())
                texto_lower = texto_limpio.lower()

                current_court = get_block_court(documento, num_pag, bidx, courts, end_page)

                for crit in parsed_criteria:
                    # Validar si el bloque corresponde al juzgado buscado
                    if not court_matches(current_court, crit["target_juzgado"]):
                        continue

                    match = False
                    if crit["exp_regex"]:
                        if crit["exp_regex"].search(texto_limpio):
                            match = True
                    else:
                        kw_clean = crit["valor"].strip().lower()
                        if kw_clean in texto_lower:
                            match = True
                        else:
                            tokens = [t for t in kw_clean.split() if t]
                            if len(tokens) > 1 and all(token in texto_lower for token in tokens):
                                match = True

                    if match:
                        coincidencias.append({
                            "termino": crit["valor"],
                            "juzgado": current_court or "Poder Judicial de Yucatán",
                            "pagina": page_num,
                            "contexto": texto_limpio
                        })

        documento.close()
    except Exception as e:
        print(f"Error analizando PDF con PyMuPDF: {e}")

    return coincidencias
