import sqlite3
from typing import TypedDict

from common.face import Face


class FetchRequest(TypedDict):
    rowid: int
    get_name: bool = False
    get_src: bool = False


class FetchResult(TypedDict):
    name: str | None = None
    src: str | None = None


class RelationalDb:
    def __init__(self, conn: sqlite3.Connection):
        self._cursor = conn.cursor()
        self._cursor.execute(
            """
CREATE TABLE IF NOT EXISTS faces (
    name TEXT NOT NULL,
    src TEXT
)
"""
        )

    def insert(self, face: Face) -> tuple[int]:
        rowid = self._cursor.execute(
            """
INSERT INTO faces (name, src) VALUES (?, ?) RETURNING rowid
""",
            (str(face["name"]), str(face["src"])),
        ).fetchone()

        return rowid

    def fetch(self, request: FetchRequest) -> FetchResult:
        if request.get("get_name", False) and request.get("get_src", False):
            name, src = self._cursor.execute(
                """
SELECT name, src FROM faces WHERE rowid = ?
""",
                (request["rowid"],),
            ).fetchone()

            return {"name": name, "src": src}

        if request["get_name"]:
            name = self._cursor.execute(
                """
SELECT name FROM faces WHERE rowid = ?
""",
                (request["rowid"],),
            ).fetchone()

            return {"name": name}

        if request["get_src"]:
            src = self._cursor.execute(
                """
SELECT src FROM faces WHERE rowid = ?
""",
                (request["rowid"],),
            ).fetchone()

            return {"src": name}

        raise ValueError(
            "`FetchRequest` must have either `get_name` or `get_src` set to True"
        )
