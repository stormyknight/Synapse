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

def getTagAssociations(cursor: sqlite3.Cursor, noteId: int)->list[int]|None:
    cursor.execute(
        f"""
        SELECT * FROM note_tags WHERE note_id = ?
        """,
        (noteId,)
    )
    return  cursor.fetchall()

def getSelectedTags(cursor: sqlite3.Cursor, tagIds: list[int])->list[int]|None:
    placeHolders = ",".join("?" for _ in tagIds)
    cursor.execute(
        f"""
        SELECT * FROM tags WHERE id IN ({placeHolders})
        """,
        (tagIds)
    )
    return cursor.fetchall()

def getTags(cursor: sqlite3.Cursor)->list[tuple]:
    cursor.execute("SELECT * FROM tags")
    return cursor.fetchall()

def removeTagAssociation(cursor: sqlite3.Cursor, tagAssociationId: int)->None:
    cursor.execute("DELETE FROM note_tags WHERE id = ?", (tagAssociationId,))