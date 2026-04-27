import math
import sqlite3


def createTag(cursor: sqlite3.Cursor, name: str) -> int | None:
    cursor.execute(
        """
        INSERT OR IGNORE INTO tags (tag_name)
        VALUES (?)
        """,
        (name,),
    )
    cursor.execute(
            """
            SELECT id FROM tags WHERE tag_name = ?
            """,
            (name,),
    )
    row = cursor.fetchone()
    return row[0] if row else None


def associateTagWithNote(cursor: sqlite3.Cursor, tagId: int,  noteId: int) -> int:
    print(noteId)
    cursor.execute(
        """
        INSERT OR IGNORE INTO note_tags (note_id, tag_id)
        VALUES (?, ?)
        """,
        (noteId,tagId,),
    )
    return cursor.lastrowid if cursor.lastrowid is not None else int(math.nan)


def getTagAssociations(cursor: sqlite3.Cursor, noteId: int)->list[int]|None:
    cursor.execute(
        """
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
        ORDER BY tag_name
        """,
        (tagIds)
    )
    return cursor.fetchall()


def getTags(cursor: sqlite3.Cursor)->list[tuple]: # type: ignore [type-arg]
    cursor.execute("SELECT * FROM tags ORDER BY tag_name")
    return cursor.fetchall()


def removeTagAssociation(cursor: sqlite3.Cursor, tagAssociationId: int)->None:
    cursor.execute("DELETE FROM note_tags WHERE id = ?", (tagAssociationId,))


def removeAllNoteTagAssociations(cursor: sqlite3.Cursor, noteId: int)-> None:
    cursor.execute(
            """
            DELETE FROM note_tags
            WHERE note_id = ?
            """,
            (noteId,)
        )
