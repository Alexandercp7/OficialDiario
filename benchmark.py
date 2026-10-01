#!/usr/bin/env python
"""
⏱️ Benchmark de Rendimiento y Velocidad (ms) para LexMonitor Yucatán.
Mide la latencia y throughput de:
1. Operaciones Criptográficas y de Base de Datos (SQLAlchemy).
2. Algoritmos de Normalización y Matching Judicial.
3. Extracción y Búsqueda de Expedientes con PyMuPDF.
4. Latencia de Endpoints HTTP REST (I/O).
"""
import sys
import time
import statistics
import threading
import urllib.request
import json
from http.server import ThreadingHTTPServer

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import database
from backend.juzgados import normalize_court_name, court_matches, LISTA_JUZGADOS_YUCATAN
from backend.scraper import buscar_terminos_en_pdf
from backend.routes import DiarioHandler
import pymupdf

def medir(func, iteraciones=100, nombre=""):
    tiempos = []
    for _ in range(iteraciones):
        t0 = time.perf_counter()
        func()
        t1 = time.perf_counter()
        tiempos.append((t1 - t0) * 1000.0)  # Convertir a milisegundos (ms)

    promedio = statistics.mean(tiempos)
    mediana = statistics.median(tiempos)
    minimo = min(tiempos)
    maximo = max(tiempos)
    p95 = sorted(tiempos)[int(len(tiempos) * 0.95)] if len(tiempos) >= 20 else maximo

    return {
        "nombre": nombre,
        "iteraciones": iteraciones,
        "promedio_ms": promedio,
        "mediana_ms": mediana,
        "min_ms": minimo,
        "max_ms": maximo,
        "p95_ms": p95
    }

