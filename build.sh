#!/usr/bin/env bash
# Script de compilación e instalación para despliegue en Render
set -o errexit

echo "📦 [1/3] Instalando dependencias de Node.js..."
npm install

echo "🎨 [2/3] Compilando frontend (React + esbuild)..."
npm run build

echo "🐍 [3/3] Instalando dependencias de Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Compilación de LexMonitor completada exitosamente."
