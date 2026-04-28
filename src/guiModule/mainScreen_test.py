# Synapse
# guiModule
# mainScreen_test.py
# pylint: disable=invalid-name


from unittest.mock import MagicMock, patch
from PyQt5.QtGui import QResizeEvent, QCloseEvent
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QHBoxLayout, QMenu, QPushButton
# pylint: disable=invalid-name
from src.guiModule import mainScreen


# Test to see if the user can type in editableContentText
# pylint: disable=invalid-name
def test_EditableContentText(qtbot)->None: # type: ignore
    # An instance of MainWindow used for testing
    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    qtbot.keyClicks(testMainScreen.editableContentText, "It worked")
    assert (
        testMainScreen.editableContentText.toPlainText() == "It worked"
    ), "Text typed into editableContentText does not match expected text"


# Test to see if the user can type in editableContentText
# pylint: disable=invalid-name
def test_titleInput(qtbot) -> None: # type: ignore
     # An instance of MainWindow used for testing
    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    qtbot.keyClicks(testMainScreen.titleInput, "It worked")
    assert (
        testMainScreen.titleInput.toPlainText() == "It worked"
    ), "Text typed into editableContentText does not match expected text"


@patch("src.guiModule.mainScreen.noteLogic")
# Test to see that save button works
# pylint: disable=invalid-name
def test_saveButton(mock_noteLogic)->None: # type: ignore
     # An instance of MainWindow used for testing
    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    mock_noteLogic.onNoteSaveClicked.return_value = "Saved!1"

    testMainScreen.onSaveNoteClicked = MagicMock()

    testMainScreen.saveButton.click()

    assert (testMainScreen.statusLabel.text() != ""), "statusLabel is unchanged"


@patch("src.guiModule.mainScreen.noteLogic")
# Test to see that save button works
# pylint: disable=invalid-name
def test_saveButton_fail(mock_noteLogic)->None: # type: ignore
    # An instance of MainWindow used for testing
    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    mock_noteLogic.onNoteSaveClicked.return_value = {"title": "Database Missing", "msg": "Database X not found.\nRun setup_database.py first."}
    testMainScreen.onSaveNoteClicked = MagicMock()

    testMainScreen.saveButton.click()

    assert (testMainScreen.statusLabel.text() == "Save failed"), "statusLabel does not equal save failed."


# Test to see that resizeEvent works
# pylint: disable=invalid-name
def test_resizeEvent()->None:
    # An instance of MainWindow used for testing
    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    # A resize event to put into resizeEvent
    testEvent: QResizeEvent =  QResizeEvent(QSize(40,50), QSize(500,500))
    testMainScreen.adjustTitleHeight=MagicMock()
    testMainScreen.adjustMainPageColumnMax=MagicMock()
    testMainScreen.resizeEvent(testEvent)
    testMainScreen.adjustTitleHeight.assert_called()
    testMainScreen.adjustMainPageColumnMax.assert_called()


# Test to see that goToMainScreen works
# pylint: disable=invalid-name
def test_goToMainScreen()->None:
    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testMainScreen.goToMainScreen()
    assert  not testMainScreen.saveButton.isVisible()


# Test to see that exitButton works
# pylint: disable=invalid-name
def test_exitButton()->None:
    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testMainScreen.exitButton.click()
    assert  not testMainScreen.saveButton.isVisible()


# Test to see that adjustMainPageColumnMax works
# pylint: disable=invalid-name
def test_adjustMainPageColumnMax()->None:
    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    originalColumnNumber: int = testMainScreen.mainPageColumnMax
    testMainScreen.resize(2000, 500)
    testMainScreen.adjustMainPageColumnMax()
    newColumnNumber: int = testMainScreen.mainPageColumnMax
    assert originalColumnNumber != newColumnNumber


# Test to see that clearLayout works
# pylint: disable=invalid-name
def test_clearLayout()->None:
    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testMainScreen.homeLayout.addLayout(QHBoxLayout())
    mainScreen.clearLayout(testMainScreen.homeLayout)
    assert testMainScreen.homeLayout.count() == 0


