# pylint: disable=invalid-name
import sqlite3
from unittest.mock import MagicMock, patch
from src.logicModule import tagLogic


# pylint: disable=invalid-name
def test_fail_noPath_createTagHandler() -> None:
    assert tagLogic.createTagHandler("name", ":memory:") == { "title": "Database Missing", "msg": "Database ':memory:' not found.\nRun setup_database.py first." }


# pylint: disable=invalid-name
@patch("src.logicModule.tagLogic.os.path")
def test_fail_databaseError_createTagHandler(mock_path) -> None: # type: ignore [no-untyped-def]
    # mock exists return
    mock_path.exists = MagicMock()
    mock_path.exists.return_value = True

    assert tagLogic.createTagHandler("name", ":memory:") == {"title": "Database Error", "msg": "SQLite error:\nunable to open database file"}


@patch("src.logicModule.tagLogic.os.path")
@patch("src.logicModule.tagLogic.sqlite3.Connection")
@patch("src.logicModule.tagLogic.generalDbFunctions")
@patch("src.logicModule.tagLogic.tagDbFunctions")
# pylint: disable=invalid-name
def test_success_createTagHandler(mock_tagDbFunctions, mock_dbFunctions, mock_connection, mock_path) -> None: # type: ignore [no-untyped-def]
      # mock exists return
    mock_path.exists = MagicMock()
    mock_path.exists.return_value = True

    # mock cursor function
    dummyCursor = MagicMock(spec=sqlite3.Cursor)
    dummyCursor.lastrowid = 1
    mock_connection.cursor = MagicMock()
    mock_connection.cursor.return_value = dummyCursor

    # mock connectDb
    mock_dbFunctions.connectDb = MagicMock()
    mock_dbFunctions.connectDb.return_value = mock_connection

    # mock createTag
    mock_tagDbFunctions.createTag.return_value = 1

    assert type(tagLogic.createTagHandler("tag", ":memory:")) == int # pylint: disable=unidiomatic-typecheck


# pylint: disable=invalid-name
def test_fail_noPath_associateTagWithNoteHandler() -> None:
    assert tagLogic.associateTagWithNoteHandler(1, 1, ":memory:") == { "title": "Database Missing", "msg": "Database ':memory:' not found.\nRun setup_database.py first." }


# pylint: disable=invalid-name
@patch("src.logicModule.tagLogic.os.path")
def test_fail_databaseError_associateTagWithNoteHandler(mock_path) -> None: # type: ignore [no-untyped-def]
    # mock exists return
    mock_path.exists = MagicMock()
    mock_path.exists.return_value = True

    assert tagLogic.associateTagWithNoteHandler(1, 1, ":memory:") == {"title": "Database Error", "msg": "SQLite error:\nunable to open database file"}


@patch("src.logicModule.tagLogic.os.path")
@patch("src.logicModule.tagLogic.sqlite3.Connection")
@patch("src.logicModule.tagLogic.generalDbFunctions")
@patch("src.logicModule.tagLogic.tagDbFunctions")
# pylint: disable=invalid-name
def test_success_associateTagWithNoteHandler(mock_tagDbFunctions, mock_dbFunctions, mock_connection, mock_path) -> None: # type: ignore [no-untyped-def]
      # mock exists return
    mock_path.exists = MagicMock()
    mock_path.exists.return_value = True

    # mock cursor function
    dummyCursor = MagicMock(spec=sqlite3.Cursor)
    dummyCursor.lastrowid = 1
    mock_connection.cursor = MagicMock()
    mock_connection.cursor.return_value = dummyCursor

    # mock connectDb
    mock_dbFunctions.connectDb = MagicMock()
    mock_dbFunctions.connectDb.return_value = mock_connection

    # mock associateTagWithNote
    mock_tagDbFunctions.associateTagWithNote.return_value = 1

    assert type(tagLogic.associateTagWithNoteHandler(1, 1, ":memory:")) == int # pylint: disable=unidiomatic-typecheck


