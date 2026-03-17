import sqlite3
import math


def addNote(cursor: sqlite3.Cursor, title: str, content: str, source: str) -> int:
    """Insert a note into the notes table and return new note id."""
    cursor.execute(
        """
        INSERT INTO notes (title, content, source)
        VALUES (?, ?, ?)
        """,
        (title, content, source),
    )
    return cursor.lastrowid if cursor.lastrowid is not None else int(math.nan)
