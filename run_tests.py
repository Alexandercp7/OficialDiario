#!/usr/bin/env python
"""
🧪 Ejecutor de pruebas automatizadas para LexMonitor Yucatán.
Ejecuta la suite completa de tests unitarios y de integración con reporte detallado.
"""
import sys
import unittest

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def main():
    print("\n" + "=" * 65)
    print("🏛️  LexMonitor Yucatán — Ejecución de Pruebas Automatizadas")
    print("=" * 65 + "\n")

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir="tests", pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 65)
    if result.wasSuccessful():
        print(f"✅ ¡Todas las pruebas pasaron con éxito! ({result.testsRun} tests ejecutados)")
        print("=" * 65 + "\n")
        sys.exit(0)
    else:
        print(f"❌ Fallos en la suite de pruebas: {len(result.failures)} fallas, {len(result.errors)} errores.")
        print("=" * 65 + "\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
