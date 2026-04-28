# Synapse
# logicModule
# noteLogic_test.py
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

    assert type(noteLogic.onNoteSaveClicked("title", "content", ":memory:", -1)) == str # pylint: disable=unidiomatic-typecheck


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
    assert type(noteLogic.onNoteSaveClicked("", "content", ":memory:", None)) == str # pylint: disable=unidiomatic-typecheck


@patch("src.logicModule.noteLogic.os.path")
@patch("src.logicModule.noteLogic.sqlite3.Connection")
@patch("src.logicModule.noteLogic.generalDbFunctions")
# test a successful onNoteSaveClicked update
# pylint: disable=invalid-name
def test_successful_update_onNoteSaveClicked(mock_dbFunctions, mock_connection, mock_path): # type: ignore
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

    assert type(noteLogic.onNoteSaveClicked("title", "content", ":memory:", 1)) == str # pylint: disable=unidiomatic-typecheck


# test onNoteSaveClicked when it fails due to no content
# pylint: disable=invalid-name
def test_fail_noContent_onNoteSaveClicked(): # type:ignore
    assert noteLogic.onNoteSaveClicked("", "", ":memory:", None) == {"title": "Cannot Save", "msg": "Note content is required."}


# test onNoteSaveClicked when it fails trying to update a note with the title removed
# pylint: disable=invalid-name
def test_fail_title_removed_onNoteSaveClicked(): # type:ignore
    assert noteLogic.onNoteSaveClicked("", "", ":memory:", 1) == {"title": "Cannot Save", "msg": "Error finding title."}


# test onNoteSaveClicked when it fails when it can't find the database
# pylint: disable=invalid-name
def test_fail_noPath_onNoteSaveClicked(): # type:ignore
    assert noteLogic.onNoteSaveClicked("title", "content    ", ":memory:", 1) == {"title": "Database Missing", "msg": "Database ':memory:' not found.\nRun setup_database.py first."}


# test onNoteSaveClicked when it fails when there is a database error
# pylint: disable=invalid-name
@patch("src.logicModule.noteLogic.os.path")
def test_fail_dbError_onNoteSaveClicked( mock_path): # type:ignore
    # mock exists return
    mock_path.exists = MagicMock()
    mock_path.exists.return_value = True

    assert noteLogic.onNoteSaveClicked("title", "content    ", ":memory:", None) == {"title": "Database Error", "msg": "SQLite error:\nunable to open database file"}


# test getNotesHandler when it fails when it can't find the database
# pylint: disable=invalid-name
def test_fail_noPath_getNotesHandler()->None:
    assert noteLogic.getNotesHandler(":memory:") == {"title": "Database Missing", "msg": "Database '{databaseName}' not found.\nRun setup_database.py first."}


# test getNotesHandler when it fails when there is a database error
# pylint: disable=invalid-name
@patch("src.logicModule.noteLogic.os.path")
def test_fail_dbError_getNotesHandler( mock_path): # type:ignore
    # mock exists return
    mock_path.exists = MagicMock()
    mock_path.exists.return_value = True

    assert noteLogic.getNotesHandler(":memory:") == {"title": "Database Error", "msg": "SQLite error:\nunable to open database file"}


@patch("src.logicModule.noteLogic.os.path")
@patch("src.logicModule.noteLogic.sqlite3.Connection")
@patch("src.logicModule.noteLogic.generalDbFunctions")
@patch("src.logicModule.noteLogic.noteDbFunctions")
# test a successful getNotes
# pylint: disable=invalid-name
def test_successful_getNotesHandler(mock_noteDbFunctions, mock_dbFunctions, mock_connection, mock_path): # type: ignore
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

    # mock getNotes return
    mock_noteDbFunctions.getNotes.return_value = []

    assert type(noteLogic.getNotesHandler(":memory:")) == list # pylint: disable=unidiomatic-typecheck


@patch("src.logicModule.noteLogic.os.path")
@patch("src.logicModule.noteLogic.sqlite3.Connection")
@patch("src.logicModule.noteLogic.generalDbFunctions")
@patch("src.logicModule.noteLogic.noteDbFunctions")
# test a successful getNotes
# pylint: disable=invalid-name
def test_successful_getNoteHandler(mock_noteDbFunctions, mock_dbFunctions, mock_connection, mock_path): # type: ignore
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

    # mock getNotes return
    mock_noteDbFunctions.getNote.return_value = ()

    assert type(noteLogic.getNoteHandler(":memory:", 1)) == tuple # pylint: disable=unidiomatic-typecheck


