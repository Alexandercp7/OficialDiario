import os
import sys
import json
import datetime
import smtplib
import ssl
import threading
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import urllib.parse
import hmac
import pymupdf
import requests
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Cargar variables de entorno desde .env
load_dotenv(os.path.join(BASE_DIR, ".env"))

import database

# Forzar salida en UTF-8 para consola en Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PUBLIC_DIR = os.path.join(BASE_DIR, "public")


# Inicializar Base de Datos Relacional y Tablas
database.init_db()


# ==================== LÓGICA DE DIARIO Y BÚSQUEDA ====================

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

def buscar_terminos_en_pdf(ruta_pdf, keywords):
    """
    Busca términos simples y combinados en los párrafos/bloques del PDF.
    Soporta términos compuestos como '800/2026 Alexander Canto':
    detecta si todas las sub-palabras están dentro del mismo párrafo.
    """
    coincidencias = []
    if not os.path.exists(ruta_pdf):
        return coincidencias

    try:
        documento = pymupdf.open(ruta_pdf)
        for num_pag in range(len(documento)):
            pagina = documento.load_page(num_pag)
            bloques = pagina.get_text("blocks")

            for bloque in bloques:
                texto_raw = bloque[4].strip()
                texto_limpio = " ".join(texto_raw.split())
                texto_lower = texto_limpio.lower()

                for kw in keywords:
                    kw_clean = kw.strip().lower()
                    if not kw_clean:
                        continue

                    match = False
                    if kw_clean in texto_lower:
                        match = True
                    else:
                        tokens = [t for t in kw_clean.split() if t]
                        if len(tokens) > 1 and all(token in texto_lower for token in tokens):
                            match = True

                    if match:
                        coincidencias.append({
                            "termino": kw,
                            "pagina": num_pag + 1,
                            "contexto": texto_limpio
                        })
        documento.close()
    except Exception as e:
        print(f"Error analizando PDF con PyMuPDF: {e}")

    return coincidencias


# ==================== NOTIFICACIONES ====================

def enviar_notificacion_email(config_email, asunto, mensaje_texto, mensaje_html):
    """Envía un correo mediante Resend API (HTTPS) o SMTP oficial del sistema."""
    try:
        recipient_raw = (config_email.get("recipient_email") or "").strip()
        if not recipient_raw:
            return False, "No se especificó un correo de destinatario válido."

        recipients = [r.strip() for r in recipient_raw.replace(";", ",").split(",") if r.strip()]
        if not recipients:
            return False, "No se especificó un correo de destinatario válido."

        # 1. Si existe RESEND_API_KEY configurada, enviar vía Resend HTTP API (ideal para Render en la nube)
        resend_api_key = os.getenv("RESEND_API_KEY", "").strip()
        if resend_api_key:
            from_email = os.getenv("RESEND_FROM_EMAIL", "").strip() or "LexMonitor Yucatán <onboarding@resend.dev>"
            payload = {
                "from": from_email,
                "to": recipients,
                "subject": asunto,
                "text": mensaje_texto,
                "html": mensaje_html
            }
            headers = {
                "Authorization": f"Bearer {resend_api_key}",
                "Content-Type": "application/json"
            }
            resp = requests.post("https://api.resend.com/emails", json=payload, headers=headers, timeout=15)
            if resp.status_code in (200, 201):
                return True, f"Correo enviado exitosamente vía Resend a {len(recipients)} destinatario(s)."
            else:
                try:
                    err_json = resp.json()
                    err_msg = err_json.get("message", resp.text)
                except Exception:
                    err_msg = resp.text
                return False, f"Error en Resend API ({resp.status_code}): {err_msg}"

        # 2. Si no hay Resend API Key, intentar mediante SMTP tradicional
        sys_smtp = database.get_system_smtp_config()
        sender = (config_email.get("sender_email") or sys_smtp.get("sender_email") or "").strip()
        password = (config_email.get("sender_password") or sys_smtp.get("sender_password") or "").replace(" ", "").strip()
        host = (config_email.get("smtp_host") or sys_smtp.get("smtp_host") or "smtp.gmail.com").strip()
        port = int(config_email.get("smtp_port") or sys_smtp.get("smtp_port") or 465)
        use_ssl = config_email.get("use_ssl")
        if use_ssl is None:
            use_ssl = sys_smtp.get("use_ssl", True)

        if not sender or not password:
            return False, "Faltan credenciales de correo (configura RESEND_API_KEY en variables de entorno o credenciales SMTP)."

        msg = MIMEMultipart("alternative")
        msg["Subject"] = asunto
        msg["From"] = f"LexMonitor Yucatán <{sender}>"
        msg["To"] = ", ".join(recipients)

        part1 = MIMEText(mensaje_texto, "plain", "utf-8")
        part2 = MIMEText(mensaje_html, "html", "utf-8")
        msg.attach(part1)
        msg.attach(part2)

        if use_ssl or port == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(host, port, context=context, timeout=15) as server:
                server.login(sender, password)
                server.sendmail(sender, recipients, msg.as_string())
        else:
            with smtplib.SMTP(host, port, timeout=15) as server:
                server.starttls()
                server.login(sender, password)
                server.sendmail(sender, recipients, msg.as_string())

        return True, f"Correo enviado a {len(recipients)} destinatario(s)."
    except smtplib.SMTPAuthenticationError:
        return False, "Error de autenticación SMTP (535): Verifica la contraseña de aplicación de 16 caracteres del remitente."
    except Exception as e:
        return False, f"Error enviando correo: {str(e)}"

