import sqlite3
from pathlib import Path
import time


LIBRARY_PATH = Path.home() / ".animora" / "library.sqlite3"


class LibraryStore:
    def __init__(self, path=None):
        path = path or LIBRARY_PATH
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute(
            """CREATE TABLE IF NOT EXISTS animations (
                id INTEGER PRIMARY KEY,
                path TEXT NOT NULL,
                name TEXT NOT NULL,
                kind TEXT NOT NULL DEFAULT 'file',
                columns INTEGER NOT NULL DEFAULT 0,
                rows INTEGER NOT NULL DEFAULT 0,
                fps INTEGER NOT NULL DEFAULT 24,
                UNIQUE(path, kind, columns, rows)
            )"""
        )
        columns = {row[1] for row in self.connection.execute("PRAGMA table_info(animations)")}
        if "last_opened" not in columns:
            self.connection.execute("ALTER TABLE animations ADD COLUMN last_opened INTEGER NOT NULL DEFAULT 0")
        self.connection.commit()

    def add(self, path, kind=None, columns=0, rows=0, fps=24):
        path = str(Path(path).resolve())
        if kind is None:
            kind = "video" if Path(path).suffix.lower() in {".avi", ".m4v", ".mkv", ".mov", ".mp4", ".webm"} else "file"
        if kind not in {"file", "sprite_sheet", "video"}:
            raise ValueError(f"Loại animation không hợp lệ: {kind}")
        if kind == "sprite_sheet" and (columns < 1 or rows < 1 or fps < 1):
            raise ValueError("Sprite sheet cần cột, hàng và FPS lớn hơn 0.")
        cursor = self.connection.execute(
            "INSERT OR IGNORE INTO animations(path, name, kind, columns, rows, fps) VALUES (?, ?, ?, ?, ?, ?)",
            (path, Path(path).name, kind, columns, rows, fps),
        )
        self.connection.commit()
        return cursor.rowcount == 1

    def list(self):
        rows = self.connection.execute("SELECT * FROM animations ORDER BY name COLLATE NOCASE, id").fetchall()
        return [dict(row) for row in rows]

    def list_recent(self, limit=8):
        rows = self.connection.execute("SELECT * FROM animations WHERE last_opened > 0 ORDER BY last_opened DESC LIMIT ?", (limit,)).fetchall()
        return [dict(row) for row in rows]

    def touch(self, animation_id):
        self.connection.execute("UPDATE animations SET last_opened = ? WHERE id = ?", (time.time_ns() // 1000, animation_id))
        self.connection.commit()

    def rename(self, animation_id, name):
        name = Path(name.strip()).name.strip()
        if not name:
            raise ValueError("Name cannot be empty.")
        self.connection.execute("UPDATE animations SET name = ? WHERE id = ?", (name, animation_id))
        self.connection.commit()

    def sort(self, order="name"):
        ordering = {"name": "name COLLATE NOCASE, id", "recent": "last_opened DESC, name COLLATE NOCASE", "type": "kind, name COLLATE NOCASE"}.get(order, "name COLLATE NOCASE, id")
        return [dict(row) for row in self.connection.execute(f"SELECT * FROM animations ORDER BY {ordering}").fetchall()]

    def get(self, animation_id):
        row = self.connection.execute("SELECT * FROM animations WHERE id = ?", (animation_id,)).fetchone()
        return dict(row) if row else None

    def remove(self, animation_id):
        self.connection.execute("DELETE FROM animations WHERE id = ?", (animation_id,))
        self.connection.commit()

    def close(self):
        self.connection.close()
