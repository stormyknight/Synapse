# pylint: disable=invalid-name
import sqlite3
from unittest.mock import MagicMock
from src.databaseModule import tagDbFunctions


# pylint: disable=invalid-name
def test_createTag() -> None:
    # mock cursor
    dummyCursor = MagicMock(spec=sqlite3.Cursor)
    dummyCursor.execute = MagicMock()
    tagDbFunctions.createTag(dummyCursor, "test")
    dummyCursor.execute.assert_called()


def test_associateTagWithNote() -> None:
    dummyCursor = MagicMock(spec=sqlite3.Cursor)
    dummyCursor.execute = MagicMock()
    tagDbFunctions.associateTagWithNote(dummyCursor, 1, 1)
    dummyCursor.execute.assert_called()


def test_getTagAssociations() -> None:
    dummyCursor = MagicMock(spec=sqlite3.Cursor)
    dummyCursor.execute = MagicMock()
    tagDbFunctions.getTagAssociations(dummyCursor, 1)
    dummyCursor.execute.assert_called()


def test_getSelectedTags() -> None:
    dummyCursor = MagicMock(spec=sqlite3.Cursor)
    dummyCursor.execute = MagicMock()
    tagDbFunctions.getSelectedTags(dummyCursor, [1])
    dummyCursor.execute.assert_called()


def test_getTags() -> None:
    dummyCursor = MagicMock(spec=sqlite3.Cursor)
    dummyCursor.execute = MagicMock()
    tagDbFunctions.getTags(dummyCursor)
    dummyCursor.execute.assert_called()


def test_removeTagAssociation() -> None:
    dummyCursor = MagicMock(spec=sqlite3.Cursor)
    dummyCursor.execute = MagicMock()
    tagDbFunctions.removeTagAssociation(dummyCursor, 1, 1)
    dummyCursor.execute.assert_called()


def test_removeAllNoteTagAssociations() -> None:
    dummyCursor = MagicMock(spec=sqlite3.Cursor)
    dummyCursor.execute = MagicMock()
    tagDbFunctions.removeAllNoteTagAssociations(dummyCursor, 1)
    dummyCursor.execute.assert_called()
