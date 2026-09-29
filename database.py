import os
import sys
import secrets
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
from contextlib import contextmanager
from dotenv import load_dotenv

from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Boolean,
    DateTime, ForeignKey, select, update, delete
)
from sqlalchemy.orm import (
    declarative_base, relationship, sessionmaker, Session
)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Cargar variables de entorno desde .env
load_dotenv(os.path.join(BASE_DIR, ".env"))

DB_FILE = os.path.join(BASE_DIR, "lexmonitor.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_FILE}")

# Render provee URLs que comienzan con postgres://, SQLAlchemy 2.0 requiere postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionFactory = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()

@contextmanager
def get_session():
    """Context manager para sesiones SQLAlchemy seguras y aisladas."""
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# ========================================================
# MODELOS DE BASE DE DATOS
# ========================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    salt = Column(String(64), nullable=False)
    telegram_chat_id = Column(String(64), nullable=True, index=True)
    telegram_username = Column(String(64), nullable=True)
    link_code = Column(String(16), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    criteria = relationship("Criterion", back_populates="user", cascade="all, delete-orphan")
    notification_config = relationship("NotificationConfig", back_populates="user", uselist=False, cascade="all, delete-orphan")
    matches = relationship("UserMatch", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("SessionToken", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "telegram_chat_id": self.telegram_chat_id,
            "telegram_username": self.telegram_username,
            "link_code": self.link_code,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }


class Criterion(Base):
    __tablename__ = "criteria"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo = Column(String(32), default="Expediente", nullable=False)
    valor = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="criteria")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "tipo": self.tipo,
            "valor": self.valor,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }


class NotificationConfig(Base):
    __tablename__ = "notification_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    channel = Column(String(32), default="email")
    recipient_email = Column(String(120), nullable=True)
    sender_email = Column(String(120), nullable=True)
    sender_password = Column(String(120), nullable=True)
    smtp_host = Column(String(120), default="smtp.gmail.com")
    smtp_port = Column(Integer, default=465)
    use_ssl = Column(Boolean, default=True)

    user = relationship("User", back_populates="notification_config")

    def to_dict(self):
        return {
            "channel": self.channel or "email",
            "email": {
                "recipient_email": self.recipient_email or "",
                "sender_email": self.sender_email or "",
                "sender_password": self.sender_password or "",
                "smtp_host": self.smtp_host or "smtp.gmail.com",
                "smtp_port": self.smtp_port or 465,
                "use_ssl": self.use_ssl if self.use_ssl is not None else True
            }
        }


class SessionToken(Base):
    __tablename__ = "session_tokens"

    token = Column(String(64), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="sessions")

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(String(32), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    estado = Column(String(32), default="completado")
    mensaje = Column(Text, nullable=True)
    triggered_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    matches = relationship("UserMatch", back_populates="scan", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "fecha": self.fecha,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None,
            "estado": self.estado,
            "mensaje": self.mensaje
        }


class UserMatch(Base):
    __tablename__ = "user_matches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_id = Column(Integer, ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    criterion_id = Column(Integer, ForeignKey("criteria.id", ondelete="SET NULL"), nullable=True)
    termino = Column(String(256), nullable=False)
    pagina = Column(Integer, nullable=False)
    contexto = Column(Text, nullable=False)
    notificado = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    scan = relationship("Scan", back_populates="matches")
    user = relationship("User", back_populates="matches")

    def to_dict(self):
        return {
            "id": self.id,
            "scan_id": self.scan_id,
            "termino": self.termino,
            "pagina": self.pagina,
            "contexto": self.contexto,
            "notificado": self.notificado,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }


class TelegramSubscriber(Base):
    __tablename__ = "telegram_subscribers"

    chat_id = Column(String(64), primary_key=True)
    first_name = Column(String(120), nullable=True)
    username = Column(String(120), nullable=True)
    email = Column(String(120), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    subscribed_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "chat_id": self.chat_id,
            "first_name": self.first_name or "",
            "username": self.username or "",
            "email": self.email or "",
            "user_id": self.user_id,
            "subscribed_at": self.subscribed_at.strftime("%Y-%m-%d %H:%M:%S") if self.subscribed_at else None
        }


class SystemSetting(Base):
    __tablename__ = "system_settings"

    key = Column(String(64), primary_key=True)
    value = Column(Text, nullable=True)


# ========================================================
# SEGURIDAD Y HASHING
# ========================================================

def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        bytes.fromhex(salt),
        100000
    ).hex()
    return hashed, salt

