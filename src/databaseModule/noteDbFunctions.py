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

# Updates the title and/or content of an existing note in the database
def updateNote(noteId: int, title: Optional[str] = None, content: Optional[str] = None) -> bool:

    if title is None and content is None:
        return False

    if not os.path.exists(databaseName):
        return False

    connection: sqlite3.Connection = connectDb(databaseName)

    cursor: sqlite3.Cursor = connection.cursor()

    updateFields: list[str] = []

    updateValues: list[str | int] = []

    # Adds title update if provided (1)
    if title is not None:
        updateFields.append("title = ?")
        updateValues.append(title)

    # Adds content update if provided (2)
    if content is not None:
        updateFields.append("content = ?")
        updateValues.append(content)

    # Appends note ID (3)
    updateValues.append(noteId)

    updateQuery: str = (
        f"UPDATE notes "
        f"SET {', '.join(updateFields)} "
        f"WHERE id = ?"
    )

    cursor.execute(updateQuery, updateValues)

    connection.commit()

    updatedRows = cursor.rowcount

    connection.close()

    return updatedRows > 0