# Test to see that openNoteFromCard works
# pylint: disable=invalid-name
@patch("src.guiModule.mainScreen.noteLogic")
def test_openNoteFromCard(mock_noteLogic)->None: # type: ignore[no-untyped-def]
    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    mock_noteLogic.getNoteHandler.return_value = (1, "title", "content")
    testMainScreen.openNoteFromCard(1)
    assert testMainScreen.titleInput.toPlainText() == "title"


# Test to see that getTagName works
# pylint: disable=invalid-name
@patch("src.guiModule.mainScreen.QInputDialog.getText")
@patch("src.guiModule.mainScreen.tagLogic.createTagHandler")
@patch("src.guiModule.mainScreen.tagLogic.associateTagWithNoteHandler")
@patch("src.guiModule.mainScreen.TagWindow.showCurrentTags")
def test_success_getTagName(mock_showCurrentTags, mock_associateTagWithNoteHandler, mock_createTagHandler, mock_getText) -> None: # type: ignore[no-untyped-def]
    mock_getText.return_value = ("test", True)
    mock_createTagHandler.return_value = 1
    mock_associateTagWithNoteHandler.return_value = 1

    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testTagWindow: mainScreen.TagWindow = mainScreen.TagWindow(testMainScreen)
    testTagWindow.getTagName()
    mock_showCurrentTags.assert_called()


# Test to see that getTagName works
# pylint: disable=invalid-name
@patch("src.guiModule.mainScreen.QInputDialog.getText")
@patch("src.guiModule.mainScreen.tagLogic.createTagHandler")
@patch("src.guiModule.mainScreen.QMessageBox.critical")
@patch("src.guiModule.mainScreen.tagLogic.associateTagWithNoteHandler")
def test_fail_associateTag_getTagName(mock_associateTagHandler, mock_critical, mock_createTagHandler, mock_getText) -> None: # type: ignore[no-untyped-def]
    mock_getText.return_value = ("test", True)
    mock_createTagHandler.return_value = 1
    mock_associateTagHandler.return_value = {"title": "", "msg": ""}

    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testTagWindow: mainScreen.TagWindow = mainScreen.TagWindow(testMainScreen)
    testTagWindow.getTagName()
    mock_critical.assert_called()


@patch("src.guiModule.mainScreen.QInputDialog.getText")
@patch("src.guiModule.mainScreen.tagLogic.createTagHandler")
@patch("src.guiModule.mainScreen.QMessageBox.critical")
def test_fail_createTag_getTagName(mock_critical, mock_createTagHandler, mock_getText) -> None: # type: ignore[no-untyped-def]
    mock_getText.return_value = ("test", True)
    mock_createTagHandler.return_value = {"title": "title", "msg": "msg"}

    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testTagWindow: mainScreen.TagWindow = mainScreen.TagWindow(testMainScreen)
    testTagWindow.getTagName()
    mock_critical.assert_called()


# Test to see that showCurrentTags works
# pylint: disable=invalid-name
@patch("src.guiModule.mainScreen.tagLogic.getTagAssociationsHandler")
@patch("src.guiModule.mainScreen.tagLogic.getSelectedTagsHandler")
def test_success_showCurrentTags(mock_getSelectedTagsHandler, mock_getTagAssociationsHandler) -> None: # type: ignore[no-untyped-def]
    mock_getTagAssociationsHandler.return_value = [(0, 1, 1)]
    mock_getSelectedTagsHandler.return_value = [(1, "test")]

    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testTagWindow: mainScreen.TagWindow = mainScreen.TagWindow(testMainScreen)

    testTagWindow.showCurrentTags()


# Test to see that showCurrentTags fails
# pylint: disable=invalid-name
@patch("src.guiModule.mainScreen.tagLogic.getTagAssociationsHandler")
@patch("src.guiModule.mainScreen.tagLogic.getSelectedTagsHandler")
@patch("src.guiModule.mainScreen.QMessageBox.critical")
def test_fail_getTagAssociationsHandler_showCurrentTags(mock_critical, mock_getSelectedTagsHandler, mock_getTagAssociationsHandler) -> None: # type: ignore[no-untyped-def]
    mock_getSelectedTagsHandler.return_value = []
    mock_getTagAssociationsHandler.return_value = {"title": "title", "msg": "msg"}

    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testTagWindow: mainScreen.TagWindow = mainScreen.TagWindow(testMainScreen)

    testTagWindow.showCurrentTags()
    mock_critical.assert_called()