def verify_password(password: str, salt: str, stored_hash: str) -> bool:
    if not password or not salt or not stored_hash:
        return False
    calc_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        bytes.fromhex(salt),
        100000
    ).hex()
    return hmac.compare_digest(calc_hash, stored_hash)

def generate_link_code() -> str:
    return secrets.token_hex(3).upper()


# ========================================================
# GESTIÓN DE USUARIOS Y AUTENTICACIÓN
# ========================================================

def create_user(name: str, email: str, password: str) -> Tuple[Optional[dict], Optional[str]]:
    email_clean = email.strip().lower()
    name_clean = name.strip()
    if not email_clean or not password or not name_clean:
        return None, "Todos los campos (nombre, correo y contraseña) son obligatorios."
    if len(password) < 6:
        return None, "La contraseña debe tener al menos 6 caracteres."

    with get_session() as session:
        existing = session.execute(select(User).where(User.email == email_clean)).scalar_one_or_none()
        if existing:
            return None, "Ya existe una cuenta registrada con este correo electrónico."

        pwd_hash, salt = hash_password(password)
        new_user = User(
            name=name_clean,
            email=email_clean,
            password_hash=pwd_hash,
            salt=salt,
            link_code=generate_link_code()
        )
        session.add(new_user)
        session.flush()

        notif_cfg = NotificationConfig(
            user_id=new_user.id,
            channel="email",
            recipient_email=email_clean,
            sender_email="",
            sender_password="",
            smtp_host="smtp.gmail.com",
            smtp_port=465,
            use_ssl=True
        )
        session.add(notif_cfg)

        # Criterio inicial de ejemplo para orientar al nuevo usuario
        sample_criterion = Criterion(
            user_id=new_user.id,
            tipo="Expediente",
            valor="800/2026"
        )
        session.add(sample_criterion)
        session.flush()

        user_dict = new_user.to_dict()
        return user_dict, None

def authenticate_user(email: str, password: str) -> Tuple[Optional[dict], Optional[str]]:
    email_clean = email.strip().lower()
    if not email_clean or not password:
        return None, "Introduce tu correo y contraseña."

    with get_session() as session:
        user = session.execute(select(User).where(User.email == email_clean)).scalar_one_or_none()
        if not user:
            return None, "No existe ninguna cuenta asociada a este correo electrónico."

        if not verify_password(password, user.salt, user.password_hash):
            return None, "Contraseña incorrecta."

        return user.to_dict(), None

def create_session_token(user_id: int, days_valid: int = 30) -> str:
    with get_session() as session:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=days_valid)
        st = SessionToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at
        )
        session.add(st)
        return token

def get_user_by_token(token: str) -> Optional[dict]:
    if not token:
        return None
    with get_session() as session:
        st = session.execute(
            select(SessionToken).where(SessionToken.token == token)
        ).scalar_one_or_none()
        if not st or st.is_expired():
            return None
        user = session.execute(select(User).where(User.id == st.user_id)).scalar_one_or_none()
        return user.to_dict() if user else None

def delete_session_token(token: str):
    if not token:
        return
    with get_session() as session:
        session.execute(delete(SessionToken).where(SessionToken.token == token))


# ========================================================
# GESTIÓN DE CRITERIOS POR USUARIO
# ========================================================

def get_user_criteria(user_id: int) -> List[dict]:
    with get_session() as session:
        rows = session.execute(
            select(Criterion).where(Criterion.user_id == user_id).order_by(Criterion.id.asc())
        ).scalars().all()
        return [r.to_dict() for r in rows]

def add_user_criterion(user_id: int, tipo: str, valor: str) -> Tuple[Optional[dict], Optional[str]]:
    val_clean = valor.strip()
    if not val_clean:
        return None, "El valor del criterio no puede estar vacío."

    with get_session() as session:
        existing = session.execute(
            select(Criterion).where(
                Criterion.user_id == user_id,
                Criterion.valor == val_clean
            )
        ).scalar_one_or_none()

        if existing:
            return existing.to_dict(), None

        c = Criterion(
            user_id=user_id,
            tipo=tipo if tipo in ("Expediente", "Nombre", "Empresa") else "Expediente",
            valor=val_clean
        )
        session.add(c)
        session.flush()
        return c.to_dict(), None

def delete_user_criterion(user_id: int, valor: str) -> bool:
    with get_session() as session:
        session.execute(
            delete(Criterion).where(
                Criterion.user_id == user_id,
                Criterion.valor == valor.strip()
            )
        )
        return True


