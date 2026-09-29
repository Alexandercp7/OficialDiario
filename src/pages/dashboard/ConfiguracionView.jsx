import React, { useState, useEffect } from 'react';
import { Mail, Send, Zap, Check, RefreshCw, Copy, ExternalLink } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useData } from '../../context/DataContext';

export default function ConfiguracionView() {
  const { currentUser, authFetch } = useAuth();
  const { appData, refreshData } = useData();

  const notifConfig = appData?.notifications || {};
  const emailCfg = notifConfig.email || {};

  const [channel, setChannel] = useState(notifConfig.channel || 'email');
  const [recipientEmail, setRecipientEmail] = useState(emailCfg.recipient_email || currentUser?.email || '');
  
  const [botInfo, setBotInfo] = useState(null);
  const [userLinked, setUserLinked] = useState(false);
  const [telegramUsername, setTelegramUsername] = useState('');
  const [linkCode, setLinkCode] = useState(currentUser?.link_code || '');

  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [statusMsg, setStatusMsg] = useState(null);
  const [copiedCode, setCopiedCode] = useState(false);

  // Sincronizar recipientEmail con appData o currentUser cuando estén listos
  useEffect(() => {
    if (emailCfg.recipient_email) {
      setRecipientEmail(emailCfg.recipient_email);
    } else if (currentUser?.email && !recipientEmail) {
      setRecipientEmail(currentUser.email);
    }
    if (notifConfig.channel) {
      setChannel(notifConfig.channel);
    }
  }, [emailCfg.recipient_email, notifConfig.channel, currentUser?.email]);

  // Cargar estado de Telegram del usuario y del Bot oficial
  const fetchTelegramStatus = async () => {
    try {
      const res = await authFetch('/api/telegram/status');
      if (res.ok) {
        const d = await res.json();
        setBotInfo(d.bot_info);
        setUserLinked(Boolean(d.user_linked));
        if (d.telegram_username) setTelegramUsername(d.telegram_username);
        if (d.user_link_code) setLinkCode(d.user_link_code);
      }
    } catch (e) {
      console.error('Error fetching tg status:', e);
    }
  };

  useEffect(() => {
    fetchTelegramStatus();
  }, []);

  const emailEnabled = channel === 'email' || channel === 'both' || channel === 'all';
  const telegramEnabled = channel === 'telegram' || channel === 'both' || channel === 'all';

  const toggleEmail = () => {
    if (emailEnabled) {
      setChannel(telegramEnabled ? 'telegram' : 'none');
    } else {
      setChannel(telegramEnabled ? 'both' : 'email');
    }
  };

  const toggleTelegram = () => {
    if (telegramEnabled) {
      setChannel(emailEnabled ? 'email' : 'none');
    } else {
      setChannel(emailEnabled ? 'both' : 'telegram');
    }
  };

  const handleCopyCode = () => {
    navigator.clipboard.writeText(`/vincular ${linkCode || currentUser?.email}`);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2500);
  };

  // Desvincular Telegram del usuario
  const handleUnlinkTelegram = async () => {
    try {
      const res = await authFetch('/api/telegram/unlink', { method: 'POST' });
      if (res.ok) {
        setUserLinked(false);
        setTelegramUsername('');
        setStatusMsg({ type: 'success', text: 'Cuenta de Telegram desvinculada exitosamente.' });
        await refreshData();
      }
    } catch (e) {
      console.error('Error desvinculando telegram:', e);
    }
  };

  // Guardar configuración del usuario
  const handleSave = async () => {
    setSaving(true);
    setStatusMsg(null);

    const payload = {
      notifications: {
        channel: channel,
        email: {
          recipient_email: recipientEmail.trim()
        }
      }
    };

    try {
      const res = await authFetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (res.ok) {
        setStatusMsg({ type: 'success', text: 'Tus preferencias de notificación se han guardado exitosamente.' });
        await refreshData();
        await fetchTelegramStatus();
      } else {
        throw new Error(data.error || 'No se pudo guardar la configuración.');
      }
    } catch (err) {
      setStatusMsg({ type: 'error', text: err.message });
    } finally {
      setSaving(false);
    }
  };

  // Probar envío de notificación
  const handleTest = async () => {
    setTesting(true);
    setStatusMsg(null);

    const payload = {
      notifications: {
        channel: channel,
        email: {
          recipient_email: recipientEmail.trim()
        }
      }
    };

    try {
      const res = await authFetch('/api/test-notification', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success) {
        setStatusMsg({ type: 'success', text: data.message || '¡Prueba enviada con éxito!' });
      } else {
        setStatusMsg({ type: 'error', text: data.message || 'Fallo al enviar prueba.' });
      }
    } catch (err) {
      setStatusMsg({ type: 'error', text: `Error: ${err.message}` });
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="animate-in fade-in duration-300 max-w-3xl">
      <div className="mb-8">
        <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">Configuración de Alertas</h2>
        <p className="text-slate-600 mt-1 text-sm md:text-base">
          Administra cómo y en qué plataformas recibes las alertas de los expedientes bajo tu vigilancia.
        </p>
      </div>

      {statusMsg && (
        <div className={`p-4 rounded-xl text-xs sm:text-sm font-medium mb-6 border ${
          statusMsg.type === 'success' 
            ? 'bg-emerald-50 text-emerald-900 border-emerald-200' 
            : 'bg-red-50 text-red-900 border-red-200'
        }`}>
          {statusMsg.text}
        </div>
      )}

      {/* Tarjetas de Estado: Mis Plataformas Activas */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
        <div className="bg-white p-4 rounded-2xl border border-slate-200/90 shadow-sm flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
              <Mail className="w-5 h-5" />
            </div>
            <div className="overflow-hidden">
              <span className="text-xs text-slate-400 font-semibold uppercase block">Plataforma Correo</span>
              <span className="text-sm font-bold text-slate-800 truncate block">
                {emailEnabled ? (recipientEmail || currentUser?.email) : 'Desactivado'}
              </span>
            </div>
          </div>
          <span className={`text-[11px] font-bold px-2.5 py-1 rounded-full border ${
            emailEnabled 
              ? 'bg-emerald-50 text-emerald-700 border-emerald-200' 
              : 'bg-slate-100 text-slate-500 border-slate-200'
          }`}>
            {emailEnabled ? 'Activo' : 'Inactivo'}
          </span>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200/90 shadow-sm flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-sky-50 text-sky-500 flex items-center justify-center shrink-0">
              <Send className="w-5 h-5" />
            </div>
            <div className="overflow-hidden">
              <span className="text-xs text-slate-400 font-semibold uppercase block">Plataforma Telegram</span>
              <span className="text-sm font-bold text-slate-800 truncate block">
                {userLinked ? (telegramUsername ? `@${telegramUsername}` : 'Cuenta Vinculada') : 'Sin Vincular'}
              </span>
            </div>
          </div>
          <span className={`text-[11px] font-bold px-2.5 py-1 rounded-full border ${
            userLinked 
              ? 'bg-emerald-50 text-emerald-700 border-emerald-200' 
              : 'bg-amber-50 text-amber-700 border-amber-200'
          }`}>
            {userLinked ? 'Vinculado' : 'Pendiente'}
          </span>
        </div>
      </div>

      <div className="space-y-6">
        {/* Canal de Correo Electrónico */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200/90">
          <div className="flex flex-col sm:flex-row gap-6 justify-between items-start sm:items-center">
            <div className="flex gap-4 items-start">
              <div className="bg-blue-50 p-3 rounded-2xl text-blue-600 shrink-0">
                <Mail className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900 text-lg">Alertas por Correo Electrónico</h3>
                <p className="text-xs sm:text-sm text-slate-500 mt-1">
                  Recibe un resumen con los extractos de tus expedientes en tu buzón personal.
                </p>
              </div>
            </div>
            <button 
              type="button"
              onClick={toggleEmail}
              className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                emailEnabled ? 'bg-blue-600' : 'bg-slate-200'
              }`}
            >
              <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                emailEnabled ? 'translate-x-6' : 'translate-x-1'
              }`} />
            </button>
          </div>

          <div className="mt-5 pt-4 border-t border-slate-100">
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Dirección de correo donde deseas recibir tus notificaciones:
            </label>
            <input 
              type="email" 
              value={recipientEmail}
              onChange={(e) => setRecipientEmail(e.target.value)}
              placeholder={currentUser?.email || "abogado@despacho.com"}
              className="w-full sm:max-w-md px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
            />
            <p className="text-[11px] text-slate-400 mt-2">
              Las notificaciones se envían de forma automática y segura a este buzón desde el servidor oficial de LexMonitor.
            </p>
          </div>
        </div>

        {/* Canal de Telegram */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200/90">
          <div className="flex flex-col sm:flex-row gap-6 justify-between items-start sm:items-center">
            <div className="flex gap-4 items-start">
              <div className="bg-sky-50 p-3 rounded-2xl text-sky-500 shrink-0">
                <Send className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900 text-lg">Alertas por Telegram (Bot Oficial)</h3>
                <p className="text-xs sm:text-sm text-slate-500 mt-1">
                  Recibe avisos inmediatos en tu dispositivo móvil mediante el bot oficial del sistema.
                </p>
              </div>
            </div>
            <button 
              type="button"
              onClick={toggleTelegram}
              className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                telegramEnabled ? 'bg-sky-500' : 'bg-slate-200'
              }`}
            >
              <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                telegramEnabled ? 'translate-x-6' : 'translate-x-1'
              }`} />
            </button>
          </div>

          <div className="mt-5 pt-4 border-t border-slate-100">
            {/* Estado de Vinculación del Usuario */}
            {userLinked ? (
              <div className="p-4 bg-emerald-50/80 rounded-2xl border border-emerald-200 space-y-3">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-2.5">
                    <div className="w-3 h-3 bg-emerald-500 rounded-full animate-pulse"></div>
                    <div>
                      <span className="text-xs sm:text-sm font-bold text-emerald-950 block">
                        Tu cuenta de Telegram está vinculada
                      </span>
                      <span className="text-xs text-emerald-800">
                        {telegramUsername ? `Usuario: @${telegramUsername}` : 'Chat verificado y activo'}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {botInfo && (
                      <a 
                        href={`https://t.me/${botInfo.username}`} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-xs bg-sky-600 hover:bg-sky-500 text-white font-semibold px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-colors shadow-sm"
                      >
                        Abrir @{botInfo.username} <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                    <button
                      type="button"
                      onClick={handleUnlinkTelegram}
                      className="text-xs text-red-600 hover:text-red-700 bg-white hover:bg-red-50 border border-red-200 font-semibold px-3 py-1.5 rounded-lg transition-colors"
                      title="Desvincular mi cuenta de Telegram"
                    >
                      Desvincular
                    </button>
                  </div>
                </div>
                <p className="text-xs text-emerald-800">
                  Las alertas automáticas de tus expedientes llegarán a tu chat privado con el bot en cuanto se publiquen.
                </p>
              </div>
            ) : (
              <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-3">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
                    <span className="text-xs sm:text-sm font-bold text-slate-800">
                      Vincular tu cuenta de Telegram
                    </span>
                  </div>
                  {botInfo && (
                    <a 
                      href={`https://t.me/${botInfo.username}`} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-xs text-sky-600 hover:text-sky-700 font-semibold flex items-center gap-1"
                    >
                      Abrir @{botInfo.username} <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>

                <p className="text-xs text-slate-600 leading-relaxed">
                  Para que el bot te reconozca y te entregue <strong>únicamente tus expedientes</strong>, abre la conversación con el bot y envía este comando:
                </p>

                <div className="flex items-center gap-2 bg-white p-2.5 rounded-xl border border-slate-300 font-mono text-xs shadow-sm">
                  <span className="text-blue-600 font-bold shrink-0">Comando:</span>
                  <span className="text-slate-800 flex-1 truncate">/vincular {linkCode || currentUser?.email}</span>
                  <button
                    type="button"
                    onClick={handleCopyCode}
                    className="px-3 py-1 bg-slate-100 hover:bg-slate-200 rounded-lg text-slate-700 text-xs font-sans font-semibold flex items-center gap-1 transition-colors"
                  >
                    {copiedCode ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copiedCode ? 'Copiado' : 'Copiar'}</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Botones de Acción */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
          <button 
            type="button"
            onClick={handleTest}
            disabled={testing || saving}
            className="w-full sm:w-auto px-5 py-2.5 rounded-xl border border-slate-300 hover:bg-slate-100 text-slate-700 text-xs sm:text-sm font-semibold transition-colors flex items-center justify-center gap-2 shadow-sm"
          >
            {testing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
            <span>{testing ? 'Probando...' : 'Probar Notificación Ahora'}</span>
          </button>

          <button 
            type="button"
            onClick={handleSave}
            disabled={saving || testing}
            className="w-full sm:w-auto bg-blue-600 hover:bg-blue-500 text-white px-8 py-2.5 rounded-xl text-xs sm:text-sm font-bold shadow-md shadow-blue-600/30 transition-all active:scale-95 flex items-center justify-center gap-2"
          >
            {saving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4 stroke-[3]" />}
            <span>{saving ? 'Guardando...' : 'Guardar Preferencias'}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
