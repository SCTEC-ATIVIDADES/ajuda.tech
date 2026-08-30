import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


PRODUCTS_PATH = Path(os.environ.get("CATALOG_PATH", "/service/produtos.json"))


class CatalogHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/products":
            self._respond(200, {"produtos": json.loads(PRODUCTS_PATH.read_text(encoding="utf-8"))})
            return
        if self.path == "/products/empty":
            self._respond(200, {"produtos": []})
            return
        if self.path == "/products/malformed":
            self._respond(200, {"produtos": {}})
            return
        if self.path == "/products/error":
            self._respond(503, {"erro": "serviço indisponível"})
            return
        self._respond(404, {"erro": "rota não encontrada"})

    def log_message(self, format, *args):
        return

    def _respond(self, status, body):
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


HTTPServer(("0.0.0.0", int(os.environ.get("PORT", "8080"))), CatalogHandler).serve_forever()
