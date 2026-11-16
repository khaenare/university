"""Простий приймач webhook-сповіщень Alertmanager: друкує кожне сповіщення в лог."""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        size = int(self.headers["Content-Length"])
        body = json.loads(self.rfile.read(size))
        print(f"=== {self.path} | {body['status'].upper()}"
              f" | група {body['groupLabels']}")
        for alert in body["alerts"]:
            labels = alert["labels"]
            summary = alert["annotations"].get("summary", "")
            print(f"    [{alert['status']}] {labels.get('alertname')}"
                  f" severity={labels.get('severity')}: {summary}")
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args):
        pass  # без стандартного журналу HTTP-запитів


HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
