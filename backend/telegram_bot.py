import os
import threading
import time
import requests
import database
from backend.config import BASE_DIR
from backend.notifier import escape_tg_html, enviar_mensaje_telegram
from backend.scraper import buscar_terminos_en_pdf

class TelegramBotManager:
    def __init__(self):
        self.running = False
        self.thread = None
        self.bot_info = None
        self.last_update_id = 0
        self.current_token = ""
        self.lock = threading.Lock()

    def get_bot_info(self, token):
        if not token:
            return None
        try:
            res = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
            data = res.json()
            if data.get("ok"):
                return data.get("result")
        except Exception as e:
            print(f"[Telegram] Error consultando getMe: {e}")
        return None

    def start_if_needed(self):
        with self.lock:
            token = database.get_system_setting("telegram_bot_token", "").strip()
            if not token:
                self.running = False
                self.bot_info = None
                return

            if self.running and self.current_token == token and self.thread and self.thread.is_alive():
                return

            self.current_token = token
            self.bot_info = self.get_bot_info(token)
            if not self.bot_info:
                print(f"[Telegram] Bot Token no válido. Esperando token correcto.")
                self.running = False
                return

            self.running = True
            username = self.bot_info.get("username", "Desconocido")
            print(f"🤖 [Telegram] Bot conectado exitosamente como @{username}. Escuchando mensajes...")
            self.thread = threading.Thread(target=self._polling_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False

    def restart(self):
        self.stop()
        time.sleep(0.3)
        self.start_if_needed()

    def _polling_loop(self):
        while self.running:
            token = self.current_token
            if not token:
                break
            try:
                url = f"https://api.telegram.org/bot{token}/getUpdates"
                params = {
                    "offset": self.last_update_id + 1,
                    "timeout": 15,
                    "allowed_updates": ["message"]
                }
                res = requests.get(url, params=params, timeout=25)
                if res.status_code == 200:
                    payload = res.json()
                    if payload.get("ok"):
                        updates = payload.get("result", [])
                        for update in updates:
                            self.last_update_id = update["update_id"]
                            if "message" in update:
                                self._handle_message(token, update["message"])
                elif res.status_code in (401, 404):
                    self.running = False
                    break
                else:
                    time.sleep(2)
            except requests.exceptions.Timeout:
                continue
            except Exception:
                time.sleep(3)

    def _handle_message(self, token, msg):
        chat = msg.get("chat", {})
        chat_id = chat.get("id")
        user = msg.get("from", {})
        first_name = escape_tg_html(user.get("first_name", "Colega"))
        username = user.get("username", "")
        text = msg.get("text", "").strip()

        if not chat_id or not text:
            return

        cmd = text.split()[0].lower() if text.startswith("/") else text.lower()
        if "@" in cmd:
            cmd = cmd.split("@")[0]

        # Comando /start
        if cmd in ("/start", "start"):
            resp = (
                f"🏛️ <b>¡Bienvenido a LexMonitor Yucatán!</b>\n\n"
                f"Hola <b>{first_name}</b>. Soy el bot de notificaciones jurídicas del Diario Oficial del Estado.\n\n"
                f"🔗 <b>Para vincular tu cuenta personal del despacho:</b>\n"
                f"Escribe <code>/vincular &lt;tu_correo_o_codigo&gt;</code>\n"
                f"<i>(Ejemplo: <code>/vincular eacanto@hotmail.com</code>)</i>\n\n"
                f"Comandos disponibles:\n"
                f"• <b>/vincular &lt;codigo_o_email&gt;</b> : Asocia tu cuenta para recibir tus alertas personalizadas.\n"
                f"• <b>/avisos</b> : Consulta tus acuerdos más recientes.\n"
                f"• <b>/buscar &lt;termino&gt;</b> : Busca un expediente en el PDF actual.\n"
                f"• <b>/ayuda</b> : Ver guía de comandos."
            )
            enviar_mensaje_telegram(token, chat_id, resp)

        # Comando /vincular o /correo
        elif cmd in ("/vincular", "/correo", "vincular"):
            partes = text.split(maxsplit=1)
            if len(partes) < 2 or not partes[1].strip():
                resp = (
                    f"⚠️ Por favor indica tu correo o código de vinculación.\n"
                    f"Ejemplo: <code>/vincular tu_correo@despacho.com</code>"
                )
            else:
                identificador = partes[1].strip()
                ok, msg_v = database.link_telegram_to_user_by_code_or_email(
                    str(chat_id), identificador, first_name, username
                )
                resp = msg_v
            enviar_mensaje_telegram(token, chat_id, resp)

        # Comando /suscribir
        elif cmd in ("/suscribir", "suscribir"):
            database.upsert_telegram_subscriber(str(chat_id), first_name, username)
            resp = (
                f"✅ <b>¡Suscripción confirmada!</b>\n\n"
                f"Has quedado registrado en la lista de notificaciones de LexMonitor.\n"
                f"Si además deseas que las alertas sean personalizadas para tus expedientes, escribe:\n"
                f"<code>/vincular &lt;tu_correo&gt;</code>"
            )
            enviar_mensaje_telegram(token, chat_id, resp)

        # Comando /desuscribir
        elif cmd in ("/desuscribir", "desuscribir"):
            database.delete_telegram_subscriber(str(chat_id))
            resp = (
                f"👋 <b>Suscripción cancelada</b>\n\n"
                f"Has sido dado de baja de las notificaciones automáticas."
            )
            enviar_mensaje_telegram(token, chat_id, resp)

        # Comando /avisos
        elif cmd in ("/avisos", "/hoy", "/ultimos", "avisos"):
            # Buscar si este chat_id está vinculado a un usuario
            subscribers = database.get_telegram_subscribers()
            sub = next((s for s in subscribers if str(s.get("chat_id")) == str(chat_id)), None)
            
            if sub and sub.get("user_id"):
                user_id = sub.get("user_id")
                history = database.get_user_history(user_id, limit=1)
                if not history or len(history) == 0:
                    resp = "ℹ️ Aún no hay registros de revisión en el sistema para tu cuenta."
                else:
                    h = history[0]
                    fecha = h.get("fecha", "")
                    coincidencias = h.get("coincidencias", [])
                    if not coincidencias:
                        resp = f"📅 <b>Diario Oficial ({fecha})</b>\nNo se encontraron acuerdos para tus criterios seguidos."
                    else:
                        total = len(coincidencias)
                        lines = [f"🏛️ <b>Tus acuerdos ({fecha})</b>\nSe encontraron <b>{total}</b> coincidencia(s):\n"]
                        for i, c in enumerate(coincidencias[:5], 1):
                            lines.append(f"<b>{i}. {escape_tg_html(c.get('termino'))}</b> (Pág. {c.get('pagina')})")
                            lines.append(f"<i>{escape_tg_html(c.get('contexto')[:240])}...</i>\n")
                        resp = "\n".join(lines)
            else:
                resp = (
                    f"ℹ️ Tu cuenta de Telegram no está vinculada a un usuario del sistema.\n"
                    f"Escribe <code>/vincular tu_correo@despacho.com</code> para consultar tus expedientes."
                )
            enviar_mensaje_telegram(token, chat_id, resp)

        # Comando /buscar <termino>
        elif cmd.startswith("/buscar"):
            partes = text.split(maxsplit=1)
            if len(partes) < 2 or not partes[1].strip():
                resp = "🔍 Escribe el término o número de expediente a buscar.\nEjemplo: <code>/buscar 800/2026</code>"
            else:
                termino = partes[1].strip()
                hoy = database.fecha_hoy_merida()
                pdf_path = os.path.join(BASE_DIR, f"{hoy}_1.pdf")
                if not os.path.exists(pdf_path):
                    pdfs = [f for f in os.listdir(BASE_DIR) if f.endswith(".pdf")]
                    if pdfs:
                        pdfs.sort(reverse=True)
                        pdf_path = os.path.join(BASE_DIR, pdfs[0])

                if not os.path.exists(pdf_path):
                    resp = "⚠️ No hay un archivo del Diario Oficial disponible localmente para consultar ahora."
                else:
                    matches = buscar_terminos_en_pdf(pdf_path, [termino])
                    if matches:
                        lines = [
                            f"🔍 <b>Resultados para:</b> <code>{escape_tg_html(termino)}</code>",
                            f"Coincidencias encontradas: <b>{len(matches)}</b>\n"
                        ]
                        for m in matches[:5]:
                            lines.append(f"• <b>Pág. {m['pagina']}:</b>")
                            lines.append(f"<i>{escape_tg_html(m['contexto'][:240])}...</i>\n")
                        resp = "\n".join(lines)
                    else:
                        resp = f"🔍 No se encontraron publicaciones para '<b>{escape_tg_html(termino)}</b>'."
            enviar_mensaje_telegram(token, chat_id, resp)

        else:
            resp = (
                f"Hola <b>{first_name}</b>. Puedes usar:\n"
                f"• <code>/vincular tu_correo@ejemplo.com</code>\n"
                f"• <code>/avisos</code> para ver tus acuerdos\n"
                f"• <code>/buscar 800/2026</code> para buscar en la edición actual"
            )
            enviar_mensaje_telegram(token, chat_id, resp)

# Singleton global para la app
telegram_bot = TelegramBotManager()
