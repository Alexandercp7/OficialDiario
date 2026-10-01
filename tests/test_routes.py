import unittest
import threading
import urllib.request
import urllib.error
import json
from http.server import ThreadingHTTPServer
from backend.routes import DiarioHandler

class TestRoutesModule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Levantar servidor de pruebas en puerto efímero (0)
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), DiarioHandler)
        cls.port = cls.server.server_port
        cls.base_url = f"http://127.0.0.1:{cls.port}"
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_health_endpoint(self):
        """Verifica que el endpoint /api/health responda 200 OK con el estado del servicio."""
        req = urllib.request.Request(f"{self.base_url}/api/health")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "ok")
            self.assertIn("LexMonitor", data.get("service", ""))

    def test_juzgados_endpoint(self):
        """Verifica que /api/juzgados devuelva el catálogo de juzgados de Yucatán."""
        req = urllib.request.Request(f"{self.base_url}/api/juzgados")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertTrue(data.get("success"))
            juzgados = data.get("juzgados", [])
            self.assertGreater(len(juzgados), 10)
            self.assertEqual(juzgados[0]["id"], "todos")

    def test_auth_me_unauthenticated(self):
        """Verifica que /api/auth/me sin token devuelva 401 Unauthorized."""
        req = urllib.request.Request(f"{self.base_url}/api/auth/me")
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 401)

    def test_keywords_unauthenticated(self):
        """Verifica que agregar criterios sin token devuelva 401 Unauthorized."""
        payload = json.dumps({"keyword": "123/2026", "tipo": "Expediente"}).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/keywords",
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 401)

    def test_not_found_route(self):
        """Verifica que una ruta inexistente devuelva 404 Not Found."""
        req = urllib.request.Request(f"{self.base_url}/api/endpoint_inventado_404")
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 404)

if __name__ == "__main__":
    unittest.main()
