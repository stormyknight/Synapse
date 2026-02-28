from datetime import datetime
import os
import sqlite3
from src.databaseModule import generalDbFunctions, noteDbFunctions


def makeDefaultTitle() -> str:
    """Create a default title when none is given."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"Untitled Note ({timestamp})"


def onNoteSaveClicked(title: str, content: str, databaseName:str)->dict[str, str]|str:
    """Save current note contents into synapse.db."""
    if not title:
        title = makeDefaultTitle()

    if not content:
        return  {"title": "Cannot Save", "msg": "Note content is required."}

    dbPath = generalDbFunctions.getDbPath(databaseName)
    if not os.path.exists(dbPath):
        return  {"title": "Database Missing", "msg": "Database '{databaseName}' not found.\nRun setup_database.py first."}

    try:
        conn = generalDbFunctions.connectDb(dbPath)
        try:
            cursor = conn.cursor()
            noteId = noteDbFunctions.addNote(cursor, title, content, "gui")
            conn.commit()
        finally:
            conn.close()

        return (f"Saved (id={noteId})")
    except sqlite3.Error as exc:
        return  {"title": "Database Error", "msg": f"SQLite error:\n{exc}"}
