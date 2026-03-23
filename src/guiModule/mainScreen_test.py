# Synapse
# guiModule
# mainScreen_test.py
# pylint: disable=invalid-name


from unittest.mock import MagicMock, patch
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtCore import QSize

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
    mock_noteLogic.onNoteSaveClicked.return_value = "Saved!"

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


# Test to see that save button works
# pylint: disable=invalid-name
def test_resizeEvent()->None:
    # An instance of MainWindow used for testing
    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    # A resize event to put into resizeEvent
    testEvent: QResizeEvent =  QResizeEvent(QSize(40,50), QSize(50,500))
    testMainScreen.adjustTitleHeight=MagicMock()
    testMainScreen.resizeEvent(testEvent)
    testMainScreen.adjustTitleHeight.assert_called()


# pylint: disable=invalid-name
def test_goToMainScreen()->None:
    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testMainScreen.goToMainScreen()
    assert  not testMainScreen.saveButton.isVisible()


# pylint: disable=invalid-name
def test_exitButton()->None:
    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    testMainScreen.exitButton.click()
    assert  not testMainScreen.saveButton.isVisible()
