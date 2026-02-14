from pytestqt.qt_compat import qt_api
import mainScreen


# Test to see if the user can type in editableContentText
def test_EditableContentText(qtbot):
    # An instance of MainWindow used for testing
    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    qtbot.keyClicks(testMainScreen.editableContentText, "It worked")

    assert (
        testMainScreen.editableContentText.toPlainText() == "I tworked"
    ), "Text typed into editableContentText does not match expected text"
