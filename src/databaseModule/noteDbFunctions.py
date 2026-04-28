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


def deleteAnalysis(cursor: sqlite3.Cursor, noteId: int) -> None:
    cursor.execute("""
            DELETE FROM note_analyses 
            WHERE note_id = ?  
            AND analysis_type IN ('summary', 'mood', 'full_analysis') 
            """,
            (noteId,)
        )


def addAnalysis(cursor: sqlite3.Cursor, noteId: int, analysisType: str, modelName, promptVersion, outputText: str, outputJson: str, inputHash: str) -> None: #type: ignore[no-untyped-def]
    cursor.execute(
                """
                INSERT INTO note_analyses
                (note_id, analysis_type, model_name, prompt_version, output_text, output_json, input_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    noteId,
                    analysisType,
                    modelName,
                    promptVersion,
                    outputText,
                    outputJson,
                    inputHash
                )
            )

def deleteNote(cursor: sqlite3.Cursor, noteId: int) -> None:
    cursor.execute("DELETE FROM notes where note_id =?",(noteId,),)