def escape_tg_html(text):
    if not text:
        return ""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def enviar_mensaje_telegram(bot_token, chat_id, mensaje):
    if not bot_token or not chat_id:
        return False, "Falta bot_token o chat_id"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": mensaje,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        data = res.json()
        if data.get("ok"):
            return True, "Enviado con éxito"
        else:
            desc = data.get("description", "Error desconocido")
            return False, f"Telegram API: {desc}"
    except Exception as e:
        return False, f"Conexión fallida: {str(e)}"


def notificar_usuario_coincidencias(user_dict, notif_cfg, fecha, coincidencias):
    """
    Envía notificaciones personalizadas EXCLUSIVAMENTE a este usuario con sus coincidencias.
    """
    if not coincidencias:
        return "Sin coincidencias para notificar."

    canal = notif_cfg.get("channel", "email")
    if canal == "none":
        return "Notificaciones desactivadas para este usuario."

    año = fecha.split("-")[0]
    enlace_pdf = f"https://www.yucatan.gob.mx/docs/diario_oficial/diarios/{año}/{fecha}_1.pdf"
    total = len(coincidencias)
    user_name = user_dict.get("name", "Usuario")

    # Contenido de correo
    asunto = f"⚖️ Alerta LexMonitor: {total} acuerdo(s) publicado(s) en Diario Oficial ({fecha})"
    
    texto_plano = f"Estimado(a) {user_name}:\n\n"
    texto_plano += f"Se han detectado {total} coincidencia(s) en el Diario Oficial de Yucatán para tus criterios seguidos ({fecha}):\n\n"
    for i, c in enumerate(coincidencias, 1):
        texto_plano += f"{i}. Término: {c.get('termino')} (Pág. {c.get('pagina')})\n"
        texto_plano += f"   Extracto: {c.get('contexto')}\n\n"
    texto_plano += f"Descargar edición completa: {enlace_pdf}\n\nLexMonitor Yucatán"

    filas_html = ""
    for i, c in enumerate(coincidencias, 1):
        termino_esc = escape_tg_html(c.get('termino', ''))
        contexto_esc = escape_tg_html(c.get('contexto', ''))
        filas_html += f"""
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #f59e0b; border-radius: 8px; padding: 14px; margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                <span style="background-color: #e0e7ff; color: #3730a3; font-weight: bold; font-family: monospace; font-size: 13px; padding: 3px 8px; border-radius: 4px;">
                    {termino_esc}
                </span>
                <span style="color: #64748b; font-size: 12px; font-weight: 600;">Página {c.get('pagina', '?')}</span>
            </div>
            <p style="margin: 0; color: #334155; font-size: 13.5px; line-height: 1.5;">{contexto_esc}</p>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f1f5f9; padding: 20px; margin: 0;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #cbd5e1; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
            <div style="background-color: #0f172a; padding: 22px 24px; border-bottom: 3px solid #f59e0b;">
                <h1 style="color: #ffffff; margin: 0; font-size: 20px; font-weight: bold;">
                    LexMonitor <span style="color: #f59e0b;">Yucatán</span>
                </h1>
                <p style="color: #94a3b8; margin: 4px 0 0 0; font-size: 12px;">Vigilancia Legal Automatizada &bull; {fecha}</p>
            </div>
            <div style="padding: 24px;">
                <p style="color: #1e293b; font-size: 15px; margin-top: 0;">
                    Estimado(a) <strong>{user_name}</strong>:
                </p>
                <p style="color: #475569; font-size: 14px; line-height: 1.5;">
                    El motor de vigilancia detectó <strong>{total} publicación(es)</strong> correspondiente(s) a los expedientes y nombres bajo tu monitoreo en la edición de hoy:
                </p>
                {filas_html}
                <div style="text-align: center; margin-top: 24px;">
                    <a href="{enlace_pdf}" style="background-color: #2563eb; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 8px; font-weight: 600; font-size: 13px; display: inline-block;">
                        Consultar PDF Original
                    </a>
                </div>
            </div>
            <div style="background-color: #f8fafc; padding: 14px 24px; text-align: center; border-top: 1px solid #e2e8f0; font-size: 11px; color: #94a3b8;">
                Este correo fue generado automáticamente por tu instancia de LexMonitor Yucatán.
            </div>
        </div>
    </body>
    </html>
    """

    res_mensajes = []

    # Enviar por correo si está activo
    if canal in ("email", "both", "all"):
        email_cfg = dict(notif_cfg.get("email", {}))
        if not email_cfg.get("recipient_email"):
            email_cfg["recipient_email"] = user_dict.get("email", "")
        ok, msg_e = enviar_notificacion_email(email_cfg, asunto, texto_plano, html)
        res_mensajes.append(f"Email: {msg_e}")

    # Enviar por Telegram si está activo y tiene chat_id
    if canal in ("telegram", "both", "all"):
        bot_token = database.get_system_setting("telegram_bot_token")
        tg_chat_id = user_dict.get("telegram_chat_id")
        if bot_token and tg_chat_id:
            msg_tg = [
                f"⚖️ <b>LexMonitor Yucatán ({fecha})</b>",
                f"Hola <b>{escape_tg_html(user_name)}</b>, se encontraron <b>{total}</b> coincidencia(s):\n"
            ]
            for i, c in enumerate(coincidencias[:5], 1):
                msg_tg.append(f"<b>{i}. {escape_tg_html(c.get('termino'))}</b> (Pág. {c.get('pagina')})")
                msg_tg.append(f"<i>{escape_tg_html(c.get('contexto')[:280])}...</i>\n")
            if total > 5:
                msg_tg.append(f"<i>(+ {total - 5} acuerdos más en la plataforma)</i>\n")
            msg_tg.append(f"🔗 <a href='{enlace_pdf}'>Ver PDF Oficial</a>")

            ok_t, msg_t = enviar_mensaje_telegram(bot_token, tg_chat_id, "\n".join(msg_tg))
            res_mensajes.append(f"Telegram: {msg_t}")
        elif not tg_chat_id:
            lcode = user_dict.get("link_code") or user_dict.get("email", "")
            res_mensajes.append(f"Telegram: Cuenta no vinculada (usa /vincular {lcode}).")

    return " | ".join(res_mensajes) if res_mensajes else "Procesado"


