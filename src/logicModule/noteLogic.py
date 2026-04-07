# Synapse
# logicModule
# noteLogic.py
# pylint: disable=invalid-name

from datetime import datetime
import os
import sqlite3
from typing import Optional

from src.databaseModule import generalDbFunctions, noteDbFunctions


def makeDefaultTitle() -> str:
    """Create a default title when none is given."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"Untitled Note ({timestamp})"


def onNoteSaveClicked(
    title: str,
    content: str,
    databaseName: str,
    noteId: Optional[int] = None
) -> dict[str, str] | str:
    """Insert a new note or update an existing one."""
    if not title:
        title = makeDefaultTitle()

    if not content:
        return {"title": "Cannot Save", "msg": "Note content is required."}

    dbPath = generalDbFunctions.getDbPath(databaseName)
    if not os.path.exists(dbPath):
        return {
            "title": "Database Missing",
            "msg": f"Database '{databaseName}' not found.\nRun setup_database.py first."
        }

    try:
        if noteId is None:
            conn = generalDbFunctions.connectDb(dbPath)
            try:
                cursor = conn.cursor()
                newNoteId = noteDbFunctions.addNote(cursor, title, content, "gui")
                conn.commit()
            finally:
                conn.close()

            return f"Saved new note (id={newNoteId})"

        updated = noteDbFunctions.updateNote(
            noteId=noteId,
            databaseName=dbPath,
            title=title,
            content=content
        )

        if updated:
            return f"Updated note (id={noteId})"

        return {
            "title": "Update Failed",
            "msg": "The note could not be updated."
        }

    except sqlite3.Error as exc:
        return {"title": "Database Error", "msg": f"SQLite error:\n{exc}"}