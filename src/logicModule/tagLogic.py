import os
import sqlite3
from src.databaseModule import generalDbFunctions, tagDbFunctions


def createTagHandler(name: str,  databaseName:str)-> int | dict[str, str]:
    dbPath = generalDbFunctions.getDbPath(databaseName)

    if not os.path.exists(dbPath):
        return {
            "title": "Database Missing",
            "msg": f"Database '{databaseName}' not found.\nRun setup_database.py first."
        }
    try:
        conn = generalDbFunctions.connectDb(dbPath)
        try:

            cursor = conn.cursor()
            tagId:int = tagDbFunctions.createTag(cursor, name)
            conn.commit()
        finally:
            conn.close()
        return tagId
    except sqlite3.Error as exc:
        return  {"title": "Database Error", "msg": f"SQLite error:\n{exc}"}


def associateTagWithNoteHandler(tagId: int, noteId: int, databaseName:str) -> int | dict[str, str]:
    dbPath = generalDbFunctions.getDbPath(databaseName)
    if not os.path.exists(dbPath):
        return {
            "title": "Database Missing",
            "msg": f"Database '{databaseName}' not found.\nRun setup_database.py first."
        }
    try:
        conn = generalDbFunctions.connectDb(dbPath)
        try:

            cursor = conn.cursor()
            associatedTagIds:int = tagDbFunctions.associateTagWithNote(cursor, tagId=tagId, noteId=noteId)
            conn.commit()
        finally:
            conn.close()
        return associatedTagIds
    except sqlite3.Error as exc:
        return  {"title": "Database Error", "msg": f"SQLite error:\n{exc}"}


def getTagAssociationsHandler(noteId: int, databaseName:str)-> list[int] | dict[str,str]:
    dbPath = generalDbFunctions.getDbPath(databaseName)
    if not os.path.exists(dbPath):
        return {
            "title": "Database Missing",
            "msg": f"Database '{databaseName}' not found.\nRun setup_database.py first."
        }
    try:
        conn = generalDbFunctions.connectDb(dbPath)
        try:
            cursor = conn.cursor()
            tagAssociation:list[int] = tagDbFunctions.getTagAssociations(cursor, noteId=noteId)
            conn.commit()
        finally:
            conn.close()
        return tagAssociation
    except sqlite3.Error as exc:
        return  {"title": "Database Error", "msg": f"SQLite error:\n{exc}"}


def getSelectedTagsHandler(tagIds: list[int], databaseName:str)->list[tuple] | dict[str,str]: # type: ignore[type-arg]
    dbPath = generalDbFunctions.getDbPath(databaseName)
    if not os.path.exists(dbPath):
        return {
            "title": "Database Missing",
            "msg": f"Database '{databaseName}' not found.\nRun setup_database.py first."
        }
    try:
        conn = generalDbFunctions.connectDb(dbPath)
        try:

            cursor = conn.cursor()
            associatedTagIds:list[tuple] = tagDbFunctions.getSelectedTags(cursor, tagIds=tagIds) # type: ignore[type-arg]
            conn.commit()
        finally:
            conn.close()
        return associatedTagIds
    except sqlite3.Error as exc:
        return  {"title": "Database Error", "msg": f"SQLite error:\n{exc}"}


def getTagsHandler( databaseName:str)->list[tuple]|dict[str,str]: # type: ignore[type-arg]
    dbPath = generalDbFunctions.getDbPath(databaseName)
    if not os.path.exists(dbPath):
        return {
            "title": "Database Missing",
            "msg": f"Database '{databaseName}' not found.\nRun setup_database.py first."
        }
    try:
        conn = generalDbFunctions.connectDb(dbPath)
        try:

            cursor = conn.cursor()
            associatedTagIds:list[tuple] = tagDbFunctions.getTags(cursor) # type: ignore[type-arg]
            conn.commit()
        finally:
            conn.close()
        return associatedTagIds
    except sqlite3.Error as exc:
        return  {"title": "Database Error", "msg": f"SQLite error:\n{exc}"}


def removeTagAssociationHandler(databaseName:str, tagAssociationId: int)->None | dict[str,str]:
    dbPath = generalDbFunctions.getDbPath(databaseName)
    if not os.path.exists(dbPath):
        return {
            "title": "Database Missing",
            "msg": f"Database '{databaseName}' not found.\nRun setup_database.py first."
        }
    try:
        conn = generalDbFunctions.connectDb(dbPath)
        try:

            cursor = conn.cursor()
            tagDbFunctions.removeTagAssociation(cursor, tagAssociationId)
            conn.commit()
        finally:
            conn.close()
        return None
    except sqlite3.Error as exc:
        return  {"title": "Database Error", "msg": f"SQLite error:\n{exc}"}