# pylint: disable=invalid-name
def test_fail_noPath_getTagAssociationsHandler() -> None:
    assert tagLogic.getTagAssociationsHandler(1, ":memory:") == { "title": "Database Missing", "msg": "Database ':memory:' not found.\nRun setup_database.py first." }


# pylint: disable=invalid-name
@patch("src.logicModule.tagLogic.os.path")
def test_fail_databaseError_getTagAssociationsHandler(mock_path) -> None: # type: ignore [no-untyped-def]
    # mock exists return
    mock_path.exists = MagicMock()
    mock_path.exists.return_value = True

    assert tagLogic.getTagAssociationsHandler(1, ":memory:") == {"title": "Database Error", "msg": "SQLite error:\nunable to open database file"}


@patch("src.logicModule.tagLogic.os.path")
@patch("src.logicModule.tagLogic.sqlite3.Connection")
@patch("src.logicModule.tagLogic.generalDbFunctions")
@patch("src.logicModule.tagLogic.tagDbFunctions")
# pylint: disable=invalid-name
def test_success_getTagAssociationsHandler(mock_tagDbFunctions, mock_dbFunctions, mock_connection, mock_path) -> None: # type: ignore [no-untyped-def]
      # mock exists return
    mock_path.exists = MagicMock()
    mock_path.exists.return_value = True

    # mock cursor function
    dummyCursor = MagicMock(spec=sqlite3.Cursor)
    mock_connection.cursor = MagicMock()
    mock_connection.cursor.return_value = dummyCursor

    # mock connectDb
    mock_dbFunctions.connectDb = MagicMock()
    mock_dbFunctions.connectDb.return_value = mock_connection

    # mock getTagAssociations
    mock_tagDbFunctions.getTagAssociations = MagicMock()
    mock_tagDbFunctions.getTagAssociations.return_value = [(0,"")]

    assert type(tagLogic.getTagAssociationsHandler(1, ":memory:")) == list # pylint: disable=unidiomatic-typecheck


# pylint: disable=invalid-name
def test_fail_noPath_getSelectedTagsHandler() -> None:
    assert tagLogic.getSelectedTagsHandler([1], ":memory:") == { "title": "Database Missing", "msg": "Database ':memory:' not found.\nRun setup_database.py first." }


# pylint: disable=invalid-name
@patch("src.logicModule.tagLogic.os.path")
def test_fail_databaseError_getSelectedTagsHandler(mock_path) -> None: # type: ignore [no-untyped-def]
    # mock exists return
    mock_path.exists = MagicMock()
    mock_path.exists.return_value = True

    assert tagLogic.getSelectedTagsHandler([1], ":memory:") == {"title": "Database Error", "msg": "SQLite error:\nunable to open database file"}


@patch("src.logicModule.tagLogic.os.path")
@patch("src.logicModule.tagLogic.sqlite3.Connection")
@patch("src.logicModule.tagLogic.generalDbFunctions")
@patch("src.logicModule.tagLogic.tagDbFunctions")
# pylint: disable=invalid-name
def test_success_getSelectedTagsHandler(mock_tagDbFunctions, mock_dbFunctions, mock_connection, mock_path) -> None: # type: ignore [no-untyped-def]
      # mock exists return
    mock_path.exists = MagicMock()
    mock_path.exists.return_value = True

    # mock cursor function
    dummyCursor = MagicMock(spec=sqlite3.Cursor)
    dummyCursor.lastrowid = [()]
    mock_connection.cursor = MagicMock()
    mock_connection.cursor.return_value = dummyCursor

    # mock connectDb
    mock_dbFunctions.connectDb = MagicMock()
    mock_dbFunctions.connectDb.return_value = mock_connection

    # mock getSelectedTags
    mock_tagDbFunctions.getSelectedTags = MagicMock()
    mock_tagDbFunctions.getSelectedTags.return_value = [(0,"")]

    assert type(tagLogic.getSelectedTagsHandler([1], ":memory:")) == list # pylint: disable=unidiomatic-typecheck


