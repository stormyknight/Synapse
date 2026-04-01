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