# ==================== MOTOR DE COTEJO GENERAL ====================

def ejecutar_cotejo_general(fecha=None, triggered_by_user_id=None):
    """
    Ejecuta el cotejo completo para una fecha (por defecto hoy).
    Descarga el PDF, busca los criterios de todos los usuarios activos,
    registra los resultados en SQLite y envía alertas a quienes tengan coincidencias.
    """
    if not fecha:
        fecha = datetime.datetime.now().strftime("%Y-%m-%d")

    archivo_local = os.path.join(BASE_DIR, f"{fecha}_1.pdf")
    temp_archivo = False

    if not os.path.exists(archivo_local):
        archivo_local = os.path.join(BASE_DIR, f"temp_{fecha}.pdf")
        temp_archivo = True
        ok, msg_descarga = descargar_diario(fecha, archivo_local)
        if not ok:
            scan_record = database.record_scan_and_user_matches(
                fecha=fecha,
                estado="error",
                mensaje=msg_descarga,
                user_matches_map={},
                triggered_by_user_id=triggered_by_user_id
            )
            return {
                "success": False,
                "date": fecha,
                "status": "error",
                "message": msg_descarga,
                "scan_record": scan_record,
                "user_matches_map": {}
            }

    # COTEJO MULTI-USUARIO PERSONALIZADO
    all_users = database.get_all_active_users_data()
    user_matches_map = {}
    total_coincidencias_global = 0

    for u_data in all_users:
        u_obj = u_data["user"]
        u_id = u_obj["id"]
        u_keywords = [c["valor"] for c in u_data.get("criteria", [])]
        if u_keywords:
            u_coincidencias = buscar_terminos_en_pdf(archivo_local, u_keywords)
            user_matches_map[u_id] = u_coincidencias
            total_coincidencias_global += len(u_coincidencias)
        else:
            user_matches_map[u_id] = []

    # Guardar en Base de Datos Relacional
    scan_record = database.record_scan_and_user_matches(
        fecha=fecha,
        estado="completado",
        mensaje=f"Cotejo completado para la edición {fecha}. ({total_coincidencias_global} coincidencia(s) en {len(all_users)} usuario(s)).",
        user_matches_map=user_matches_map,
        triggered_by_user_id=triggered_by_user_id
    )

    # Notificar a CADA usuario con coincidencias en sus propios canales
    notificaciones_despachadas = []
    for u_data in all_users:
        u_obj = u_data["user"]
        u_id = u_obj["id"]
        u_notif_cfg = u_data.get("config", {})
        u_matches = user_matches_map.get(u_id, [])

        if u_matches:
            status_envio = notificar_usuario_coincidencias(u_obj, u_notif_cfg, fecha, u_matches)
            notificaciones_despachadas.append({
                "user_id": u_id,
                "name": u_obj.get("name"),
                "email": u_obj.get("email"),
                "total_matches": len(u_matches),
                "status": status_envio
            })

    # Limpiar archivo temporal
    if temp_archivo and os.path.exists(archivo_local):
        try:
            os.remove(archivo_local)
        except Exception:
            pass

    return {
        "success": True,
        "date": fecha,
        "status": "completado",
        "total_users_checked": len(all_users),
        "users_with_matches": len(notificaciones_despachadas),
        "total_matches": total_coincidencias_global,
        "notifications": notificaciones_despachadas,
        "scan_record": scan_record,
        "user_matches_map": user_matches_map
    }