# ========================================================
# GESTIÓN DE CONFIGURACIÓN Y NOTIFICACIONES
# ========================================================

def get_user_notification_config(user_id: int) -> dict:
    with get_session() as session:
        cfg = session.execute(
            select(NotificationConfig).where(NotificationConfig.user_id == user_id)
        ).scalar_one_or_none()

        if not cfg:
            user = session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
            cfg = NotificationConfig(
                user_id=user_id,
                channel="email",
                recipient_email=user.email if user else "",
                smtp_host="smtp.gmail.com",
                smtp_port=465,
                use_ssl=True
            )
            session.add(cfg)
            session.flush()
        return cfg.to_dict()

def update_user_notification_config(user_id: int, payload: dict) -> bool:
    with get_session() as session:
        cfg = session.execute(
            select(NotificationConfig).where(NotificationConfig.user_id == user_id)
        ).scalar_one_or_none()

        if not cfg:
            cfg = NotificationConfig(user_id=user_id)
            session.add(cfg)

        if "channel" in payload:
            cfg.channel = payload["channel"]

        email_data = payload.get("email", {})
        if email_data and "recipient_email" in email_data:
            cfg.recipient_email = email_data["recipient_email"].strip()

        return True

def unlink_user_telegram(user_id: int) -> bool:
    with get_session() as session:
        user = session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
        if user:
            user.telegram_chat_id = None
            user.telegram_username = None
            return True
        return False


# ========================================================
# CONFIGURACIÓN DEL SISTEMA (TELEGRAM BOT Y GLOBAL DESDE .ENV)
# ========================================================

def get_system_setting(key: str, default: str = "") -> str:
    with get_session() as session:
        row = session.execute(
            select(SystemSetting).where(SystemSetting.key == key)
        ).scalar_one_or_none()
        if row and row.value is not None and row.value.strip():
            return row.value.strip()

    # Mapeo a variables de entorno de .env
    env_map = {
        "smtp_sender_email": os.getenv("DEFAULT_SMTP_SENDER_EMAIL", ""),
        "smtp_sender_password": os.getenv("DEFAULT_SMTP_SENDER_PASSWORD", ""),
        "smtp_host": os.getenv("DEFAULT_SMTP_HOST", "smtp.gmail.com"),
        "smtp_port": os.getenv("DEFAULT_SMTP_PORT", "465"),
        "smtp_use_ssl": os.getenv("DEFAULT_SMTP_USE_SSL", "true"),
        "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN", "")
    }
    return env_map.get(key, os.getenv(key.upper(), default))

def set_system_setting(key: str, value: str):
    with get_session() as session:
        row = session.execute(
            select(SystemSetting).where(SystemSetting.key == key)
        ).scalar_one_or_none()
        if row:
            row.value = value
        else:
            row = SystemSetting(key=key, value=value)
            session.add(row)

def get_system_smtp_config() -> dict:
    """Retorna la configuración por defecto de correo del sistema (cargada desde .env o base de datos)."""
    return {
        "sender_email": get_system_setting("smtp_sender_email"),
        "sender_password": get_system_setting("smtp_sender_password"),
        "smtp_host": get_system_setting("smtp_host", "smtp.gmail.com"),
        "smtp_port": int(get_system_setting("smtp_port", "465")),
        "use_ssl": str(get_system_setting("smtp_use_ssl", "true")).lower() in ("true", "1", "yes")
    }



def get_telegram_subscribers() -> List[dict]:
    with get_session() as session:
        rows = session.execute(
            select(TelegramSubscriber).order_by(TelegramSubscriber.subscribed_at.desc())
        ).scalars().all()
        return [r.to_dict() for r in rows]

def upsert_telegram_subscriber(chat_id: str, first_name: str, username: str, email: str = "", user_id: Optional[int] = None):
    with get_session() as session:
        cid = str(chat_id).strip()
        sub = session.execute(
            select(TelegramSubscriber).where(TelegramSubscriber.chat_id == cid)
        ).scalar_one_or_none()
        if sub:
            sub.first_name = first_name
            sub.username = username
            if email:
                sub.email = email
            if user_id:
                sub.user_id = user_id
        else:
            sub = TelegramSubscriber(
                chat_id=cid,
                first_name=first_name,
                username=username,
                email=email,
                user_id=user_id
            )
            session.add(sub)

