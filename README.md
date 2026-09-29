# 🏛️ LexMonitor Yucatán — Sistema de Vigilancia Jurídica y Notificaciones

Sistema automatizado multiusuario de monitoreo, cotejo y alertas en tiempo real sobre las publicaciones del **Diario Oficial del Estado de Yucatán**.

La plataforma permite a abogados, despachos y personas interesadas dar seguimiento personalizado a sus expedientes judiciales, partes involucradas y materias legales, recibiendo notificaciones inmediatas por **Correo Electrónico** y **Telegram**.

---

## 🚀 Arquitectura y Tecnologías

- **Backend & API:** Python 3.10+ (Servidor HTTP nativo de alto rendimiento con endpoints REST).
- **Base de Datos:** SQLite Relacional con **SQLAlchemy 2.0 ORM** (`lexmonitor.db`), aislamiento completo entre usuarios y sesiones seguras con tokens criptográficos (HMAC-SHA256).
- **Extracción de Contenido:** PyMuPDF (`fitz`) y `requests` para descarga y análisis inteligente de boletines PDF del Diario Oficial.
- **Frontend:** React 19, Lucide Icons, Tailwind CSS y empaquetador ultrarrápido con `esbuild`.
- **Canales de Alerta:** Integración con API de Telegram Bots y servidor de correo SMTP (Gmail con contraseñas de aplicación, Outlook o servidor propio).

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado en tu computadora:

1. **Python 3.10 o superior**: [python.org/downloads](https://www.python.org/downloads/)
   - *Nota:* En Windows, asegúrate de marcar la casilla *"Add python.exe to PATH"*.
2. **Node.js 18 o superior & npm**: [nodejs.org](https://nodejs.org/)

---

## 🛠️ Instalación y Puesta en Marcha Local

Sigue estos sencillos pasos desde una terminal (PowerShell, Bash o CMD) en la carpeta del proyecto:

### 1. Clonar o abrir el proyecto
```bash
cd c:\Users\eacan\Desktop\Proyectos\Diario
```

### 2. Instalar dependencias de Python
Crea y activa un entorno virtual (opcional pero recomendado) e instala las librerías:
```bash
pip install -r requirements.txt
```
> *Librerías incluidas:* `sqlalchemy`, `pymupdf`, `requests`, `python-dotenv`.

### 3. Instalar dependencias de Frontend
Instala los paquetes necesarios para React y el compilador `esbuild`:
```bash
npm install
```

### 4. Configurar Variables de Entorno (`.env`)
El proyecto incluye un archivo de plantilla llamado `.env.example`. Crea una copia con el nombre `.env`:

**En Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**En Linux / macOS:**
```bash
cp .env.example .env
```

Abre `.env` en tu editor de código y completa los valores:

```ini
# Puerto del servidor web
PORT=5000

# Base de datos relacional (por defecto SQLite)
DATABASE_URL=sqlite:///lexmonitor.db

# Bot de Telegram (Obtenido desde @BotFather en Telegram)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Configuración del correo emisor del sistema (SMTP)
# En Gmail: Activa verificación en 2 pasos y crea una contraseña de aplicación en myaccount.google.com/apppasswords
DEFAULT_SMTP_SENDER_EMAIL=tu_correo_remitente@gmail.com
DEFAULT_SMTP_SENDER_PASSWORD=abcd efgh ijkl mnop
DEFAULT_SMTP_HOST=smtp.gmail.com
DEFAULT_SMTP_PORT=465
DEFAULT_SMTP_USE_SSL=true
```

> 🔒 **Seguridad y Privacidad:** Las credenciales del bot y del correo emisor son gestionadas centralmente por el sistema. Los usuarios individuales **no** configuran contraseñas SMTP ni tokens de bots; cada usuario solo indica a qué correo desea recibir sus alertas o vincula su cuenta personal de Telegram.

### 5. Compilar el Frontend
Genera el paquete optimizado de la interfaz de usuario:
```bash
npm run build
```
*(Si vas a hacer cambios en el código de React en vivo, puedes usar `npm run watch` en otra terminal para compilar automáticamente al guardar).*

### 6. Iniciar el Servidor
Ejecuta el servidor principal:
```bash
python server.py
```

Al iniciar, verás en la consola:
```text
============================================================
🏛️  LexMonitor Yucatán — Servidor Iniciado
============================================================
🌐 URL Local:         http://localhost:5000
📦 Base de Datos:     SQLAlchemy ORM (lexmonitor.db)
🤖 Bot de Telegram:   Vinculación activa con webhook / polling
============================================================
```

¡Listo! Abre tu navegador en **[http://localhost:5000](http://localhost:5000)**.

---

## 💡 Guía de Uso del Sistema

### 1. Autenticación Multiusuario
- Dirígete a la pestaña **"Crear Cuenta"** e ingresa tu Nombre, Correo y Contraseña.
- Inicia sesión. El sistema emite un token de sesión criptográfico con duración de 30 días.
- Cada cuenta cuenta con un espacio aislado: **ningún usuario puede ver los expedientes, búsquedas o notificaciones de otros usuarios**.

### 2. Configurar Criterios de Monitoreo
En la sección **"Criterios de Monitoreo"**:
- Agrega expedientes específicos (ej. `1234/2025`), nombres de personas/empresas (ej. `Constructora Peninsular`) o juzgados.
- Asigna un color distintivo y una etiqueta para identificar rápidamente los hallazgos.

### 3. Vincular Telegram
- Ve a **"Ajustes"**.
- Verás tu código personal de vinculación (ejemplo: `LEX800`).
- Abre Telegram, busca tu bot configurado y envíale el comando:
  ```text
  /vincular LEX800
  ```
- El bot confirmará tu vinculación al instante y tu panel mostrará el estado **"Conectado a Telegram"**.

### 4. Configurar Correo de Notificación
- En **"Ajustes"**, confirma la dirección de correo electrónico donde deseas recibir tus boletines.
- Haz clic en **"Enviar Alerta de Prueba"** para verificar que el envío funciona correctamente tanto a tu correo como a tu Telegram.

### 5. Ejecutar Cotejo de Publicaciones
En la sección **"Cotejo Diario"**:
- Selecciona la fecha del Diario Oficial que deseas cotejar (o la fecha de hoy).
- Pulsa **"Ejecutar Cotejo"**.
- El sistema descargará el PDF oficial de Yucatán, indexará su texto y comparará cada una de tus palabras clave contra los acuerdos publicados.
- Los hallazgos se guardan en tu base de datos y se envían de inmediato a tus canales de notificación activos.

---

## 🗄️ Estructura de la Base de Datos Relacional

El archivo `lexmonitor.db` contiene las siguientes tablas administradas con SQLAlchemy:

| Tabla | Descripción |
| :--- | :--- |
| `users` | Usuarios registrados, nombres, correos y contraseñas con hash PBKDF2. |
| `session_tokens` | Tokens de sesión activos con fecha de expiración. |
| `criteria` | Criterios y palabras clave monitoreadas por cada usuario (aislamiento por `user_id`). |
| `notification_configs` | Preferencias de canales (Email / Telegram) y código personal de vinculación. |
| `telegram_subscribers` | Chat IDs de Telegram vinculados al usuario. |
| `scans` | Registro de ejecuciones de escaneo por fecha y URL del diario oficial. |
| `user_matches` | Coincidencias encontradas para cada usuario con extracto y página del PDF. |
| `system_settings` | Parámetros globales y de configuración. |

---

## 🛑 Resolución de Problemas Comunes

- **Error: `Address already in use` o el puerto 5000 está ocupado:**
  Si cerraste la terminal sin detener el proceso anterior, puedes liberar el puerto en PowerShell ejecutando:
  ```powershell
  Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess | Stop-Process -Force
  ```
  O cambiar el puerto en tu `.env` a `PORT=5001`.

- **Error al compilar JavaScript (`npm run build` falla):**
  Asegúrate de haber corrido `npm install`. Si agregaste nuevos componentes, verifica que no haya errores de sintaxis en `src/App.jsx`.

- **No llegan los correos de prueba:**
  - Verifica que en tu `.env` tengas `DEFAULT_SMTP_HOST=smtp.gmail.com` y `DEFAULT_SMTP_PORT=465`.
  - En Gmail no debes usar tu contraseña personal habitual, sino una **Contraseña de Aplicación de 16 caracteres** generada en Google Account Security.

---

## ⏰ Automatización Diaria Gratuita (Cron Job Externo para Render)

Para que el sistema revise el Diario Oficial automáticamente todos los días hábiles en plataformas como **Render** (sin importar que el servidor esté en modo suspensión):

### 1. Endpoint protegido implementado
El servidor cuenta con un endpoint dedicado que despierta el servicio, ejecuta el cotejo para todos los usuarios activos y despacha las alertas:
* **Ruta:** `POST` o `GET` `/api/cron/scan`
* **Autenticación requerida:** Clave secreta definida en `CRON_SECRET` de tu `.env`.
* **Soporta parámetros:**
  * Header: `X-Cron-Secret: <CRON_SECRET>`
  * O Query string: `?secret=<CRON_SECRET>`
  * *(Opcional)* Fecha específica: `&date=YYYY-MM-DD` (por defecto toma el día actual).

### 2. Configuración en cron-job.org (Gratis)
1. Crea una cuenta gratuita en **[cron-job.org](https://cron-job.org/)**.
2. Haz clic en **Create Cronjob**.
3. Configura los siguientes campos:
   * **Title:** `LexMonitor Yucatán - Escaneo Matutino`
   * **URL:** `https://tu-app.onrender.com/api/cron/scan?secret=lex_cron_2026_secreto`
   * **Schedule:** Cada día a las `08:00` (hora local de Mérida/CDMX), de **Lunes a Viernes**.
4. ¡Listo! A las 8:00 AM, `cron-job.org` enviará la petición, Render se despertará automáticamente, ejecutará el cotejo y enviará los correos y mensajes de Telegram a los abogados correspondientes.

