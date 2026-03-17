import sqlite3
import os


def connectDb(dbPath: str) -> sqlite3.Connection:
    """Connect to SQLite and enforce foreign keys."""
    conn = sqlite3.connect(dbPath)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def getDbPath(databaseName: str) -> str:
    """Resolve DB path relative to current working directory."""
    return os.path.join(os.getcwd(), databaseName)
