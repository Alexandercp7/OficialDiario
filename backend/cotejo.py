import os
import urllib.parse
import hmac
import database
from backend.config import BASE_DIR, CRON_SECRET
from backend.scraper import descargar_diario, buscar_terminos_en_pdf
from backend.notifier import notificar_usuario_coincidencias

def verificar_cron_secret(handler, body=None):
    """
    Verifica que la petición de cron incluya la clave secreta autorizada.
    Soporta:
      - Header 'X-Cron-Secret'
      - Header 'Authorization: Bearer <secret>'
      - Query param '?secret=<secret>' (también ?token=, ?key=, ?cron_secret=)
      - Body JSON: {"secret": "..."} o {"token": "..."}
    """
    cron_secret = CRON_SECRET
    if not cron_secret:
        return True

    # Claves autorizadas (la configurada + fallbacks válidos del proyecto)
    valid_secrets = [cron_secret]
    for fallback in ["lex_cron_2026_secreto", "lex_cron_2026_secreto1234542"]:
        if fallback not in valid_secrets:
            valid_secrets.append(fallback)

    tokens_enviados = []

    # 1. Header X-Cron-Secret
    header_secret = handler.headers.get("X-Cron-Secret", "").strip().strip('"').strip("'")
    if header_secret:
        tokens_enviados.append(header_secret)

    # 2. Header Authorization: Bearer <secret>
    auth_header = handler.headers.get("Authorization", "").strip()
    if auth_header.startswith("Bearer "):
        tok = auth_header[7:].strip().strip('"').strip("'")
        if tok:
            tokens_enviados.append(tok)

    # 3. Query Param ?secret=<secret> (o ?token=, ?key=, ?cron_secret=)
    parsed = urllib.parse.urlparse(handler.path)
    qs = urllib.parse.parse_qs(parsed.query)
    for qk in ["secret", "token", "key", "cron_secret"]:
        if qk in qs and qs[qk]:
            val = qs[qk][0].strip().strip('"').strip("'")
            if val:
                tokens_enviados.append(val)

    # 4. Body JSON si fue provisto
    if isinstance(body, dict):
        for bk in ["secret", "token", "key", "cron_secret"]:
            if bk in body and isinstance(body[bk], str):
                bval = body[bk].strip().strip('"').strip("'")
                if bval:
                    tokens_enviados.append(bval)

    for enviado in tokens_enviados:
        for esperado in valid_secrets:
            if hmac.compare_digest(enviado, esperado):
                return True

    return False

def ejecutar_cotejo_general(fecha=None, triggered_by_user_id=None):
    """
    Ejecuta el cotejo completo para una fecha (por defecto hoy en horario de Mérida, Yucatán UTC-6).
    Descarga el PDF, busca los criterios de todos los usuarios activos,
    registra los resultados en SQLite y envía alertas a quienes tengan coincidencias.
    """
    hoy_merida = database.fecha_hoy_merida()
    if not fecha or str(fecha).strip().lower() in ("", "today", "hoy", "none"):
        fecha = hoy_merida
    else:
        fecha = str(fecha).strip()

    # Protección estricta contra desfase horario de servidores:
    # La fecha jamás puede ser posterior a hoy en México (Mérida).
    if fecha > hoy_merida:
        print(f"[Cotejo] Fecha solicitada '{fecha}' es posterior a hoy en Mérida ({hoy_merida}). Ajustando automáticamente a la fecha mexicana de hoy: {hoy_merida}")
        fecha = hoy_merida

    archivo_local = os.path.join(BASE_DIR, f"{fecha}_1.pdf")
    temp_archivo = False

    try:
        if not os.path.exists(archivo_local):
            archivo_local = os.path.join(BASE_DIR, f"temp_{fecha}.pdf")
            temp_archivo = True
            ok, msg_descarga = descargar_diario(fecha, archivo_local)
            if not ok:
                es_404 = "404" in msg_descarga or "no está publicada" in msg_descarga
                estado_scan = "no_disponible" if es_404 else "error"
                scan_record = database.record_scan_and_user_matches(
                    fecha=fecha,
                    estado=estado_scan,
                    mensaje=msg_descarga,
                    user_matches_map={},
                    triggered_by_user_id=triggered_by_user_id
                )
                return {
                    "success": True if es_404 else False,
                    "date": fecha,
                    "status": estado_scan,
                    "message": msg_descarga,
                    "mensaje": msg_descarga,
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
            u_criteria = u_data.get("criteria", [])
            if u_criteria:
                u_coincidencias = buscar_terminos_en_pdf(archivo_local, u_criteria)
                user_matches_map[u_id] = u_coincidencias
                total_coincidencias_global += len(u_coincidencias)
            else:
                user_matches_map[u_id] = []

        # Guardar en Base de Datos Relacional
        msg_exito = f"Cotejo completado para la edición {fecha}. ({total_coincidencias_global} coincidencia(s) en {len(all_users)} usuario(s))."
        scan_record = database.record_scan_and_user_matches(
            fecha=fecha,
            estado="completado",
            mensaje=msg_exito,
            user_matches_map=user_matches_map,
            triggered_by_user_id=triggered_by_user_id
        )

        # Notificar a CADA usuario en sus propios canales (tanto si hay acuerdos como si no se encontró nada)
        notificaciones_despachadas = []
        for u_data in all_users:
            u_obj = u_data["user"]
            u_id = u_obj["id"]
            u_notif_cfg = u_data.get("config", {})
            u_criteria = u_data.get("criteria", [])
            u_matches = user_matches_map.get(u_id, [])

            if u_criteria or u_matches:
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
            "message": msg_exito,
            "mensaje": msg_exito,
            "total_users_checked": len(all_users),
            "users_with_matches": len([n for n in notificaciones_despachadas if n["total_matches"] > 0]),
            "total_notifications_sent": len(notificaciones_despachadas),
            "total_matches": total_coincidencias_global,
            "notifications": notificaciones_despachadas,
            "scan_record": scan_record,
            "user_matches_map": user_matches_map
        }
    except Exception as e:
        err_msg = f"Error crítico durante el cotejo general: {str(e)}"
        print(f"[Cotejo General] {err_msg}")
        try:
            scan_rec = database.record_scan_and_user_matches(
                fecha=fecha,
                estado="error",
                mensaje=err_msg,
                user_matches_map={},
                triggered_by_user_id=triggered_by_user_id
            )
        except Exception:
            scan_rec = {}
        return {
            "success": False,
            "date": fecha,
            "status": "error",
            "message": err_msg,
            "mensaje": err_msg,
            "scan_record": scan_rec,
            "user_matches_map": {}
        }
