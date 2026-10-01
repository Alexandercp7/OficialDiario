import os
import json
import datetime
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler
import database
from backend.config import PUBLIC_DIR
from backend.juzgados import LISTA_JUZGADOS_YUCATAN
from backend.notifier import enviar_notificacion_email, enviar_mensaje_telegram, escape_tg_html
from backend.telegram_bot import telegram_bot
from backend.cotejo import verificar_cron_secret, ejecutar_cotejo_general

class DiarioHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Cron-Secret")
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
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
            })
            return

        if path == "/api/cron/scan":
            if not verificar_cron_secret(self):
                print(f"[Cron GET] Petición no autorizada desde {self.client_address[0]}")
                self.responder_json(401, {
                    "success": False,
                    "error": "No autorizado. Token de cron inválido o ausente. Usa ?secret=<CRON_SECRET> o header X-Cron-Secret."
                })
                return

            parsed_qs = urllib.parse.parse_qs(parsed.query)
            fecha = parsed_qs.get("date", [None])[0]
            is_async = parsed_qs.get("async", ["false"])[0].lower() in ("true", "1", "yes")

            print(f"[Cron GET] Ejecución solicitada para fecha: {fecha or 'hoy'} (Hora Mérida: {database.ahora_merida().strftime('%H:%M:%S')})")

            try:
                if is_async:
                    # Responder inmediatamente y procesar en segundo plano
                    threading.Thread(
                        target=ejecutar_cotejo_general,
                        kwargs={"fecha": fecha, "triggered_by_user_id": None},
                        daemon=True
                    ).start()
                    self.responder_json(200, {
                        "success": True,
                        "message": "Cotejo programado iniciado en segundo plano exitosamente.",
                        "mode": "async",
                        "fecha": fecha or database.fecha_hoy_merida()
                    })
                    return

                resultado = ejecutar_cotejo_general(fecha=fecha, triggered_by_user_id=None)
                status_http = 200 if resultado.get("success") else 500
                self.responder_json(status_http, resultado)
                return
            except Exception as e:
                print(f"[Cron GET] Error inesperado: {e}")
                self.responder_json(500, {
                    "success": False,
                    "status": "error",
                    "error": f"Error interno en ejecución de cron: {str(e)}"
                })
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

        if path == "/api/juzgados":
            self.responder_json(200, {
                "success": True,
                "juzgados": LISTA_JUZGADOS_YUCATAN
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
            if not verificar_cron_secret(self, body=body):
                print(f"[Cron POST] Petición no autorizada desde {self.client_address[0]}")
                self.responder_json(401, {
                    "success": False,
                    "error": "No autorizado. Token de cron inválido o ausente. Usa ?secret=<CRON_SECRET> o header X-Cron-Secret."
                })
                return

            parsed_qs = urllib.parse.parse_qs(parsed.query)
            fecha = body.get("date")
            if not fecha:
                fecha = parsed_qs.get("date", [None])[0]
            is_async = body.get("async", False) or parsed_qs.get("async", ["false"])[0].lower() in ("true", "1", "yes")

            print(f"[Cron POST] Ejecución solicitada para fecha: {fecha or 'hoy'} (Hora Mérida: {database.ahora_merida().strftime('%H:%M:%S')})")

            try:
                if is_async:
                    threading.Thread(
                        target=ejecutar_cotejo_general,
                        kwargs={"fecha": fecha, "triggered_by_user_id": None},
                        daemon=True
                    ).start()
                    self.responder_json(200, {
                        "success": True,
                        "message": "Cotejo programado iniciado en segundo plano exitosamente.",
                        "mode": "async",
                        "fecha": fecha or database.fecha_hoy_merida()
                    })
                    return

                resultado = ejecutar_cotejo_general(fecha=fecha, triggered_by_user_id=None)
                status_http = 200 if resultado.get("success") else 500
                self.responder_json(status_http, resultado)
                return
            except Exception as e:
                print(f"[Cron POST] Error inesperado: {e}")
                self.responder_json(500, {
                    "success": False,
                    "status": "error",
                    "error": f"Error interno en ejecución de cron: {str(e)}"
                })
                return

        # ----------------- ENDPOINTS QUE REQUIEREN USUARIO AUTENTICADO -----------------
        user = self.get_current_user()
        if not user:
            self.responder_json(401, {"error": "Debes iniciar sesión para realizar esta acción."})
            return

        if path == "/api/keywords":
            kw = body.get("keyword", "").strip()
            juzgado = body.get("juzgado", "Todos los Juzgados").strip()
            tipo = body.get("tipo", "").strip()
            if not tipo:
                tipo = "Expediente" if ("/" in kw and any(ch.isdigit() for ch in kw)) else "Nombre / Frase"
            if not kw:
                self.responder_json(400, {"error": "El término o número de expediente no puede estar vacío."})
                return

            c_dict, err = database.add_user_criterion(user["id"], tipo, kw, juzgado=juzgado)
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
            if not resultado.get("success") or resultado.get("status") == "no_disponible":
                scan_rec = resultado.get("scan_record", {})
                self.responder_json(200, {
                    **scan_rec,
                    "coincidencias": [],
                    "total_coincidencias": 0,
                    "estado": resultado.get("status", "error"),
                    "mensaje": resultado.get("message") or resultado.get("mensaje") or "La edición no está disponible aún."
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
            crit_id = body.get("id")
            database.delete_user_criterion(user["id"], valor=kw, criterion_id=crit_id)
            criteria = database.get_user_criteria(user["id"])
            self.responder_json(200, {
                "success": True,
                "keywords": [c["valor"] for c in criteria],
                "criteria": criteria
            })
        else:
            self.responder_json(404, {"error": "Ruta no encontrada"})
