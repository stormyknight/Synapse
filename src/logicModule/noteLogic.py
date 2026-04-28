# Synapse
# logicModule
# noteLogic.py
# pylint: disable=invalid-name

from datetime import datetime
import os
import sqlite3
from typing import Optional
import json
import hashlib
from src.databaseModule import generalDbFunctions, noteDbFunctions
from src.logicModule import LLM_Helper
from src.databaseModule import tagDbFunctions


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


# Functions for analyzing note contents and sending commands to the LLM
def analyzeNoteContent(content: str) -> dict[str, str | list[str]]:
    """
    Run local LLM analysis on the note content and return:
    - summary
    - tags
    - mood
    """
    return LLM_Helper.analyzeNote(content) # type: ignore [no-any-return]


def summarizeNoteContent(content: str) -> str:
    """
    Return a short summary of the note content.
    """
    return LLM_Helper.generateSummary(content) # type: ignore [no-any-return]


def suggestTagsForNote(content: str) -> list[str]:
    """
    Return a list of suggested tags for the note content.
    """
    return LLM_Helper.generateTags(content) # type: ignore [no-any-return]


def detectMoodForNote(content: str) -> str | list[str]:
    """
    Return a short mood label for the note content.
    """
    return LLM_Helper.generateMood(content) # type: ignore [no-any-return]


def analyzeAndStoreNote(
    noteId: int,
    content: str,
    databaseName: str
) -> dict[str, str | list[str]]:
    """
    Analyze note content with the local LLM and store:
    - summary in note_analyses
    - mood in note_analyses
    - full JSON in note_analyses
    - tags in tags and note_tags
    """
    dbPath = generalDbFunctions.getDbPath(databaseName)
    if not os.path.exists(dbPath):
        return {
            "summary": "Database not found.",
            "tags": [],
            "mood": "unavailable"
        }

    result: dict[str, str | list[str]] = LLM_Helper.analyzeNote(content)

    summary = result.get("summary", "")
    mood = result.get("mood", "")
    tags = result.get("tags", [])

    modelName = LLM_Helper.MODEL_NAME
    promptVersion = "v1"
    inputHash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    outputJson = json.dumps(result)

    connection = generalDbFunctions.connectDb(dbPath)
    cursor = connection.cursor()

    try:

        # Remove old analysis rows for this note
        noteDbFunctions.deleteAnalysis(cursor, noteId)

        # remove old tag links for this note
        tagDbFunctions.removeAllNoteTagAssociations(cursor, noteId)

        if isinstance(summary, str) and summary.strip():
            noteDbFunctions.addAnalysis(cursor, noteId, "summary", modelName, promptVersion, summary, outputJson, inputHash)

        if isinstance(mood, str) and mood.strip():
            noteDbFunctions.addAnalysis(cursor, noteId, "mood", modelName, promptVersion, mood, outputJson, inputHash)

        noteDbFunctions.addAnalysis(cursor,noteId,
                "full_analysis", modelName, promptVersion,  summary if isinstance(summary, str) else "", outputJson, inputHash)

        if isinstance(tags, list):
            for tag in tags:
                cleanTag: str = str(tag).strip().lower()
                if not cleanTag:
                    continue

                tagId = tagDbFunctions.createTag(cursor, cleanTag)

                if tagId is not None:
                    tagDbFunctions.associateTagWithNote(cursor, tagId, noteId)

        connection.commit()
        return result

    except sqlite3.Error as exc:
        return {
            "summary": f"Database error: {exc}",
            "tags": [],
            "mood": "unavailable"
        }

    finally:
        connection.close()


def deleteNoteHandler(noteId: int, databaseName: str) -> None | dict[str, str]:
    dbPath = generalDbFunctions.getDbPath(databaseName)

    if not os.path.exists(dbPath):
        print(1)
        return {
            "title": "Database Missing",
            "msg": f"Database '{databaseName}' not found.\nRun setup_database.py first."
        }
    try:
        conn = generalDbFunctions.connectDb(dbPath)
        try:

            cursor = conn.cursor()
            noteDbFunctions.deleteNote(cursor, noteId)
            conn.commit()
            return None
        finally:
            conn.close()
    except sqlite3.Error as exc:
        print(exc)
        return  {"title": "Database Error", "msg": f"SQLite error:\n{exc}"}
