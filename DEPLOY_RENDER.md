# 🚀 Guía Completa de Despliegue en Render — LexMonitor Yucatán

Esta guía te explica paso a paso cómo desplegar todo el sistema (**Backend en Python**, **Frontend en React**, **Base de Datos PostgreSQL** y el **Bot de Telegram**) en la nube de **[Render](https://render.com/)**.

---

## 🌟 Novedades Implementadas

1. **Aviso cuando el bot no encuentra nada:**
   - Si se ejecuta el cotejo matutino o manual y **no se detectan acuerdos** para los expedientes del usuario, el sistema ahora envía automáticamente un mensaje claro por **Telegram** y/o **Correo**:
     > *"⚖️ LexMonitor Yucatán: El bot revisó la edición de hoy del Diario Oficial del Estado y no ha encontrado acuerdos ni publicaciones para tus expedientes o términos registrados. Todo se encuentra al día y sin novedades procesales hoy."*
2. **Archivos de despliegue listos para Render:**
   - [`render.yaml`](file:///c:/Users/eacan/Desktop/Proyectos/Diario/render.yaml): Blueprint para despliegue automático con 1 solo clic.
   - [`Dockerfile`](file:///c:/Users/eacan/Desktop/Proyectos/Diario/Dockerfile): Contenedor multi-stage optimizado (Node 20 + Python 3.11).
   - [`build.sh`](file:///c:/Users/eacan/Desktop/Proyectos/Diario/build.sh): Script de compilación si prefieres el entorno nativo de Python en Render.

---

## 🛠️ Opción 1: Despliegue Automático con Blueprint (Recomendada)

Render cuenta con la función **Blueprints**, que lee el archivo `render.yaml` y configura tanto el **Web Service** como la **Base de Datos PostgreSQL** de forma 100% automática.

### Pasos:
1. **Sube tus cambios a GitHub:**
   ```bash
   git add .
   git commit -m "feat: soporte para render y aviso de no coincidencias"
   git push origin main
   ```
2. Entra a tu cuenta en **[dashboard.render.com](https://dashboard.render.com/)**.
3. Haz clic en el botón **New +** (arriba a la derecha) y selecciona **Blueprint**.
4. Conecta tu repositorio de GitHub `OficialDiario` (o el nombre de tu repo).
5. Render detectará el archivo [`render.yaml`](file:///c:/Users/eacan/Desktop/Proyectos/Diario/render.yaml) y te mostrará:
   - **Web Service:** `lexmonitor-yucatan` (usando Docker).
   - **Database:** `lexmonitor-db` (PostgreSQL administrado gratuito).
6. Haz clic en **Apply**.
7. En la pestaña de configuración del Web Service, agrega tus variables secretas:
   - `TELEGRAM_BOT_TOKEN`: El token que te dio `@BotFather`.
   - `BREVO_API_KEY` o `RESEND_API_KEY`: Tu clave para envío de correos (o las variables SMTP si usas Gmail).
8. ¡Listo! Render compilará el frontend, preparará el backend y te entregará tu URL pública: `https://lexmonitor-yucatan.onrender.com`.

---

## 🚢 Opción 2: Despliegue Manual como Web Service

Si prefieres crearlo manualmente desde el panel de Render:

1. Ve a **New +** ➡️ **Web Service**.
2. Conecta tu repositorio de GitHub.
3. Elige el método de runtime:
   - **Recomendado (Docker):**
     - **Runtime:** `Docker`
     - Render detectará el [`Dockerfile`](file:///c:/Users/eacan/Desktop/Proyectos/Diario/Dockerfile) automáticamente.
   - **O Nativo de Python:**
     - **Runtime:** `Python 3`
     - **Build Command:** `./build.sh`
     - **Start Command:** `python server.py`
4. En **Environment Variables**, agrega:
   | Variable | Valor / Descripción |
   | :--- | :--- |
   | `PORT` | `5000` *(Render inyecta su propio puerto si es necesario)* |
   | `DATABASE_URL` | La URL de tu base de datos PostgreSQL en Render (ej. `postgresql://...`) o déjala vacía para usar SQLite local |
   | `TELEGRAM_BOT_TOKEN` | Token de tu bot en Telegram |
   | `CRON_SECRET` | Clave secreta para autorizar el escaneo automático (ej. `lex_cron_2026_secreto`) |
   | `BREVO_API_KEY` o `RESEND_API_KEY` | *(Opcional)* Clave API para enviar correos sin problemas de puertos SMTP |
5. Haz clic en **Deploy Web Service**.

---

## ⏰ Programación Diaria Gratuita (Cron Job)

Dado que las instancias gratuitas de Render se suspenden tras 15 minutos de inactividad, puedes despertarla y ejecutar la revisión matutina sin costo usando **[cron-job.org](https://cron-job.org/)**:

1. Crea una cuenta gratis en **[cron-job.org](https://cron-job.org/)**.
2. Haz clic en **Create Cronjob**.
3. Configura:
   - **Title:** `LexMonitor Yucatán - Revisión Diaria`
   - **URL:** `https://tu-servicio.onrender.com/api/cron/scan?secret=TU_CRON_SECRET`
   - **Schedule:** De Lunes a Viernes a las `08:00` (Hora de Mérida / CDMX).
4. Guarda el cronjob.

Cada mañana a las 8:00 AM:
- Si hay acuerdos: el bot enviará la lista con los expedientes, página y extracto.
- Si no hay acuerdos: el bot enviará el mensaje avisando que revisó el boletín y no hay nada publicado hoy para tus expedientes.
