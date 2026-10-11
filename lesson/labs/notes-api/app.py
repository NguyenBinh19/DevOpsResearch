"""Tiny standard-library API used by the DevOps lessons. Local lab data only."""

import json
import os
import sqlite3
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


DB_PATH = Path(os.getenv("NOTES_DB", "notes.db"))
HOST = os.getenv("NOTES_HOST", "127.0.0.1")
PORT = int(os.getenv("NOTES_PORT", "8000"))
VERSION = os.getenv("NOTES_VERSION", "lab-1")


@contextmanager
def database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    try:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, body TEXT NOT NULL)"
        )
        connection.commit()
        yield connection
        connection.commit()
    finally:
        connection.close()


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            self.reply(200, {"status": "ok", "version": VERSION})
        elif path == "/notes":
            with database() as db:
                rows = db.execute("SELECT id, body FROM notes ORDER BY id").fetchall()
            self.reply(200, {"notes": [{"id": row[0], "body": row[1]} for row in rows]})
        else:
            self.reply(404, {"error": "not_found"})

    def do_POST(self):
        if urlparse(self.path).path != "/notes":
            self.reply(404, {"error": "not_found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 4096:
                raise ValueError("body size")
            payload = json.loads(self.rfile.read(length))
            body = payload["body"]
            if not isinstance(body, str) or not body.strip() or len(body) > 1000:
                raise ValueError("body value")
        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            self.reply(400, {"error": "invalid_note"})
            return
        with database() as db:
            cursor = db.execute("INSERT INTO notes (body) VALUES (?)", (body.strip(),))
            note_id = cursor.lastrowid
        self.reply(201, {"id": note_id, "body": body.strip()})


if __name__ == "__main__":
    with database():
        pass
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Notes API {VERSION} listening on http://{HOST}:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