def run_benchmarks():
    print("\n" + "=" * 78)
    print(" 🏛️  LEXMONITOR YUCATÁN — BENCHMARK DE VELOCIDAD Y RENDIMIENTO (ms)")
    print("=" * 78)
    print(f" Entorno: Python {sys.version.split()[0]} | DB: SQLite / SQLAlchemy ORM")
    print("=" * 78 + "\n")

    resultados = []

    # -------------------------------------------------------------
    # 1. CRIPTOGRAFÍA Y BASE DE DATOS
    # -------------------------------------------------------------
    print(" [1/4] Evaluando Criptografía y Base de Datos...")

    # A) Hasheo de contraseña (PBKDF2-SHA256 con 100,000 rondas)
    r1 = medir(lambda: database.hash_password("PasswordSegura2026!"), iteraciones=15, nombre="Hasheo PBKDF2 (100k rondas)")
    resultados.append(r1)

    pwd_hash, salt = database.hash_password("PasswordSegura2026!")
    # B) Verificación de contraseña
    r2 = medir(lambda: database.verify_password("PasswordSegura2026!", salt, pwd_hash), iteraciones=15, nombre="Verificación Password")
    resultados.append(r2)

    # C) Generación de código de enlace
    r3 = medir(lambda: database.generate_link_code(), iteraciones=1000, nombre="Generación Link Code")
    resultados.append(r3)

    # D) Inserción de Usuario en BD (transacción ORM)
    email_base = f"bench_{int(time.time())}"
    counter = [0]
    def db_insert():
        counter[0] += 1
        database.create_user(f"User {counter[0]}", f"{email_base}_{counter[0]}@bench.com", "Pass123!")
    r4 = medir(db_insert, iteraciones=30, nombre="Creación de Usuario (ORM Insert)")
    resultados.append(r4)

    # Preparar usuario y token para lectura
    user_test, _ = database.create_user("Bench Reader", f"reader_{int(time.time())}@bench.com", "Pass123!")
    token_test = database.create_session_token(user_test["id"])

    # E) Búsqueda por Token de Sesión (ORM Select con índice)
    r5 = medir(lambda: database.get_user_by_token(token_test), iteraciones=100, nombre="Lookup Token de Sesión (ORM)")
    resultados.append(r5)

    # F) Agregar criterio de búsqueda
    crit_count = [0]
    def add_crit():
        crit_count[0] += 1
        database.add_user_criterion(user_test["id"], "Expediente", f"{crit_count[0]}/2026", "Juzgado Primero Civil")
    r6 = medir(add_crit, iteraciones=30, nombre="Creación Criterio (ORM)")
    resultados.append(r6)

    # G) Lectura de criterios del usuario
    r7 = medir(lambda: database.get_user_criteria(user_test["id"]), iteraciones=100, nombre="Consulta Criterios (ORM)")
    resultados.append(r7)

    # -------------------------------------------------------------
    # 2. ALGORITMOS DE TEXTO Y JUZGADOS
    # -------------------------------------------------------------
    print(" [2/4] Evaluando Algoritmos de Normalización y Matching Judicial...")

    nombre_juzgado_test = "NOTIFICACIONES DEL JUZGADO PRIMERO MIXTO DE LO CIVIL, FAMILIAR Y MERCANTIL DE MÉRIDA"
    
    # A) Normalización de nombres de juzgados
    r8 = medir(lambda: normalize_court_name(nombre_juzgado_test), iteraciones=1000, nombre="Normalización de Juzgado")
    resultados.append(r8)

    # B) Matching de Juzgados
    r9 = medir(lambda: court_matches(nombre_juzgado_test, "Juzgado 1° Mixto"), iteraciones=1000, nombre="Matching de Juzgados")
    resultados.append(r9)

    # C) Búsqueda en catálogo de 40 juzgados
    def scan_catalogo():
        return [j for j in LISTA_JUZGADOS_YUCATAN if court_matches(j["nombre"], "Oralidad Familiar")]
    r10 = medir(scan_catalogo, iteraciones=500, nombre="Filtro Catálogo Completo (40 Juzgados)")
    resultados.append(r10)

    # -------------------------------------------------------------
    # 3. EXTRACCIÓN Y BÚSQUEDA EN DOCUMENTO PDF CON PyMuPDF
    # -------------------------------------------------------------
    print(" [3/4] Evaluando PyMuPDF (Generación y Escaneo de Documento Legal)...")

    # Crear PDF sintético de prueba con texto legal real
    temp_pdf_path = "temp_benchmark_doc.pdf"
    doc = pymupdf.open()
    
    # Portada / Sumario
    p1 = doc.new_page()
    p1.insert_text((50, 50), "DIARIO OFICIAL DEL ESTADO DE YUCATAN\nSUMARIO\nPODER JUDICIAL\nNOTIFICACIONES DEL JUZGADO PRIMERO MERCANTIL ......... 2\nNOTIFICACIONES DEL JUZGADO SEGUNDO CIVIL ......... 3\nGOBIERNO MUNICIPAL ......... 5")
    
    # Páginas de acuerdos
    p2 = doc.new_page()
    p2.insert_text((50, 50), "NOTIFICACIONES DEL JUZGADO PRIMERO MERCANTIL\nJUICIO EJECUTIVO MERCANTIL EXPEDIENTE 69/2026 AUTO DE FECHA...\nMARIO PEREZ VS JUAN LOPEZ.- EXPEDIENTE 104/2026 AUTO")

    p3 = doc.new_page()
    p3.insert_text((50, 50), "NOTIFICACIONES DEL JUZGADO SEGUNDO CIVIL\nJUICIO ORDINARIO CIVIL EXPEDIENTE 203/2026 SENTENCIA DEFINITIVA\nAUTO DE FECHA 28 DE SEPTIEMBRE EXPEDIENTE 550/2026")

    doc.save(temp_pdf_path)
    doc.close()

    # Benchmark de búsqueda con PyMuPDF
    criterios_prueba = [
        {"valor": "69/2026", "juzgado": "Juzgado Primero Mercantil"},
        {"valor": "203/2026", "juzgado": "Juzgado Segundo Civil"},
        {"valor": "JUAN LOPEZ", "juzgado": "Todos"}
    ]

    r11 = medir(lambda: buscar_terminos_en_pdf(temp_pdf_path, criterios_prueba), iteraciones=20, nombre="Escaneo PyMuPDF (3 págs, 3 criterios)")
    resultados.append(r11)

    import os
    if os.path.exists(temp_pdf_path):
        os.remove(temp_pdf_path)

    # -------------------------------------------------------------
    # 4. LATENCIA DE ENDPOINTS HTTP REST
    # -------------------------------------------------------------
    print(" [4/4] Evaluando Latencia de Red HTTP Local...")

    # Levantar servidor en puerto efímero
    server = ThreadingHTTPServer(("127.0.0.1", 0), DiarioHandler)
    server_port = server.server_port
    base_url = f"http://127.0.0.1:{server_port}"
    th = threading.Thread(target=server.serve_forever, daemon=True)
    th.start()

    time.sleep(0.1)

    # A) Endpoint GET /api/health
    def http_health():
        req = urllib.request.Request(f"{base_url}/api/health")
        with urllib.request.urlopen(req) as resp:
            resp.read()
    r12 = medir(http_health, iteraciones=50, nombre="HTTP GET /api/health")
    resultados.append(r12)

    # B) Endpoint GET /api/juzgados
    def http_juzgados():
        req = urllib.request.Request(f"{base_url}/api/juzgados")
        with urllib.request.urlopen(req) as resp:
            resp.read()
    r13 = medir(http_juzgados, iteraciones=50, nombre="HTTP GET /api/juzgados (JSON Payload)")
    resultados.append(r13)

    # C) Endpoint GET /api/auth/me con Token
    def http_auth_me():
        req = urllib.request.Request(
            f"{base_url}/api/auth/me",
            headers={"Authorization": f"Bearer {token_test}"}
        )
        with urllib.request.urlopen(req) as resp:
            resp.read()
    r14 = medir(http_auth_me, iteraciones=50, nombre="HTTP GET /api/auth/me (Auth + DB Query)")
    resultados.append(r14)

    server.shutdown()
    server.server_close()

    # -------------------------------------------------------------
    # TABLA DE RESULTADOS
    # -------------------------------------------------------------
    print("\n" + "=" * 90)
    print(f" {'OPERACIÓN':<42} | {'PROM (ms)':<10} | {'MED (ms)':<9} | {'MIN (ms)':<9} | {'P95 (ms)':<9}")
    print("-" * 90)

    for res in resultados:
        nom = res["nombre"]
        prom = f"{res['promedio_ms']:.3f} ms"
        med = f"{res['mediana_ms']:.3f} ms"
        mn = f"{res['min_ms']:.3f} ms"
        p95 = f"{res['p95_ms']:.3f} ms"
        print(f" {nom:<42} | {prom:<10} | {med:<9} | {mn:<9} | {p95:<9}")

    print("=" * 90)
    print(" ✅ Benchmark finalizado con éxito.\n")

if __name__ == "__main__":
    run_benchmarks()