def verificar_cron_secret(handler):
    """
    Verifica que la petición de cron incluya la clave secreta autorizada.
    Soporta:
      - Header 'X-Cron-Secret'
      - Header 'Authorization: Bearer <secret>'
      - Query param '?secret=<secret>'
    """
    cron_secret = os.getenv("CRON_SECRET", "lex_cron_2026_secreto").strip()
    if not cron_secret:
        return True

    # 1. Header X-Cron-Secret
    header_secret = handler.headers.get("X-Cron-Secret", "").strip()
    if header_secret and hmac.compare_digest(header_secret, cron_secret):
        return True

    # 2. Header Authorization: Bearer <secret>
    auth_header = handler.headers.get("Authorization", "").strip()
    if auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
        if hmac.compare_digest(token, cron_secret):
            return True

    # 3. Query Param ?secret=<secret>
    parsed = urllib.parse.urlparse(handler.path)
    qs = urllib.parse.parse_qs(parsed.query)
    if "secret" in qs and qs["secret"]:
        if hmac.compare_digest(qs["secret"][0].strip(), cron_secret):
            return True

    return False


# ==================== BOT DE TELEGRAM ====================

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
                hoy = datetime.datetime.now().strftime("%Y-%m-%d")
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

telegram_bot = TelegramBotManager()