# Test to see that showCurrentTags fails
# pylint: disable=invalid-name
@patch("src.guiModule.mainScreen.tagLogic.getTagAssociationsHandler")
@patch("src.guiModule.mainScreen.tagLogic.getSelectedTagsHandler")
@patch("src.guiModule.mainScreen.QMessageBox.critical")
def test_fail_getSelectedTagsHandler_showCurrentTags(mock_critical, mock_getSelectedTagsHandler, mock_getTagAssociationsHandler) -> None: # type: ignore[no-untyped-def]
    mock_getSelectedTagsHandler.return_value = {"title": "title", "msg": "msg"}
    mock_getTagAssociationsHandler.return_value = [(1, "test", 1)]

    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testTagWindow: mainScreen.TagWindow = mainScreen.TagWindow(testMainScreen)

    testTagWindow.showCurrentTags()
    mock_critical.assert_called()


# Test to see that showCurrentTags works
# pylint: disable=invalid-name
@patch("src.guiModule.mainScreen.tagLogic.getTagAssociationsHandler")
@patch("src.guiModule.mainScreen.tagLogic.getSelectedTagsHandler")
def test_success_showAvailableTags(mock_getSelectedTagsHandler, mock_getTagAssociationsHandler) -> None: # type: ignore[no-untyped-def]
    mock_getTagAssociationsHandler.return_value = [(0, 1, 1)]
    mock_getSelectedTagsHandler.return_value = [(1, "test")]

    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testTagWindow: mainScreen.TagWindow = mainScreen.TagWindow(testMainScreen)

    testTagWindow.showAvailableTags()


# Test to see that showCurrentTags fails
# pylint: disable=invalid-name
@patch("src.guiModule.mainScreen.tagLogic.getTagAssociationsHandler")
@patch("src.guiModule.mainScreen.tagLogic.getSelectedTagsHandler")
@patch("src.guiModule.mainScreen.QMessageBox.critical")
def test_fail_getTagAssociationsHandler_showAvailableTags(mock_critical, mock_getSelectedTagsHandler, mock_getTagAssociationsHandler) -> None: # type: ignore[no-untyped-def]
    mock_getSelectedTagsHandler.return_value = []
    mock_getTagAssociationsHandler.return_value = {"title": "title", "msg": "msg"}

    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testTagWindow: mainScreen.TagWindow = mainScreen.TagWindow(testMainScreen)

    testTagWindow.showAvailableTags()
    mock_critical.assert_called()


@patch("src.guiModule.mainScreen.tagLogic.removeTagAssociationHandler")
def test_success_removeTag(mock_removeTagAssociationHandler) -> None: # type: ignore[no-untyped-def]
    mock_removeTagAssociationHandler.return_value = None

    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testTagWindow: mainScreen.TagWindow = mainScreen.TagWindow(testMainScreen)

    assert testTagWindow.removeTag(1) is None


@patch("src.guiModule.mainScreen.tagLogic.removeTagAssociationHandler")
@patch("src.guiModule.mainScreen.QMessageBox.critical")
def test_fail_removeTag(mock_critical, mock_removeTagAssociationHandler) -> None: # type: ignore[no-untyped-def]
    mock_removeTagAssociationHandler.return_value = {"title": "title", "msg": "msg"}

    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testTagWindow: mainScreen.TagWindow = mainScreen.TagWindow(testMainScreen)

    testTagWindow.removeTag(1)
    mock_critical.assert_called()


@patch("src.guiModule.mainScreen.tagLogic.associateTagWithNoteHandler")
def test_success_associateTag(mock_associateTagWithNoteHandler) -> None: # type: ignore[no-untyped-def]
    mock_associateTagWithNoteHandler.return_value = 1

    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testTagWindow: mainScreen.TagWindow = mainScreen.TagWindow(testMainScreen)

    testTagWindow.associateTag(1, 1)


