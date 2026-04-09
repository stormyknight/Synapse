import os
import sqlite3
from src.databaseModule import generalDbFunctions, tagDbFunctions


def createTagHandler(name: str,  databaseName:str):
    dbPath = generalDbFunctions.getDbPath(databaseName)
    
    if not os.path.exists(dbPath):
        print(2.1)
        return {
            "title": "Database Missing",
            "msg": f"Database '{databaseName}' not found.\nRun setup_database.py first."
        }
    
    try:
        conn = generalDbFunctions.connectDb(dbPath)
        try:
            
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
            
            cursor = conn.cursor()
            associatedTagIds:int = tagDbFunctions.associateTagWithNote(cursor, tagId=tagId, noteId=noteId) # type: ignore[type-arg]
            conn.commit()
        finally:
            conn.close()
        print(associatedTagIds)
        return associatedTagIds
    except sqlite3.Error as exc:
        return  {"title": "Database Error", "msg": f"SQLite error:\n{exc}"}
    
def getTagAssociationsHandler(noteId: int, databaseName:str)->list[tuple]|dict[str,str]:
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
            tagAssociation:list[int] = tagDbFunctions.getTagAssociations(cursor, noteId=noteId) # type: ignore[type-arg]
            conn.commit()
        finally:
            conn.close()
        return tagAssociation
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
            
            cursor = conn.cursor()
            associatedTagIds:list[tuple] = tagDbFunctions.getSelectedTags(cursor, tagIds=tagIds) # type: ignore[type-arg]
            conn.commit()
        finally:
            conn.close()
        return associatedTagIds
    except sqlite3.Error as exc:
        return  {"title": "Database Error", "msg": f"SQLite error:\n{exc}"}
    
def getTagsHandler( databaseName:str)->list[tuple]|dict[str,str]:
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
            tagDbFunctions.removeTagAssociation(cursor, tagAssociationId) # type: ignore[type-arg]
            conn.commit()
        finally:
            conn.close()
        return None
    except sqlite3.Error as exc:
        return  {"title": "Database Error", "msg": f"SQLite error:\n{exc}"}