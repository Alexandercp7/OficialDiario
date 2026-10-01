import os
import smtplib
import ssl
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import database

def escape_tg_html(text):
    """Escapa caracteres especiales para mensajes HTML de Telegram y correos."""
    if not text:
        return ""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def enviar_notificacion_email(config_email, asunto, mensaje_texto, mensaje_html):
    """Envía un correo mediante Brevo REST API, Resend API (HTTPS) o SMTP oficial del sistema."""
    try:
        recipient_raw = (config_email.get("recipient_email") or "").strip()
        if not recipient_raw:
            return False, "No se especificó un correo de destinatario válido."

        recipients = [r.strip() for r in recipient_raw.replace(";", ",").split(",") if r.strip()]
        if not recipients:
            return False, "No se especificó un correo de destinatario válido."

        # 1. Si existe BREVO_API_KEY configurada, enviar vía Brevo REST API
        brevo_api_key = os.getenv("BREVO_API_KEY", "").strip()
        if brevo_api_key:
            sys_smtp = database.get_system_smtp_config()
            sender_email = (os.getenv("BREVO_SENDER_EMAIL") or sys_smtp.get("sender_email") or "alexitoelegante@gmail.com").strip()
            sender_name = os.getenv("BREVO_SENDER_NAME", "LexMonitor Yucatán").strip()
            payload = {
                "sender": {"name": sender_name, "email": sender_email},
                "to": [{"email": r} for r in recipients],
                "subject": asunto,
                "htmlContent": mensaje_html,
                "textContent": mensaje_texto
            }
            headers = {
                "accept": "application/json",
                "api-key": brevo_api_key,
                "content-type": "application/json"
            }
            resp = requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers, timeout=15)
            if resp.status_code in (200, 201):
                return True, f"Correo enviado exitosamente vía Brevo a {len(recipients)} destinatario(s)."
            else:
                try:
                    err_json = resp.json()
                    err_msg = err_json.get("message", resp.text)
                except Exception:
                    err_msg = resp.text
                return False, f"Error en Brevo API ({resp.status_code}): {err_msg} (Remitente: '{sender_email}')"

        # 2. Si existe RESEND_API_KEY configurada, enviar vía Resend HTTP API
        resend_api_key = os.getenv("RESEND_API_KEY", "").strip()
        if resend_api_key:
            raw_from = os.getenv("RESEND_FROM_EMAIL", "").strip().strip('"').strip("'")
            if not raw_from or "@" not in raw_from:
                from_email = "onboarding@resend.dev"
            elif "<" in raw_from and ">" in raw_from:
                name_part, email_part = raw_from.split("<", 1)
                email_clean = email_part.replace(">", "").strip()
                name_clean = "".join(c for c in name_part if c.isascii() and (c.isalnum() or c in " .-_")).strip()
                from_email = f"{name_clean} <{email_clean}>" if name_clean else email_clean
            else:
                from_email = raw_from

            # Resend no permite enviar desde dominios gratuitos no verificados (como @gmail.com)
            freemails = ["@gmail.", "@yahoo.", "@hotmail.", "@outlook.", "@live.", "@icloud."]
            if any(fm in from_email.lower() for fm in freemails):
                from_email = "onboarding@resend.dev"

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
                return False, f"Error en Resend API ({resp.status_code}): {err_msg} (Remitente: '{from_email}')"

        # 3. Si no hay Brevo ni Resend, intentar mediante SMTP tradicional
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

def enviar_mensaje_telegram(bot_token, chat_id, mensaje):
    """Envía un mensaje de texto formateado con HTML a través del Bot API de Telegram."""
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
        juz_txt = f" [{c.get('juzgado')}]" if c.get('juzgado') else ""
        texto_plano += f"{i}. Término: {c.get('termino')}{juz_txt} (Pág. {c.get('pagina')})\n"
        texto_plano += f"   Extracto: {c.get('contexto')}\n\n"
    texto_plano += f"Descargar edición completa: {enlace_pdf}\n\nLexMonitor Yucatán"

    filas_html = ""
    for i, c in enumerate(coincidencias, 1):
        termino_esc = escape_tg_html(c.get('termino', ''))
        juzgado_esc = escape_tg_html(c.get('juzgado', 'Poder Judicial de Yucatán'))
        contexto_esc = escape_tg_html(c.get('contexto', ''))
        filas_html += f"""
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #2563eb; border-radius: 8px; padding: 14px; margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 6px;">
                <span style="background-color: #e0e7ff; color: #1e40af; font-weight: bold; font-family: monospace; font-size: 13px; padding: 3px 8px; border-radius: 4px;">
                    {termino_esc}
                </span>
                <span style="background-color: #ffffff; color: #0f172a; font-weight: 600; font-size: 11.5px; padding: 2px 8px; border-radius: 4px; border: 1px solid #cbd5e1;">
                    🏛️ {juzgado_esc}
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
                juz_txt = f" | 🏛️ {escape_tg_html(c.get('juzgado', ''))}" if c.get('juzgado') else ""
                msg_tg.append(f"<b>{i}. {escape_tg_html(c.get('termino'))}</b>{juz_txt} (Pág. {c.get('pagina')})")
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