# pylint: disable=invalid-name
def test_fail_noPath_getTagsHandler() -> None:
    assert tagLogic.getTagsHandler(":memory:") == { "title": "Database Missing", "msg": "Database ':memory:' not found.\nRun setup_database.py first." }


# pylint: disable=invalid-name
@patch("src.logicModule.tagLogic.os.path")
def test_fail_databaseError_getTagsHandler(mock_path) -> None: # type: ignore [no-untyped-def]
    # mock exists return
    mock_path.exists = MagicMock()
    mock_path.exists.return_value = True

    assert tagLogic.getTagsHandler(":memory:") == {"title": "Database Error", "msg": "SQLite error:\nunable to open database file"}


@patch("src.logicModule.tagLogic.os.path")
@patch("src.logicModule.tagLogic.sqlite3.Connection")
@patch("src.logicModule.tagLogic.generalDbFunctions")
@patch("src.logicModule.tagLogic.tagDbFunctions")
# pylint: disable=invalid-name
def test_success_getTagsHandler(mock_tagDbFunctions, mock_dbFunctions, mock_connection, mock_path) -> None: # type: ignore [no-untyped-def]
      # mock exists return
    mock_path.exists = MagicMock()
    mock_path.exists.return_value = True

    # mock cursor function
    dummyCursor = MagicMock(spec=sqlite3.Cursor)
    dummyCursor.lastrowid = [()]
    mock_connection.cursor = MagicMock()
    mock_connection.cursor.return_value = dummyCursor

    # mock connectDb
    mock_dbFunctions.connectDb = MagicMock()
    mock_dbFunctions.connectDb.return_value = mock_connection

    # mock getSelectedTags
    mock_tagDbFunctions.getTags = MagicMock()
    mock_tagDbFunctions.getTags.return_value = [(0,"")]

    assert type(tagLogic.getTagsHandler(":memory:")) == list # pylint: disable=unidiomatic-typecheck


# pylint: disable=invalid-name
def test_fail_noPath_removeTagAssociationHandler() -> None:
    assert tagLogic.removeTagAssociationHandler(":memory:", 1, 1) == { "title": "Database Missing", "msg": "Database ':memory:' not found.\nRun setup_database.py first." }


# pylint: disable=invalid-name
@patch("src.logicModule.tagLogic.os.path")
def test_fail_databaseError_removeTagAssociationHandler(mock_path) -> None: # type: ignore [no-untyped-def]
    # mock exists return
    mock_path.exists = MagicMock()
    mock_path.exists.return_value = True

    assert tagLogic.removeTagAssociationHandler(":memory:", 1, 1) == {"title": "Database Error", "msg": "SQLite error:\nunable to open database file"}


@patch("src.logicModule.tagLogic.os.path")
@patch("src.logicModule.tagLogic.sqlite3.Connection")
@patch("src.logicModule.tagLogic.generalDbFunctions")
# pylint: disable=invalid-name
def test_success_removeTagAssociationHandler(mock_dbFunctions, mock_connection, mock_path) -> None: # type: ignore [no-untyped-def]
      # mock exists return
    mock_path.exists = MagicMock()
    mock_path.exists.return_value = True

    # mock cursor function
    dummyCursor = MagicMock(spec=sqlite3.Cursor)
    dummyCursor.lastrowid = [()]
    mock_connection.cursor = MagicMock()
    mock_connection.cursor.return_value = dummyCursor

    # mock connectDb
    mock_dbFunctions.connectDb = MagicMock()
    mock_dbFunctions.connectDb.return_value = mock_connection

    assert tagLogic.removeTagAssociationHandler(":memory:", 1, 1) is None # pylint: disable=unidiomatic-typecheck
