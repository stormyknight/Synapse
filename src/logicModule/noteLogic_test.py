# pylint: disable=invalid-name
import sqlite3
from typing import Any
from unittest.mock import MagicMock, patch
from src.logicModule import noteLogic


class DummyNow():
    # the fummyVar is because now() normally takes a parameter in adition to self and it will not work if that argument isn't there. It serves no other purpose
    # pylint: disable=unused-argument
    def strftime(self, dummyVar:Any)->str:
        return "date"


@patch("src.logicModule.noteLogic.datetime")
# testing makeDefaultTitle
# pylint: disable=invalid-name
def test_makeDefaultTitle(mock_datetime)->None: # type:ignore
    # setting datetime.now() return value to dummy value
    mock_datetime.now.return_value = DummyNow()

    assert noteLogic.makeDefaultTitle() == "Untitled Note (date)", "makeDefultTitle failed"


@patch("src.logicModule.noteLogic.os.path")
@patch("src.logicModule.noteLogic.sqlite3.Connection")
@patch("src.logicModule.noteLogic.generalDbFunctions")
# test a successful onNoteSaveClicked with a title
# pylint: disable=invalid-name
def test_successful_onNoteSaveClicked(mock_dbFunctions, mock_connection, mock_path): # type: ignore
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

    assert type(noteLogic.onNoteSaveClicked("title", "content", ":memory:")) == str # pylint: disable=unidiomatic-typecheck


@patch("src.logicModule.noteLogic.os.path")
@patch("src.logicModule.noteLogic.sqlite3.Connection")
@patch("src.logicModule.noteLogic.generalDbFunctions")
# test a successful onNoteSaveClicked with no title
# pylint: disable=invalid-name
def test_successful_noTitle_onNoteSaveClicked(mock_dbFunctions, mock_connection, mock_path): # type: ignore
    # mock exists return
    mock_path.exists = MagicMock()
    mock_path.exists.return_value = True

    # mock cursor function
    dummy_cursor = MagicMock(spec=sqlite3.Cursor)
    mock_connection.cursor = MagicMock()
    mock_connection.cursor.return_value = dummy_cursor

    # mock connectDb
    mock_dbFunctions.connectDb = MagicMock()
    mock_dbFunctions.connectDb.return_value = mock_connection

    assert type(noteLogic.onNoteSaveClicked("", "content", ":memory:")) == str # pylint: disable=unidiomatic-typecheck


# test onNoteSaveClicked when it fails due to no content
# pylint: disable=invalid-name
def test_fail_noContent_onNoteSaveClicked(): # type:ignore
    assert noteLogic.onNoteSaveClicked("", "", ":memory:") == {"title": "Cannot Save", "msg": "Note content is required."}


# test onNoteSaveClicked when it fails when it can't find the database
# pylint: disable=invalid-name
def test_fail_noPath_onNoteSaveClicked(): # type:ignore
    assert noteLogic.onNoteSaveClicked("title", "content    ", ":memory:") == {"title": "Database Missing", "msg": "Database '{databaseName}' not found.\nRun setup_database.py first."}


# test onNoteSaveClicked when it fails when there is a database error
# pylint: disable=invalid-name
@patch("src.logicModule.noteLogic.os.path")
def test_fail_dbError_onNoteSaveClicked( mock_path): # type:ignore
    # mock exists return
    mock_path.exists = MagicMock()
    mock_path.exists.return_value = True

    assert noteLogic.onNoteSaveClicked("title", "content    ", ":memory:") == {"title": "Database Error", "msg": "SQLite error:\nunable to open database file"}
