import sqlite3

from ..typing import Face


class Db:
    def __init__(self, *, database: str = "faces.db"):
        self._conn = sqlite3.connect(database=database)
        self._cursor = self._conn.cursor()
        self._cursor.execute(
            """
create table if not exists faces (
    id primary rowid,
    url text not null,
    name text not null
)
"""
        )

        self._is_closed = False

    def close(self):
        if self._is_closed:
            return

        self._conn.commit()
        self._conn.close()
        self._is_closed = True

    def insert(self, face: Face):
        assert face.name is not None, "`name` must not be `None`"

        self._cursor.execute(
            """
insert into faces (url, name) values (?, ?)
""",
            (face.image, face.name),
        )

    def fetch_name(self, id: int) -> str:
        return self._cursor.execute(
            """
select name from faces where id = ?
""",
            (id,),
        ).fetchone()
