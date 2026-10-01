"""
🏛️ LexMonitor Yucatán — Servidor Principal
Punto de entrada modularizado y orquestador del sistema.
"""
import os
import sys
from http.server import ThreadingHTTPServer

import database
from backend.config import BASE_DIR, PUBLIC_DIR, PORT
from backend.juzgados import (
    LISTA_JUZGADOS_YUCATAN,
    normalize_court_name,
    court_matches,
)
from backend.scraper import (
    descargar_diario,
    build_pdf_court_map,
    get_block_court,
    buscar_terminos_en_pdf,
)
from backend.notifier import (
    escape_tg_html,
    enviar_notificacion_email,
    enviar_mensaje_telegram,
    notificar_usuario_coincidencias,
)
from backend.telegram_bot import (
    TelegramBotManager,
    telegram_bot,
)
from backend.cotejo import (
    verificar_cron_secret,
    ejecutar_cotejo_general,
)
from backend.routes import DiarioHandler

# Inicializar Base de Datos Relacional y Tablas al arrancar
database.init_db()

def run_server(port=PORT):
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    server_address = ("", port)
    httpd = ThreadingHTTPServer(server_address, DiarioHandler)
    print(f"\n=======================================================")
    print(f"⚖️ LexMonitor Yucatán iniciado con arquitectura modular.")
    print(f"👉 Abre en tu navegador: http://localhost:{port}")
    print(f"=======================================================\n")
    
    telegram_bot.start_if_needed()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo servidor...")
        telegram_bot.stop()
        httpd.server_close()

if __name__ == "__main__":
    puerto = PORT
    if len(sys.argv) > 1:
        try:
            puerto = int(sys.argv[1])
        except ValueError:
            pass
    run_server(puerto)
