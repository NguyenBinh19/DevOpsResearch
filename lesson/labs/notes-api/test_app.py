"""Small integration tests for the teaching API, using only Python's standard library."""

import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, ProxyHandler, build_opener

import app


# Always connect directly to the local lab server, even if the host has a proxy.
local_http = build_opener(ProxyHandler({}))


class NotesApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        app.DB_PATH = Path(cls.temp_dir.name) / "notes.db"
        cls.server = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.temp_dir.cleanup()

    def test_health(self):
        with local_http.open(self.base_url + "/health", timeout=3) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(json.load(response)["status"], "ok")

    def test_create_and_list_note(self):
        payload = json.dumps({"body": "first note"}).encode("utf-8")
        request = Request(
            self.base_url + "/notes",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with local_http.open(request, timeout=3) as response:
            self.assertEqual(response.status, 201)
            created_id = json.load(response)["id"]
        with local_http.open(self.base_url + "/notes", timeout=3) as response:
            notes = json.load(response)["notes"]
        self.assertIn({"id": created_id, "body": "first note"}, notes)

    def test_reject_empty_note(self):
        request = Request(
            self.base_url + "/notes",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with self.assertRaises(HTTPError) as error:
            local_http.open(request, timeout=3)
        self.assertEqual(error.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
