"""Append-only application ledger; original input bytes remain recoverable."""
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from .core import validate


class Ledger:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute("CREATE TABLE IF NOT EXISTS forecasts (event_id TEXT PRIMARY KEY, sha256 TEXT NOT NULL, imported_at TEXT NOT NULL, raw BLOB NOT NULL)")
        self.db.execute("CREATE TABLE IF NOT EXISTS amendments (id INTEGER PRIMARY KEY, event_id TEXT NOT NULL, recorded_at TEXT NOT NULL, raw TEXT NOT NULL)")
        for table in ("forecasts", "amendments"):
            for action in ("UPDATE", "DELETE"):
                self.db.execute(f"CREATE TRIGGER IF NOT EXISTS no_{table}_{action} BEFORE {action} ON {table} BEGIN SELECT RAISE(ABORT, 'append-only ledger'); END")

    def freeze(self, raw):
        document = validate(json.loads(raw))
        digest = hashlib.sha256(raw).hexdigest()
        with self.db:
            self.db.execute("INSERT INTO forecasts VALUES (?, ?, ?, ?)",
                            (document["event_id"], digest, datetime.now(timezone.utc).isoformat(), raw))
        return digest

    def get(self, event_id):
        row = self.db.execute("SELECT sha256, raw FROM forecasts WHERE event_id=?", (event_id,)).fetchone()
        if row is None:
            raise ValueError("Unknown event")
        if hashlib.sha256(row[1]).hexdigest() != row[0]:
            raise ValueError("Stored forecast checksum mismatch")
        return json.loads(row[1])

    def amend(self, event_id, amendment):
        document = self.get(event_id)
        if set(amendment) != {"fight_id", "kind", "note"}:
            raise ValueError("Amendment requires fight_id, kind and note")
        if amendment["kind"] not in {"void", "note"} or not isinstance(amendment["note"], str):
            raise ValueError("Invalid amendment")
        if amendment["fight_id"] not in {f["fight_id"] for f in document["fights"]}:
            raise ValueError("Unknown fight")
        with self.db:
            self.db.execute("INSERT INTO amendments(event_id, recorded_at, raw) VALUES (?, ?, ?)",
                            (event_id, datetime.now(timezone.utc).isoformat(), json.dumps(amendment)))

    def voids(self, event_id):
        amendments = [json.loads(r[0]) for r in self.db.execute("SELECT raw FROM amendments WHERE event_id=? ORDER BY id", (event_id,))]
        return {a["fight_id"] for a in amendments if a["kind"] == "void"}
