import os
import sqlite3
from src.databaseModule import generalDbFunctions, tagDbFunctions


def createTagHandler(name: str,  databaseName:str):
    dbPath = generalDbFunctions.getDbPath(databaseName)
    print(2)
    if not os.path.exists(dbPath):
        print(2.1)
        return {
            "title": "Database Missing",
            "msg": f"Database '{databaseName}' not found.\nRun setup_database.py first."
        }
    print(3)
    try:
        conn = generalDbFunctions.connectDb(dbPath)
        try:
            print(4)
            cursor = conn.cursor()
            tagId:int = tagDbFunctions.createTag(cursor, name) # type: ignore[type-arg]
            conn.commit()
        finally:
            conn.close()
        print(tagId)
        return tagId
    except sqlite3.Error as exc:
        return  {"title": "Database Error", "msg": f"SQLite error:\n{exc}"}

def associateTagWithNoteHandler(tagId: int, noteId: int, databaseName:str):
    dbPath = generalDbFunctions.getDbPath(databaseName)
    if not os.path.exists(dbPath):
        return {
            "title": "Database Missing",
            "msg": f"Database '{databaseName}' not found.\nRun setup_database.py first."
        }
    try:
        conn = generalDbFunctions.connectDb(dbPath)
        try:
            print(4)
            cursor = conn.cursor()
            associatedTagIds:int = tagDbFunctions.associateTagWithNote(cursor, tagId=tagId, noteId=noteId) # type: ignore[type-arg]
            conn.commit()
        finally:
            conn.close()
        print(associatedTagIds)
        return associatedTagIds
    except sqlite3.Error as exc:
        return  {"title": "Database Error", "msg": f"SQLite error:\n{exc}"}
    
def getAssociatedTagIdsHandler(noteId: int, databaseName:str)->list[int]|dict[str,str]:
    dbPath = generalDbFunctions.getDbPath(databaseName)
    if not os.path.exists(dbPath):
        return {
            "title": "Database Missing",
            "msg": f"Database '{databaseName}' not found.\nRun setup_database.py first."
        }
    try:
        conn = generalDbFunctions.connectDb(dbPath)
        try:
            print(4)
            cursor = conn.cursor()
            associatedTagIds:list[int] = tagDbFunctions.getAssociatedTagIds(cursor, noteId=noteId) # type: ignore[type-arg]
            conn.commit()
        finally:
            conn.close()
        return associatedTagIds
    except sqlite3.Error as exc:
        return  {"title": "Database Error", "msg": f"SQLite error:\n{exc}"}
    

def getSelectedTagsHandler(tagIds: list[int], databaseName:str)->list[tuple]|dict[str,str]:
    dbPath = generalDbFunctions.getDbPath(databaseName)
    if not os.path.exists(dbPath):
        return {
            "title": "Database Missing",
            "msg": f"Database '{databaseName}' not found.\nRun setup_database.py first."
        }
    try:
        conn = generalDbFunctions.connectDb(dbPath)
        try:
            print(4)
            cursor = conn.cursor()
            associatedTagIds:list[tuple] = tagDbFunctions.getSelectedTags(cursor, tagIds=tagIds) # type: ignore[type-arg]
            conn.commit()
        finally:
            conn.close()
        return associatedTagIds
    except sqlite3.Error as exc:
        return  {"title": "Database Error", "msg": f"SQLite error:\n{exc}"}