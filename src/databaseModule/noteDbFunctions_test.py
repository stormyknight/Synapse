# pylint: disable=invalid-name
from unittest.mock import MagicMock
import sqlite3

from src.databaseModule import noteDbFunctions


# test addNote
# pylint: disable=invalid-name
def test_addNote()-> None:
    # mock cursor
    dummyCursor = MagicMock(spec=sqlite3.Cursor)
    dummyCursor.execute = MagicMock()
    noteDbFunctions.addNote(dummyCursor, "Title", "content", "source")
    dummyCursor.execute.assert_called()


# test updateNote
# pylint: disable=invalid-name
def test_updateNotes()->None:
    # mock cursor
    dummyCursor = MagicMock(spec=sqlite3.Cursor)
    dummyCursor.execute = MagicMock()
    noteDbFunctions.updateNote(dummyCursor, 1, "Title", "content")
    dummyCursor.execute.assert_called()


# pylint: disable=invalid-name
def test_getNotes()->None:
    # mock cursor
    dummyCursor = MagicMock(spec=sqlite3.Cursor)
    dummyCursor.execute = MagicMock()
    noteDbFunctions.getNotes(dummyCursor)
    dummyCursor.execute.assert_called()


# pylint: disable=invalid-name
def test_getNote()->None:
    # mock cursor
    dummyCursor = MagicMock(spec=sqlite3.Cursor)
    dummyCursor.execute = MagicMock()
    noteDbFunctions.getNote(dummyCursor, 1)
    dummyCursor.execute.assert_called()


# pylint: disable=invalid-name
def test_deleteAnalysis() -> None:
    # mock cursor
    dummyCursor = MagicMock(spec=sqlite3.Cursor)
    dummyCursor.execute = MagicMock()
    noteDbFunctions.deleteAnalysis(dummyCursor, 1)
    dummyCursor.execute.assert_called()


# pylint: disable=invalid-name
def test_addAnalysis() -> None:
    # mock cursor
    dummyCursor = MagicMock(spec=sqlite3.Cursor)
    dummyCursor.execute = MagicMock()
    noteDbFunctions.addAnalysis(dummyCursor, 1, "summary", "mName", "V2", "output", "Json", "hash")
    dummyCursor.execute.assert_called()
