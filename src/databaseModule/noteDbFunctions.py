import sqlite3
import math
from typing import Optional


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


# Updates the title and/or content of an existing note in the database
def updateNote(cursor: sqlite3.Cursor, noteId: int, title: Optional[str] = None, content: Optional[str] = None) -> int:
    updateFields: list[str] = []
    updateValues: list[str | int] = []

    if title is not None:
        updateFields.append("title = ?")
        updateValues.append(title)

    if content is not None:
        updateFields.append("content = ?")
        updateValues.append(content)

    updateValues.append(noteId)

    updateQuery: str = (
        f"UPDATE notes "
        f"SET {', '.join(updateFields)} "
        f"WHERE id = ?"
    )

    cursor.execute(updateQuery, updateValues)

    return noteId


def getNotes(cursor: sqlite3.Cursor)->list: # type: ignore[type-arg]
    cursor.execute("SELECT * FROM notes")
    return cursor.fetchall()


def getNote(cursor: sqlite3.Cursor, clickedId: int)->tuple: # type: ignore[type-arg]
    cursor.execute("SELECT * FROM notes WHERE id = ?", (clickedId,))
    return cursor.fetchone() # type: ignore[no-any-return]
