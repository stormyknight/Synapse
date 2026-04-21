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
    return LLM_Helper.analyze_note(content)


def summarizeNoteContent(content: str) -> str:
    """
    Return a short summary of the note content.
    """
    return LLM_Helper.generate_summary(content)


def suggestTagsForNote(content: str) -> list[str]:
    """
    Return a list of suggested tags for the note content.
    """
    return LLM_Helper.generate_tags(content)


def detectMoodForNote(content: str) -> str:
    """
    Return a short mood label for the note content.
    """
    return LLM_Helper.generate_mood(content)


def analyzeAndStoreNote(
    note_id: int,
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

    result = LLM_Helper.analyze_note(content)

    summary = result.get("summary", "")
    mood = result.get("mood", "")
    tags = result.get("tags", [])

    model_name = LLM_Helper.MODEL_NAME
    prompt_version = "v1"
    input_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    output_json = json.dumps(result)

    connection = generalDbFunctions.connectDb(dbPath)
    cursor = connection.cursor()
    


    try:

        # Remove old analysis rows for this note
        cursor.execute("""
            DELETE FROM note_analyses
            WHERE note_id = ? 
            AND analysis_type IN ('summary', 'mood', 'full_analysis')
            """,
            (note_id,)
        )

        # remove old tag links for this note
        cursor.execute(
            """
            DELETE FROM note_tags
            WHERE note_id = ?
            """,
            (note_id,)
        )

        if isinstance(summary, str) and summary.strip():
            cursor.execute(
                """
                INSERT INTO note_analyses
                (note_id, analysis_type, model_name, prompt_version, output_text, output_json, input_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    note_id,
                    "summary",
                    model_name,
                    prompt_version,
                    summary,
                    output_json,
                    input_hash
                )
            )

        if isinstance(mood, str) and mood.strip():
            cursor.execute(
                """
                INSERT INTO note_analyses
                (note_id, analysis_type, model_name, prompt_version, output_text, output_json, input_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    note_id,
                    "mood",
                    model_name,
                    prompt_version,
                    mood,
                    output_json,
                    input_hash
                )
            )

        cursor.execute(
            """
            INSERT INTO note_analyses
            (note_id, analysis_type, model_name, prompt_version, output_text, output_json, input_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                note_id,
                "full_analysis",
                model_name,
                prompt_version,
                summary if isinstance(summary, str) else "",
                output_json,
                input_hash
            )
        )

        if isinstance(tags, list):
            for tag in tags:
                clean_tag = str(tag).strip().lower()
                if not clean_tag:
                    continue

                cursor.execute(
                    """
                    INSERT OR IGNORE INTO tags (tag_name)
                    VALUES (?)
                    """,
                    (clean_tag,)
                )

                cursor.execute(
                    """
                    SELECT id FROM tags
                    WHERE tag_name = ?
                    """,
                    (clean_tag,)
                )
                tag_row = cursor.fetchone()

                if tag_row is not None:
                    tag_id = tag_row[0]

                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO note_tags (note_id, tag_id)
                        VALUES (?, ?)
                        """,
                        (note_id, tag_id)
                    )

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