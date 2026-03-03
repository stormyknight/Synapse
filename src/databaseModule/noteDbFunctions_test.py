# pylint: disable=invalid-name
from unittest.mock import MagicMock
import sqlite3

from src.databaseModule import noteDbFunctions


# test addNote
# pylint: disable=invalid-name
def test_addNote()-> None:
    # mock cursor
    dummy_cursor = MagicMock(spec=sqlite3.Cursor)
    dummy_cursor.execute = MagicMock()
    noteDbFunctions.addNote(dummy_cursor, "Title", "content", "source")
    dummy_cursor.execute.assert_called()