# ==================== SERVIDOR HTTP ====================

class DiarioHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def responder_json(self, status, payload):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def get_auth_token(self):
        auth_header = self.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:].strip()
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        if "token" in qs:
            return qs["token"][0].strip()
        return None

    def get_current_user(self):
        token = self.get_auth_token()
        if not token:
            return None
        return database.get_user_by_token(token)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # ----------------- ENDPOINTS PÚBLICOS Y DE AUTH -----------------
        if path == "/api/health":
            self.responder_json(200, {
                "status": "ok",
                "service": "LexMonitor Yucatán",
                "timestamp": datetime.datetime.utcnow().isoformat()
            })
            return

        if path == "/api/cron/scan":
            if not verificar_cron_secret(self):
                self.responder_json(401, {"error": "No autorizado. Token de cron inválido o ausente."})
                return
            parsed_qs = urllib.parse.parse_qs(parsed.query)
            fecha = parsed_qs.get("date", [None])[0]
            resultado = ejecutar_cotejo_general(fecha=fecha, triggered_by_user_id=None)
            self.responder_json(200 if resultado.get("success") else 400, resultado)
            return

        if path == "/api/auth/me":
            user = self.get_current_user()
            if not user:
                self.responder_json(401, {"error": "No autenticado o sesión expirada"})
                return
            criteria = database.get_user_criteria(user["id"])
            config = database.get_user_notification_config(user["id"])
            self.responder_json(200, {
                "user": user,
                "criteria": criteria,
                "config": config
            })
            return

        if path == "/api/telegram/status":
            token = database.get_system_setting("telegram_bot_token")
            bot_info = telegram_bot.bot_info
            if token and not bot_info:
                bot_info = telegram_bot.get_bot_info(token)
            
            user = self.get_current_user()
            user_linked = bool(user and user.get("telegram_chat_id"))

            self.responder_json(200, {
                "configured": bool(token),
                "bot_info": {"username": bot_info.get("username"), "first_name": bot_info.get("first_name")} if bot_info else None,
                "user_linked": user_linked,
                "telegram_username": user.get("telegram_username") if user else None,
                "user_link_code": user.get("link_code") if user else None
            })
            return


        # ----------------- DATOS PERSONALIZADOS DEL USUARIO -----------------
        if path == "/api/data":
            user = self.get_current_user()
            if not user:
                self.responder_json(401, {"error": "Debes iniciar sesión para consultar tus datos."})
                return

            criteria = database.get_user_criteria(user["id"])
            config = database.get_user_notification_config(user["id"])
            history = database.get_user_history(user["id"])

            self.responder_json(200, {
                "user": user,
                "keywords": [c["valor"] for c in criteria],
                "criteria": criteria,
                "notifications": config,
                "history": history
            })
            return

        # ----------------- SERVIR ARCHIVOS ESTÁTICOS -----------------
        if path == "/":
            file_path = os.path.join(PUBLIC_DIR, "index.html")
            content_type = "text/html; charset=utf-8"
        else:
            file_name = path.lstrip("/")
            file_path = os.path.join(PUBLIC_DIR, file_name)
            if path.endswith(".css"):
                content_type = "text/css; charset=utf-8"
            elif path.endswith(".js"):
                content_type = "application/javascript; charset=utf-8"
            else:
                content_type = "text/plain; charset=utf-8"

        if os.path.exists(file_path) and os.path.isfile(file_path):
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.end_headers()
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.responder_json(404, {"error": "Archivo no encontrado"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(length) if length > 0 else b"{}"

        try:
            body = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except Exception:
            body = {}

        # ----------------- AUTENTICACIÓN: REGISTRO -----------------
        if path == "/api/auth/register":
            name = body.get("name", "").strip()
            email = body.get("email", "").strip()
            password = body.get("password", "").strip()

            user_dict, err = database.create_user(name, email, password)
            if err:
                self.responder_json(400, {"error": err})
                return

            token = database.create_session_token(user_dict["id"])
            criteria = database.get_user_criteria(user_dict["id"])
            config = database.get_user_notification_config(user_dict["id"])

            self.responder_json(200, {
                "success": True,
                "token": token,
                "user": user_dict,
                "criteria": criteria,
                "config": config
            })
            return

        # ----------------- AUTENTICACIÓN: INICIO DE SESIÓN -----------------
        elif path == "/api/auth/login":
            email = body.get("email", "").strip()
            password = body.get("password", "").strip()

            user_dict, err = database.authenticate_user(email, password)
            if err:
                self.responder_json(401, {"error": err})
                return

            token = database.create_session_token(user_dict["id"])
            criteria = database.get_user_criteria(user_dict["id"])
            config = database.get_user_notification_config(user_dict["id"])

            self.responder_json(200, {
                "success": True,
                "token": token,
                "user": user_dict,
                "criteria": criteria,
                "config": config
            })
            return

        # ----------------- AUTENTICACIÓN: CERRAR SESIÓN -----------------
        elif path == "/api/auth/logout":
            token = self.get_auth_token()
            if token:
                database.delete_session_token(token)
            self.responder_json(200, {"success": True})
            return

        # ----------------- ENDPOINT PÚBLICO PROTEGIDO PARA CRON EXTERNO -----------------
        if path == "/api/cron/scan":
            if not verificar_cron_secret(self):
                self.responder_json(401, {"error": "No autorizado. Token de cron inválido o ausente."})
                return
            fecha = body.get("date")
            if not fecha:
                parsed_qs = urllib.parse.parse_qs(parsed.query)
                fecha = parsed_qs.get("date", [None])[0]
            resultado = ejecutar_cotejo_general(fecha=fecha, triggered_by_user_id=None)
            self.responder_json(200 if resultado.get("success") else 400, resultado)
            return

        # ----------------- ENDPOINTS QUE REQUIEREN USUARIO AUTENTICADO -----------------
        user = self.get_current_user()
        if not user:
            self.responder_json(401, {"error": "Debes iniciar sesión para realizar esta acción."})
            return

        if path == "/api/keywords":
            kw = body.get("keyword", "").strip()
            tipo = body.get("tipo", "Expediente")
            if not kw:
                self.responder_json(400, {"error": "El término no puede estar vacío."})
                return

            c_dict, err = database.add_user_criterion(user["id"], tipo, kw)
            if err:
                self.responder_json(400, {"error": err})
                return

            criteria = database.get_user_criteria(user["id"])
            self.responder_json(200, {
                "success": True,
                "keywords": [c["valor"] for c in criteria],
                "criteria": criteria
            })

        elif path == "/api/config":
            notifications = body.get("notifications")
            if notifications:
                safe_notif = {}
                if "channel" in notifications:
                    safe_notif["channel"] = notifications["channel"]
                email_data = notifications.get("email", {})
                if "recipient_email" in email_data:
                    safe_notif["email"] = {
                        "recipient_email": email_data["recipient_email"].strip()
                    }
                database.update_user_notification_config(user["id"], safe_notif)

            config = database.get_user_notification_config(user["id"])
            self.responder_json(200, {"success": True, "notifications": config})


        elif path == "/api/test-notification":
            temp_cfg = body.get("notifications", database.get_user_notification_config(user["id"]))
            canal = temp_cfg.get("channel", "email")
            email_cfg = dict(temp_cfg.get("email", {}))
            if not email_cfg.get("recipient_email"):
                email_cfg["recipient_email"] = user["email"]

            sender_display = os.getenv("RESEND_FROM_EMAIL") or database.get_system_smtp_config().get('sender_email') or "LexMonitor HTTPS Gateway"
            if canal == "email":
                ok, msg = enviar_notificacion_email(
                    email_cfg,
                    f"⚖️ Prueba de Alerta Personalizada — LexMonitor",
                    f"Hola {user['name']},\nEsta es una confirmación de que tu canal de correo en LexMonitor Yucatán está recibiendo las alertas oficiales correctamente.",
                    f"""<div style="font-family:sans-serif;padding:24px;border-radius:12px;background:#f8fafc;border:1px solid #cbd5e1;max-width:550px;">
                        <h2 style="color:#0f172a;margin-top:0;">⚖️ LexMonitor <span style="color:#f59e0b;">Yucatán</span></h2>
                        <h3 style="color:#2563eb;margin-bottom:8px;">¡Canal de Alertas por Correo Verificado!</h3>
                        <p style="color:#334155;font-size:14px;line-height:1.5;">Hola <strong>{escape_tg_html(user['name'])}</strong>,</p>
                        <p style="color:#334155;font-size:14px;line-height:1.5;">Tu canal de correo está listo y activo para recibir avisos de tus expedientes monitoreados en el Diario Oficial de Yucatán.</p>
                        <div style="margin-top:16px;padding:12px;background:#ffffff;border-radius:8px;border:1px solid #e2e8f0;font-size:13px;color:#475569;">
                            <strong>Destinatario:</strong> {escape_tg_html(email_cfg.get('recipient_email'))}<br>
                            <strong>Servidor Remitente:</strong> {escape_tg_html(sender_display)}
                        </div>
                    </div>"""
                )

                self.responder_json(200 if ok else 400, {"success": ok, "message": msg})

            elif canal == "telegram":
                bot_token = database.get_system_setting("telegram_bot_token")
                if not bot_token:
                    self.responder_json(400, {"success": False, "message": "Introduce primero el Bot Token de Telegram."})
                    return

                bot_info = telegram_bot.get_bot_info(bot_token)
                if not bot_info:
                    self.responder_json(400, {"success": False, "message": "El Bot Token es inválido o no conecta con Telegram."})
                    return

                # Si el usuario tiene chat_id personal
                tg_cid = user.get("telegram_chat_id")
                if tg_cid:
                    ok, msg = enviar_mensaje_telegram(
                        bot_token, tg_cid,
                        f"🧪 <b>Prueba de Alerta Personalizada</b>\nHola <b>{escape_tg_html(user['name'])}</b>, tu cuenta de Telegram está vinculada con éxito al bot oficial @{bot_info.get('username', 'yucamonitor_bot')} de LexMonitor."
                    )
                    self.responder_json(200 if ok else 400, {"success": ok, "message": msg})
                else:
                    link_target = user.get('link_code') or user.get('email')
                    self.responder_json(200, {
                        "success": True,
                        "message": f"Bot @{bot_info.get('username')} verificado. Para recibir alertas personales, abre el bot y envía: /vincular {link_target}"
                    })

            elif canal in ("both", "all"):
                res_list = []
                ok_m, msg_m = enviar_notificacion_email(
                    email_cfg,
                    "⚖️ Prueba Dual de Alertas — LexMonitor",
                    f"Hola {user['name']}, prueba dual de alertas por Correo y Telegram.",
                    f"""<div style="font-family:sans-serif;padding:24px;border-radius:12px;background:#f8fafc;border:1px solid #cbd5e1;max-width:550px;">
                        <h2 style="color:#0f172a;margin-top:0;">⚖️ LexMonitor <span style="color:#f59e0b;">Yucatán</span></h2>
                        <h3 style="color:#10b981;margin-bottom:8px;">¡Prueba Dual de Notificaciones Exitosa!</h3>
                        <p style="color:#334155;font-size:14px;">Canal de correo oficial activo para <strong>{escape_tg_html(user['name'])}</strong> ({escape_tg_html(email_cfg.get('recipient_email'))}).</p>
                    </div>"""
                )
                res_list.append(f"📧 Correo: {msg_m}")

                bot_token = database.get_system_setting("telegram_bot_token")
                tg_cid = user.get("telegram_chat_id")
                if bot_token and tg_cid:
                    ok_t, msg_t = enviar_mensaje_telegram(
                        bot_token, tg_cid,
                        f"🧪 <b>Prueba Dual LexMonitor</b>\n¡Canal de Telegram activo para <b>{escape_tg_html(user['name'])}</b>!\nRecibirás aquí tus alertas en cuanto se detecten acuerdos."
                    )
                    res_list.append(f"🤖 Telegram: {msg_t}")
                elif bot_token:
                    link_target = user.get('link_code') or user.get('email')
                    res_list.append(f"🤖 Telegram: Vincula tu cuenta enviando /vincular {link_target} a @yucamonitor_bot.")
                else:
                    res_list.append("🤖 Telegram: Falta Bot Token.")

                self.responder_json(200, {"success": True, "message": " | ".join(res_list)})

            else:
                self.responder_json(400, {"success": False, "message": "Selecciona un canal (Correo o Telegram) para probar."})

        elif path == "/api/scan":
            fecha = body.get("date")
            resultado = ejecutar_cotejo_general(fecha=fecha, triggered_by_user_id=user["id"])
            if not resultado.get("success"):
                self.responder_json(200, {
                    **resultado.get("scan_record", {}),
                    "coincidencias": [],
                    "total_coincidencias": 0,
                    "error": resultado.get("message")
                })
                return

            user_current_matches = resultado.get("user_matches_map", {}).get(user["id"], [])
            scan_rec = resultado.get("scan_record", {})
            self.responder_json(200, {
                **scan_rec,
                "total_coincidencias": len(user_current_matches),
                "coincidencias": user_current_matches
            })

        elif path == "/api/telegram/unlink":
            database.unlink_user_telegram(user["id"])
            self.responder_json(200, {"success": True, "user_linked": False})


        else:
            self.responder_json(404, {"error": "Ruta no encontrada"})

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(length) if length > 0 else b"{}"

        try:
            body = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except Exception:
            body = {}

        user = self.get_current_user()
        if not user:
            self.responder_json(401, {"error": "No autorizado"})
            return

        if path == "/api/keywords":
            kw = body.get("keyword", "").strip()
            database.delete_user_criterion(user["id"], kw)
            criteria = database.get_user_criteria(user["id"])
            self.responder_json(200, {
                "success": True,
                "keywords": [c["valor"] for c in criteria],
                "criteria": criteria
            })
        else:
            self.responder_json(404, {"error": "Ruta no encontrada"})


def run_server(port=5000):
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    server_address = ("", port)
    httpd = ThreadingHTTPServer(server_address, DiarioHandler)
    print(f"\n=======================================================")
    print(f"⚖️ LexMonitor Yucatán iniciado con arquitectura relacional.")
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
    puerto = int(os.getenv("PORT", 5000))
    if len(sys.argv) > 1:
        try:
            puerto = int(sys.argv[1])
        except ValueError:
            pass
    run_server(puerto)

