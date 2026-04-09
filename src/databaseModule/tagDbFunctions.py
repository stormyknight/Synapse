import math
import sqlite3

def createTag(cursor: sqlite3.Cursor, name: str):
    cursor.execute(
        """
        INSERT INTO tags (tag_name)
        VALUES (?)
        """,
        (name,),
    )
    return cursor.lastrowid if cursor.lastrowid is not None else int(math.nan)

def associateTagWithNote(cursor: sqlite3.Cursor, tagId: int,  noteId: int):
    cursor.execute(
        """
        INSERT INTO note_tags (note_id, tag_id)
        VALUES (?, ?)
        """,
        (noteId,tagId,),
    )
    return cursor.lastrowid if cursor.lastrowid is not None else int(math.nan)

def getAssociatedTagIds(cursor: sqlite3.Cursor, noteId: int)->list[int]|None:
    cursor.execute(
        f"""
        SELECT tag_id FROM note_tags WHERE note_id = ?
        """,
        (noteId,)
    )
    return [idTuple[0] for idTuple in cursor.fetchall()]

def getSelectedTags(cursor: sqlite3.Cursor, tagIds: list[int])->list[int]|None:
    placeHolders = ",".join("?" for _ in tagIds)
    cursor.execute(
        f"""
        SELECT * FROM tags WHERE id IN ({placeHolders})
        """,
        (tagIds)
    )
    return cursor.fetchall()