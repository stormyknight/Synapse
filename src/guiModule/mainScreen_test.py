# Synapse
# guiModule
# mainScreen_test.py
# pylint: disable=invalid-name


from unittest.mock import MagicMock, patch
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QHBoxLayout
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
    testMainScreen.resize(700, 500)
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