# test getNoteHandler when it fails when it can't find the database
# pylint: disable=invalid-name
def test_fail_noPath_getNoteHandler()->None:
    assert noteLogic.getNoteHandler(":memory:",1) == {"title": "Database Missing", "msg": "Database '{databaseName}' not found.\nRun setup_database.py first."}


# test getNoteHandler when it fails when there is a database error
# pylint: disable=invalid-name
@patch("src.logicModule.noteLogic.os.path")
def test_fail_dbError_getNoteHandler( mock_path): # type:ignore
    # mock exists return
    mock_path.exists = MagicMock()
    mock_path.exists.return_value = True

    assert noteLogic.getNoteHandler(":memory:", 1) == {"title": "Database Error", "msg": "SQLite error:\nunable to open database file"}


# pylint: disable=invalid-name
@patch("src.logicModule.noteLogic.LLM_Helper")
def test_summarizeNoteContent(mock_heper) -> None:  # type: ignore[no-untyped-def]

    # mock llm_helper return
    mock_heper.generateSummary = MagicMock()
    mock_heper.generateSummary.return_value = "content"

    assert noteLogic.summarizeNoteContent("content") == "content"


# pylint: disable=invalid-name
@patch("src.logicModule.noteLogic.LLM_Helper")
def test_suggestTagsForNote(mock_helper) -> None: # type: ignore[no-untyped-def]
    # mock llm_helper return
    mock_helper.generateTags = MagicMock()
    mock_helper.generateTags.return_value = "content"

    assert noteLogic.suggestTagsForNote("content") == "content"


# pylint: disable=invalid-name
@patch("src.logicModule.noteLogic.LLM_Helper")
def test_detectMoodForNote(mock_helper) -> None: # type: ignore[no-untyped-def]
    # mock llm_helper return
    mock_helper.generateMood = MagicMock()
    mock_helper.generateMood.return_value = "content"

    assert noteLogic.detectMoodForNote("content") == "content"


# pylint: disable=invalid-name
def test_faile_noPath_analyzeAndStoreNote() -> None:
    assert noteLogic.analyzeAndStoreNote(1, "content", ":memory:") == { "summary": "Database not found.", "tags": [], "mood": "unavailable"}


# pylint: disable=invalid-name
@patch("src.logicModule.noteLogic.os.path")
@patch("src.logicModule.noteLogic.sqlite3.Connection")
@patch("src.logicModule.noteLogic.generalDbFunctions")
@patch("src.logicModule.noteLogic.LLM_Helper")
def test_success_analyzeAndStoreNote(mock_LLM_Helper, mock_dbFunctions, mock_connection, mock_path) -> None: # type: ignore[no-untyped-def]
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

    # mock analyze_note
    mock_LLM_Helper.analyzeNote = MagicMock()
    mock_LLM_Helper.analyzeNote.return_value = {"summary": "", "mood": "", "tags": []}

    assert noteLogic.analyzeAndStoreNote(1, "content", ":memory:") == {"summary": "", "mood": "", "tags": []}


# pylint: disable=invalid-name
@patch("src.logicModule.noteLogic.os.path")
@patch("src.logicModule.noteLogic.sqlite3.Connection")
@patch("src.logicModule.noteLogic.generalDbFunctions")
@patch("src.logicModule.noteLogic.LLM_Helper")
def test_fail_noTags_analyzeAndStoreNote(mock_LLM_Helper, mock_dbFunctions, mock_connection, mock_path) -> None: # type: ignore[no-untyped-def]
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

    # mock analyze_note
    mock_LLM_Helper.analyzeNote = MagicMock()
    mock_LLM_Helper.analyzeNote.return_value = {"summary": "", "mood": "", "tags": [""]}

    assert noteLogic.analyzeAndStoreNote(1, "content", ":memory:") == {"summary": "", "mood": "", "tags": [""]}

# pylint: disable=invalid-name
@patch("src.logicModule.noteLogic.os.path")
@patch("src.logicModule.noteLogic.sqlite3.Connection")
@patch("src.logicModule.noteLogic.generalDbFunctions")
@patch("src.logicModule.noteLogic.noteDbFunctions")
def test_success_deleteNoteHandler(mock_noteDbFunctions, mock_dbFunctions, mock_connection, mock_path) -> None:
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

    # mock deleteNote
    mock_noteDbFunctions.deleteNote.return_value = None

    assert noteLogic.deleteNoteHandler(1, ":memory:") is None
