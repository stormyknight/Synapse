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
        if noteId is not None:
            return  {"title": "Cannot Save", "msg": "Error finding title."}
        title = makeDefaultTitle()

    if not content:
        return {"title": "Cannot Save", "msg": "Note content is required."}

    dbPath = generalDbFunctions.getDbPath(databaseName)
    if not os.path.exists(dbPath):
        return {
            "title": "Database Missing",
            "msg": f"Database '{databaseName}' not found.\nRun setup_database.py first."
        }

    returnMsg: str = ""
    updated = None
    try:
        conn = generalDbFunctions.connectDb(dbPath)
        try:
            cursor = conn.cursor()
            if noteId is None:
                newNoteId = noteDbFunctions.addNote(cursor, title, content, "gui")
                conn.commit()
                returnMsg = f"Saved new note (id={newNoteId})"
            else:
                updated = noteDbFunctions.updateNote(
                    cursor=cursor,
                    noteId=noteId,
                    title=title,
                    content=content
                )
                conn.commit()
        finally:
            conn.close()

        if updated:
            returnMsg = f"Updated note (id={noteId})"
        return returnMsg

    except sqlite3.Error as exc:
        return  {"title": "Database Error", "msg": f"SQLite error:\n{exc}"}


def getNotesHandler(databaseName:str)-> dict[str, str]|list: # type: ignore[type-arg]
    dbPath = generalDbFunctions.getDbPath(databaseName)
    if not os.path.exists(dbPath):
        return  {"title": "Database Missing", "msg": "Database '{databaseName}' not found.\nRun setup_database.py first."}

    try:
        conn = generalDbFunctions.connectDb(dbPath)
        try:
            cursor = conn.cursor()
            allNotes:list = noteDbFunctions.getNotes(cursor) # type: ignore[type-arg]
            conn.commit()
        finally:
            conn.close()

        return allNotes
    except sqlite3.Error as exc:
        return  {"title": "Database Error", "msg": f"SQLite error:\n{exc}"}


def getNoteHandler(databaseName:str, noteId: int)->tuple|dict[str, str]: # type: ignore[type-arg]
    dbPath = generalDbFunctions.getDbPath(databaseName)
    if not os.path.exists(dbPath):
        return  {"title": "Database Missing", "msg": "Database '{databaseName}' not found.\nRun setup_database.py first."}
    try:
        conn = generalDbFunctions.connectDb(dbPath)
        try:
            cursor = conn.cursor()
            note:tuple = noteDbFunctions.getNote(cursor, noteId) # type: ignore[type-arg]
            conn.commit()
        finally:
            conn.close()

        return note
    except sqlite3.Error as exc:
        return  {"title": "Database Error", "msg": f"SQLite error:\n{exc}"}