@patch("src.guiModule.mainScreen.tagLogic.associateTagWithNoteHandler")
@patch("src.guiModule.mainScreen.QMessageBox.critical")
def test_fail_associateTag(mock_critical, mock_associateTagWithNoteHandler) -> None: # type: ignore[no-untyped-def]
    mock_associateTagWithNoteHandler.return_value = {"title": "title", "msg": "msg"}

    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testTagWindow: mainScreen.TagWindow = mainScreen.TagWindow(testMainScreen)

    testTagWindow.associateTag(1, 1)
    mock_critical.assert_called()


def test_setCurrentNoteId() -> None:
    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testTagWindow: mainScreen.TagWindow = mainScreen.TagWindow(testMainScreen)

    testTagWindow.setCurrentNoteId(1)
    assert testTagWindow.currentNoteId == 1


@patch("src.guiModule.mainScreen.TagWindow.close")
def test_closeEvent(mock_close) -> None:  # type: ignore[no-untyped-def]
    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testMainScreen.closeEvent(QCloseEvent())
    mock_close.assert_called()


def test_createNewNote() -> None:
    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testMainScreen.currentNoteId = 1
    assert testMainScreen.currentNoteId == 1
    testMainScreen.createNewNote()
    assert testMainScreen.currentNoteId is None


def test_changeSortOrder() -> None:
    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testMainScreen.changeSortOrder("name")
    assert testMainScreen.currentSortMode == "name"


def test_tags_displayNotesOnHome() -> None:
    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testMainScreen.changeSortOrder("tag")
    assert testMainScreen.currentSortMode == "tag"


def test_showMenu() -> None:
    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testMainScreen.showMenu(QMenu(), QPushButton())


@patch("src.guiModule.mainScreen.QMessageBox.warning")
def test_fail_newNote_onAnalyzeNoteClicked(mock_warning) -> None: # type: ignore[no-untyped-def]
    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testMainScreen.onAnalyzeNoteClicked()
    mock_warning.assert_called()


@patch("src.guiModule.mainScreen.QMessageBox.warning")
def test_fail_noContent_onAnalyzeNoteClicked(mock_warning) -> None: # type: ignore[no-untyped-def]
    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testMainScreen.currentNoteId = 1
    testMainScreen.onAnalyzeNoteClicked()
    mock_warning.assert_called()


@patch("src.guiModule.mainScreen.noteLogic.analyzeAndStoreNote")
def test_fail_databaseError_onAnalyzeNoteClicked(mock_analyzeAndStoreNote) -> None: # type: ignore[no-untyped-def]
    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testMainScreen.currentNoteId = 1
    testMainScreen.editableContentText.setText("testing")
    testMainScreen.onAnalyzeNoteClicked()

    mock_analyzeAndStoreNote.return_value = 1
    assert testMainScreen.statusLabel.text() == "Analyze failed"


@patch("src.guiModule.mainScreen.QMessageBox.information")
@patch("src.guiModule.mainScreen.noteLogic.analyzeAndStoreNote")
def test_success_onAnalyzeNoteClicked(mock_analyzeAndStoreNote, mock_information) -> None: # type: ignore[no-untyped-def]
    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testMainScreen.currentNoteId = 1
    testMainScreen.editableContentText.setText("testing")
    mock_analyzeAndStoreNote.return_value = {  "summary": "summary", "tags": ["tags"], "mood": "mood" }
    testMainScreen.onAnalyzeNoteClicked()

    mock_information.assert_called()


@patch("src.guiModule.mainScreen.TagWindow.show")
def test_showTagWindow(mock_show) -> None: # type: ignore[no-untyped-def]
    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testMainScreen.showTagWindow(1)
    mock_show.assert_called()


@patch("src.guiModule.mainScreen.QMessageBox.question")
def test_success_deleteNoteFunction(mock_question) -> None: # type: ignore[no-untyped-def]
    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testMainScreen.deleteNoteFunction(1)

    mock_question.assert_called()


@patch("src.guiModule.mainScreen.noteLogic.deleteNoteHandler")
@patch("src.guiModule.mainScreen.QMessageBox.critical")
def test_faile_deleteNoteFunction(mock_critical, mock_deleteNoteHandler) -> None: # type: ignore[no-untyped-def]
    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testMainScreen.deleteNoteFunction(1)

    mock_deleteNoteHandler.return_value = {"title": "", "msg": ""}

    mock_critical.assert_called()
