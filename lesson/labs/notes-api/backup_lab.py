"""Back up the Notes API SQLite database and restore to a separate lab file."""

import sqlite3
from pathlib import Path


source = Path("notes.db")
backup = Path("notes-backup.db")
restored = Path("restored-notes.db")

if not source.exists():
    raise SystemExit("notes.db is missing; create a note with app.py first")
if backup.exists() or restored.exists():
    raise SystemExit("Remove old lab backup/restore files only after checking their contents")

with sqlite3.connect(source) as live, sqlite3.connect(backup) as copy:
    live.backup(copy)

with sqlite3.connect(backup) as saved, sqlite3.connect(restored) as copy:
    saved.backup(copy)

with sqlite3.connect(source) as live, sqlite3.connect(restored) as copy:
    live_count = live.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
    restored_count = copy.execute("SELECT COUNT(*) FROM notes").fetchone()[0]

print(f"Original notes: {live_count}")
print(f"Restored notes: {restored_count}")
print(f"Restored file: {restored.resolve()}")