def delete_telegram_subscriber(chat_id: str) -> bool:
    with get_session() as session:
        session.execute(
            delete(TelegramSubscriber).where(TelegramSubscriber.chat_id == str(chat_id).strip())
        )
        return True

def link_telegram_to_user_by_code_or_email(chat_id: str, identifier: str, first_name: str, username: str) -> Tuple[bool, str]:
    """
    Permite a un usuario vincular su bot de Telegram enviando /vincular <codigo> o /correo <email>.
    """
    clean_id = identifier.strip().lower()
    with get_session() as session:
        user = session.execute(
            select(User).where(
                (User.link_code == identifier.strip().upper()) |
                (User.email == clean_id)
            )
        ).scalar_one_or_none()

        if not user:
            return False, f"No se encontró ninguna cuenta registrada con el código o correo '{identifier}'."

        user.telegram_chat_id = str(chat_id).strip()
        user.telegram_username = username
        
        # También registrar en suscriptores
        sub = session.execute(
            select(TelegramSubscriber).where(TelegramSubscriber.chat_id == str(chat_id).strip())
        ).scalar_one_or_none()
        if sub:
            sub.user_id = user.id
            sub.email = user.email
            sub.first_name = first_name
            sub.username = username
        else:
            sub = TelegramSubscriber(
                chat_id=str(chat_id).strip(),
                first_name=first_name,
                username=username,
                email=user.email,
                user_id=user.id
            )
            session.add(sub)

        return True, f"¡Excelente! Tu cuenta de Telegram ha sido vinculada al usuario <b>{user.name}</b> ({user.email}). Recibirás tus avisos judiciales aquí."


# ========================================================
# HISTORIAL Y RESULTADOS MULTI-USUARIO
# ========================================================

def get_user_history(user_id: int, limit: int = 30) -> List[dict]:
    with get_session() as session:
        scans = session.execute(
            select(Scan).order_by(Scan.timestamp.desc()).limit(limit)
        ).scalars().all()

        history_list = []
        for s in scans:
            u_matches = session.execute(
                select(UserMatch).where(
                    UserMatch.scan_id == s.id,
                    UserMatch.user_id == user_id
                )
            ).scalars().all()

            history_list.append({
                "id": s.id,
                "fecha": s.fecha,
                "timestamp": s.timestamp.strftime("%Y-%m-%d %H:%M:%S") if s.timestamp else None,
                "estado": s.estado,
                "mensaje": s.mensaje,
                "total_coincidencias": len(u_matches),
                "coincidencias": [m.to_dict() for m in u_matches]
            })

        return history_list

def record_scan_and_user_matches(
    fecha: str,
    estado: str,
    mensaje: str,
    user_matches_map: Dict[int, List[dict]],
    triggered_by_user_id: Optional[int] = None
) -> dict:
    with get_session() as session:
        scan = Scan(
            fecha=fecha,
            timestamp=datetime.utcnow(),
            estado=estado,
            mensaje=mensaje,
            triggered_by_user_id=triggered_by_user_id
        )
        session.add(scan)
        session.flush()

        for uid, matches in user_matches_map.items():
            for m in matches:
                um = UserMatch(
                    scan_id=scan.id,
                    user_id=uid,
                    termino=m.get("termino", ""),
                    pagina=int(m.get("pagina", 1)),
                    contexto=m.get("contexto", ""),
                    notificado=m.get("notificado", False)
                )
                session.add(um)

        session.flush()
        return scan.to_dict()

def get_all_active_users_data() -> List[dict]:
    """
    Retorna la lista de todos los usuarios con sus criterios y configs de notificación
    para realizar la búsqueda y despacho de notificaciones personalizadas.
    """
    with get_session() as session:
        users = session.execute(select(User)).scalars().all()
        result = []
        for u in users:
            cfg = session.execute(
                select(NotificationConfig).where(NotificationConfig.user_id == u.id)
            ).scalar_one_or_none()
            criteria_rows = session.execute(
                select(Criterion).where(Criterion.user_id == u.id)
            ).scalars().all()

            result.append({
                "user": u.to_dict(),
                "config": cfg.to_dict() if cfg else {},
                "criteria": [c.to_dict() for c in criteria_rows]
            })
        return result


# ========================================================
# INICIALIZACIÓN DE BASE DE DATOS
# ========================================================

def init_db():
    Base.metadata.create_all(engine)
    print("📦 Base de datos relacional SQLite inicializada con éxito (lexmonitor.db).")

if __name__ == "__main__":
    init_db()

